#!/usr/bin/env python3
"""Builds the Camp Interlaken library page (library.html) from frames.json and
_work/section_map.json.

Two commands.

    python3 build_delivery.py ingest /path/to/lightroom/export
        Reads every JPEG in that folder, converts to sRGB with the profile
        embedded, and writes two tiers into img/: present at 2560px for the
        lightbox, thumb at 900px for the cards.

    python3 build_delivery.py build
        Regenerates the NAVFILT, FINEART and LIBRARY marker regions.

Export out of Lightroom as sRGB, not ProPhoto. The ingest converts either way,
but the file the client receives should be sRGB from the start.

Label keys: fa Fine Art, sig Signature Campscape, dev Development / Campaign,
pub Publication-Ready, day Daily / Social. sig + fa count as scapes in the
ballot; dev + pub + day count as story.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "library.html")
IMG = os.path.join(HERE, "img")

LABELS = {
    "fa": "Fine Art",
    "sig": "Signature Campscape",
    "dev": "Development / Campaign",
    "pub": "Publication-Ready",
    "day": "Daily / Social",
}

FRAMES = json.load(open(os.path.join(HERE, "frames.json")))
SECTIONS = json.load(open(os.path.join(HERE, "sections.json")))
# Noah's proposed forty-two, in his slideshow order (recovered by hash-match from the
# downloaded slideshow, 2026-07-31). The page presents these as the set; the camp
# challenges frames with out/in swaps.
FORTY_TWO = json.load(open(os.path.join(HERE, "noahs_42.json")))

# True since 2026-07-31: STATE.md records the owner's confirmation that the camp's
# releases cover the population-facing set.
INCLUDE_FACES = True

# The fine-art twelve. No why-lines on the page: "If we call it fine art it is"
# (Noah, 2026-07-31). Selected by a full visual pass over the sig+fa pool
# (_work/fa_sheets/), not by the written justification fields.
FINE_TWELVE = [
    "CILWEB1-17", "CILWEB1-102", "CILWEB1-19", "CILWEB1-142", "CILWEB1-143",
    "CILWEB1-91", "CILWEB1-89", "CILWEB1-16", "CILWEB1-22", "CILWEB1-116",
    "CILWEB1-66", "CILWEB1-63",
]


def by_num():
    """frame number -> frame dict (CILWEB1.jpg is frame 1)."""
    out = {}
    for f in FRAMES:
        m = re.match(r"CILWEB1-(\d+)$", f["id"])
        out[int(m.group(1)) if m else 1] = f
    return out


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def card(f):
    """One card: the image and its number. Viewing only."""
    return ('    <div class="card">'
            f'<button class="ph" type="button" data-file="{f["file"]}" '
            f'data-id="{f["id"]}" aria-label="View {f["id"]}">'
            f'<img loading="lazy" src="img/thumb/{f["file"]}" alt="{f["id"]}"></button>'
            f'<span class="num">{f["id"].rsplit("-", 1)[-1] if "-" in f["id"] else "1"}</span>'
            '</div>')




SLIDE_PAGE = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Camp Interlaken</title><meta name=robots content=noindex><style>
*{margin:0;padding:0;box-sizing:border-box}html,body{height:100%;background:#14110d;overflow:hidden;
font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;color:#ede7dd}
#s{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
#s img{max-width:100vw;max-height:100vh;object-fit:contain;opacity:0;transition:opacity .5s ease}
#s img.on{opacity:1}#c{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;
justify-content:center;background:#14110d;z-index:5;transition:opacity .6s}#c.off{opacity:0;pointer-events:none}
h1{font-family:Georgia,serif;font-weight:600;font-size:clamp(24px,5vw,40px)}
p{margin-top:12px;color:#a69b8a;font-size:14px}
button{margin-top:32px;background:none;border:1px solid rgba(226,167,62,.5);color:#e2a73e;
padding:11px 22px;border-radius:3px;font-size:13px;letter-spacing:.16em;text-transform:uppercase;cursor:pointer}
#n{position:fixed;bottom:14px;right:18px;font-size:12px;color:#a69b8a}
#h{position:fixed;top:10px;right:14px;z-index:6;font-size:28px;color:#a69b8a;text-decoration:none;
padding:6px 10px;text-shadow:0 1px 6px #000}#h:hover{color:#ede7dd}
.z{position:fixed;top:0;bottom:0;width:34%;z-index:3;cursor:pointer}#p{left:0}#x{right:0}
</style></head><body>
<div id=c><h1>Camp Interlaken</h1><p>__SUB__</p><button id=b>Begin</button><p style="margin-top:18px;font-size:12px"><a href="#" id=cl style="color:#a69b8a;text-decoration:underline">Copy this page's link to share</a></p></div>
<div id=s><img id=a><img id=d style=position:absolute></div>
<div class=z id=p></div><div class=z id=x></div><div id=n></div>
<a id=h href="library.html" aria-label="Back to the gallery">&times;</a>
<script>var U=__IMGS__,MS=__MS__,i=0,t=null,sh=null;
var A=document.getElementById("a"),B=document.getElementById("d"),N=document.getElementById("n");
function go(k){i=(k+U.length)%U.length;var I=sh===A?B:A,O=sh===A?A:B;
I.onload=function(){O.classList.remove("on");I.classList.add("on");sh=I;N.textContent=(i+1)+" / "+U.length;};I.src=U[i];}
function st(d){go(i+d);}function ar(){clearInterval(t);t=setInterval(function(){st(1);},MS);}
document.getElementById("b").onclick=function(){document.getElementById("c").className="off";go(0);ar();};
document.getElementById("x").onclick=function(){st(1);ar();};
document.getElementById("p").onclick=function(){st(-1);ar();};
document.getElementById("cl").onclick=function(e){e.preventDefault();var a=this;
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(location.href).then(function(){a.textContent="Link copied";});}
else{window.prompt("Copy this link:",location.href);}};
document.addEventListener("keydown",function(e){if(e.key==="ArrowRight"){st(1);ar();}
if(e.key==="ArrowLeft"){st(-1);ar();}if(e.key==="Escape"){location.href="library.html";}
if(e.key===" "){e.preventDefault();if(t){clearInterval(t);t=null;}else ar();}});
</scr"""  """ipt></body></html>"""


