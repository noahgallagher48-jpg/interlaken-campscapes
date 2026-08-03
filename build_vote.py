#!/usr/bin/env python3
"""Builds two standalone picker pages from frames.json / sections.json / times.json.

    favorites.html   every placed frame, chronological. The community favorites
                     vote: each voter picks ten and sends them with their name
                     and connection to camp. Aggregates into the resonance
                     report for the camp's development work.
    twenty.html      the marketing shortlist, Noah cuts it to ten.

Both pages are noindex and unlinked from the library. Picks persist in
localStorage until sent. Regenerate: python3 build_vote.py

FORM wiring: once the Google Form exists, fill FORM below with the viewform
base URL and the entry IDs (from the form's public HTML) and regenerate. Until
then the send flow falls back to email and copy.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = json.load(open(os.path.join(HERE, "frames.json")))
SECTIONS = json.load(open(os.path.join(HERE, "sections.json")))
TIMES = json.load(open(os.path.join(HERE, "_work", "times.json")))

# The marketing pool (2026-08-03, expanded same day on Noah's word: "activity
# shots, those are marketing"): kids and energy, water skiing, the activities,
# the gatherings, the place by day, the sky. Noah cuts it down; no cap.
TWENTY = [63, 42, 112, 119, 3, 48,
          150, 151, 152, 153, 154, 155, 156, 157,
          120, 121, 122, 130, 186, 187, 188, 190, 177,
          9, 68, 71, 74,
          2, 23, 93, 161, 38, 83, 97, 144, 14, 17]

TO = "noah@abba-photo.com"

# Google Form behind favorites.html. None until the form exists; then set base
# to the form's formResponse URL and the entry IDs from its public HTML. The
# page then submits silently in the background: tap Send, done, no mail client.
# FORM = {"base": "https://docs.google.com/forms/d/e/FORM_ID/formResponse",
#         "name": "entry.111", "conn": "entry.222",
#         "email": "entry.333", "picks": "entry.444"}
FORM = None

CONNECTIONS = ["Current parent", "Alumni", "Staff", "Board", "Friend of camp"]

PANEL = """<div id=send><div id=sheet>
<h2>Send your ten</h2>
<label for=nm>Name</label><input id=nm autocomplete=name>
<div class=lbl>Connection to camp</div><div id=conns>__CONNS__</div>
<label for=em>Email <span class=opt>(optional)</span></label><input id=em type=email autocomplete=email>
<div class=row><button id=sgo class=go type=button>Send</button><button id=scp type=button>Copy instead</button><button id=sx type=button>Back</button></div>
</div></div>"""

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
#conns{display:flex;flex-wrap:wrap;gap:8px}
#conns button{background:none;border:1px solid rgba(237,231,221,.3);color:#c9bfa9;padding:8px 12px;border-radius:16px;font-size:13px;cursor:pointer}
#conns button.on{background:#e2a73e;border-color:#e2a73e;color:#14110d;font-weight:600}
#sheet .row{display:flex;gap:10px;margin-top:20px;flex-wrap:wrap}
#sheet .row button{background:none;border:1px solid rgba(226,167,62,.55);color:#e2a73e;padding:10px 16px;border-radius:3px;font-size:12px;letter-spacing:.1em;text-transform:uppercase;cursor:pointer}
#sheet .row button.go{background:#e2a73e;color:#14110d;font-weight:600}
footer{max-width:1180px;margin:34px auto 0;padding:0 20px 30px;color:#7d745f;font-size:12px;letter-spacing:.14em;text-transform:uppercase}
</style></head><body>
<header><h1>__TITLE__</h1><div class=sub>__SUB__</div>
<p class=instr>__INSTR__</p></header>
__WALL__
<div id=bar><div id=cnt></div>__BARBTNS__</div>
<div id=toast></div>
<div id=lb><img id=lbi alt=""><button class="nav pv" aria-label="Previous"></button><button class="nav nx" aria-label="Next"></button><button class=x aria-label="Close">&times;</button><div id=lbbar><span class=id id=lbid></span><button class=pk id=lbpk type=button>Pick</button></div></div>
__PANEL__
<footer>Photographs Noah Gallagher &middot; Abba Photo</footer>
<script>
var CAP=__CAP__,KEY=__KEY__,SUBJ=__SUBJ__,TO=__TO__,FORM=__FORM__;
var F=__LIST__;
var picks=new Set(JSON.parse(localStorage.getItem(KEY)||"[]"));
var cards={},cur=-1,tt=null;
function $(i){return document.getElementById(i);}
function save(){localStorage.setItem(KEY,JSON.stringify(Array.from(picks)));}
function toast(m){var t=$("toast");t.textContent=m;t.className="on";
clearTimeout(tt);tt=setTimeout(function(){t.className="";},2600);}
function bar(){$("cnt").textContent=CAP<99?picks.size+" of "+CAP+" picked":picks.size+" picked";}
function mark(n){var c=cards[n];if(c)c.className=picks.has(n)?"card on":"card";
var pk=$("lbpk");
if(cur>=0){var k=F[cur].n;pk.className=picks.has(k)?"pk on":"pk";pk.textContent=picks.has(k)?"Picked":"Pick";}}
function toggle(n){if(!picks.has(n)&&picks.size>=CAP){toast("That is "+CAP+". Unpick one to add this one.");return;}
picks.has(n)?picks.delete(n):picks.add(n);save();bar();mark(n);}
document.querySelectorAll(".card").forEach(function(c){var n=+c.dataset.n;cards[n]=c;
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
function list(){return Array.from(picks).sort(function(a,b){return a-b;}).join(", ");}
function enc(s){return encodeURIComponent(s);}
function copyOut(s,m){if(navigator.clipboard&&navigator.clipboard.writeText){
navigator.clipboard.writeText(s).then(function(){toast(m);},function(){window.prompt("Copy this:",s);});}
else window.prompt("Copy this:",s);}
if($("send")){
var conn=localStorage.getItem(KEY+":conn")||"";
$("nm").value=localStorage.getItem(KEY+":name")||"";
$("em").value=localStorage.getItem(KEY+":email")||"";
document.querySelectorAll("#conns button").forEach(function(b){
if(b.textContent===conn)b.className="on";
b.onclick=function(){conn=b.textContent;
document.querySelectorAll("#conns button").forEach(function(x){x.className=x===b?"on":"";});};});
$("go").onclick=function(){if(!picks.size){toast("Nothing picked yet.");return;}
$("send").className="on";};
$("sx").onclick=function(){$("send").className="";};
function fields(){var n=$("nm").value.trim();
if(!n){toast("Your name goes first.");return null;}
if(!conn){toast("Tap your connection to camp.");return null;}
var e=$("em").value.trim();
localStorage.setItem(KEY+":name",n);localStorage.setItem(KEY+":conn",conn);
localStorage.setItem(KEY+":email",e);
return {n:n,c:conn,e:e};}
function body_(f){return "Name: "+f.n+"\\nConnection: "+f.c+(f.e?"\\nEmail: "+f.e:"")+"\\nPicks: "+list();}
$("sgo").onclick=function(){var f=fields();if(!f)return;var b=this;
if(FORM){var fd=new FormData();fd.append(FORM.name,f.n);fd.append(FORM.conn,f.c);
if(f.e)fd.append(FORM.email,f.e);fd.append(FORM.picks,list());
b.disabled=true;
fetch(FORM.base,{method:"POST",mode:"no-cors",body:fd}).then(function(){
$("send").className="";b.disabled=false;$("go").textContent="Sent";
toast("Got it. Thank you, "+f.n+".");},function(){b.disabled=false;
toast("That did not go through. Try once more.");});}
else location.href="mailto:"+TO+"?subject="+enc(SUBJ+" from "+f.n)+"&body="+enc(body_(f));};
$("scp").onclick=function(){var f=fields();if(!f)return;
copyOut(body_(f)+"\\n(send to "+TO+")","Copied. Text or email it to Noah.");};
}else{
$("cp").onclick=function(){if(!picks.size){toast("Nothing picked yet.");return;}
copyOut(SUBJ+": "+list(),"Copied.");};
}
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


def emit(name, title, sub, instr, frames, cap, key, subj, panel):
    if panel:
        pan = PANEL.replace("__CONNS__", "".join(
            f'<button type=button>{c}</button>' for c in CONNECTIONS))
        btns = '<button id=rv type=button>My picks</button><button id=go class=go type=button>Send</button>'
    else:
        pan = ""
        btns = ('<button id=rv type=button>My picks</button>'
                '<button id=cp class=go type=button>Copy</button>')
    html = (PAGE.replace("__TITLE__", title).replace("__SUB__", sub)
            .replace("__INSTR__", instr).replace("__WALL__", cards(frames))
            .replace("__BARBTNS__", btns).replace("__PANEL__", pan)
            .replace("__CAP__", str(cap)).replace("__KEY__", json.dumps(key))
            .replace("__SUBJ__", json.dumps(subj)).replace("__TO__", json.dumps(TO))
            .replace("__FORM__", json.dumps(FORM if panel else None))
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
         "to pick it. Your picks save on this device until you send them, with your "
         "name and your connection to camp.",
         [(n, nums[n]) for n in chron], 10, "cil-fav", "Interlaken favorites", panel=True)
    emit("twenty.html", "Camp Interlaken &middot; the marketing pool",
         f"{len(TWENTY)} frames &middot; cut it down",
         "Tap the circle on the frames that go out. No cap. Copy puts the numbered "
         "list on the clipboard; if it balks, a box pops up with the list to grab.",
         [(n, nums[n]) for n in TWENTY], 99, "cil-twenty", "Interlaken marketing picks",
         panel=False)


if __name__ == "__main__":
    build()
