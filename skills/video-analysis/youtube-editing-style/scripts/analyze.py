#!/usr/bin/env python3
"""Download footage and analyze actual MP4 video through OpenRouter. Stdlib only."""
import argparse
import base64
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

MODEL = 'google/gemini-3.8-flash'
API = 'https://openrouter.ai/api/v1/chat/completions'


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def key():
    value = os.getenv('OPENROUTER_API_KEY')
    if value:
        return value
    try:
        value = json.loads((Path.home()/'.claude/settings.json').read_text()).get('env', {}).get('OPENROUTER_API_KEY')
        if isinstance(value, str) and value.strip():
            return value.strip()
    except (OSError, ValueError, AttributeError):
        pass
    raise RuntimeError('No OpenRouter key: set OPENROUTER_API_KEY or configure env.OPENROUTER_API_KEY in ~/.claude/settings.json.')


def run(args):
    subprocess.run(args, check=True)


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))


def read_stream(response, raw_path):
    parts, usage, events = [], {}, []
    finish, done = None, False
    with raw_path.open('wb') as raw:
        for line in response:
            raw.write(line)
            raw.flush()
            line = line.decode('utf-8').strip()
            if not line.startswith('data:'):
                continue
            data = line[5:].strip()
            if data == '[DONE]':
                done = True
                break
            event = json.loads(data)
            events.append(event)
            if event.get('error'):
                raise RuntimeError(f'OpenRouter stream error: {event["error"]}')
            if event.get('usage'):
                usage = event['usage']
            for choice in event.get('choices', []):
                value = choice.get('delta', {}).get('content')
                if isinstance(value, str):
                    parts.append(value)
                if choice.get('finish_reason'):
                    finish = choice['finish_reason']
    text = ''.join(parts)
    if not done or finish != 'stop' or not text.strip():
        raw_path.with_suffix('.partial.md').write_text(text, encoding='utf-8')
        raise RuntimeError(f'Incomplete stream: done={done}, finish={finish}, text characters={len(text)}. Raw stream retained; no automatic retry.')
    return {'choices': [{'message': {'content': text}, 'finish_reason': finish}], 'usage': usage,
            'id': next((e.get('id') for e in events if e.get('id')), None)}