def slideshow_pages(lookup):
    """slideshow-one.html: 42 seconds. slideshow-two.html: 90 seconds. Independent,
    shareable links; images load from the repo."""
    urls = ["img/present/" + lookup[fid]["file"] for fid in FORTY_TWO]
    for name, ms, sub in (("slideshow-one.html", 1000, "42 frames &middot; 42 seconds"),
                          ("slideshow-two.html", round(90000 / len(urls)), "42 frames &middot; 90 seconds")):
        html = (SLIDE_PAGE.replace("__IMGS__", json.dumps(urls))
                .replace("__MS__", str(ms)).replace("__SUB__", sub))
        open(os.path.join(HERE, name), "w").write(html)
        print(f"wrote {name} ({ms}ms/frame)")

def build():
    """Two blocks: the forty-two (Noah's order) and the full gallery (chronological,
    everything, the forty-two included). Emits R42 and RALL for the slideshows."""
    times = json.load(open(os.path.join(HERE, "_work", "times.json")))
    placed = {n for _, secs in SECTIONS for _, ns in secs for n in ns}
    nums = by_num()
    lookup = {f["id"]: f for f in FRAMES}
    shown = sorted((nums[n] for n in placed), key=lambda f: times.get(f["id"], "9999"))

    # Noah's groupings (gallery pass, 2026-08-02): named runs gathered at the
    # chronological position of their first member. Frame 2 leads the gallery.
    GROUPS = [
        ("Tushball", [3, 112, 113]),
        ("Indoor campfire", [4, 6, 7, 8, 9, 10, 11, 12]),
        ("Shabbat", list(range(42, 78))),
    ]
    grouped = {n for _, ns in GROUPS for n in ns}
    first_of = {}
    for name, ns in GROUPS:
        members = [nums[n] for n in ns if n in placed]
        if members:
            first_of[min(ns, key=lambda n: times.get(nums[n]["id"], "9999") if n in placed else "9999")] = (name, members)

    lead = [nums[2]] if 2 in placed else []
    gal = ['  <div class="wall">']
    gal.extend(card(f) for f in lead)
    for f in shown:
        m = re.match(r"CILWEB1-(\d+)$", f["id"])
        n = int(m.group(1)) if m else 1
        if n == 2:
            continue
        if n in first_of:
            name, members = first_of[n]
            gal.append('  </div>')
            gal.append(f'  <h3 class="run">{name}</h3>')
            gal.append('  <div class="wall">')
            gal.extend(card(g) for g in members)
            gal.append('  </div>')
            gal.append('  <div class="wall">')
            continue
        if n in grouped:
            continue
        gal.append(card(f))
    gal.append('  </div>')
    rall = [{"id": f["id"], "file": f["file"]} for f in shown]
    gal.append('  <script>window.RALL = ' + json.dumps(rall) + ';</script>')

    picks = ['  <div class="wall">']
    picks.extend(card(lookup[fid]) for fid in FORTY_TWO)
    picks.append('  </div>')

    html = open(PAGE).read()

    def fill(html, start, end, body):
        i, j = html.find(start), html.find(end)
        if i < 0 or j < 0:
            sys.exit(f"marker {start} missing")
        head = html.find("-->", i) + 3
        return html[:head] + "\n" + body + "\n  " + html[j:]

    html = fill(html, "<!-- PICKS:START", "<!-- PICKS:END -->", "\n".join(picks))
    html = fill(html, "<!-- GALLERY:START", "<!-- GALLERY:END -->", "\n".join(gal))
    open(PAGE, "w").write(html)
    slideshow_pages(lookup)
    print(f"wrote {PAGE}")
    print(f"forty-two: {len(FORTY_TWO)} · gallery: {len(shown)}")


def ingest(folder):
    import io
    from PIL import Image, ImageCms
    os.makedirs(os.path.join(IMG, "present"), exist_ok=True)
    os.makedirs(os.path.join(IMG, "thumb"), exist_ok=True)
    srgb = ImageCms.createProfile("sRGB")
    srgb_icc = ImageCms.ImageCmsProfile(srgb).tobytes()
    names = sorted(f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg")))
    if not names:
        sys.exit(f"no JPEGs in {folder}")
    for n in names:
        im = Image.open(os.path.join(folder, n))
        icc = im.info.get("icc_profile")
        im = im.convert("RGB")
        if icc:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            desc = ImageCms.getProfileDescription(src).strip()
            if "sRGB" not in desc:
                im = ImageCms.profileToProfile(
                    im, src, srgb, outputMode="RGB",
                    renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)
                print(f"  {n}: converted from {desc}")
        out = os.path.splitext(n)[0] + ".jpg"
        a = im.copy(); a.thumbnail((2560, 2560), Image.LANCZOS)
        a.save(os.path.join(IMG, "present", out), quality=88,
               icc_profile=srgb_icc, subsampling=0)
        b = im.copy(); b.thumbnail((900, 900), Image.LANCZOS)
        b.save(os.path.join(IMG, "thumb", out), quality=82, icc_profile=srgb_icc)
    print(f"ingested {len(names)} frames")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        if len(sys.argv) < 3:
            sys.exit("usage: build_delivery.py ingest /path/to/export/folder")
        ingest(sys.argv[2])
    else:
        build()
