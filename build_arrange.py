#!/usr/bin/env python3
"""Builds arrange.html, the visual gallery-arrangement tool.

Model (2026-08-03, second cut, per Noah): use-case / theme groups that hold
COPIES. Pulling a frame into a group never removes it from anywhere else; a
frame can sit in as many groups as it needs. All frames stays whole at the
bottom as the palette. The exported arrangement is the foundation for the
presented gallery and, after his pick-group pass, the voting form.

Mechanics: drag from All frames into a group to copy it there; drag between
groups to move; drag a group copy back onto All frames (or hit its X) to take
it out of that group. Tap works everywhere drag does: tap a frame to select,
tap a group title to put it there, tap a frame inside a group to slot in
front of it. Copy arrangement exports JSON for the session. Everything
persists in localStorage. Regenerate: python3 build_arrange.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = json.load(open(os.path.join(HERE, "frames.json")))
SECTIONS = json.load(open(os.path.join(HERE, "sections.json")))
TIMES = json.load(open(os.path.join(HERE, "_work", "times.json")))

SEED_GROUPS = [
    ("Tushball", [3, 112, 113]),
    ("Indoor campfire", [4, 6, 7, 8, 9, 10, 11, 12]),
    ("Shabbat", list(range(42, 78))),
]

PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>Camp Interlaken &middot; arrange</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#14110d;color:#ede7dd;font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;padding-bottom:60px}
header{position:sticky;top:0;z-index:9;background:rgba(24,20,15,.97);border-bottom:1px solid rgba(226,167,62,.35);padding:12px 18px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
h1{font-family:Georgia,serif;font-weight:600;font-size:19px;margin-right:auto}
header button{background:none;border:1px solid rgba(226,167,62,.55);color:#e2a73e;padding:8px 13px;border-radius:3px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;cursor:pointer}
header button.go{background:#e2a73e;color:#14110d;font-weight:600}
.help{width:100%;color:#a69b8a;font-size:12.5px;line-height:1.5}
.grp{max-width:1280px;margin:20px auto 0;padding:0 14px}
.ghead{display:flex;align-items:center;gap:10px;border-bottom:1px solid rgba(237,231,221,.14);padding-bottom:6px;cursor:pointer}
.gname{font-family:Georgia,serif;font-size:18px;color:#c9bfa9;font-weight:500}
.gcnt{font-size:12px;color:#7d745f}
.ghead .tools{margin-left:auto;display:flex;gap:6px}
.ghead .tools button{background:none;border:1px solid rgba(237,231,221,.25);color:#a69b8a;border-radius:3px;font-size:12px;padding:4px 9px;cursor:pointer}
.lane{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;padding:12px 0 4px;min-height:56px}
.lane.over{outline:2px dashed rgba(226,167,62,.6);outline-offset:4px}
.th{position:relative;cursor:grab;border-radius:2px;overflow:hidden;background:#1d1913}
.th img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;pointer-events:none}
.th .n{position:absolute;left:5px;bottom:4px;font-size:10.5px;color:#cfc6b4;text-shadow:0 1px 4px #000;pointer-events:none}
.th .v{position:absolute;top:4px;right:4px;width:24px;height:24px;border:0;border-radius:3px;background:rgba(20,17,13,.55);color:#ede7dd;font-size:12px;cursor:pointer;line-height:24px}
.th .rm{position:absolute;top:4px;left:4px;width:24px;height:24px;border:0;border-radius:3px;background:rgba(20,17,13,.55);color:#ede7dd;font-size:15px;cursor:pointer;line-height:24px}
.th .u{position:absolute;top:4px;left:4px;min-width:20px;height:20px;border-radius:10px;background:#e2a73e;color:#14110d;font-size:11px;font-weight:700;line-height:20px;text-align:center;padding:0 4px;pointer-events:none}
.th.parked img{opacity:.35}
.th.sel{outline:3px solid #e2a73e;outline-offset:-3px}
.th.drag{opacity:.35}
.th.mark{outline:2px dashed rgba(226,167,62,.8);outline-offset:-2px}
#toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:#ede7dd;color:#14110d;padding:10px 16px;border-radius:4px;font-size:13px;opacity:0;pointer-events:none;transition:opacity .25s;z-index:12;max-width:88vw;text-align:center}
#toast.on{opacity:1}
#lb{position:fixed;inset:0;background:rgba(10,8,6,.97);display:none;align-items:center;justify-content:center;z-index:10}
#lb.on{display:flex}
#lb img{max-width:100vw;max-height:100vh;object-fit:contain}
#lb .x{position:fixed;top:8px;right:12px;font-size:30px;color:#a69b8a;background:none;border:0;cursor:pointer;padding:6px 10px}
</style></head><body>
<header><h1>Arrange the gallery</h1>
<button id=ng type=button>+ Group</button>
<button id=rs type=button>Start over</button>
<button id=cp class=go type=button>Copy arrangement</button>
<div class=help>Groups hold copies: pulling a frame into a group never takes it from
anywhere else, and a frame can live in as many groups as it needs. All frames stays whole
at the bottom; the gold number on a frame there counts the groups holding it, and a dimmed
frame sits in Out of the vote. Drag from All frames into a group to add it, drag between
groups to move, and the &#215; on a copy takes it out of that group only. Tapping works the
same: tap a frame, then tap a group title to add it there, or tap a frame inside a group
to slot in front. &#8599; shows any frame large. Everything saves as you go; Copy
arrangement when done and paste it to me.</div>
</header>
<div id=board></div>
<div id=toast></div>
<div id=lb><img id=lbi alt=""><button class=x aria-label="Close">&times;</button></div>
<script>
var FR=__FRAMES__,ALL=__ALL__,SEED=__SEED__,KEY="cil-arrange";
var state=null,sel=null,dragEl=null,tt=null;
function $(i){return document.getElementById(i);}
function toast(m){var t=$("toast");t.textContent=m;t.className="on";
clearTimeout(tt);tt=setTimeout(function(){t.className="";},2400);}
function load(){try{var s=JSON.parse(localStorage.getItem(KEY));
if(s&&s.groups&&s.out)return {groups:s.groups,out:s.out};}catch(e){}
return JSON.parse(JSON.stringify(SEED));}
function isPal(el){return el&&el.dataset.kind==="pal";}
function laneOf(el){return el.closest(".grp");}
function read(){var gs=[],out=[];
document.querySelectorAll(".grp").forEach(function(g){
if(g.dataset.kind==="pal")return;
var ns=Array.from(g.querySelectorAll(".th")).map(function(t){return +t.dataset.n;});
if(g.dataset.kind==="out")out=ns;
else gs.push({name:g.querySelector(".gname").textContent,frames:ns});});
state={groups:gs,out:out};}
function save(){read();localStorage.setItem(KEY,JSON.stringify(state));count();}
function dupe(laneEl,n,skip){return Array.from(laneEl.querySelectorAll(".th")).some(
function(t){return +t.dataset.n===n&&t!==skip;});}
function place(el,src,laneEl,before){
var pal=laneEl.closest(".grp").dataset.kind==="pal";
if(pal){if(src==="g"){el.remove();save();}return;}
var n=+el.dataset.n;
if(src==="p"){if(dupe(laneEl,n)){toast(n+" is already in that group.");return;}
var c=thumb(n,"g");before?laneEl.insertBefore(c,before):laneEl.appendChild(c);save();}
else{if(laneEl!==el.parentNode&&dupe(laneEl,n,el)){toast(n+" is already in that group.");return;}
before?laneEl.insertBefore(el,before):laneEl.appendChild(el);save();}}
function thumb(n,kind){var d=document.createElement("div");d.className="th";d.dataset.n=n;
d.dataset.src=kind;d.draggable=true;
d.innerHTML='<img loading="lazy" src="img/thumb/'+FR[n]+'" alt="'+n+'">'+
'<span class="n">'+n+'</span>'+
(kind==="p"?'<span class="u" style="display:none"></span>':'<button class="rm" type="button" aria-label="Remove">&#215;</button>')+
'<button class="v" type="button" aria-label="View">&#8599;</button>';
d.addEventListener("dragstart",function(e){dragEl=d;d.classList.add("drag");
e.dataTransfer.effectAllowed="copyMove";try{e.dataTransfer.setData("text/plain",String(n));}catch(x){}});
d.addEventListener("dragend",function(){d.classList.remove("drag");
document.querySelectorAll(".th.mark").forEach(function(m){m.classList.remove("mark");});
document.querySelectorAll(".lane.over").forEach(function(l){l.classList.remove("over");});});
d.addEventListener("dragover",function(e){e.preventDefault();
if(dragEl&&dragEl!==d)d.classList.add("mark");});
d.addEventListener("dragleave",function(){d.classList.remove("mark");});
d.addEventListener("drop",function(e){e.preventDefault();e.stopPropagation();
d.classList.remove("mark");
if(dragEl&&dragEl!==d)place(dragEl,dragEl.dataset.src,d.parentNode,d);dragEl=null;});
d.querySelector(".v").onclick=function(e){e.stopPropagation();
$("lbi").src="img/present/"+FR[n];$("lb").className="on";};
if(kind==="g")d.querySelector(".rm").onclick=function(e){e.stopPropagation();
if(sel===d)sel=null;d.remove();save();};
d.onclick=function(){
if(sel===d){d.classList.remove("sel");sel=null;return;}
if(sel){place(sel,sel.dataset.src,d.parentNode,d);sel.classList.remove("sel");sel=null;return;}
sel=d;d.classList.add("sel");};
return d;}
function lane(){var l=document.createElement("div");l.className="lane";
l.addEventListener("dragover",function(e){e.preventDefault();l.classList.add("over");});
l.addEventListener("dragleave",function(){l.classList.remove("over");});
l.addEventListener("drop",function(e){e.preventDefault();l.classList.remove("over");
if(dragEl)place(dragEl,dragEl.dataset.src,l,null);dragEl=null;});
return l;}
function section(kind,name,ns){var g=document.createElement("div");g.className="grp";g.dataset.kind=kind;
var h=document.createElement("div");h.className="ghead";
h.innerHTML='<span class="gname">'+name+'</span><span class="gcnt"></span>';
if(kind==="g"){var t=document.createElement("span");t.className="tools";
["\\u2191","\\u2193"].forEach(function(a,i){var b=document.createElement("button");b.textContent=a;
b.onclick=function(e){e.stopPropagation();
var sib=i?g.nextElementSibling:g.previousElementSibling;
if(!sib||sib.dataset.kind!=="g")return;
if(i)g.parentNode.insertBefore(sib,g);else g.parentNode.insertBefore(g,sib);
save();};t.appendChild(b);});
var r=document.createElement("button");r.textContent="rename";
r.onclick=function(e){e.stopPropagation();
var nm=window.prompt("Group name",g.querySelector(".gname").textContent);
if(nm){g.querySelector(".gname").textContent=nm;save();}};t.appendChild(r);
var x=document.createElement("button");x.textContent="\\u00d7";
x.onclick=function(e){e.stopPropagation();
if(!window.confirm("Delete this group? Its copies go away; every frame is still in All frames."))return;
if(sel&&laneOf(sel)===g)sel=null;g.remove();save();};t.appendChild(x);
h.appendChild(t);}
h.onclick=function(){if(sel){place(sel,sel.dataset.src,g.querySelector(".lane"),null);
sel.classList.remove("sel");sel=null;}};
g.appendChild(h);
var l=lane();var tk=kind==="pal"?"p":"g";
ns.forEach(function(n){l.appendChild(thumb(n,tk));});
g.appendChild(l);
return g;}
function count(){var use={},outset={};
document.querySelectorAll('.grp[data-kind="g"] .th').forEach(function(t){
use[t.dataset.n]=(use[t.dataset.n]||0)+1;});
document.querySelectorAll('.grp[data-kind="out"] .th').forEach(function(t){outset[t.dataset.n]=1;});
document.querySelectorAll(".grp").forEach(function(g){
g.querySelector(".gcnt").textContent="("+g.querySelectorAll(".th").length+")";});
document.querySelectorAll('.grp[data-kind="pal"] .th').forEach(function(t){
var n=t.dataset.n,b=t.querySelector(".u"),c=use[n]||0;
b.textContent=c;b.style.display=c?"":"none";
t.classList.toggle("parked",!!outset[n]);});}
function render(){var b=$("board");b.innerHTML="";
state.groups.forEach(function(gr){b.appendChild(section("g",gr.name,gr.frames));});
b.appendChild(section("out","Out of the vote",state.out));
b.appendChild(section("pal","All frames",ALL));
count();}
state=load();render();
$("ng").onclick=function(){var nm=window.prompt("Group name","");if(!nm)return;
var out=document.querySelector('.grp[data-kind="out"]');
out.parentNode.insertBefore(section("g",nm,[]),out);save();};
$("rs").onclick=function(){if(window.confirm("Throw away this arrangement and reseed?")){
localStorage.removeItem(KEY);state=load();sel=null;render();}};
$("cp").onclick=function(){read();
var used={};state.groups.forEach(function(g){g.frames.forEach(function(n){used[n]=1;});});
state.out.forEach(function(n){used[n]=1;});
var exp={groups:state.groups,out:state.out,
unused:ALL.filter(function(n){return !used[n];})};
var s=JSON.stringify(exp,null,1);
if(navigator.clipboard&&navigator.clipboard.writeText){
navigator.clipboard.writeText(s).then(function(){toast("Arrangement copied. Paste it to me in the session.");},
function(){window.prompt("Copy this:",s);});}
else window.prompt("Copy this:",s);};
document.querySelector("#lb .x").onclick=function(){$("lb").className="";};
$("lb").onclick=function(e){if(e.target.id==="lb")$("lb").className="";};
</script></body></html>"""


def build():
    nums = {}
    for f in FRAMES:
        m = re.match(r"CILWEB1-(\d+)$", f["id"])
        nums[int(m.group(1)) if m else 1] = f
    placed = {n for _, secs in SECTIONS for _, ns in secs for n in ns}
    groups = [{"name": name, "frames": [n for n in ns if n in placed]}
              for name, ns in SEED_GROUPS]
    allf = sorted(placed, key=lambda n: TIMES.get(nums[n]["id"], "9999"))
    if 2 in placed:
        allf = [2] + [n for n in allf if n != 2]
    seed = {"groups": groups, "out": []}
    files = {n: nums[n]["file"] for n in placed}
    html = (PAGE.replace("__FRAMES__", json.dumps(files))
            .replace("__ALL__", json.dumps(allf))
            .replace("__SEED__", json.dumps(seed)))
    open(os.path.join(HERE, "arrange.html"), "w").write(html)
    print(f"wrote arrange.html ({len(placed)} frames, {len(groups)} seeded groups)")


if __name__ == "__main__":
    build()
