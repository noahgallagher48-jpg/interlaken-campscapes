#!/usr/bin/env python3
"""Builds the two picker pages from frames.json / sections.json / times.json.

    favorites.html   THE SURVEY (Noah's structure, rev 4, 2026-08-04):
                     five sections, headings instruction-only (no themes
                     shown to voters), 25 picks per ballot proportional
                     to set size: bridge-with 2/8, bridge-without 2/6,
                     landscapes 6/23, Shabbat 7/27, rest 8/26 (rest
                     includes the restored first looks 195-197).
                     Pools from his arrangement paste of 2026-08-03,
                     swept against _work/killed.json 2026-08-16: 13 and
                     108 replaced by their keepers 12 and 109, 194 out.
    twenty.html      the marketing pool, Noah cuts it down. No cap.

Both pages are noindex and unlinked from the library. Picks persist in
localStorage until sent. Regenerate: python3 build_vote.py

Votes submit to Web3Forms (api.web3forms.com) with the public access key
below; every vote arrives as an email to noah@abba-photo.com with subject
"Interlaken favorites: <name>". No Google Form, no mail client, no clipboard.
The key is public by design (client-side); the account is Web3Forms free tier
under noah@abba-photo.com, created 2026-08-04.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = json.load(open(os.path.join(HERE, "frames.json")))
import killed as _killed
SECTIONS = _killed.strip(json.load(open(os.path.join(HERE, "sections.json"))))
_killed.check(SECTIONS, __file__)
TIMES = json.load(open(os.path.join(HERE, "_work", "times.json")))

TO = "noah@abba-photo.com"

# Web3Forms public access key; submissions email to noah@abba-photo.com.
W3F_KEY = "b3bc124c-7812-4c4e-8fce-6ea6b9d1c5a2"

CONNECTIONS = ["Current parent", "Alumni", "Staff", "Board", "Friend of camp"]

# ---- THE SURVEY: Noah's Book 87 (arrangement paste, 2026-08-03), classified
# into his four sections by a visual pass; order within each section follows
# his Book order. Judgment calls: 97 (two figures at the rail) sits in the
# rest, not bridge-with-people; 37 reads as the fountain bridge, empty.
SURVEY = [
    {"k": "bp", "title": "The bridge, with people", "q": 2,
     "frames": [58, 23, 63, 61, 60, 170, 57, 161]},
    {"k": "bn", "title": "The bridge, without people", "q": 2,
     "frames": [14, 16, 94, 93, 62, 37]},
    {"k": "ls", "title": "Landscapes, nobody in them", "q": 6,
     "frames": [1, 36, 25, 24, 20, 88, 87, 89, 85, 84, 83, 90, 38, 19, 32, 31,
                40, 178, 109, 101, 124, 145, 140]},
    {"k": "sh", "title": "Shabbat", "q": 7,
     "frames": [42, 43, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54, 56, 68, 71,
                73, 74, 75, 76, 77, 78, 79, 173, 99, 175, 100, 177]},
    {"k": "rest", "title": "The rest", "q": 8,
     "frames": [3, 169, 8, 12, 81, 98, 97, 46, 123, 125, 182, 179, 111, 110,
                185, 184, 188, 193, 160, 158, 153, 186, 148,
                195, 196, 197]},
]
WORDS = {2: "pick two", 3: "pick three", 4: "pick four", 5: "pick five", 6: "pick six", 7: "pick seven", 8: "pick eight"}

def heading(s):
    if s.get("opt"):
        return f"Up to {WORDS[s['q']]} images, if you like"
    return WORDS[s["q"]].capitalize() + " images"

# The marketing pool (2026-08-03): Noah cuts it down; no cap.
TWENTY = [63, 42, 112, 119, 3, 48,
          150, 151, 152, 153, 154, 155, 156, 157,
          120, 121, 122, 130, 186, 187, 188, 190, 177,
          9, 68, 71, 74,
          2, 23, 93, 161, 38, 83, 97, 144, 14, 17]

CSS = """*{margin:0;padding:0;box-sizing:border-box}
body{background:#14110d;color:#ede7dd;font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;padding-bottom:86px}
header{padding:40px 20px 8px;max-width:1180px;margin:0 auto}
h1{font-family:Georgia,serif;font-weight:600;font-size:clamp(24px,4.5vw,34px)}
.sub{color:#a69b8a;font-size:14px;margin-top:6px}
.instr{color:#c9bfa9;font-size:15px;line-height:1.55;margin:16px 0 4px;max-width:640px}
section.sv{max-width:1180px;margin:34px auto 0;padding:0 14px}
h2.sv{font-family:Georgia,serif;font-weight:500;font-size:21px;color:#c9bfa9;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;border-bottom:1px solid rgba(237,231,221,.14);padding-bottom:6px}
h2.sv .q{font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#e2a73e}
h2.sv .scnt{font-size:12.5px;color:#7d745f;margin-left:auto}
h2.sv.full .scnt{color:#8fb573}
.wall{columns:3 360px;column-gap:16px;padding-top:16px}
.card{position:relative;break-inside:avoid;margin-bottom:16px}
.ph{display:block;width:100%;border:0;padding:0;background:#1d1913;cursor:pointer;border-radius:2px;overflow:hidden}
.ph img{display:block;width:100%;height:auto}
.num{position:absolute;left:9px;bottom:8px;font-size:12px;color:#cfc6b4;text-shadow:0 1px 4px #000}
.sel{position:absolute;top:8px;right:8px;width:34px;height:34px;border-radius:50%;border:2px solid rgba(237,231,221,.85);background:rgba(20,17,13,.35);cursor:pointer;box-shadow:0 1px 5px rgba(0,0,0,.5)}
.card.on .sel{background:#e2a73e;border-color:#e2a73e}
.card.on .sel::after{content:"";position:absolute;inset:9px 9px 12px;border:solid #14110d;border-width:0 0 3px 3px;transform:rotate(-45deg)}
.card.on .ph{outline:3px solid #e2a73e;outline-offset:-3px}
body.rv .card:not(.on){display:none}
#bar{position:fixed;left:0;right:0;bottom:0;background:rgba(24,20,15,.97);border-top:1px solid rgba(226,167,62,.35);display:flex;align-items:center;gap:10px;padding:12px 16px;z-index:8}
#cnt{font-size:14px;color:#ede7dd;flex:1;min-width:0}
#bar button{background:none;border:1px solid rgba(226,167,62,.55);color:#e2a73e;padding:9px 14px;border-radius:3px;font-size:12px;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;white-space:nowrap}
#bar button.go{background:#e2a73e;color:#14110d;font-weight:600}
#toast{position:fixed;left:50%;bottom:78px;transform:translateX(-50%);background:#ede7dd;color:#14110d;padding:10px 16px;border-radius:4px;font-size:13px;opacity:0;pointer-events:none;transition:opacity .25s;z-index:12;max-width:88vw;text-align:center}
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
#send{position:fixed;inset:0;background:rgba(10,8,6,.9);display:none;align-items:center;justify-content:center;z-index:11;padding:18px}
#send.on{display:flex}
#sheet{background:#1d1913;border:1px solid rgba(226,167,62,.35);border-radius:6px;padding:24px 22px;width:min(430px,100%)}
#sheet h2{font-family:Georgia,serif;font-weight:600;font-size:20px;margin-bottom:16px}
#sheet label,#sheet .lbl{display:block;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#a69b8a;margin:14px 0 6px}
#sheet .opt{text-transform:none;letter-spacing:0}
#sheet input{width:100%;background:#14110d;border:1px solid rgba(237,231,221,.25);border-radius:3px;color:#ede7dd;padding:10px 12px;font-size:15px}
#sheet textarea{width:100%;background:#14110d;border:1px solid rgba(237,231,221,.25);border-radius:3px;color:#ede7dd;padding:10px 12px;font-size:15px;font-family:inherit;resize:vertical;min-height:64px}
#sheet textarea::placeholder,#sheet input::placeholder{color:#7d745f}
#conns{display:flex;flex-wrap:wrap;gap:8px}
#conns button{background:none;border:1px solid rgba(237,231,221,.3);color:#c9bfa9;padding:8px 12px;border-radius:16px;font-size:13px;cursor:pointer}
#conns button.on{background:#e2a73e;border-color:#e2a73e;color:#14110d;font-weight:600}
#sheet .row{display:flex;gap:10px;margin-top:20px;flex-wrap:wrap}
#sheet .row button{background:none;border:1px solid rgba(226,167,62,.55);color:#e2a73e;padding:10px 16px;border-radius:3px;font-size:12px;letter-spacing:.1em;text-transform:uppercase;cursor:pointer}
#sheet .row button.go{background:#e2a73e;color:#14110d;font-weight:600}
footer{max-width:1180px;margin:34px auto 0;padding:0 20px 30px;color:#7d745f;font-size:12px;letter-spacing:.14em;text-transform:uppercase}"""

SURVEY_PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>Camp Interlaken &middot; favorites</title><style>
__CSS__
</style></head><body>
<header><h1>Camp Interlaken</h1><div class=sub>Summer 2026 &middot; the favorites vote</div>
<p class=instr>Five sets of photographs. Each set says how many to pick: the ones that
stay with you. Twenty five in all.
Tap a photo to see it large, tap the circle to pick it. Your picks save on this device
until you send them.</p></header>
__SECTIONS__
<div id=bar><div id=cnt></div><button id=rv type=button>My picks</button><button id=go class=go type=button>Send</button></div>
<div id=toast></div>
<div id=lb><img id=lbi alt=""><button class="nav pv" aria-label="Previous"></button><button class="nav nx" aria-label="Next"></button><button class=x aria-label="Close">&times;</button><div id=lbbar><span class=id id=lbid></span><button class=pk id=lbpk type=button>Pick</button></div></div>
<div id=send><div id=sheet>
<h2>Send your picks</h2>
<label for=nm>Name</label><input id=nm autocomplete=name>
<div class=lbl>Connection to camp</div><div id=conns>__CONNS__</div>
<label for=wb>What does your favorite image bring back for you? <span class=opt>(optional)</span></label><textarea id=wb placeholder="A moment, a sound, a summer."></textarea>
<label for=em>Email <span class=opt>(optional)</span></label><input id=em type=email autocomplete=email>
<div class=row><button id=sgo class=go type=button>Send</button><button id=sx type=button>Back</button></div>
</div></div>
<footer>Photographs Noah Gallagher &middot; Abba Photo</footer>
<script>
var KEY="cil-survey3",SUBJ="Interlaken favorites",W3F=__W3F__;
var SECS=__SECS__;
var picks={},cur=null,tt=null;
try{picks=JSON.parse(localStorage.getItem(KEY))||{};}catch(e){picks={};}
SECS.forEach(function(s){if(!Array.isArray(picks[s.k]))picks[s.k]=[];});
function $(i){return document.getElementById(i);}
function sec(k){for(var i=0;i<SECS.length;i++)if(SECS[i].k===k)return SECS[i];}
function toast(m){var t=$("toast");t.textContent=m;t.className="on";
clearTimeout(tt);tt=setTimeout(function(){t.className="";},2600);}
function save(){localStorage.setItem(KEY,JSON.stringify(picks));}
function total(){var n=0;SECS.forEach(function(s){n+=picks[s.k].length;});return n;}
function need(){var m=0;SECS.forEach(function(s){if(!s.opt)m+=s.q;});return m;}
function reqtotal(){var n=0;SECS.forEach(function(s){if(!s.opt)n+=picks[s.k].length;});return n;}
function bar(){
$("cnt").textContent=total()+" picked";
SECS.forEach(function(s){var h=$("h-"+s.k);
h.querySelector(".scnt").textContent=picks[s.k].length+" of up to "+s.q;
h.className=picks[s.k].length>0?"sv full":"sv";});}
function mark(k,n){var c=document.querySelector('#s-'+k+' .card[data-n="'+n+'"]');
if(c)c.className=picks[k].indexOf(n)>=0?"card on":"card";
if(cur){var s=sec(cur.k),m=s.frames[cur.i],pk=$("lbpk");
pk.className=picks[cur.k].indexOf(m)>=0?"pk on":"pk";
pk.textContent=picks[cur.k].indexOf(m)>=0?"Picked":"Pick";}}
function toggle(k,n){var a=picks[k],i=a.indexOf(n),s=sec(k);
if(i<0&&a.length>=s.q){toast("That set has its "+s.q+". Unpick one first.");return;}
i<0?a.push(n):a.splice(i,1);save();bar();mark(k,n);}
document.querySelectorAll("section.sv .card").forEach(function(c){
var k=c.closest("section").dataset.k,n=+c.dataset.n;
if(picks[k].indexOf(n)>=0)c.className="card on";
c.querySelector(".sel").onclick=function(e){e.stopPropagation();toggle(k,n);};
c.querySelector(".ph").onclick=function(){open_(k,sec(k).frames.indexOf(n));};});
function open_(k,i){var s=sec(k);cur={k:k,i:(i+s.frames.length)%s.frames.length};
var n=s.frames[cur.i];
$("lbi").src="img/present/"+s.files[cur.i];
$("lbid").textContent=n;
$("lb").className="on";mark(k,n);}
function shut(){$("lb").className="";cur=null;}
document.querySelector("#lb .x").onclick=shut;
document.querySelector("#lb .pv").onclick=function(){if(cur)open_(cur.k,cur.i-1);};
document.querySelector("#lb .nx").onclick=function(){if(cur)open_(cur.k,cur.i+1);};
$("lbpk").onclick=function(){if(cur)toggle(cur.k,sec(cur.k).frames[cur.i]);};
document.addEventListener("keydown",function(e){if(!cur)return;
if(e.key==="ArrowRight")open_(cur.k,cur.i+1);if(e.key==="ArrowLeft")open_(cur.k,cur.i-1);
if(e.key==="Escape")shut();});
$("rv").onclick=function(){document.body.classList.toggle("rv");
this.textContent=document.body.classList.contains("rv")?"See all":"My picks";};
function enc(s){return encodeURIComponent(s);}
/* Whatever they pick is a ballot (Noah, 2026-08-24). One favorite counts. */
$("go").onclick=function(){
if(!total()){toast("Pick at least one favorite first.");return;}
$("send").className="on";};
$("sx").onclick=function(){$("send").className="";};
var conn=localStorage.getItem(KEY+":conn")||"";
$("nm").value=localStorage.getItem(KEY+":name")||"";
$("em").value=localStorage.getItem(KEY+":email")||"";
document.querySelectorAll("#conns button").forEach(function(b){
if(b.textContent===conn)b.className="on";
b.onclick=function(){conn=b.textContent;
document.querySelectorAll("#conns button").forEach(function(x){x.className=x===b?"on":"";});};});
function lists(){var o={};SECS.forEach(function(s){
o[s.k]=picks[s.k].slice().sort(function(a,b){return a-b;}).join(", ");});return o;}
$("sgo").onclick=function(){
if(!total()){$("send").className="";toast("Pick at least one favorite first.");return;}
var n=$("nm").value.trim();
if(!n){toast("Your name goes first.");return;}
if(!conn){toast("Tap your connection to camp.");return;}
var e=$("em").value.trim(),wb=$("wb").value.trim();
localStorage.setItem(KEY+":name",n);localStorage.setItem(KEY+":conn",conn);
localStorage.setItem(KEY+":email",e);
var L=lists(),b=this;
var payload={access_key:W3F,subject:SUBJ+": "+n,from_name:"Interlaken favorites vote",
botcheck:"",name:n,connection:conn,email:e,what_it_brings_back:wb,
bridge_with_people:L.bp,bridge_without_people:L.bn,landscapes:L.ls,shabbat:L.sh,the_rest:L.rest};
b.disabled=true;b.textContent="Sending…";
fetch("https://api.web3forms.com/submit",{method:"POST",
headers:{"Content-Type":"application/json",Accept:"application/json"},
body:JSON.stringify(payload)}).then(function(r){return r.json();}).then(function(r){
if(r.success){$("send").className="";b.textContent="Sent";
toast("Got it. Thank you, "+n+".");}
else{b.disabled=false;b.textContent="Send my picks";
toast("That did not go through. Try once more.");}},
function(){b.disabled=false;b.textContent="Send my picks";
toast("That did not go through. Try once more.");});};
bar();
</script><script data-goatcounter="https://abba-photo.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script></body></html>"""

POOL_PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>Camp Interlaken &middot; the marketing pool</title><style>
__CSS__
</style></head><body>
<header><h1>Camp Interlaken &middot; the marketing pool</h1><div class=sub>__N__ frames &middot; cut it down</div>
<p class=instr>Tap the circle on the frames that go out. No cap. Copy puts the numbered
list on the clipboard; if it balks, a box pops up with the list to grab.</p></header>
<section class=sv data-k=all>
__WALL__
</section>
<div id=bar><div id=cnt></div><button id=rv type=button>My picks</button><button id=cp class=go type=button>Copy</button></div>
<div id=toast></div>
<div id=lb><img id=lbi alt=""><button class="nav pv" aria-label="Previous"></button><button class="nav nx" aria-label="Next"></button><button class=x aria-label="Close">&times;</button><div id=lbbar><span class=id id=lbid></span><button class=pk id=lbpk type=button>Pick</button></div></div>
<footer>Photographs Noah Gallagher &middot; Abba Photo</footer>
<script>
var KEY="cil-twenty",F=__LIST__;
var picks=new Set(JSON.parse(localStorage.getItem(KEY)||"[]")),cur=-1,tt=null;
function $(i){return document.getElementById(i);}
function toast(m){var t=$("toast");t.textContent=m;t.className="on";
clearTimeout(tt);tt=setTimeout(function(){t.className="";},2400);}
function save(){localStorage.setItem(KEY,JSON.stringify(Array.from(picks)));}
function bar(){$("cnt").textContent=picks.size+" picked";}
function mark(n){var c=document.querySelector('.card[data-n="'+n+'"]');
if(c)c.className=picks.has(n)?"card on":"card";
if(cur>=0){var k=F[cur].n,pk=$("lbpk");
pk.className=picks.has(k)?"pk on":"pk";pk.textContent=picks.has(k)?"Picked":"Pick";}}
function toggle(n){picks.has(n)?picks.delete(n):picks.add(n);save();bar();mark(n);}
document.querySelectorAll(".card").forEach(function(c){var n=+c.dataset.n;
if(picks.has(n))c.className="card on";
c.querySelector(".sel").onclick=function(e){e.stopPropagation();toggle(n);};
c.querySelector(".ph").onclick=function(){open_(F.findIndex(function(f){return f.n===n;}));};});
function open_(i){cur=(i+F.length)%F.length;var f=F[cur];
$("lbi").src="img/present/"+f.f;$("lbid").textContent=f.n;
$("lb").className="on";mark(f.n);}
function shut(){$("lb").className="";cur=-1;}
document.querySelector("#lb .x").onclick=shut;
document.querySelector("#lb .pv").onclick=function(){open_(cur-1);};
document.querySelector("#lb .nx").onclick=function(){open_(cur+1);};
$("lbpk").onclick=function(){if(cur>=0)toggle(F[cur].n);};
document.addEventListener("keydown",function(e){if(cur<0)return;
if(e.key==="ArrowRight")open_(cur+1);if(e.key==="ArrowLeft")open_(cur-1);
if(e.key==="Escape")shut();});
$("rv").onclick=function(){document.body.classList.toggle("rv");
this.textContent=document.body.classList.contains("rv")?"See all":"My picks";};
$("cp").onclick=function(){if(!picks.size){toast("Nothing picked yet.");return;}
var s="Interlaken marketing picks: "+Array.from(picks).sort(function(a,b){return a-b;}).join(", ");
if(navigator.clipboard&&navigator.clipboard.writeText){
navigator.clipboard.writeText(s).then(function(){toast("Copied.");},
function(){window.prompt("Copy this:",s);});}
else window.prompt("Copy this:",s);};
bar();
</script><script data-goatcounter="https://abba-photo.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script></body></html>"""


# The SURVEY and TWENTY lists are hardcoded, so the sections.json filter above
# does not cover them. A killed frame in either list stops the build here.
_kills = _killed.killed()
_bad = sorted((set(n for s in SURVEY for n in s["frames"]) | set(TWENTY)) & _kills)
if _bad:
    raise SystemExit(f"build_vote.py: killed frames in ballot lists: {_bad}")


def by_num():
    out = {}
    for f in FRAMES:
        m = re.match(r"CILWEB1-(\d+)$", f["id"])
        out[int(m.group(1)) if m else 1] = f
    return out


def cards(pairs):
    out = ['<div class="wall">']
    for n, f in pairs:
        out.append(f'<div class="card" data-n="{n}">'
                   f'<button class="ph" type="button" aria-label="View {n}">'
                   f'<img loading="lazy" src="img/thumb/{f["file"]}" alt="{f["id"]}"></button>'
                   f'<button class="sel" type="button" aria-label="Pick {n}"></button>'
                   f'<span class="num">{n}</span></div>')
    out.append('</div>')
    return "\n".join(out)


def build():
    nums = by_num()

    secs_html, secs_js = [], []
    for s in SURVEY:
        pairs = [(n, nums[n]) for n in s["frames"]]
        secs_html.append(
            f'<section class=sv data-k={s["k"]} id=s-{s["k"]}>\n'
            f'<h2 class=sv id=h-{s["k"]}><span>{heading(s)}</span>'
            f'<span class=scnt></span></h2>\n'
            + cards(pairs) + '\n</section>')
        secs_js.append({"k": s["k"], "title": s["title"], "q": s["q"],
                        "opt": bool(s.get("opt")),
                        "frames": s["frames"],
                        "files": [nums[n]["file"] for n in s["frames"]]})
    conns = "".join(f'<button type=button>{c}</button>' for c in CONNECTIONS)
    html = (SURVEY_PAGE.replace("__CSS__", CSS)
            .replace("__SECTIONS__", "\n".join(secs_html))
            .replace("__CONNS__", conns)
            .replace("__W3F__", json.dumps(W3F_KEY))
            .replace("__SECS__", json.dumps(secs_js)))
    open(os.path.join(HERE, "favorites.html"), "w").write(html)
    print(f"wrote favorites.html (survey, {sum(len(s['frames']) for s in SURVEY)} frames "
          f"across {len(SURVEY)} sections, {sum(s['q'] for s in SURVEY)} picks)")

    pairs = [(n, nums[n]) for n in TWENTY]
    html = (POOL_PAGE.replace("__CSS__", CSS)
            .replace("__N__", str(len(TWENTY)))
            .replace("__WALL__", cards(pairs))
            .replace("__LIST__", json.dumps(
                [{"n": n, "f": f["file"]} for n, f in pairs])))
    open(os.path.join(HERE, "twenty.html"), "w").write(html)
    print(f"wrote twenty.html ({len(TWENTY)} frames)")


if __name__ == "__main__":
    build()
