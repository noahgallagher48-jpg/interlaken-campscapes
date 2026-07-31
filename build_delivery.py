#!/usr/bin/env python3
"""Fills the sample-set section of delivery.html from a table of frames.

Two commands.

    python3 build_delivery.py ingest /path/to/lightroom/export
        Reads every JPEG in that folder, converts to sRGB with the profile
        embedded, and writes two tiers into img/: present at 2560px for the
        lightbox, thumb at 900px for the page. Prints a FRAMES skeleton to paste
        below, one entry per file, so the table starts from what actually landed.

    python3 build_delivery.py build
        Regenerates everything between the FRAMES markers in delivery.html from
        the FRAMES table. With an empty table the page keeps its waiting state,
        so running this before any frames exist changes nothing visible.

Export out of Lightroom as sRGB, not ProPhoto. ProPhoto renders flat and
desaturated on most surfaces, and stripping the profile during a resize makes it
worse. The ingest step converts and embeds correctly either way, but the file the
client receives should be sRGB from the start.

Label keys: fa Fine Art, sig Signature Campscape, dev Development / Campaign,
pub Publication-Ready, day Daily / Social, arc Archive.
"""
import io
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
    "arc": "Archive",
}

# One entry per delivered frame. Order here is the order on the page.
#   id            what the camp calls it, shown on the thumbnail
#   file          filename inside img/present and img/thumb
#   label         a key from LABELS
#   use           where this image should live, named plainly
#   why           the off-frame meaning. What the picture is really about
#   justification why it earns the label, verifiable in the image itself
#   production    paper, process, size window, lab routing. Print-grade only
#   availability  how it may be published and the notation that rides with it
#   faces         True where a minor is clearly identifiable. Held off the page while
#                 INCLUDE_FACES is False, per the client-page rule in CLAUDE.md and
#                 Drea's Jul 17 scenes-not-faces direction.
#
# The table lives in frames.json so it can be regenerated and hand-edited without
# touching this file. FRAMES below is the fallback when that file is absent.
FRAMES = []

# True since 2026-07-31: STATE.md records the owner's confirmation that the camp's
# releases cover the population-facing set. The faces field stays on every such frame
# so later public reuse outside this page remains a deliberate decision.
INCLUDE_FACES = True

_TABLE = os.path.join(HERE, "frames.json")
if os.path.exists(_TABLE):
    import json as _json
    FRAMES = _json.load(open(_TABLE))

EMPTY = """  <div class="empty">
    <b>The frames land here</b>
    The sample set arrives on this page first, then the full library within 30 days of the last on-site day. The counts in the agreement (12 Mastered Campscapes, 30 Storytelling Candids) are floors, not targets; the archive carries everything beyond them.
  </div>"""

# The fine-art twelve. No why-lines on the page: "If we call it fine art it is"
# (Noah, 2026-07-31). The label carries the claim; justification and specs stay in
# frames.json and ride with the use-guide layer, never under the frame.
FINE_TWELVE = [
    "CILWEB1-17", "CILWEB1-101", "CILWEB1-14", "CILWEB1-63", "CILWEB1-66",
    "CILWEB1-141", "CILWEB1-143", "CILWEB1-34", "CILWEB1-16", "CILWEB1-108",
    "CILWEB1-81", "CILWEB1-51",
]


def fineart(frames):
    """The twelve. Image and its number, nothing else."""
    by_id = {f["id"]: f for f in frames}
    out = ['  <div class="fagrid">']
    for fid in FINE_TWELVE:
        f = by_id[fid]
        out.append('    <div class="facard">'
                   f'<a href="img/present/{f["file"]}" target="_blank" rel="noopener">'
                   f'<img loading="lazy" src="img/thumb/{f["file"]}" alt="{fid}"></a>'
                   f'<p class="why"><span class="fid">{fid}</span></p></div>')
    out.append('  </div>')
    return "\n".join(out)


def ingest(folder):
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
    print(f"\ningested {len(names)} frames into img/present and img/thumb\n")
    print("FRAMES skeleton, paste into build_delivery.py and fill it in:\n")
    for n in names:
        out = os.path.splitext(n)[0] + ".jpg"
        stem = os.path.splitext(n)[0]
        print(f'    {{"id": "{stem}", "file": "{out}", "label": "", "use": "",')
        print(f'     "why": "", "justification": "", "production": "", "availability": ""}},')


