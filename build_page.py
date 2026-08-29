#!/usr/bin/env python3
"""Builds delivery.html.

The shape is Noah's (2026-08-14): his picks first as a slow single-column read,
the whole library below as a fast grid, Play runs the picks full screen with a
cross-fade. Presentation grade; every feature pays off instantly or is out.

Downloads (Noah, same day: clear options, minimal clutter). Two sizes exist per
the Aug 3 spec, a print file and a web file, so the page says exactly that and
offers three verbs:
- All full res: the Drive folder.
- All for web: the 2560px set zipped IN THE BROWSER from this site's own
  files (a store-only zip writer inline; JPEGs do not recompress). The button
  carries the honest size and shows progress while it gathers.
- Select frames: tap to mark, then take the selection as a web zip or fire the
  full-res Drive downloads one by one (the browser asks once to allow it).
Per frame, on hover and in the lightbox: Full and Web. Nothing else.

Share mechanics, all utility: OG tags so a pasted URL unfurls with frame one,
deep links (#209), Copy link, ?play autostart.

    python3 build_page.py
"""
import json
import os
import re
import sys

from PIL import Image

import killed as _killed

HERE = os.path.dirname(os.path.abspath(__file__))
TITLE = "Camp Interlaken · July 2026"
CANON = "https://www.abba-photo.com/interlaken-campscapes"
FOLDER = "1HsgxIW_O2UkrAx8gKageMM1xg6t__cdi"
ALT = "Camp Interlaken JCC, Eagle River, Wisconsin, July 2026"

FRAMES = json.load(open(os.path.join(HERE, "frames.json")))
SECTIONS = _killed.strip(json.load(open(os.path.join(HERE, "sections.json"))))
_killed.check(SECTIONS, __file__)
TIMES = json.load(open(os.path.join(HERE, "_work", "times.json")))
# Master dimensions, read off the Drive files 2026-08-22 (ranged header fetches;
# _work/master_dims.json). Print sizes come from the MASTER, never a web tier.
sys.path.insert(0, os.path.expanduser("~/Abba_Photo/dashboard/tools"))
from print_sizes import print_line
MDIMS = json.load(open(os.path.join(HERE, "_work", "master_dims.json")))


def print_text(n):
    """The per-frame print line, from the master's true resolution. Empty when
    no master is on file or its shape disagrees with the display tier (never
    promise a size off a file we have doubts about)."""
    m = MDIMS.get(str(n))
    if not m:
        return ""
    pl = print_line(m["w"], m["h"])
    if pl["note"]:
        return "Prints true as a custom cut"
    parts = [(pl[k], lab) for k, lab in
             (("metal", "metal"), ("paper", "paper"), ("canvas", "canvas")) if pl[k]]
    if not parts:
        return ""
    return "Prints to " + " &middot; ".join(
        f"<b>{sz.replace('x', '&times;')}&Prime;</b> {lab}" for sz, lab in parts)
def _no_placeholders(m, what):
    """A "local-NNNN" value is an id recorded BEFORE Drive committed the upload.
    Building a page with one ships a 404 to the client. Refuse at every point
    that writes, copies, or loads a map, not just at the one that writes it.
    Codex, 2026-08-28: the guard existed in one place and the other paths were
    open."""
    bad = [k for k, v in m.items() if isinstance(v, str) and v.startswith("local-")]
    if bad:
        raise SystemExit(f"STOPPED: {len(bad)} placeholder Drive ids in {what} "
                         f"({bad[:4]}). Let Drive finish uploading, then refresh the map.")
    return m


DRIVE = _no_placeholders(json.load(open(os.path.join(HERE, "_work", "frame_drive.json"))), "frame_drive.json")
WEBIDS = _no_placeholders(json.load(open(os.path.join(HERE, "_work", "drive_web_ids.json"))), "drive_web_ids.json")
ARR = json.load(open(os.path.join(HERE, "_work", "arrangement_current.json")))

num2id = {}
for f in FRAMES:
    m = re.match(r"CILWEB1-(\d+)$", f["id"])
    num2id[int(m.group(1)) if m else 1] = f["id"]

K = _killed.killed()
placed = sorted({n for _, gs in SECTIONS for _, ns in gs for n in ns},
                key=lambda n: TIMES.get(num2id[n], "9999"))
