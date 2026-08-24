#!/usr/bin/env python3
"""Builds tour.html: the Interlaken interactive tour (2026-08-05), a real
deliverable for Interlaken that also serves as the reference product. A schematic map of camp (drawn, labeled as a sketch, NOT geography) with
tappable places; each opens a room of that place's frames from the library.
The waterfront room heroes the full panorama in a deep-zoom viewer
(lib/openseadragon.min.js, vendored). Noindex, unlinked. Regenerate:
python3 build_tour.py"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = json.load(open(os.path.join(HERE, "frames.json")))
NUMS = {}
for f in FRAMES:
    parts = f["id"].split("-")
    NUMS[int(parts[-1]) if parts[-1].isdigit() else 1] = f

# (key, label, cx%, cy%, frames)
PLACES = [
    ("water", "The waterfront", 30, 78, [23, 36, 37, 115, 116, 117, 118, 119, 120, 192]),
    ("boats", "On the water", 62, 84, [150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 161]),
    ("bridge", "The bridge", 48, 62, [57, 58, 59, 60, 61, 62, 63]),
    ("gather", "Shabbat", 68, 56, [42, 43, 44, 45, 54, 65, 68, 71, 73, 74, 75, 76, 77, 78, 79, 99, 100]),
    ("kfar", "K'far Noar", 22, 38, [24, 25, 28, 29, 31, 32, 33, 162, 163, 164]),
    ("cabins", "Cabins and bunks", 50, 34, [30, 34, 35, 38, 40, 107, 126, 127]),
    ("games", "Games and the wall", 76, 30, [110, 111, 112, 113, 121, 122, 130, 160]),
    ("night", "After dark", 84, 12, [14, 16, 18, 19, 20, 21, 22, 102, 105, 17, 101, 104]),
]
DEEPZOOM = {"water": 192}  # room key -> frame for the deep-zoom hero

def room_js():
    data = []
    for k, label, x, y, nums in PLACES:
        fr = [{"n": n, "f": NUMS[n]["file"]} for n in nums if n in NUMS]
        data.append({"k": k, "label": label, "frames": fr,
                     "dz": NUMS[DEEPZOOM[k]]["file"] if k in DEEPZOOM else None})
    return json.dumps(data)

def map_svg():
    dots = []
    for k, label, x, y, _ in PLACES:
        anchor = "end" if x > 70 else ("middle" if 30 <= x <= 70 else "start")
        lx = x - 2.2 if anchor == "end" else (x if anchor == "middle" else x + 2.2)
        ly = y - 3.4
        dots.append(
            f'<g class="node" data-k="{k}">'
            f'<circle cx="{x}" cy="{y}" r="2.1" class="dot"/>'
            f'<circle cx="{x}" cy="{y}" r="4.2" class="halo"/>'
            f'<text x="{lx}" y="{ly}" text-anchor="{anchor}">{label}</text></g>')
    return "\n".join(dots)

PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>Camp Interlaken &middot; the tour</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#14110d;color:#ede7dd;font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;line-height:1.55}
header{padding:42px 20px 6px;max-width:1000px;margin:0 auto}
h1{font-family:Georgia,serif;font-weight:600;font-size:clamp(24px,4.5vw,34px)}
.sub{color:#a69b8a;font-size:14px;margin-top:6px;max-width:60ch}
#map{max-width:1000px;margin:18px auto 60px;padding:0 14px}
#map svg{width:100%;height:auto;display:block;border:1px solid rgba(237,231,221,.14);border-radius:10px;background:
  radial-gradient(120% 90% at 50% -10%, #1b1712 0%, #14110d 60%),#14110d}
.lake{fill:#1c2a2e}
.shore{stroke:#3a4a4e;stroke-width:.5;fill:none}
.path{stroke:rgba(237,231,221,.22);stroke-width:.55;fill:none;stroke-dasharray:1.6 1.9}
.node{cursor:pointer;pointer-events:bounding-box}
.node .dot{fill:#e2a73e}
.node .halo{fill:rgba(226,167,62,.16)}
.node:hover .halo,.node:active .halo{fill:rgba(226,167,62,.32)}
.node text{fill:#c9bfa9;font-size:3.1px;font-family:Georgia,serif;letter-spacing:.04em}
.sketchnote{color:#7d745f;font-size:12.5px;margin-top:10px}
#room{position:fixed;inset:0;background:rgba(10,8,6,.98);display:none;z-index:9;overflow-y:auto}
#room.on{display:block}
#room .in{max-width:1100px;margin:0 auto;padding:26px 16px 80px}
#room h2{font-family:Georgia,serif;font-weight:600;font-size:26px;display:flex;align-items:baseline;gap:14px}
#room h2 small{color:#7d745f;font-size:13px;font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif}
#room .x{position:fixed;top:10px;right:16px;font-size:36px;color:#ede7dd;background:none;border:0;cursor:pointer;z-index:11}
#dz{width:100%;height:56vh;background:#000;border-radius:6px;margin-top:16px;display:none}
#dz.on{display:block}
.dznote{color:#7d745f;font-size:12.5px;margin-top:6px;display:none}
.dznote.on{display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin-top:18px}
.grid button{border:0;padding:0;background:#1d1913;border-radius:4px;overflow:hidden;cursor:pointer}
.grid img{width:100%;height:auto;display:block}
#lb{position:fixed;inset:0;background:rgba(5,4,3,.98);display:none;align-items:center;justify-content:center;z-index:12}
#lb.on{display:flex}
#lb img{max-width:96vw;max-height:92vh;object-fit:contain}
#lb .x{position:fixed;top:8px;right:14px;font-size:34px;color:#ede7dd;background:none;border:0;cursor:pointer}
footer{max-width:1000px;margin:0 auto;padding:0 20px 50px;color:#7d745f;font-size:12.5px}
a{color:#e2a73e}
</style></head><body>
<header><h1>Camp Interlaken &middot; the tour</h1>
<p class=sub>Tap a place. Its photographs open.</p></header>

<div id=map>
<svg viewBox="0 0 100 100" aria-label="A sketch of camp">
  <path class=lake d="M0,88 C 18,82 34,90 52,87 C 70,84 84,92 100,88 L100,100 L0,100 Z"/>
  <path class=shore d="M0,88 C 18,82 34,90 52,87 C 70,84 84,92 100,88"/>
  <path class=path d="M30,76 C 36,68 42,66 48,62 C 55,57 60,56 68,54 C 60,48 54,40 50,34 C 40,36 30,36 22,38 M48,62 C 60,50 72,38 84,14"/>
  __NODES__
</svg>
<p class=sketchnote>A sketch of the ground, not a survey. The real thing sits on the camp's own map.</p>
</div>

<div id=room><button class=x aria-label="Close">&times;</button><div class=in>
<h2 id=rtitle></h2>
<div id=dz></div><p class=dznote id=dznote>Pinch or scroll to look closer. This frame holds it.</p>
<div class=grid id=rgrid></div>
</div></div>

<div id=lb><button class=x aria-label="Close">&times;</button><img id=lbi alt=""></div>

<footer>Photographs Noah Gallagher &middot; Abba Photo &middot;
<a href="https://www.abba-photo.com">abba-photo.com</a></footer>

<script src="lib/openseadragon.min.js"></script>
<script>
var ROOMS=__ROOMS__;var byk={};ROOMS.forEach(function(r){byk[r.k]=r;});
var viewer=null;
function openRoom(k){var r=byk[k];if(!r)return;
document.getElementById("rtitle").innerHTML=r.label+' <small>'+r.frames.length+" frames</small>";
var g=document.getElementById("rgrid");g.innerHTML="";
r.frames.forEach(function(f){
  if(r.dz&&f.f===r.dz)return;
  var b=document.createElement("button");
  var i=document.createElement("img");i.loading="lazy";i.src="img/thumb/"+f.f;i.alt=r.label;
  b.appendChild(i);b.onclick=function(){document.getElementById("lbi").src="img/present/"+f.f;
  document.getElementById("lb").className="on";};g.appendChild(b);});
var dz=document.getElementById("dz"),dn=document.getElementById("dznote");
if(viewer){viewer.destroy();viewer=null;}
if(r.dz){dz.className="on";dn.className="dznote on";
viewer=OpenSeadragon({element:dz,tileSources:{type:"image",url:"img/present/"+r.dz},
showNavigationControl:false,gestureSettingsMouse:{clickToZoom:true,scrollToZoom:true}});}
else{dz.className="";dn.className="dznote";}
document.getElementById("room").className="on";document.body.style.overflow="hidden";}
function closeRoom(){document.getElementById("room").className="";document.body.style.overflow="";
if(viewer){viewer.destroy();viewer=null;}}
document.querySelectorAll(".node").forEach(function(n){
n.addEventListener("click",function(){openRoom(n.dataset.k);});});
document.querySelector("#room .x").onclick=closeRoom;
document.querySelector("#lb .x").onclick=function(){document.getElementById("lb").className="";};
document.getElementById("lb").addEventListener("click",function(e){
if(e.target.id==="lb")this.className="";});
document.addEventListener("keydown",function(e){if(e.key!=="Escape")return;
if(document.getElementById("lb").className==="on")document.getElementById("lb").className="";
else if(document.getElementById("room").className==="on")closeRoom();});
</script>
<script data-goatcounter="https://abba-photo.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body></html>"""

def build():
    html = PAGE.replace("__NODES__", map_svg()).replace("__ROOMS__", room_js())
    open(os.path.join(HERE, "tour.html"), "w").write(html)
    total = sum(len([n for n in p[4] if n in NUMS]) for p in PLACES)
    print(f"wrote tour.html ({len(PLACES)} places, {total} frames)")

if __name__ == "__main__":
    build()
