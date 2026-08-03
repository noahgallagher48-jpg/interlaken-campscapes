#!/usr/bin/env python3
"""Builds two standalone picker pages from frames.json / sections.json / times.json.

    favorites.html   every placed frame, chronological. For the camp's people:
                     each person picks ten, sends the list to noah@abba-photo.com.
                     Aggregated by hand to find the frames that resonate.
    twenty.html      the marketing shortlist, Noah cuts it to ten.

Both pages are noindex and unlinked from the library. Picks persist in
localStorage until sent. Regenerate: python3 build_vote.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = json.load(open(os.path.join(HERE, "frames.json")))
SECTIONS = json.load(open(os.path.join(HERE, "sections.json")))
TIMES = json.load(open(os.path.join(HERE, "_work", "times.json")))

# The marketing shortlist (2026-08-03): kids and energy, the gatherings, the
# place by day, the sky. Noah picks ten from these.
TWENTY = [63, 42, 112, 119, 3, 48, 9, 68, 71, 74,
          2, 23, 93, 161, 38, 83, 97, 144, 14, 17]

TO = "noah@abba-photo.com"

PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>__TITLE__</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#14110d;color:#ede7dd;font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;padding-bottom:86px}
header{padding:40px 20px 8px;max-width:1180px;margin:0 auto}
h1{font-family:Georgia,serif;font-weight:600;font-size:clamp(24px,4.5vw,34px)}
.sub{color:#a69b8a;font-size:14px;margin-top:6px}
.instr{color:#c9bfa9;font-size:15px;line-height:1.55;margin:16px 0 4px;max-width:640px}
.wall{max-width:1180px;margin:18px auto 0;padding:0 14px;display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px}
.card{position:relative}
.ph{display:block;width:100%;border:0;padding:0;background:#1d1913;cursor:pointer;border-radius:2px;overflow:hidden}
.ph img{display:block;width:100%;height:100%;object-fit:cover;aspect-ratio:4/3}
.num{position:absolute;left:7px;bottom:6px;font-size:11px;color:#cfc6b4;text-shadow:0 1px 4px #000}
.sel{position:absolute;top:6px;right:6px;width:30px;height:30px;border-radius:50%;border:2px solid rgba(237,231,221,.85);background:rgba(20,17,13,.35);cursor:pointer;box-shadow:0 1px 5px rgba(0,0,0,.5)}
.card.on .sel{background:#e2a73e;border-color:#e2a73e}
.card.on .sel::after{content:"";position:absolute;inset:7px 8px 9px;border:solid #14110d;border-width:0 0 3px 3px;transform:rotate(-45deg)}
.card.on .ph{outline:3px solid #e2a73e;outline-offset:-3px}
body.rv .card:not(.on){display:none}
#bar{position:fixed;left:0;right:0;bottom:0;background:rgba(24,20,15,.97);border-top:1px solid rgba(226,167,62,.35);display:flex;align-items:center;gap:10px;padding:12px 16px;z-index:8}
#cnt{font-size:14px;color:#ede7dd;flex:1;min-width:0}
#bar button{background:none;border:1px solid rgba(226,167,62,.55);color:#e2a73e;padding:9px 14px;border-radius:3px;font-size:12px;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;white-space:nowrap}
#bar button.go{background:#e2a73e;color:#14110d;font-weight:600}
#toast{position:fixed;left:50%;bottom:78px;transform:translateX(-50%);background:#ede7dd;color:#14110d;padding:10px 16px;border-radius:4px;font-size:13px;opacity:0;pointer-events:none;transition:opacity .25s;z-index:9;max-width:88vw;text-align:center}
#toast.on{opacity:1}
#lb{position:fixed;inset:0;background:rgba(10,8,6,.97);display:none;align-items:center;justify-content:center;z-index:10}
#lb.on{display:flex}
#lb img{max-width:100vw;max-height:calc(100vh - 70px);object-fit:contain}
#lb .x{position:fixed;top:8px;right:12px;font-size:30px;color:#a69b8a;background:none;border:0;cursor:pointer;padding:6px 10px}
#lb .nav{position:fixed;top:0;bottom:70px;width:26%;background:none;border:0;cursor:pointer}
#lb .pv{left:0}#lb .nx{right:0}
#lbbar{position:fixed;left:0;right:0;bottom:0;height:70px;display:flex;align-items:center;justify-content:center;gap:16px}
#lbbar .pk{background:none;border:1px solid rgba(226,167,62,.55);color:#e2a73e;padding:10px 18px;border-radius:3px;font-size:12px;letter-spacing:.1em;text-transform:uppercase;cursor:pointer}
#lbbar .pk.on{background:#e2a73e;color:#14110d;font-weight:600}
#lbbar .id{color:#a69b8a;font-size:13px}
footer{max-width:1180px;margin:34px auto 0;padding:0 20px 30px;color:#7d745f;font-size:12px;letter-spacing:.14em;text-transform:uppercase}
</style></head><body>
<header><h1>__TITLE__</h1><div class=sub>__SUB__</div>
<p class=instr>__INSTR__</p></header>
__WALL__
<div id=bar><div id=cnt></div><button id=rv type=button>My picks</button><button id=cp type=button>Copy</button><button id=go class=go type=button>Email</button></div>
<div id=toast></div>
<div id=lb><img id=lbi alt=""><button class="nav pv" aria-label="Previous"></button><button class="nav nx" aria-label="Next"></button><button class=x aria-label="Close">&times;</button><div id=lbbar><span class=id id=lbid></span><button class=pk id=lbpk type=button>Pick</button></div></div>
<footer>Photographs Noah Gallagher &middot; Abba Photo</footer>
<script>
var CAP=__CAP__,KEY=__KEY__,SUBJ=__SUBJ__,TO=__TO__;
var F=__LIST__;
var picks=new Set(JSON.parse(localStorage.getItem(KEY)||"[]"));
var cards={},cur=-1,tt=null;
function save(){localStorage.setItem(KEY,JSON.stringify(Array.from(picks)));}
function toast(m){var t=document.getElementById("toast");t.textContent=m;t.className="on";
clearTimeout(tt);tt=setTimeout(function(){t.className="";},2400);}
function bar(){document.getElementById("cnt").textContent=picks.size+" of "+CAP+" picked";}
function mark(n){var c=cards[n];if(c)c.className=picks.has(n)?"card on":"card";
var pk=document.getElementById("lbpk");
if(cur>=0){var k=F[cur].n;pk.className=picks.has(k)?"pk on":"pk";pk.textContent=picks.has(k)?"Picked":"Pick";}}
function toggle(n){if(!picks.has(n)&&picks.size>=CAP){toast("That is "+CAP+". Unpick one to add this one.");return;}
picks.has(n)?picks.delete(n):picks.add(n);save();bar();mark(n);}
document.querySelectorAll(".card").forEach(function(c){var n=+c.dataset.n;cards[n]=c;
if(picks.has(n))c.className="card on";
c.querySelector(".sel").onclick=function(e){e.stopPropagation();toggle(n);};
c.querySelector(".ph").onclick=function(){open_(F.findIndex(function(f){return f.n===n;}));};});
function open_(i){cur=(i+F.length)%F.length;var f=F[cur];
document.getElementById("lbi").src="img/present/"+f.f;
document.getElementById("lbid").textContent=f.n;
document.getElementById("lb").className="on";mark(f.n);}
function shut(){document.getElementById("lb").className="";cur=-1;}
document.querySelector("#lb .x").onclick=shut;
document.querySelector("#lb .pv").onclick=function(){open_(cur-1);};
document.querySelector("#lb .nx").onclick=function(){open_(cur+1);};
document.getElementById("lbpk").onclick=function(){if(cur>=0)toggle(F[cur].n);};
document.addEventListener("keydown",function(e){if(cur<0)return;
if(e.key==="ArrowRight")open_(cur+1);if(e.key==="ArrowLeft")open_(cur-1);
if(e.key==="Escape")shut();});
document.getElementById("rv").onclick=function(){document.body.classList.toggle("rv");
this.textContent=document.body.classList.contains("rv")?"See all":"My picks";};
function list(){return Array.from(picks).sort(function(a,b){return a-b;}).join(", ");}
function name_(){var n=localStorage.getItem(KEY+":name")||"";
n=window.prompt("Your name",n)||"";if(n)localStorage.setItem(KEY+":name",n);return n;}
document.getElementById("go").onclick=function(){if(!picks.size){toast("Nothing picked yet.");return;}
var n=name_();if(!n)return;
location.href="mailto:"+TO+"?subject="+encodeURIComponent(SUBJ+" from "+n)+
"&body="+encodeURIComponent("Name: "+n+"\\nPicks: "+list());};
document.getElementById("cp").onclick=function(){if(!picks.size){toast("Nothing picked yet.");return;}
var n=name_();if(!n)return;var s=SUBJ+" from "+n+": "+list()+"  (send to "+TO+")";
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(s).then(function(){toast("Copied. Text or email it to Noah.");});}
else window.prompt("Copy this:",s);};
bar();
</script></body></html>"""


