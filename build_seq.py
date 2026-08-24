#!/usr/bin/env python3
"""Builds seq.html, the forty-seven in Noah's order.

The set is the "Print" group of `_work/arrangement_current.json`: the frames he
would put in a book of his own. Two views off the same sequence, because the
page does two jobs. Read runs one frame at a time at full width, which is how
you walk someone through it. Spreads pairs them as facing pages, which is how
you sequence a book. Lightbox on any frame.

Nothing is captioned. The label is the claim; justification lives in the guide
layer, never under the frame.

    python3 build_seq.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GROUP = "Print"
TITLE = "Camp Interlaken &middot; July 2026"

FRAMES = json.load(open(os.path.join(HERE, "frames.json")))
import killed as _killed
ARR = json.load(open(os.path.join(HERE, "_work", "arrangement_current.json")))
_K = _killed.killed()
for _g in ARR["groups"]: _g["frames"] = [n for n in _g["frames"] if n not in _K]

num2file = {}
for f in FRAMES:
    m = re.match(r"CILWEB1-(\d+)$", f["id"])
    num2file[int(m.group(1)) if m else 1] = f["id"]

seq = next(g["frames"] for g in ARR["groups"] if g["name"] == GROUP)
ids = [num2file[n] for n in seq]

PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>__TITLE__</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#14110d;color:#ede7dd;font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif}
header{position:sticky;top:0;z-index:9;background:rgba(20,17,13,.96);backdrop-filter:blur(6px);
  border-bottom:1px solid rgba(226,167,62,.3);padding:13px 20px;display:flex;align-items:center;gap:14px}
h1{font-family:Georgia,serif;font-weight:500;font-size:17px;letter-spacing:.01em;margin-right:auto}
h1 span{color:#8b8271;font-size:13px;font-family:-apple-system,sans-serif;margin-left:9px}
.tog{display:flex;gap:0;border:1px solid rgba(226,167,62,.45);border-radius:3px;overflow:hidden}
.tog button{background:none;border:none;color:#e2a73e;padding:7px 14px;font-size:11px;letter-spacing:.09em;
  text-transform:uppercase;cursor:pointer;font-family:inherit}
.tog button.on{background:#e2a73e;color:#14110d}
main{padding:26px 20px 90px;max-width:1500px;margin:0 auto}
figure{margin:0 0 26px;position:relative;cursor:zoom-in}
figure img{display:block;width:100%;height:auto;background:#1d1913}
.n{position:absolute;left:10px;bottom:10px;font-family:ui-monospace,Menlo,monospace;font-size:10.5px;
  color:rgba(237,231,221,.5);background:rgba(20,17,13,.6);padding:2px 7px;border-radius:2px}
body.spreads main{display:grid;grid-template-columns:1fr 1fr;gap:3px 3px;max-width:1500px}
body.spreads figure{margin:0 0 34px}
body.spreads .pair{grid-column:span 2;display:grid;grid-template-columns:1fr 1fr;gap:3px;margin-bottom:34px}
body.spreads .pair figure{margin:0;display:flex;align-items:center;background:#0e0c09}
@media(max-width:820px){body.spreads main{grid-template-columns:1fr}
  body.spreads .pair{grid-column:span 1;grid-template-columns:1fr}}
#lb{position:fixed;inset:0;background:rgba(9,8,6,.97);display:none;align-items:center;justify-content:center;z-index:40}
#lb.on{display:flex}
#lb img{max-width:96vw;max-height:92vh;object-fit:contain}
#lb .x,#lb .p,#lb .nx{position:absolute;background:none;border:none;color:#ede7dd;font-size:34px;
  cursor:pointer;padding:16px 22px;line-height:1;opacity:.62}
#lb .x{top:6px;right:10px;font-size:26px}#lb .p{left:2px}#lb .nx{right:2px}
#lb .x:hover,#lb .p:hover,#lb .nx:hover{opacity:1}
#lb .c{position:absolute;bottom:14px;left:50%;transform:translateX(-50%);font-family:ui-monospace,Menlo,monospace;
  font-size:11.5px;color:rgba(237,231,221,.55)}
</style></head><body>
<header>
  <a href="https://www.abba-photo.com/" style="font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.24em;color:#e2a73e;text-decoration:none;margin-right:14px">ABBA PHOTO</a>
  <h1>__TITLE__<span>__COUNT__ frames</span></h1>
  <div class=tog>
    <button id=bRead class=on>Read</button><button id=bSpread>Spreads</button>
  </div>
</header>
<main id=m></main>
<div id=lb><button class=x>&times;</button><button class=p>&lsaquo;</button>
<img id=lbi alt=""><button class=nx>&rsaquo;</button><div class=c id=lbc></div></div>
<script>
var IDS=__IDS__,NUMS=__NUMS__,i=0,spread=false;
function fig(k){return '<figure data-k="'+k+'"><img loading=lazy src="img/present/'+IDS[k]+
  '.jpg" alt=""><span class=n>'+NUMS[k]+'</span></figure>';}
function render(){var m=document.getElementById('m'),h='';
  if(!spread){for(var k=0;k<IDS.length;k++)h+=fig(k);}
  else{h+=fig(0);for(var k=1;k<IDS.length;k+=2){h+='<div class=pair>'+fig(k)+
    (k+1<IDS.length?fig(k+1):'')+'</div>';}}
  m.innerHTML=h;}
function open_(k){i=k;var lb=document.getElementById('lb');
  document.getElementById('lbi').src='img/present/'+IDS[i]+'.jpg';
  document.getElementById('lbc').textContent=(i+1)+' / '+IDS.length+'  ·  '+NUMS[i];
  lb.classList.add('on');}
function step(d){open_((i+d+IDS.length)%IDS.length);}
document.getElementById('m').onclick=function(e){var f=e.target.closest('figure');
  if(f)open_(+f.dataset.k);};
document.querySelector('#lb .x').onclick=function(){document.getElementById('lb').classList.remove('on');};
document.querySelector('#lb .p').onclick=function(e){e.stopPropagation();step(-1);};
document.querySelector('#lb .nx').onclick=function(e){e.stopPropagation();step(1);};
document.getElementById('lb').onclick=function(e){if(e.target.id==='lb')this.classList.remove('on');};
document.onkeydown=function(e){if(!document.getElementById('lb').classList.contains('on'))return;
  if(e.key==='Escape')document.getElementById('lb').classList.remove('on');
  if(e.key==='ArrowRight')step(1);if(e.key==='ArrowLeft')step(-1);};
var sx=0;document.getElementById('lb').addEventListener('touchstart',function(e){sx=e.touches[0].clientX;});
document.getElementById('lb').addEventListener('touchend',function(e){var d=e.changedTouches[0].clientX-sx;
  if(Math.abs(d)>44)step(d<0?1:-1);});
document.getElementById('bRead').onclick=function(){spread=false;document.body.classList.remove('spreads');
  this.classList.add('on');document.getElementById('bSpread').classList.remove('on');render();};
document.getElementById('bSpread').onclick=function(){spread=true;document.body.classList.add('spreads');
  this.classList.add('on');document.getElementById('bRead').classList.remove('on');render();};
render();
</script>
<script data-goatcounter="https://abba-photo.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body></html>"""

html = (PAGE.replace("__IDS__", json.dumps(ids))
            .replace("__NUMS__", json.dumps(seq))
            .replace("__COUNT__", str(len(ids)))
            .replace("__TITLE__", TITLE))
open(os.path.join(HERE, "seq.html"), "w").write(html)
print(f"wrote seq.html ({len(ids)} frames, from the {GROUP} group)")