picks = [n for n in next(g["frames"] for g in ARR["groups"] if g["name"] == "Print")
         if n not in K and n in placed]
BIG = {"CIL_HiRes_New718-30.jpg"}


def dl(n):
    e = DRIVE.get(str(n))
    if not e:
        return ""
    if e["file"] in BIG:
        return f'https://drive.google.com/file/d/{e["id"]}/view'
    return f'https://drive.google.com/uc?export=download&id={e["id"]}'


def rec(n):
    p = os.path.join(HERE, "img", "present", f"{num2id[n]}.jpg")
    w, h = Image.open(p).size
    wid = WEBIDS.get(str(n))
    wd = f"https://drive.google.com/uc?export=download&id={wid}" if wid else ""
    # f/wpx/hpx are what book_layout's JS reads. Adding them here means the
    # page keeps ONE global ALL that serves both the gallery and the book tab.
    return {"n": n, "id": num2id[n], "d": dl(n), "wd": wd, "w": w, "h": h,
            "pr": print_text(n), "f": f"{num2id[n]}.jpg", "wpx": w, "hpx": h}


_stage = os.path.expanduser("~/Desktop/ABBA/interlaken/web3840_stage")
_fd_files = {rec["file"] for rec in DRIVE.values()}
web_mb = round(sum(os.path.getsize(os.path.join(_stage, f)) for f in _fd_files
                   if os.path.exists(os.path.join(_stage, f))) / 1e6)
ZIP_URL = ("https://github.com/noahgallagher48-jpg/interlaken-campscapes/releases/"
           "download/interlaken-2026-web/Camp-Interlaken-web.zip")

from book_layout import CSS as BOOK_CSS, HTML as BOOK_HTML, JS as BOOK_JS

PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>__TITLE__</title>
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="Photographs by Noah Gallagher · Abba Photo">
<meta property="og:image" content="__OGIMG__">
<meta property="og:type" content="website">
<meta property="og:url" content="__CANON__/delivery.html">
<meta name="twitter:card" content="summary_large_image">
<link rel=icon href='data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="%23100e0b"/><circle cx="16" cy="16" r="7" fill="none" stroke="%23daa143" stroke-width="2.4"/></svg>'>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--book-bar:#1b1712;/* warm lane bar; book_layout reads this */
--ground:#100e0b;--ink:#ece6da;--muted:#9a9080;--faint:#6e6557;--gold:#daa143;
  --serif:"Iowan Old Style",Palatino,"Palatino Linotype",Georgia,serif;
  --mono:"SF Mono",ui-monospace,Menlo,monospace}
