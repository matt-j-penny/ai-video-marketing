// yt-feed-research page helpers.
// Paste this WHOLE file into one javascript_tool call after EVERY navigation
// (page loads wipe window.* state). Then call the helpers in later calls.
//
// window.__extract()          -> array of "ix | id | title | channel | views | age | vph | mult | subs" rows
//                                (also cached on window.__rows; page through it in slices — see SKILL.md)
// window.__dismissAny(ix, mode) -> 'video' = Not interested, 'channel' = Don't recommend channel
//                                returns "ix:ok" | "ix:already" | "ix:no-item" | "ix:no-btn" | "ix:no-entry"
//                                (no-item = no tile at that index; no-entry = the menu opened but had no
//                                entry for the requested mode. Channel mode never falls back to the video
//                                entry: a "Don't recommend channel"-less menu returns no-entry, and the
//                                caller decides whether to run 'video' instead.)
//
// All matching assumes the English YouTube UI (menu text 'Not interested' / '... recommend',
// aria-labels 'More actions' / 'Action menu' / 'More', ' views', ' ago', 'VPH', 'Subscribers').

const clean = s => (s||'').replace(/[^\w\s.,:'&()!?$%+-]/g,'').trim();

window.__extract = () => {
  const items = [...document.querySelectorAll('ytd-rich-item-renderer')];
  return window.__rows = items.map((el, ix) => {
    if (el.querySelector('ytd-ad-slot-renderer')) return null;               // skip ads
    const hrefs = [...el.querySelectorAll('a')].map(a => a.getAttribute('href')||'');
    const id  = ((hrefs.find(h=>h.includes('/watch'))||'').match(/v=([\w-]{11})/)||[])[1];
    const sid = ((hrefs.find(h=>h.includes('/shorts/'))||'').match(/shorts\/([\w-]{11})/)||[])[1];
    if (!id && !sid) return null;                                            // dismissed/empty tiles
    const t = (el.innerText||'').replace(/\n+/g,'~');
    const lines = t.split('~').map(clean).filter(Boolean);
    const durIx = lines.findIndex(l=>/^\d+(:\d+)+$/.test(l));                // duration line precedes title
    const title = clean(lines[durIx+1]||lines[0]).slice(0,70);
    const chan  = clean(lines[durIx+2]).slice(0,25);
    const views = (t.match(/([\d.,]+[KMB]?) views/)||[])[1]||'?';
    const age   = (t.match(/(\d+ \w+ ago)/)||[])[1]||'?';
    // VidIQ badges (absent on shorts): views-per-hour, outlier multiplier, channel subs
    const vph   = (t.match(/([\d.,]+[KMB]?) VPH/)||[])[1]||'-';
    const mult  = (t.match(/~([\d.]+)x(?:~|$)/)||[])[1]||'-';
    const subs  = (t.match(/([\d.,]+[KMB]?)~Subscribers/)||[])[1]||'-';
    return [ix, sid?('S_'+sid):id, title, chan, views, age, vph+'vph', mult+'x', subs+'subs'].join(' | ');
  }).filter(Boolean);
};

// The 3-dot menu renders in one of THREE markups depending on tile type/AB bucket:
// classic ytd-menu-service-item-renderer, new yt-lockup yt-list-item-view-model,
// or a plain-button overlay. Search all three, visible elements only.
window.__pickEntry = (mode) => {
  const vis = e => { const r = e.getBoundingClientRect(); return r.width>0 && r.height>0; };
  const want = mode==='channel' ? 'recommend' : 'Not interested';
  const pools = [
    ...document.querySelectorAll('ytd-menu-service-item-renderer, yt-list-item-view-model'),
    ...document.querySelectorAll('ytd-popup-container button, tp-yt-iron-dropdown button, body > div button')
  ];
  // One path per mode: no falling back to the video entry when channel mode finds nothing.
  const entry = pools.find(e => (e.innerText||'').includes(want) && vis(e) && (e.innerText||'').length < 60);
  return entry || null;
};

window.__dismissAny = async (ix, mode) => {
  const el = [...document.querySelectorAll('ytd-rich-item-renderer')][ix];
  if (!el) return ix+':no-item';
  const t0 = (el.innerText||'');
  // idempotent: safe to re-run after a CDP timeout (the page-side loop usually finished anyway)
  if (t0.includes('removed') || t0.includes("won't recommend") || t0.includes('Feedback shared')) return ix+':already';
  const btn = el.querySelector('button[aria-label="More actions"], button[aria-label="Action menu"], button[aria-label="More"]');
  if (!btn) return ix+':no-btn';
  el.scrollIntoView({block:'center'});
  await new Promise(r=>setTimeout(r,300));
  btn.click();
  await new Promise(r=>setTimeout(r,800));
  const entry = window.__pickEntry(mode);
  if (!entry) { document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'})); return ix+':no-entry'; }
  entry.click();
  await new Promise(r=>setTimeout(r,400));
  return ix+':ok';
};
'helpers injected'