def field(key, value, placeholder):
    if value:
        return f'      <div class="field"><span class="k">{key}</span><span class="v">{value}</span></div>'
    return (f'      <div class="field"><span class="k">{key}</span>'
            f'<span class="v mut">{placeholder}</span></div>')


def block(f):
    """One card on the gallery wall. Viewing only; choosing happens in the ballot."""
    out = ['    <figure class="pick">']
    out.append('      <div class="ph">'
               f'<a href="img/present/{f["file"]}" target="_blank" rel="noopener">'
               f'<img loading="lazy" src="img/thumb/{f["file"]}" alt="{f["id"]}"></a></div>')
    out.append('    </figure>')
    return "\n".join(out)


def ballot(shown):
    """The voting section. Two picks per set; clicking is choosing, not viewing."""
    out = []
    current = None
    for f in shown:
        if f.get("label") != current:
            if current is not None:
                out.append("  </div>")
            current = f.get("label")
            out.append(f'  <h3 class="group"><span class="tag {current}">'
                       f'{LABELS.get(current, "Unlabelled")}</span>'
                       f'<span class="quota" data-group="{current}">0 picked</span></h3>')
            out.append('  <div class="bgrid">')
        out.append(f'    <button class="bpick" type="button" data-id="{f["id"]}" '
                   f'data-group="{f["label"]}" aria-pressed="false" '
                   f'aria-label="Pick {f["id"]}">'
                   f'<img loading="lazy" src="img/thumb/{f["file"]}" alt="{f["id"]}"></button>')
    out.append("  </div>")
    return "\n".join(out)


def build():
    html = open(PAGE).read()
    start = "<!-- FRAMES:START"
    end = "<!-- FRAMES:END -->"
    i = html.find(start)
    j = html.find(end)
    if i < 0 or j < 0:
        sys.exit("FRAMES markers missing from delivery.html")
    head_end = html.find("-->", i) + 3
    shown = [f for f in FRAMES if INCLUDE_FACES or not f.get("faces")]
    held = len(FRAMES) - len(shown)
    if not shown:
        body = EMPTY
    else:
        out, current = [], None
        for f in shown:
            if f.get("label") != current:
                if current is not None:
                    out.append("  </div>")
                current = f.get("label")
                out.append(f'  <h3 class="group"><span class="tag {current}">'
                           f'{LABELS.get(current, "Unlabelled")}</span></h3>')
                out.append('  <div class="wall">')
            out.append(block(f))
        out.append("  </div>")
        body = "\n".join(out)
    if held:
        body += (f'\n  <div class="empty" style="text-align:left">'
                 f'<b>{held} more frames are finished and held back</b>'
                 f'They show campers close enough to recognise. They are yours, at full '
                 f'resolution, in your full-resolution folder. They go on this page the moment the '
                 f'camp confirms the releases cover them, and not before.</div>')
    html = html[:head_end] + "\n" + body + "\n  " + html[j:]

    bs = html.find("<!-- BALLOT:START")
    be = html.find("<!-- BALLOT:END -->")
    if bs >= 0 and be >= 0:
        bhead = html.find("-->", bs) + 3
        html = html[:bhead] + "\n" + ballot(shown) + "\n  " + html[be:]

    fs = html.find("<!-- FINEART:START")
    fe = html.find("<!-- FINEART:END -->")
    if fs >= 0 and fe >= 0:
        fhead = html.find("-->", fs) + 3
        html = html[:fhead] + "\n" + fineart(FRAMES) + "\n  " + html[fe:]
    open(PAGE, "w").write(html)

    missing = [f["file"] for f in FRAMES
               if not os.path.exists(os.path.join(IMG, "thumb", f["file"]))]
    blank = [f["id"] for f in FRAMES if not f.get("label")]
    print(f"wrote {PAGE}")
    print(f"frames on the page: {len(FRAMES)}")
    if missing:
        print("MISSING from img/thumb:", missing)
    if blank:
        print("no label yet:", blank)
    by = {}
    for f in FRAMES:
        by[LABELS.get(f.get("label"), "unlabelled")] = by.get(LABELS.get(f.get("label"), "unlabelled"), 0) + 1
    if by:
        print("by label:", by)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        if len(sys.argv) < 3:
            sys.exit("usage: build_delivery.py ingest /path/to/export/folder")
        ingest(sys.argv[2])
    else:
        build()