html{scroll-behavior:smooth}
body{background:var(--ground);color:var(--ink);line-height:1.55;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
a{color:var(--gold);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:3px}
img{display:block;max-width:100%;height:auto}
button.lnk{background:none;border:0;color:var(--muted);cursor:pointer;font:inherit;
  font-size:inherit;padding:0;letter-spacing:inherit}
button.lnk:hover{color:var(--gold);text-decoration:underline;text-underline-offset:3px}

/* ---- opening ---- */
.home{position:absolute;top:16px;left:20px;z-index:5;font-family:var(--mono);font-size:11px;letter-spacing:.28em;text-transform:uppercase;color:var(--gold)}
.open{position:relative;min-height:52vh;display:flex;flex-direction:column;align-items:center;
  justify-content:center;text-align:center;padding:72px 24px 56px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.34em;text-transform:uppercase;
  color:var(--gold);margin-bottom:22px}
h1{font-family:var(--serif);font-weight:400;font-size:clamp(30px,5.4vw,54px);
  letter-spacing:.015em;text-wrap:balance}
.date{font-family:var(--mono);font-size:12px;letter-spacing:.22em;text-transform:uppercase;
  color:var(--muted);margin-top:14px}
.rule{width:44px;border-top:1px solid rgba(218,161,67,.6);margin:34px 0}
.play{display:inline-flex;align-items:center;gap:11px;background:none;color:var(--ink);
  border:1px solid rgba(236,230,218,.34);border-radius:44px;padding:13px 30px;
  font-size:13px;letter-spacing:.14em;text-transform:uppercase;cursor:pointer;
  font-family:inherit;transition:border-color .25s,color .25s}
.play:hover{border-color:var(--gold);color:var(--gold)}
.play .tri{font-size:10px;position:relative;top:-1px}
.dlline{margin-top:26px;font-size:13px;color:var(--faint)}
.opts{margin-top:9px}
.opts a,.opts button.lnk{color:var(--muted)}
.opts .dot{color:var(--faint);margin:0 9px}

.wrap{max-width:1560px;margin:0 auto;padding:0 clamp(16px,3vw,44px)}
.reader{max-width:1180px;margin:0 auto;padding:0 clamp(16px,3vw,44px)}

/* ---- the picks: a slow read ---- */
.reader figure{margin:0 0 clamp(26px,4.5vh,52px);position:relative}
.reader figure img{width:100%;cursor:zoom-in;background:#181510}
.reader figure.tall img{width:auto;max-width:100%;max-height:92vh;margin:0 auto}

/* ---- the grid: a fast browse ---- */
.secthead{display:flex;align-items:baseline;justify-content:space-between;gap:14px;
  padding:64px 0 22px;border-top:1px solid rgba(236,230,218,.1);margin-top:26px}
.secthead h2{font-family:var(--serif);font-weight:400;font-size:23px;letter-spacing:.01em}
.secthead span{font-family:var(--mono);font-size:11px;letter-spacing:.14em;color:var(--faint)}
.grid{columns:3 340px;column-gap:12px;padding-bottom:24px}
.grid figure{break-inside:avoid;margin:0 0 12px;position:relative}
.grid figure img{width:100%;cursor:zoom-in;background:#181510}

figure .tag{position:absolute;left:0;right:0;bottom:0;display:flex;align-items:center;gap:12px;
  padding:20px 10px 7px;font-family:var(--mono);font-size:10.5px;color:rgba(236,230,218,.66);
  background:linear-gradient(transparent,rgba(10,8,6,.7));opacity:0;transition:opacity .2s}
figure:hover .tag{opacity:1}
figure .tag .links{margin-left:auto;display:flex;gap:12px}
figure .tag a{letter-spacing:.06em}
.fadein{opacity:0;transition:opacity .6s ease}
.fadein.in{opacity:1}

/* ---- selection ---- */
figure .pick{position:absolute;top:9px;right:9px;width:23px;height:23px;border-radius:50%;
  border:1.5px solid rgba(236,230,218,.85);background:rgba(10,8,6,.42);display:none;
  align-items:center;justify-content:center;font-size:13px;line-height:1;color:var(--ground);
  pointer-events:none}
body.sel .pick{display:flex}
body.sel figure img{cursor:pointer}
figure.on .pick{background:var(--gold);border-color:var(--gold)}
figure.on .pick::after{content:"\\2713"}
figure.on img{outline:2px solid var(--gold);outline-offset:-2px}
#selbar{position:fixed;left:50%;bottom:22px;transform:translateX(-50%) translateY(90px);
  z-index:45;display:flex;align-items:center;gap:20px;background:rgba(18,15,11,.96);
  border:1px solid rgba(236,230,218,.16);border-radius:44px;padding:12px 26px;
  font-family:var(--mono);font-size:12px;letter-spacing:.05em;white-space:nowrap;
  transition:transform .3s ease;box-shadow:0 8px 30px rgba(0,0,0,.5)}
body.sel #selbar{transform:translateX(-50%) translateY(0)}
#selbar .ct{color:var(--muted)}
#selbar button.lnk{font-family:var(--mono);font-size:12px;color:var(--gold)}
#selbar button.lnk:disabled{color:var(--faint);cursor:default;text-decoration:none}
#selbar .done{color:var(--muted)}

footer{max-width:1180px;margin:0 auto;padding:44px clamp(16px,3vw,44px) 84px;
  border-top:1px solid rgba(236,230,218,.1);display:flex;justify-content:space-between;
  gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--faint)}
footer a{color:var(--muted)}footer a:hover{color:var(--gold)}

/* ---- lightbox ---- */
/* NEUTRAL, not the camp's warm ground (Noah, 2026-08-28): 'use their colors
   on the main pages but not in album layout or lightbox'. A tinted surround
   changes how the photograph reads, and this is where people judge them. */
#lb{position:fixed;inset:0;background:rgba(18,18,20,.985);display:none;
  align-items:center;justify-content:center;z-index:50}