def by_num():
    out = {}
    for f in FRAMES:
        m = re.match(r"CILWEB1-(\d+)$", f["id"])
        out[int(m.group(1)) if m else 1] = f
    return out


def cards(frames):
    out = ['<div class="wall">']
    for n, f in frames:
        out.append(f'<div class="card" data-n="{n}">'
                   f'<button class="ph" type="button" aria-label="View {n}">'
                   f'<img loading="lazy" src="img/thumb/{f["file"]}" alt="{f["id"]}"></button>'
                   f'<button class="sel" type="button" aria-label="Pick {n}"></button>'
                   f'<span class="num">{n}</span></div>')
    out.append('</div>')
    return "\n".join(out)


def emit(name, title, sub, instr, frames, cap, key, subj):
    html = (PAGE.replace("__TITLE__", title).replace("__SUB__", sub)
            .replace("__INSTR__", instr).replace("__WALL__", cards(frames))
            .replace("__CAP__", str(cap)).replace("__KEY__", json.dumps(key))
            .replace("__SUBJ__", json.dumps(subj)).replace("__TO__", json.dumps(TO))
            .replace("__LIST__", json.dumps([{"n": n, "f": f["file"]} for n, f in frames])))
    open(os.path.join(HERE, name), "w").write(html)
    print(f"wrote {name} ({len(frames)} frames)")


def build():
    nums = by_num()
    placed = {n for _, secs in SECTIONS for _, ns in secs for n in ns}
    chron = sorted(placed, key=lambda n: TIMES.get(nums[n]["id"], "9999"))
    if 2 in placed:
        chron = [2] + [n for n in chron if n != 2]
    emit("favorites.html", "Camp Interlaken", f"Summer 2026 &middot; {len(chron)} photographs",
         "Pick the ten that stay with you. Tap a photo to see it large, tap the circle "
         "to pick it. Your picks save on this device until you send them.",
         [(n, nums[n]) for n in chron], 10, "cil-fav", "Interlaken favorites")
    emit("twenty.html", "Camp Interlaken &middot; twenty frames", "Cut to ten",
         "Tap the circle on the ten that go out. Copy sends the list to the clipboard.",
         [(n, nums[n]) for n in TWENTY], 10, "cil-twenty", "Interlaken marketing ten")


if __name__ == "__main__":
    build()