def request(content, model, api_key, response_path):
    payload = {'model': model, 'messages': [{'role': 'user', 'content': content}],
               'stream': True, 'max_tokens': 16000, 'temperature': 0.2,
               'provider': {'require_parameters': True}}
    req = urllib.request.Request(API, data=json.dumps(payload).encode(), headers={
        'Authorization': 'Bearer '+api_key, 'Content-Type': 'application/json',
        'Accept': 'text/event-stream', 'X-Title': 'YouTube Editing Style'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=900) as response:
            write_json(response_path.with_suffix('.headers.json'), {
                'content_type': response.headers.get('Content-Type'),
                'generation_id': response.headers.get('X-Generation-Id')})
            result = read_stream(response, response_path.with_suffix('.raw.txt'))
    except urllib.error.HTTPError as exc:
        response_path.with_suffix('.raw.txt').write_bytes(exc.read())
        raise RuntimeError(f'OpenRouter HTTP {exc.code}; raw error retained, no automatic retry.') from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError('OpenRouter connection failed or timed out; raw stream retained if available; no automatic retry.') from None
    write_json(response_path, result)
    return result['choices'][0]['message']['content'], result['usage']


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source')
    p.add_argument('--out-dir', required=True, type=Path)
    p.add_argument('--model', default=MODEL)
    p.add_argument('--focus', default='')
    p.add_argument('--first-seconds', type=float, help='Analyze only this many seconds from the start')
    p.add_argument('--clip-seconds', type=int, default=180)
    p.add_argument('--processing', choices=['agentic', 'static', 'default'], default='agentic')
    p.add_argument('--prepare-only', action='store_true')
    p.add_argument('--resume', action='store_true')
    a = p.parse_args()
    if not 10 <= a.clip_seconds <= 300:
        p.error('--clip-seconds must be between 10 and 300')
    for name in ['ffmpeg', 'ffprobe'] + (['yt-dlp'] if a.source.startswith(('https://', 'http://')) else []):
        if not shutil.which(name):
            raise RuntimeError(f'Missing dependency: {name}')
    if a.first_seconds is not None and (not math.isfinite(a.first_seconds) or a.first_seconds <= 0):
        p.error('--first-seconds must be a positive finite number')
    api_key = None if a.prepare_only else key()
    folder = a.out_dir.expanduser().resolve()
    config = {'source': a.source, 'model': a.model, 'focus': a.focus, 'clip_seconds': a.clip_seconds, 'processing': a.processing, 'first_seconds': a.first_seconds}
    prompt = (Path(__file__).resolve().parents[1]/'references/analysis-prompt.md').read_text()
    config['analysis_prompt'] = prompt
    config_path = folder/'config.json'
    if folder.exists() and any(folder.iterdir()):
        if not a.resume or not config_path.exists() or json.loads(config_path.read_text()) != config:
            raise RuntimeError('Output directory is not empty. Use a fresh directory, or --resume with the identical configuration.')
    folder.mkdir(parents=True, exist_ok=True)
    write_json(config_path, config)
    (folder/'prompt.md').write_text(prompt, encoding='utf-8')
    source = folder/'source.mp4'
    if not source.exists():
        if a.source.startswith(('https://', 'http://')):
            print('Downloading source with yt-dlp...', flush=True)
            run(['yt-dlp', '--no-playlist', '--no-progress', '--write-info-json',
                 '-f', 'bv*[height<=1080]+ba/b[height<=1080]/best', '--merge-output-format', 'mp4',
                 '--remux-video', 'mp4', '-o', str(folder/'source.%(ext)s'), '--', a.source])
        else:
            local = Path(a.source).expanduser().resolve()
            if not local.is_file():
                raise RuntimeError('Local source does not exist.')
            run(['ffmpeg', '-v', 'error', '-n', '-i', str(local), '-map', '0:v:0', '-map', '0:a:0?',
                 '-c:v', 'libx264', '-crf', '18', '-c:a', 'aac', str(source)])
    media = probe(source)
    duration = float(media['format']['duration'])
    if not math.isfinite(duration) or duration <= 0 or not any(s['codec_type']=='video' for s in media['streams']):
        raise RuntimeError('Source is not a valid finite video.')
    source_duration = duration
    if a.first_seconds is not None:
        duration = min(duration, a.first_seconds)
    clips = []
    start = 0.0
    while start < duration:
        length = min(a.clip_seconds, duration-start)
        clips.append({'index': len(clips)+1, 'start': start, 'duration': length})
        if start+length >= duration:
            break
        start += a.clip_seconds-2
    manifest_path = folder/'manifest.json'
    old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest = {**config, 'duration': duration, 'source_duration': source_duration, 'has_audio': any(s['codec_type']=='audio' for s in media['streams']),
                'clips': clips, 'usage': old.get('usage', {}), 'status': 'preparing'}
    write_json(manifest_path, manifest)
    reports = []
    for clip in clips:
        stem = f'clip-{clip["index"]:03d}'
        mp4 = folder/(stem+'.mp4')
        if not mp4.exists():
            print(f'Preparing {stem} at {clip["start"]:.1f}s...', flush=True)
            temp = folder/(stem+'.tmp.mp4')
            run(['ffmpeg', '-v', 'error', '-y', '-i', str(source), '-ss', str(clip['start']), '-t', str(clip['duration']),
                 '-map', '0:v:0', '-map', '0:a:0?', '-vf', "scale=w='min(1280,iw)':h='min(720,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2",
                 '-c:v', 'libx264', '-preset', 'fast', '-b:v', '600k', '-maxrate', '800k', '-bufsize', '1600k',
                 '-c:a', 'aac', '-b:a', '80k', '-movflags', '+faststart', str(temp)])
            probe(temp)
            temp.replace(mp4)
        if mp4.stat().st_size > 24*1024*1024:
            raise RuntimeError(f'{stem} exceeds the local 24 MiB upload guard. Use a fresh run with shorter --clip-seconds.')
        if a.prepare_only:
            continue
        report = folder/(stem+'.md')
        response_path = folder/(stem+'.response.json')
        if not report.exists():
            if response_path.exists():
                raise RuntimeError(f'{response_path} already exists without a completed report. Inspect it before repeating a potentially billed call.')
            print(f'Analyzing {stem} ({clip["index"]}/{len(clips)}) with {a.model}...', flush=True)
            context = (f'Original video duration: {duration:.3f} seconds. This clip starts at {clip["start"]:.3f} '
                       f'seconds and lasts {clip["duration"]:.3f} seconds. Add that start offset to ALL reported timestamps. '
                       f'Audio track present: {manifest["has_audio"]}. User focus: {a.focus or "Complete editing style"}.\n\n')
            video = {'url': 'data:video/mp4;base64,'+base64.b64encode(mp4.read_bytes()).decode()}
            if a.processing != 'default':
                video['processing'] = a.processing
            text, usage = request([{'type': 'text', 'text': context+prompt}, {'type': 'video_url', 'video_url': video}],
                                  a.model, api_key, response_path)
            report.write_text(text, encoding='utf-8')
            manifest['usage'][stem] = usage
            write_json(manifest_path, manifest)
        reports.append(report.read_text())
    if a.prepare_only:
        manifest['status'] = 'prepared'
    else:
        guide = folder/'guide.md'
        if not guide.exists():
            if len(reports)==1:
                guide.write_text(reports[0], encoding='utf-8')
            else:
                response_path = folder/'synthesis.response.json'
                if response_path.exists():
                    raise RuntimeError('A synthesis response already exists; inspect it before repeating the call.')
                print('Synthesizing the whole-video recreation guide...', flush=True)
                synthesis = ('Combine the following sequential clip analyses into ONE cohesive whole-video editing style guide. '
                             'You are synthesizing evidence, not viewing the video again. Preserve original timestamps, uncertainties and '
                             'coverage gaps; deduplicate 2-second clip overlaps. Separate repeated motifs from isolated techniques, and '
                             'do not invent observations or turn suggested settings into measurements. Include all 12 sections specified '
                             'below, plus a concrete tool-agnostic recreation workflow and sample beat plan.\n\n'+prompt+
                             '\n\nCLIP REPORTS:\n\n'+'\n\n---\n\n'.join(reports))
                text, usage = request([{'type': 'text', 'text': synthesis}], a.model, api_key, response_path)
                guide.write_text(text, encoding='utf-8')
                manifest['usage']['synthesis'] = usage
        manifest['status'] = 'complete'
    write_json(manifest_path, manifest)
    print(str(folder/('manifest.json' if a.prepare_only else 'guide.md')))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