#lb.on{display:flex}
#lb img{max-width:95vw;max-height:88vh;object-fit:contain}
#lb button{position:absolute;background:none;border:0;color:var(--ink);font-size:32px;
  cursor:pointer;padding:16px 22px;opacity:.55;line-height:1;transition:opacity .2s}
#lb button:hover{opacity:1}
#lb .x{top:8px;right:12px;font-size:24px}#lb .p{left:4px}#lb .nx{right:4px}
#lb .c{position:absolute;bottom:16px;left:50%;transform:translateX(-50%);
  font-family:var(--mono);font-size:11.5px;color:rgba(236,230,218,.6);
  display:flex;gap:18px;align-items:center;white-space:nowrap}
#lb .c a,#lb .c button.cp{position:static;font-size:11.5px;font-family:var(--mono);
  padding:0;opacity:1;color:var(--gold);letter-spacing:.04em;background:none;border:0;cursor:pointer}
#lb .c button.cp:hover{text-decoration:underline;text-underline-offset:3px}
.sz{font-size:11px;color:#a69b8a;padding:5px 10px 8px;line-height:1.45}
.sz b{color:#cfc4b2;font-weight:600}
#lb .c .szl{font-size:11.5px;color:#a69b8a;flex-basis:100%;text-align:center}
#lb .c .szl b{color:#cfc4b2;font-weight:600}

/* ---- slideshow ---- */
#ss{position:fixed;inset:0;background:#070605;display:none;z-index:60}
#ss.on{display:block}
#ss .lay{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  opacity:0;transition:opacity 1.3s ease-in-out}
#ss .lay.show{opacity:1}
#ss .lay img{max-width:100vw;max-height:100vh;object-fit:contain}
#ss .close{position:absolute;top:10px;right:16px;background:none;border:0;
  color:rgba(236,230,218,.5);font-size:26px;cursor:pointer;z-index:3;padding:12px}
#ss .close:hover{color:var(--ink)}
#ss .hint{position:absolute;bottom:20px;left:50%;transform:translateX(-50%);z-index:3;
  font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;color:rgba(236,230,218,.36);
  transition:opacity .6s;pointer-events:none}
#ss.playing .hint{opacity:0}

#toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);z-index:70;
  background:var(--ink);color:var(--ground);font-family:var(--mono);font-size:12px;
  padding:9px 18px;border-radius:4px;opacity:0;pointer-events:none;transition:opacity .3s}
