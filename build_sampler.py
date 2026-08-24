#!/usr/bin/env python3
"""Builds sampler.html: five presentation techniques on Interlaken frames, for
Noah's eye only (unlinked, noindex). Each room is a candidate house standard.

    1. The wall     print-preview at true scale over a sofa (his "I need that")
    2. The book     StPageFlip flippable album (the Bader-book preview shape)
    3. Deep zoom    OpenSeadragon inside the waterfront panorama
    4. Justified    order-true justified rows (fixes the columns order-break)
    5. Voice + then/now   the voice-note frame shape and the slider interaction
       (then side is the same frame aged in CSS, a labeled stand-in until a camp
       archival photo exists)

Libraries vendored in lib/ (page-flip 2.0.7, openseadragon 4.1.1).
Regenerate: python3 build_sampler.py
"""
import json
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

BOOK_PAGES = [2, 63, 42, 47, 71, 74, 87, 93, 16, 115]     # the flip book
JUSTIFIED = [2, 3, 9, 11, 14, 23, 33, 38, 42, 48, 63, 68, 71, 74, 83, 93, 97, 112, 144, 161]
WALL_FRAME = 141          # sunset, the print-store spine
ZOOM_FRAME = 192          # the full waterfront panorama
VOICE_FRAME = 115         # the imperfect-days statement
THEN_FRAME = 93           # the marquee bridge

VOICE_QUOTE = ("Part of a number of images that for me are a statement that marketing "
               "images don't have to be perfect days, because not every day is a perfect "
               "day. I'm showing camp on imperfect days. I'm showing beautiful spaces on "
               "imperfect days, and I think that can be important.")


def f(n):
    return "CILWEB1.jpg" if n == 1 else f"CILWEB1-{n}.jpg"


def aspect(n):
    im = Image.open(os.path.join(HERE, "img", "thumb", f(n)))
    return im.width / im.height


PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content=noindex>
<title>The sampler</title>
<script src="lib/page-flip.browser.js"></script>
<script src="lib/openseadragon.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#14110d;color:#ede7dd;font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.6}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
header{padding:54px 0 10px}
h1{font-family:Georgia,serif;font-weight:600;font-size:clamp(26px,4.5vw,36px)}
.sub{color:#a69b8a;font-size:14.5px;margin-top:8px;max-width:64ch}
nav.rooms{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 6px}
nav.rooms a{color:#e2a73e;border:1px solid rgba(226,167,62,.4);border-radius:16px;padding:6px 13px;font-size:12.5px;letter-spacing:.06em;text-decoration:none}
nav.rooms a:hover{background:rgba(226,167,62,.12)}
section{padding:46px 0 40px;border-bottom:1px solid rgba(237,231,221,.1)}
h2{font-family:Georgia,serif;font-weight:500;font-size:24px;color:#c9bfa9}
.why{color:#a69b8a;font-size:14.5px;margin:6px 0 22px;max-width:64ch}
.tag{display:inline-block;font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;border-radius:3px;padding:3px 8px;background:rgba(226,167,62,.14);color:#e2a73e;vertical-align:4px;margin-left:10px}

/* the wall */
#scene{position:relative;border-radius:6px;overflow:hidden;
background:
 radial-gradient(120% 90% at 32% 8%, rgba(255,252,244,.85) 0%, rgba(255,252,244,0) 55%),
 radial-gradient(140% 100% at 50% 118%, rgba(60,48,34,.22) 0%, rgba(60,48,34,0) 46%),
 linear-gradient(180deg,#ece5d8 0%,#e4dccc 80%,#d6cdbb 83.6%,#cec4b1 83.9%,#c8bda8 100%)}
#scene::before{content:"";position:absolute;left:0;right:0;top:83.2%;height:1%;
background:linear-gradient(180deg,#efe9dc 0%,#ded4c2 55%,rgba(90,74,54,.35) 100%)}
#scene::after{content:"";position:absolute;left:0;right:0;top:84.2%;bottom:0;
background:repeating-linear-gradient(90deg, rgba(96,76,52,.16) 0 2px, rgba(0,0,0,0) 2px 118px),
linear-gradient(180deg, rgba(171,142,104,.5) 0%, rgba(140,112,80,.55) 100%);mix-blend-mode:multiply}
#scene svg{display:block;width:100%;height:auto}
#art{position:absolute;box-shadow:0 14px 40px rgba(30,25,15,.45);background:#fff;transition:width .35s ease}
#art .inner{border:1px solid #ccc}
#art img{display:block;width:100%;height:auto}
.sizes{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}
.sizes button{background:none;border:1px solid rgba(226,167,62,.5);color:#e2a73e;padding:8px 14px;border-radius:3px;font-size:12.5px;letter-spacing:.08em;cursor:pointer}
.sizes button.on{background:#e2a73e;color:#14110d;font-weight:600}
.scalenote{color:#7d745f;font-size:12.5px;margin-top:8px}

/* the book */
#bookwrap{display:flex;justify-content:center;padding:8px 0}
#book .page{background:#f7f3ea;color:#3a3428;overflow:hidden}
#book .page .ph{position:absolute;inset:24px;display:flex;align-items:center;justify-content:center;flex-direction:column}
#book .page img{max-width:100%;max-height:88%;box-shadow:0 3px 14px rgba(40,30,10,.25)}
#book .page .cap{font-family:Georgia,serif;font-size:11px;color:#8a8172;margin-top:10px;letter-spacing:.08em}
#book .page.cover{background:#1d1913;color:#ede7dd}
#book .page.cover .ph{border:1px solid rgba(226,167,62,.5);inset:16px}
#book .page.cover h3{font-family:Georgia,serif;font-weight:600;font-size:22px;text-align:center}
#book .page.cover p{font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:#a69b8a;margin-top:8px}
.booknote{text-align:center;color:#7d745f;font-size:12.5px;margin-top:12px}

/* deep zoom */
#osd{width:100%;height:64vh;background:#0d0b08;border-radius:6px}

/* justified */
.jrow{display:flex;flex-wrap:wrap;gap:8px}
.jrow .ji{flex-grow:calc(var(--r)*100);flex-basis:calc(var(--r)*220px);position:relative;min-width:120px}
.jrow .ji img{width:100%;height:100%;object-fit:cover;display:block;border-radius:2px}
.jrow .ji span{position:absolute;left:8px;bottom:6px;font-size:11px;color:#cfc6b4;text-shadow:0 1px 4px #000}

/* voice */
.voice{display:grid;grid-template-columns:1.2fr 1fr;gap:26px;align-items:center}
@media(max-width:760px){.voice{grid-template-columns:1fr}}
.voice img{width:100%;height:auto;border-radius:3px}
.vcard{background:#1d1913;border:1px solid rgba(226,167,62,.3);border-radius:6px;padding:22px}
.vbtn{display:flex;align-items:center;gap:14px;margin-bottom:14px}
.vbtn button{width:52px;height:52px;border-radius:50%;border:2px solid #e2a73e;background:none;color:#e2a73e;font-size:18px;cursor:pointer}
.vbtn .vt{font-size:13px;color:#a69b8a}
.vq{font-family:Georgia,serif;font-size:15.5px;color:#cfc6b4;font-style:italic;line-height:1.65}
.vs{color:#7d745f;font-size:12px;margin-top:10px;letter-spacing:.1em;text-transform:uppercase}

/* then / now */
.tn{position:relative;border-radius:6px;overflow:hidden;user-select:none}
.tn img{display:block;width:100%;height:auto}
.tn .then{position:absolute;inset:0;overflow:hidden}
.tn .then img{filter:sepia(.55) grayscale(.65) contrast(.92) brightness(.92)}
.tn .bar{position:absolute;top:0;bottom:0;width:3px;background:#ede7dd;box-shadow:0 0 8px rgba(0,0,0,.6)}
.tn .knob{position:absolute;top:50%;transform:translate(-50%,-50%);width:40px;height:40px;border-radius:50%;background:#ede7dd;color:#14110d;display:flex;align-items:center;justify-content:center;font-weight:700;box-shadow:0 2px 10px rgba(0,0,0,.5)}
.tn .lab{position:absolute;top:12px;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:#ede7dd;text-shadow:0 1px 4px #000}
.tn .lab.l{left:14px}.tn .lab.r{right:14px}
#toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);background:#ede7dd;color:#14110d;padding:10px 16px;border-radius:4px;font-size:13px;opacity:0;pointer-events:none;transition:opacity .25s;z-index:9}
#toast.on{opacity:1}
footer{padding:36px 0 46px;color:#7d745f;font-size:12px;letter-spacing:.14em;text-transform:uppercase}
</style></head><body><div class=wrap>

<header>
  <h1>The sampler</h1>
  <p class=sub>Five ways to put photographs in front of people, each on Interlaken frames.
  Walk it on the phone. What earns its keep becomes house standard; what does not, dies here.</p>
  <nav class=rooms><a href="#wall">The wall</a><a href="#book">The book</a><a href="#zoom">Deep zoom</a><a href="#just">Justified</a><a href="#voice">The voice</a><a href="#then">Then and now</a></nav>
</header>

<section id=wall>
  <h2>The wall</h2>
  <p class=why>A print at true scale over an 84-inch sofa. Tap a size. This is the print
  store's closer: not "buy a print," but "this is your wall."</p>
  <div id=scene>
    <svg viewBox="0 0 1000 620" aria-hidden=true>
      <rect x=0 y=520 width=1000 height=8 fill="#b9ae9b"/>
      <ellipse cx="500" cy="516" rx="250" ry="16" fill="rgba(50,38,24,.28)"/>
      <g fill="#4a4238">
        <rect x="310" y="380" width="380" height="118" rx="16" />
        <rect x="290" y="356" width="52" height="118" rx="14" />
        <rect x="658" y="356" width="52" height="118" rx="14" />
        <rect x="318" y="346" width="176" height="52" rx="12" fill="#564c40" />
        <rect x="506" y="346" width="176" height="52" rx="12" fill="#564c40" />
        <rect x="322" y="498" width="14" height="26" /><rect x="664" y="498" width="14" height="26" />
      </g>
      <g>
        <rect x="330" y="392" width="340" height="12" rx="6" fill="rgba(255,250,238,.10)"/>
        <rect x="318" y="352" width="170" height="10" rx="5" fill="rgba(255,250,238,.12)"/>
        <rect x="512" y="352" width="170" height="10" rx="5" fill="rgba(255,250,238,.12)"/>
      </g>
      <g stroke="#8a7a62" stroke-width="5" fill="none" opacity=".55">
        <line x1="118" y1="520" x2="118" y2="330"/><circle cx="118" cy="318" r="16" fill="#3a3226" stroke="none"/>
      </g>
      <ellipse cx="118" cy="522" rx="34" ry="7" fill="rgba(50,38,24,.22)"/>
    </svg>
    <div id=art><div class=inner><img src="img/present/__WALLF__" alt=""></div></div>
  </div>
  <div class=sizes>
    <button data-w=16 data-h=24>16 &times; 24</button>
    <button data-w=24 data-h=36 class=on>24 &times; 36</button>
    <button data-w=40 data-h=60>40 &times; 60</button>
  </div>
  <p class=scalenote>Scale is honest: the sofa is 84 inches; the frame resizes true to it.</p>
</section>

<section id=book>
  <h2>The book <span class=tag>The Bader-book preview shape</span></h2>
  <p class=why>Drag a page corner, or tap the page edges. Layouts delivered like this get
  approved in a day; nobody has to imagine what the book will feel like.</p>
  <div id=bookwrap><div id=bookel></div></div>
  <p class=booknote>Demo pages, one frame each; a real layout carries spreads, pairings, and the narrative order.</p>
</section>

<section id=zoom>
  <h2>Deep zoom</h2>
  <p class=why>Pinch and wander inside the waterfront panorama. The point makes itself:
  the file holds up, and the big print will too.</p>
  <div id=osd></div>
</section>

<section id=just>
  <h2>Justified rows</h2>
  <p class=why>Every frame uncropped, full width, and the order is YOUR order. The current
  masonry columns silently shuffle the sequence; this layout keeps the narrative.</p>
  <div class=jrow>
__JUST__
  </div>
</section>

<section id=voice>
  <h2>The voice on the frame</h2>
  <p class=why>Tap play, hear the photographer for twenty seconds. Nothing else delivers
  this. The transcript below is your own ledger note for this frame; the audio is one
  phone recording away.</p>
  <div class=voice>
    <img src="img/present/__VOICEF__" alt="">
    <div class=vcard>
      <div class=vbtn><button id=vplay aria-label="Play">&#9654;</button><span class=vt>0:21 &middot; Noah, on this frame</span></div>
      <p class=vq>&ldquo;__VQ__&rdquo;</p>
      <p class=vs>Voice note lands here; this is the shape</p>
    </div>
  </div>
</section>

<section id=then>
  <h2>Then and now</h2>
  <p class=why>Drag the handle. In the real version the left side is the camp's archival
  photo of the same spot; here it is a stand-in (your frame, aged in CSS) so the
  interaction can be felt. This is "the bridge is still the same" as a thing alumni do
  with a thumb.</p>
  <div class=tn id=tnbox>
    <img src="img/present/__THENF__" alt="">
    <div class=then id=tnthen><img src="img/present/__THENF__" alt=""></div>
    <div class=bar id=tnbar></div><div class=knob id=tnknob>&harr;</div>
    <span class="lab l">Then &middot; stand-in</span><span class="lab r">Now &middot; July 2026</span>
  </div>
</section>

<div id=toast></div>
<footer>Photographs Noah Gallagher &middot; Abba Photo &middot; a private sampler</footer>
</div>
<script>
function $(i){return document.getElementById(i);}
var tt=null;function toast(m){var t=$("toast");t.textContent=m;t.className="on";
clearTimeout(tt);tt=setTimeout(function(){t.className="";},2600);}

/* the wall: sofa is 84in wide and spans 420 of 1000 viewBox units, so
   pixels-per-inch = 5 * sceneWidth / 1000. The chosen size's long side is the
   print's long side; mat is the art element's 4.2% padding. */
(function(){
var AR=__WALLAR__;
function place(longIn){var scene=$("scene"),art=$("art");
var sw=scene.clientWidth, u=sw/1000, ppi=5*u;
var printW=(AR>=1?longIn:longIn*AR)*ppi;
var artW=printW/(1-0.084);
var imgH=printW/AR;
var artH=imgH+artW*0.084;
art.style.width=artW+"px";
art.style.padding=(artW*0.042)+"px";
art.style.left=(sw-artW)/2+"px";
art.style.top=Math.max(14, 165*u-artH/2)+"px";}
var cur=36;
document.querySelectorAll(".sizes button").forEach(function(b){
b.onclick=function(){document.querySelectorAll(".sizes button").forEach(function(x){x.className="";});
b.className="on";cur=Math.max(+b.dataset.w,+b.dataset.h);place(cur);};});
window.addEventListener("resize",function(){place(cur);});
place(cur);})();

/* the book */
(function(){
var el=$("bookel");
var w=Math.min(430,Math.floor(window.innerWidth*0.42)),h=Math.floor(w*1.32);
if(window.innerWidth<720){w=Math.floor(window.innerWidth*0.8);h=Math.floor(w*1.32);}
var pages=__BOOKPAGES__;
var html='<div class="page cover" data-density="hard"><div class="ph"><div><h3>Camp Interlaken</h3><p>Summer 2026</p></div></div></div>';
pages.forEach(function(p){html+='<div class="page"><div class="ph"><img src="img/present/'+p.f+'"><span class="cap">'+p.n+'</span></div></div>';});
html+='<div class="page cover" data-density="hard"><div class="ph"><div><p>Photographs Noah Gallagher</p></div></div></div>';
el.innerHTML=html;
var pf=new St.PageFlip(el,{width:w,height:h,size:"fixed",maxShadowOpacity:.4,showCover:true,mobileScrollSupport:true});
pf.loadFromHTML(document.querySelectorAll("#bookel .page"));
})();

/* deep zoom */
OpenSeadragon({id:"osd",prefixUrl:"",showNavigationControl:false,
tileSources:{type:"image",url:"img/present/__ZOOMF__"},
gestureSettingsMouse:{clickToZoom:true,scrollToZoom:true},
gestureSettingsTouch:{pinchToZoom:true,flickEnabled:true},
defaultZoomLevel:0,minZoomLevel:0,maxZoomPixelRatio:3,visibilityRatio:1});

/* voice */
$("vplay").onclick=function(){toast("This is where your 20-second note plays. Record one on the phone and it drops in.");};

/* then and now */
(function(){var box=$("tnbox"),then=$("tnthen"),bar=$("tnbar"),knob=$("tnknob");
function set(p){p=Math.max(2,Math.min(98,p));
then.style.clipPath="inset(0 "+(100-p)+"% 0 0)";
bar.style.left=p+"%";knob.style.left=p+"%";}
function fromEvent(e){var r=box.getBoundingClientRect();
var x=(e.touches?e.touches[0].clientX:e.clientX)-r.left;
set(x/r.width*100);}
var drag=false;
box.addEventListener("pointerdown",function(e){drag=true;fromEvent(e);});
window.addEventListener("pointermove",function(e){if(drag)fromEvent(e);});
window.addEventListener("pointerup",function(){drag=false;});
box.addEventListener("touchmove",function(e){fromEvent(e);e.preventDefault();},{passive:false});
set(46);})();
</script><script data-goatcounter="https://abba-photo.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script></body></html>"""


def build():
    just = "\n".join(
        f'    <div class="ji" style="--r:{aspect(n):.4f}">'
        f'<img loading="lazy" src="img/thumb/{f(n)}" alt="{n}"><span>{n}</span></div>'
        for n in JUSTIFIED)
    bookpages = [{"n": n, "f": f(n)} for n in BOOK_PAGES]
    html = (PAGE
            .replace("__WALLF__", f(WALL_FRAME))
            .replace("__WALLAR__", f"{aspect(WALL_FRAME):.4f}")
            .replace("__BOOKPAGES__", json.dumps(bookpages))
            .replace("__ZOOMF__", f(ZOOM_FRAME))
            .replace("__JUST__", just)
            .replace("__VOICEF__", f(VOICE_FRAME))
            .replace("__VQ__", VOICE_QUOTE)
            .replace("__THENF__", f(THEN_FRAME)))
    open(os.path.join(HERE, "sampler.html"), "w").write(html)
    print("wrote sampler.html")


if __name__ == "__main__":
    build()
