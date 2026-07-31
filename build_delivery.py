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


def card(f, r42=False, in42=False):
    """One card. r42: a forty-two card, carries Replace. in42: a library card whose
    frame already sits in the forty-two, carries a badge instead of +."""
    out = ('    <div class="card">'
           f'<button class="ph" type="button" data-file="{f["file"]}" '
           f'data-id="{f["id"]}" data-group="{f["label"]}" '
           f'aria-label="View {f["id"]}">'
           f'<img loading="lazy" src="img/thumb/{f["file"]}" alt="{f["id"]}"></button>'
           f'<span class="num">{f["id"].rsplit("-", 1)[-1] if "-" in f["id"] else "1"}</span>')
    if r42:
        out += (f'<button class="rep" type="button" data-id="{f["id"]}" '
                f'aria-label="Mark {f["id"]} to come out of the forty-two">Replace</button>')
    elif in42:
        out += '<span class="in42">in the 42</span>'
    else:
        out += (f'<button class="pick" type="button" data-id="{f["id"]}" '
                f'data-group="{f["label"]}" data-file="{f["file"]}" '
                f'aria-pressed="false" aria-label="Swap {f["id"]} into the forty-two">+</button>')
    return out + '</div>' 


def build():
    """Two blocks: the forty-two (Noah's order) and the full gallery (chronological,
    everything, the forty-two included). Emits R42 and RALL for the slideshows."""
    times = json.load(open(os.path.join(HERE, "_work", "times.json")))
    placed = {n for _, secs in SECTIONS for _, ns in secs for n in ns}
    nums = by_num()
    lookup = {f["id"]: f for f in FRAMES}
    shown = sorted((nums[n] for n in placed), key=lambda f: times.get(f["id"], "9999"))

    ft = ['  <div class="grid">']
    ft.extend(card(lookup[fid], r42=True) for fid in FORTY_TWO)
    ft.append('  </div>')
    r42 = [{"id": fid, "file": lookup[fid]["file"]} for fid in FORTY_TWO]
    ft.append('  <script>window.R42 = ' + json.dumps(r42) + ';</script>')

    gal = ['  <div class="grid">']
    gal.extend(card(f, in42=f["id"] in set(FORTY_TWO)) for f in shown)
    gal.append('  </div>')
    rall = [{"id": f["id"], "file": f["file"]} for f in shown]
    gal.append('  <script>window.RALL = ' + json.dumps(rall) + ';</script>')

    html = open(PAGE).read()

    def fill(html, start, end, body):
        i, j = html.find(start), html.find(end)
        if i < 0 or j < 0:
            sys.exit(f"marker {start} missing")
        head = html.find("-->", i) + 3
        return html[:head] + "\n" + body + "\n  " + html[j:]

    html = fill(html, "<!-- FORTYTWO:START", "<!-- FORTYTWO:END -->", "\n".join(ft))
    html = fill(html, "<!-- GALLERY:START", "<!-- GALLERY:END -->", "\n".join(gal))
    open(PAGE, "w").write(html)
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