#toast.on{opacity:1}
@media (max-width:640px){.open{min-height:40vh;padding-top:56px}.grid{columns:2 150px}
  #selbar{gap:13px;padding:11px 18px;font-size:11px}}
.toptabs{display:flex;gap:8px;justify-content:center;margin:4px 0 48px}
/* the tabs need air on BOTH sides: measured 76px above and 0 below, so the
   photograph started hard against the buttons (Noah, 8/27: mind the spacing) */
.toptab{background:transparent;border:1px solid rgba(236,230,218,.28);color:inherit;
 border-radius:24px;padding:10px 24px;font:600 14px inherit;cursor:pointer;letter-spacing:.01em}
.toptab[aria-selected=true]{background:var(--gold);border-color:var(--gold);color:var(--ground)}
#tab-gallery{display:none}
#tab-gallery.on{display:block}
__BOOKCSS__
</style></head><body>

<a class=home href="https://www.abba-photo.com/">Abba Photo</a>
<div class=open>
  <p class=eyebrow style="visibility:hidden">.</p>
  <h1>Camp Interlaken</h1>
  <p class=date>Eagle River, Wisconsin &middot; July 2026</p>
  <div class=rule></div>
  <button class=play id=play><span class=tri>&#9654;</span> Play</button>
  <p class=dlline>Your photographs in two sizes: full resolution for print, web for screens</p>
  <p class="dlline opts">
    <a href="https://drive.google.com/drive/folders/__FOLDER__" target=_blank rel=noopener>All full res</a>
    <span class=dot>&middot;</span>
    <button class=lnk id=zipall>All for web (__WEBMB__ MB)</button>
    <span class=dot>&middot;</span>
    <button class=lnk id=selmode>Select frames</button>
    <span class=dot>&middot;</span>
    <a href="field-guide.html">The field guide</a>
  </p>
  <p class=dlline style="margin-top:8px;font-size:12px">Full resolution comes from Google Drive. No sign-in needed.</p>
</div>

<div class=toptabs role=tablist>
  <button class=toptab role=tab data-tab=gallery aria-selected=true>Gallery</button>
  <button class=toptab role=tab data-tab=book aria-selected=false>Book layout</button>
</div>

<div id=tab-gallery class=on>
  <div class=reader id=picks></div>

  <div class=wrap>
    <div class=secthead><h2>Everything</h2><span>__NLIB__ &middot; IN THE ORDER THEY WERE MADE</span></div>
    <div class=grid id=grid></div>
  </div>
</div>

<div id=tab-book>
 <div class=wrap>
  <p class=bklede>Choose the photographs for the book, then see how they lay out on the page.
  The strip along the bottom is the book in order, and it drags.</p>
  <div class=bkwho>
   <span class=bkwholab>Picking as</span>
   <button class=bkwhobtn id=bkwho-camp data-who=camp>Camp Interlaken</button>
   <button class=bkwhobtn id=bkwho-noah data-who=noah>Noah</button>
   <span class=bkwhonote id=bkwhonote></span>
  </div>
  <div class=bkchips role=tablist>
   <button class=bkchip role=tab aria-selected=true data-view=mine id=bkchip-mine>My picks</button>
   <button class=bkchip role=tab aria-selected=false data-view=picks>Noah&#x27;s Picks</button>
   <button class=bkchip role=tab aria-selected=false data-view=clientpicks>Camp Interlaken&#x27;s picks</button>
   <button class=bkchip role=tab aria-selected=false data-view=all>All photographs</button>
   <button class=bkchip role=tab aria-selected=false data-view=book>In the book</button>
  </div>
  <div class=bkgrid id=bkgrid></div>
 </div>
</div>
__BOOKHTML__

<footer>
  <span>Photographs by Noah Gallagher</span>
  <span>Abba Photo &middot; <a href="https://www.abba-photo.com" target=_blank rel=noopener>abba-photo.com</a></span>
</footer>

<div id=selbar><span class=ct id=selct>0 selected</span>
  <button class=lnk id=selweb disabled>Web</button>
  <button class=lnk id=selfull disabled>Full res</button>
  <button class="lnk done" id=seldone>Done</button></div>

<div id=lb><button class=x aria-label=Close>&times;</button>
  <button class=p aria-label=Previous>&lsaquo;</button>
  <img id=lbi alt="__ALTT__">
  <button class=nx aria-label=Next>&rsaquo;</button><div class=c id=lbc></div></div>

<div id=ss><button class=close id=ssx aria-label=Close>&times;</button>
  <div class=lay id=la><img alt="__ALTT__"></div><div class=lay id=lbb><img alt="__ALTT__"></div>
  <div class=hint>CLICK TO PAUSE &middot; ESC TO LEAVE</div></div>

<div id=toast>Link copied</div>

<script>
var PICKS=__PICKS__,ALL=__ALL__,ALT=__ALT__;
/* book_layout reads this before it runs; it defaults to Kingswood otherwise */
window.BKCLIENT = {name:"Camp Interlaken", place:"Eagle River, Wisconsin &middot; July 2026",
                   slug:"interlaken", set:"cil1"};
/* the book tab's "Noah's Picks" chip reads this; without it the chip shows
   its empty-state note rather than his selection */
var BOOKPICKS=__BOOKPICKS__, CLIENTPICKS=[];
/* BOOKSEND was missing entirely, so Save the book threw on
   BOOKSEND.drive_endpoint before the .catch() existed: the button stuck on
   "Saving" and neither the inbox route nor the JSON fallback ran. Codex
   caught it 2026-08-28. The web3forms key is the standing route (same
   public key as the vote page and Kingswood's book_send.json): a saved
   book lands in the noah@abba-photo.com inbox. Local download stays as
   the last-resort fallback the code already carries. */
var BOOKSEND={"drive_endpoint":"","web3forms_key":"b3bc124c-7812-4c4e-8fce-6ea6b9d1c5a2","subject":"Interlaken book"};
function src(f){return 'img/present/'+f.id+'.jpg';}
function webname(f){return 'Interlaken-'+f.n+'.jpg';}
function fig(f,tall){return '<figure data-n="'+f.n+'" id="f'+f.n+'"'+
  (tall&&f.h>f.w?' class=tall':'')+'>'+
  '<img class=fadein loading=lazy width='+f.w+' height='+f.h+' src="'+src(f)+'" alt="'+ALT+'">'+
  '<span class=pick></span>'+
  '<div class=tag><span>'+f.n+'</span><span class=links>'+
  (f.d?'<a href="'+f.d+'">Full</a>':'')+
  (f.wd?'<a href="'+f.wd+'">Web</a>':'<a href="'+src(f)+'" download="'+webname(f)+'">Web</a>')+'</span></div>'+
  (f.pr?'<div class=sz>'+f.pr+'</div>':'')+'</figure>';}
document.getElementById('picks').innerHTML=PICKS.map(function(f){return fig(f,true);}).join('');
document.getElementById('grid').innerHTML=ALL.map(function(f){return fig(f,false);}).join('');
document.querySelectorAll('img.fadein').forEach(function(im){
  if(im.complete)im.classList.add('in');
  else im.addEventListener('load',function(){im.classList.add('in');});});

var toastT=null;
function toast(m){var t=document.getElementById('toast');t.textContent=m;
  t.classList.add('on');clearTimeout(toastT);
  toastT=setTimeout(function(){t.classList.remove('on');},2100);}

/* ---- selection ---- */
var selected={};
function selCount(){return Object.keys(selected).length;}
function selSync(){var c=selCount();
  document.getElementById('selct').textContent=c+' selected';
  document.getElementById('selweb').disabled=!c;
  document.getElementById('selfull').disabled=!c;}
function selToggle(n,el){if(selected[n]){delete selected[n];el.classList.remove('on');}
  else{selected[n]=1;el.classList.add('on');}selSync();}
function selFrames(){return ALL.filter(function(f){return selected[f.n];});}
document.getElementById('selmode').onclick=function(){
  document.body.classList.add('sel');selSync();};
document.getElementById('seldone').onclick=function(){
  document.body.classList.remove('sel');selected={};
  document.querySelectorAll('figure.on').forEach(function(g){g.classList.remove('on');});};

/* ---- store-only zip writer ---- */
var CRCT=(function(){var t=[],c,k,n;for(n=0;n<256;n++){c=n;
  for(k=0;k<8;k++)c=(c&1)?(0xEDB88320^(c>>>1)):(c>>>1);t[n]=c>>>0;}return t;})();
function crc32(u8){var c=0xFFFFFFFF,i;
  for(i=0;i<u8.length;i++)c=CRCT[(c^u8[i])&0xFF]^(c>>>8);
  return (c^0xFFFFFFFF)>>>0;}
function le16(v){return new Uint8Array([v&255,(v>>>8)&255]);}
function le32(v){return new Uint8Array([v&255,(v>>>8)&255,(v>>>16)&255,(v>>>24)&255]);}
function zipBuild(entries){var parts=[],central=[],off=0,DT=((46<<9)|(7<<5)|19),i;
  for(i=0;i<entries.length;i++){var e=entries[i],
    nm=new TextEncoder().encode(e.name),crc=crc32(e.data),
    loc=[le32(0x04034b50),le16(20),le16(0x0800),le16(0),le16(0),le16(DT),
         le32(crc),le32(e.data.length),le32(e.data.length),le16(nm.length),le16(0)];
    loc.forEach(function(p){parts.push(p);});parts.push(nm);parts.push(e.data);
    var hdr=[le32(0x02014b50),le16(20),le16(20),le16(0x0800),le16(0),le16(0),le16(DT),
         le32(crc),le32(e.data.length),le32(e.data.length),le16(nm.length),
         le16(0),le16(0),le16(0),le16(0),le32(0),le32(off)];
    central.push({h:hdr,n:nm});
    off+=30+nm.length+e.data.length;}
  var cdOff=off,cdLen=0;
  central.forEach(function(c){c.h.forEach(function(p){parts.push(p);cdLen+=p.length;});
    parts.push(c.n);cdLen+=c.n.length;});
  [le32(0x06054b50),le16(0),le16(0),le16(entries.length),le16(entries.length),
   le32(cdLen),le32(cdOff),le16(0)].forEach(function(p){parts.push(p);});
  return new Blob(parts,{type:'application/zip'});}
function saveBlob(blob,name){var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);
  a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove();},4000);}
