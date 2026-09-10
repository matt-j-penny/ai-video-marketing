// ig-feed-research page helpers — home-feed loop (live-calibrated 2026-07-12).
// Paste this WHOLE file into one javascript_tool call after EVERY navigation
// (page loads wipe window.* state). Then call the helpers in later calls.
//
//   __feed(from)           -> rows for loaded articles, cached on window.__rows; returns
//                             only rows from index `from` onward (default 0 = all), so after
//                             __more() call __feed(<lastSeenIx+1>) to read just the new tail
//                             "ix | SUGGESTED|followed|AD | user | reel|carousel|post | likes | caption"
//   __more(px)             -> scroll the document down by px (default 1200), for the lazy loader
//   __feedDismiss(ix,mode) -> 'post' = Not interested only; 'account' = Not interested,
//                             then "Don't suggest posts from <user>" on the collapsed card
//                             returns 'ix:ok'/'ix:ok-account' | 'ix:already' | 'ix:no-item'
//                                   | 'ix:ad' (refused, never dismiss ads) | 'ix:no-btn' | 'ix:no-entry'
//
// IG class names are minified and rotate (x1lliihq...) — every selector here is
// structural: article/video/aria-label/innerText. Menus are NOT role=dialog —
// entries are found by scanning visible childless text leaves OUTSIDE any article;
// the account-level follow-up renders INSIDE the collapsed article.
// NEVER return raw hrefs/query strings/innerHTML — the harness safety filter blocks
// the whole result. Cleaned text only.

const clean = s => (s||'').replace(/[^\w\s.,:'&()!?$%+@#/-]/g,'').trim();
const vis = e => { const r = e.getBoundingClientRect(); return r.width>0 && r.height>0 && r.top < innerHeight && r.bottom > 0; };
const wait = ms => new Promise(r=>setTimeout(r,ms));

// Article indexes stay stable within a page session: dismissed posts collapse to
// a "Post hidden" card in place, scrolling only appends. Re-run __feed(from) after
// each __more() with from = last seen index + 1 to get only the new tail (tool
// results truncate around 1.5KB, so never re-read the whole list).
window.__feed = (from) => {
  const arts = [...document.querySelectorAll('article')];
  window.__rows = arts.map((el, ix) => {
    const t = (el.innerText||'');
    // AD rows: no "Suggested for you" marker but Sponsored/Ad/Learn more text.
    // Never dismiss ads (opens ad-preference dialogs); __feedDismiss refuses them.
    const sug = t.includes('Suggested for you') ? 'SUGGESTED'
              : /\b(Sponsored|Ad)\b|Learn more/.test(t) ? 'AD'
              : 'followed';
    const lines = t.split('\n').map(clean).filter(Boolean);
    const user  = (lines[0]||'?').slice(0,30);
    const likes = (t.match(/([\d.,]+[KM]?) (likes|others)/i)||[])[1]||'?';
    // Next control first: a carousel whose first slide is a video is still a carousel.
    const kind  = el.querySelector('svg[aria-label="Next"], button[aria-label="Next"]') ? 'carousel'
                : el.querySelector('video') ? 'reel'
                : 'post';
    const cap   = lines.slice(1).filter(l => !/^(Follow|Following|Suggested for you|Like|Comment|Share|Save|more|Original audio)$/i.test(l))
                    .join(' ').slice(0,160);
    return [ix, sug, user, kind, likes+' likes', cap].join(' | ');
  });
  return window.__rows.slice(from || 0);
};

// The home feed is a normal document scroll — JS scrolling is safe here (unlike
// the reels viewer). Real wheel scrolls get eaten by carousel posts under the
// cursor, so this is the one hardened advance path.
window.__more = async (px) => {
  document.documentElement.scrollTop += (px || 1200);
  await wait(2000);
  return 'arts=' + document.querySelectorAll('article').length + ' y=' + Math.round(scrollY) + '/' + document.documentElement.scrollHeight;
};

// Menu/card entries are plain text leaves in overlay divs (NOT role=dialog).
// No root = scan the document but skip anything inside an <article> (menu overlay
// entries). Pass a root element to scope the scan to that element only (the
// account-level offer lives INSIDE the collapsed article, and neighbouring
// collapsed cards carry the same offer text for a different user).
const findEntry = (re, root) => {
  const pool = [...(root||document).querySelectorAll('button, [role="button"], [role="menuitem"], div, span')]
    .filter(e => vis(e) && e.children.length === 0 && re.test(clean(e.innerText))
              && (root ? true : !e.closest('article')));
  const leaf = pool[0];
  return leaf ? (leaf.closest('[role="button"]') || leaf.closest('button') || leaf) : null;
};

window.__feedDismiss = async (ix, mode) => {
  const el = [...document.querySelectorAll('article')][ix];
  if (!el) return ix+':no-item';
  if (/Post hidden|won.?t suggest/i.test(el.innerText||'')) return ix+':already';
  // Ads: no "Suggested for you" marker, Sponsored/Ad/Learn more text. Refuse:
  // their menu opens ad-preference dialogs, not "Not interested".
  const txt = el.innerText||'';
  if (!txt.includes('Suggested for you') && /\b(Sponsored|Ad)\b|Learn more/.test(txt)) return ix+':ad';
  const svg = el.querySelector('svg[aria-label="More options"], svg[aria-label="More"]');
  const btn = svg && (svg.closest('[role="button"]') || svg.closest('button') || svg.parentElement);
  if (!btn) return ix+':no-btn';
  el.scrollIntoView({block:'center'});
  await wait(500);
  btn.click();
  await wait(900);
  const entry = findEntry(/^not interested$/i);
  if (!entry) {
    // followed-account posts have no "Not interested" — close and move on.
    // If the menu visibly sticks open, send a real `computer` Escape.
    document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}));
    return ix+':no-entry';
  }
  entry.click();
  await wait(1200);
  if (mode !== 'account') return ix+':ok';
  // account tier: the collapsed "Post hidden" card offers "Don't suggest posts
  // from <user>" (curly apostrophe stripped by clean -> match don.?t). Re-resolve
  // the article at ix (React may re-render the collapsed card into a new node)
  // and scope the scan to it so a neighbouring collapsed card's offer for a
  // different user can't be clicked by mistake.
  const card = [...document.querySelectorAll('article')][ix];
  const block = card && findEntry(/^don.?t suggest posts from/i, card);
  if (!block) return ix+':ok';           // post-level landed; account option absent
  block.click();
  await wait(800);
  return ix+':ok-account';
};
'helpers injected'