var zipping=false;
function zipWeb(frames,zipname,btn,label){
  if(zipping||!frames.length)return;zipping=true;
  var entries=[],k=0;
  function next(){
    if(k>=frames.length){
      btn.textContent='Packing\\u2026';
      setTimeout(function(){saveBlob(zipBuild(entries),zipname);
        btn.textContent=label;zipping=false;},30);return;}
    var f=frames[k];btn.textContent='Preparing '+(k+1)+' / '+frames.length;
    fetch(src(f)).then(function(r){return r.arrayBuffer();}).then(function(b){
      entries.push({name:webname(f),data:new Uint8Array(b)});k++;next();
    },function(){k++;next();});}
  next();}
var zab=document.getElementById('zipall');
zab.onclick=function(){location.href='__ZIPURL__';};
document.getElementById('selweb').onclick=function(){
  var fs=selFrames().filter(function(f){return f.wd;});
  if(!fs.length)return;
  toast('Starting '+fs.length+' download'+(fs.length>1?'s':''));
  fs.forEach(function(f,j){setTimeout(function(){
    var a=document.createElement('a');a.href=f.wd;document.body.appendChild(a);
    a.click();a.remove();},j*900);});};
document.getElementById('selfull').onclick=function(){
  var fs=selFrames().filter(function(f){return f.d;});
  if(!fs.length)return;
  toast('Starting '+fs.length+' download'+(fs.length>1?'s':''));
  fs.forEach(function(f,j){setTimeout(function(){
    var a=document.createElement('a');a.href=f.d;document.body.appendChild(a);
    a.click();a.remove();},j*600);});};

/* ---- lightbox with deep links ---- */
var set=ALL,i=0,lb=document.getElementById('lb');
function preloadAround(){[i+1,i-1].forEach(function(k){
  var f=set[(k+set.length)%set.length];if(f)(new Image()).src=src(f);});}
function open_(arr,k,silent){set=arr;i=k;var f=set[i];
  document.getElementById('lbi').src=src(f);
  document.getElementById('lbc').innerHTML=(i+1)+' / '+set.length+
    '<span>'+f.n+'</span>'+(f.d?'<a href="'+f.d+'">Full res</a>':'')+
    (f.wd?'<a href="'+f.wd+'">Web</a>':'<a href="'+src(f)+'" download="'+webname(f)+'">Web</a>')+
    '<button class=cp id=cpl>Copy link</button>'+
    (f.pr?'<span class=szl>'+f.pr+'</span>':'');
  document.getElementById('cpl').onclick=function(){
    var u=location.origin+location.pathname+'#'+f.n;
    (navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject())
      .then(function(){toast('Link copied');},
            function(){window.prompt('Copy this:',u);});};
  lb.classList.add('on');
  if(!silent)history.replaceState(null,'','#'+f.n);
  preloadAround();}
function closeLB(){lb.classList.remove('on');
  history.replaceState(null,'',location.pathname);}
function step(d){open_(set,(i+d+set.length)%set.length);}
function wire(id,arr){document.getElementById(id).onclick=function(e){
  if(e.target.tagName==='A')return;var g=e.target.closest('figure');if(!g)return;
  var n=+g.dataset.n;
  if(document.body.classList.contains('sel')){selToggle(n,g);return;}
  open_(arr,arr.findIndex(function(x){return x.n===n;}));};}
wire('picks',PICKS);wire('grid',ALL);
document.querySelector('#lb .x').onclick=closeLB;
document.querySelector('#lb .p').onclick=function(e){e.stopPropagation();step(-1);};
document.querySelector('#lb .nx').onclick=function(e){e.stopPropagation();step(1);};
lb.onclick=function(e){if(e.target.id==='lb')closeLB();};

/* ---- slideshow ---- */
var ss=document.getElementById('ss'),LA=document.getElementById('la'),
    LB2=document.getElementById('lbb'),cur=0,front=LA,tmr=null,run=false;
function paint(el,f){el.firstElementChild.src=src(f);}
function advance(){var nxt=(front===LA)?LB2:LA;cur=(cur+1)%PICKS.length;
  paint(nxt,PICKS[cur]);nxt.classList.add('show');front.classList.remove('show');front=nxt;
  var pre=PICKS[(cur+1)%PICKS.length];if(pre)(new Image()).src=src(pre);
  tmr=setTimeout(advance,4400);}
function startSS(){cur=0;front=LA;paint(LA,PICKS[0]);
  LA.classList.add('show');LB2.classList.remove('show');
  ss.classList.add('on','playing');run=true;
  clearTimeout(tmr);tmr=setTimeout(advance,4400);
  if(PICKS[1])paint(LB2,PICKS[1]);}
function stopSS(){clearTimeout(tmr);run=false;ss.classList.remove('on','playing');}
document.getElementById('play').onclick=startSS;
document.getElementById('ssx').onclick=function(e){e.stopPropagation();stopSS();};
ss.onclick=function(){if(run){clearTimeout(tmr);run=false;ss.classList.remove('playing');}
  else{run=true;ss.classList.add('playing');tmr=setTimeout(advance,1100);}};
document.onkeydown=function(e){
  if(ss.classList.contains('on')){
    if(e.key==='Escape')stopSS();
    if(e.key===' '){e.preventDefault();ss.click();}
    if(e.key==='ArrowRight'){clearTimeout(tmr);advance();}return;}
  if(lb.classList.contains('on')){
    if(e.key==='Escape')closeLB();
    if(e.key==='ArrowRight')step(1);if(e.key==='ArrowLeft')step(-1);return;}
  if(e.key==='Escape'&&document.body.classList.contains('sel'))
    document.getElementById('seldone').click();};
var sx=0;lb.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;});
lb.addEventListener('touchend',function(e){var d=e.changedTouches[0].clientX-sx;
  if(Math.abs(d)>44)step(d<0?1:-1);});

/* arriving with intent */
(function(){
  if(location.search.indexOf('play')>-1){startSS();return;}
  var m=location.hash.match(/^#(\\d+)$/);
  if(m){var n=+m[1],k=ALL.findIndex(function(x){return x.n===n;});
    if(k>-1)open_(ALL,k,true);}
})();
</script>
<script data-goatcounter="https://abba-photo.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
<script>
__BOOKJS__
document.querySelectorAll(".toptab").forEach(function(b){
  b.onclick=function(){
    var which=b.getAttribute("data-tab");
    document.querySelectorAll(".toptab").forEach(function(o){
      o.setAttribute("aria-selected", o===b ? "true" : "false"); });
    document.getElementById("tab-gallery").className = which==="gallery" ? "on" : "";
    document.getElementById("tab-book").className = which==="book" ? "on" : "";
    document.getElementById("bklane").className = which==="book" ? "bklane on" : "bklane";
    window.scrollTo(0,0);
  };
});

bkWire();
</script>
</body></html>"""

precs = [rec(n) for n in picks]
arecs = [rec(n) for n in placed]
_pickn = [r["n"] for r in precs]
html = (PAGE.replace("__BOOKPICKS__", json.dumps(_pickn))
            .replace("__BOOKCSS__", BOOK_CSS)
            .replace("__BOOKHTML__", BOOK_HTML)
            .replace("__BOOKJS__", BOOK_JS.replace("__BKBLEEDHERO__", "{}"))
            .replace("__PICKS__", json.dumps(precs))
            .replace("__ALL__", json.dumps(arecs))
            .replace("__ALT__", json.dumps(ALT))
            .replace("__ALTT__", ALT)
            .replace("__TITLE__", TITLE)
            .replace("__CANON__", CANON)
            .replace("__OGIMG__", f"{CANON}/img/present/{precs[0]['id']}.jpg")
            .replace("__FOLDER__", FOLDER)
            .replace("__WEBMB__", str(web_mb))
            .replace("__ZIPURL__", ZIP_URL)
            .replace("__NLIB__", str(len(placed))))

open(os.path.join(HERE, "delivery.html"), "w").write(html)
print(f"wrote delivery.html: picks {len(precs)}, library {len(arecs)}, "
      f"{sum(1 for r in arecs if r['d'])} full-res links, web set {web_mb} MB")
