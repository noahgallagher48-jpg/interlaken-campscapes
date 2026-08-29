#!/usr/bin/env python3
"""Builds the Interlaken book for Miller's press, ported from the Kingswood
builder 2026-08-29. The two stay line-compatible on purpose: a fix proven in
one belongs in the other.

THE SEQUENCE, in order of authority:
  1. _work/book_spec.json       the per-page layout spec; when present it IS
                                the book (styles: matte/bleed/pair/stack/grid/
                                hero/bleedhero, same schema as Kingswood's)
  2. _work/book_saved.json      a "Save the book" payload from the delivery
                                page's book tab ({group, frames, saved, ...}).
                                Arrives in the noah@abba-photo.com inbox; drop
                                the JSON here and rebuild. This is the client's
                                or Noah's latest word on the sequence.
  3. the "Book" lane            in _work/arrangement_current.json, the standing
                                provisional sequence.

MASTERS come from _work/frame_drive.json (frame number -> master filename) and
are read out of ~/Desktop/ABBA/interlaken/masters_cache, the full-resolution
local cache. No dependency on the web tier: the press never sees a 3840.

    python3 build_book.py              preview PDF, 150 DPI, spreads
    python3 build_book.py --press      300 DPI single pages for the lab
    python3 build_book.py --submit     press build, then zip it the way
                                       Miller's order form asks

Pagination mirrors the delivery page's book tab exactly: 12x8 landscape pages,
two portraits paired on one page, everything else matted on the page's warm
white (MATTE_ALL), so what gets approved on screen is what the PDF produces.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ARR = os.path.join(HERE, "_work", "arrangement_current.json")
SAVED = os.path.join(HERE, "_work", "book_saved.json")
FRAME_DRIVE = os.path.join(HERE, "_work", "frame_drive.json")
MASTERS = os.path.expanduser("~/Desktop/ABBA/interlaken/masters_cache")
OUTDIR = os.path.join(HERE, "book")
BOOK_GROUP = "Book"

import millers                    # the press spec, shared and checkable

SIZE_KEY = millers.DEFAULT_SIZE   # "12x8". Any key in millers.SIZES.
PAGE_IN = millers.SIZES[SIZE_KEY]["trim"]   # trim, inches. Bleed is added on top.

# COVER_FRAME None = typographic cover. Noah has not picked an Interlaken cover
# frame, and the proven order route (linen) takes no cover artwork at all: its
# cover is foil text on the order form. A photo cover only matters if the order
# moves to Custom Image, so nothing here blocks the linen order.
COVER_FRAME = None
COVER_SCRIM = 0.20                # ink over the cover frame so type reads;
                                  # tiled at Kingswood 2026-08-26, 0.20 won
# The page ground matches the book tab's on-screen spread exactly (it renders
# on the host page's --ink, #ece6da), so screen approval and press output agree.
GROUND = (236, 230, 218)          # #ece6da, the delivery page's warm white
INK = (16, 14, 11)                # #100e0b, the page's ground colour as ink
ACCENT = (218, 161, 67)           # #daa143, the page's gold
MARGIN = 0.06                     # of the short edge, for matted frames
MAX_CROP = 0.12                   # crop more of a frame than this and it gets matted
MATTE_ALL = True                  # nothing bleeds; every frame sits whole inside
                                  # the margin at its own proportions (the
                                  # standing 2026-08-23 ruling, same as Kingswood)
FONT = "/System/Library/Fonts/Avenir Next.ttc"

from book_spreads import MONTAGE_SPREADS   # one definition, shared with the viewer

SPEC = os.path.join(HERE, "_work", "book_spec.json")
STYLE_COUNTS = {"matte": (1, 1), "bleed": (1, 1), "pair": (2, 2),
                "stack": (2, 2), "grid": (2, 6), "hero": (1, 1),
                "bleedhero": (1, 1)}

TITLE = "Camp Interlaken"
SUBTITLE = "Eagle River, Wisconsin  ·  July 2026"


def lane():
    """The sequence and where it came from. book_saved.json outranks the
    arrange lane: it is the newest deliberate save from the book tab."""
    if os.path.exists(SAVED):
        p = json.load(open(SAVED))
        seq = list(p.get("frames", []))
        if not seq:
            sys.exit(f"{SAVED} exists but its frames list is empty")
        return seq, [], f"book_saved.json (saved {p.get('saved', 'undated')})"
    a = json.load(open(ARR))
    by_name = {g["name"]: g["frames"] for g in a["groups"]}
    if BOOK_GROUP not in by_name:
        sys.exit(f"No '{BOOK_GROUP}' lane in {ARR} and no {SAVED}.\n"
                 f"Save a book from the delivery page's book tab, or fill the lane.")
    aside = set(a.get("aside", []))
    seq = list(by_name[BOOK_GROUP])
    return seq, [n for n in seq if n in aside], f"'{BOOK_GROUP}' lane (provisional)"


def sources():
    """frame number -> master path, from the same map the delivery page uses,
    so the book can never name a frame the delivery does not know."""
    d = json.load(open(FRAME_DRIVE))
    out = {}
    for n, e in d.items():
        p = os.path.join(MASTERS, e["file"])
        if os.path.exists(p):
            out[int(n)] = p
    return out


def fit(im, box):
    """Cover-crop to the box, or mat it if that would cut too much away."""
    from PIL import Image
    bw, bh = box
    scale = max(bw / im.width, bh / im.height)
    kept = (bw / (im.width * scale)) * (bh / (im.height * scale))
    if 1 - kept > MAX_CROP:
        return None, 1 - kept
    w, h = round(im.width * scale), round(im.height * scale)
    im = im.resize((w, h), Image.LANCZOS)
    return im.crop(((w - bw) // 2, (h - bh) // 2,
                    (w - bw) // 2 + bw, (h - bh) // 2 + bh)), 1 - kept


def matted(im, page):
    from PIL import Image
    pw, ph = page
    m = round(min(pw, ph) * MARGIN)
    box = (pw - 2 * m, ph - 2 * m)
    c = im.copy()
    c.thumbnail(box, Image.LANCZOS)
    out = Image.new("RGB", page, GROUND)
    out.paste(c, ((pw - c.width) // 2, (ph - c.height) // 2))
    return out


def pair(a, b, page):
    """Two portraits facing each other on one landscape page."""
    from PIL import Image
    pw, ph = page
    m = round(min(pw, ph) * MARGIN)
    gut = round(m * 0.9)
    cell = ((pw - 2 * m - gut) // 2, ph - 2 * m)
    out = Image.new("RGB", page, GROUND)
    for i, im in enumerate((a, b)):
        c = im.copy()
        c.thumbnail(cell, Image.LANCZOS)
        x = m + i * (cell[0] + gut) + (cell[0] - c.width) // 2
        out.paste(c, (x, m + (cell[1] - c.height) // 2))
    return out


def montage(frames, page, cols=None):
    """A grid of supporting frames on one page, to face a hero on the other.
    One outer margin, one gutter, cells cover-cropped to a common shape."""
    from PIL import Image
    pw, ph = page
    n = len(frames)
    if n == 0:
        return Image.new("RGB", page, GROUND)
    cols = cols or (1 if n == 1 else 2 if n <= 4 else 3)
    rows = -(-n // cols)
    m = round(min(pw, ph) * MARGIN)
    gut = round(m * 0.55)
    cw = (pw - 2 * m - gut * (cols - 1)) // cols
    chh = (ph - 2 * m - gut * (rows - 1)) // rows
    out = Image.new("RGB", page, GROUND)
    for i, im in enumerate(frames):
        s = max(cw / im.width, chh / im.height)
        w, h = round(im.width * s), round(im.height * s)
        cell = im.resize((w, h), Image.LANCZOS).crop(
            ((w - cw) // 2, (h - chh) // 2, (w - cw) // 2 + cw, (h - chh) // 2 + chh))
        x = m + (i % cols) * (cw + gut)
        y = m + (i // cols) * (chh + gut)
        out.paste(cell, (x, y))
    return out


def stack(a, b, page):
    """Two landscapes stacked on one page, matted, common width."""
    from PIL import Image
    pw, ph = page
    m = round(min(pw, ph) * MARGIN)
    gut = round(m * 0.9)
    cell = (pw - 2 * m, (ph - 2 * m - gut) // 2)
    out = Image.new("RGB", page, GROUND)
    for i, im in enumerate((a, b)):
        c = im.copy()
        c.thumbnail(cell, Image.LANCZOS)
        y = m + i * (cell[1] + gut) + (cell[1] - c.height) // 2
        out.paste(c, (m + (cell[0] - c.width) // 2, y))
    return out


def bleed_page(im, canvas):
    """One frame edge to edge, filling the full canvas INCLUDING the bleed.
    Refuses to crop away more than MAX_CROP; the caller falls back to a matte."""
    from PIL import Image
    cw, ch = canvas
    scale = max(cw / im.width, ch / im.height)
    kept = (cw / (im.width * scale)) * (ch / (im.height * scale))
    if 1 - kept > MAX_CROP:
        return None, 1 - kept
    w, h = round(im.width * scale), round(im.height * scale)
    c = im.resize((w, h), Image.LANCZOS)
    return c.crop(((w - cw) // 2, (h - ch) // 2,
                   (w - cw) // 2 + cw, (h - ch) // 2 + ch)), 1 - kept


def load_spec():
    """Read and validate _work/book_spec.json. Returns (spec, problems).
    A spec with problems refuses to render rather than shipping a page
    nobody chose."""
    if not os.path.exists(SPEC):
        return None, []
    spec = json.load(open(SPEC))
    problems = []
    size = spec.get("size", SIZE_KEY)
    if size not in millers.SIZES:
        problems.append(f"unknown size {size}; valid: {sorted(millers.SIZES)}")
    for i, pg in enumerate(spec.get("pages", []), 1):
        st = pg.get("style")
        if st not in STYLE_COUNTS:
            problems.append(f"page {i}: unknown style {st!r}; valid: {sorted(STYLE_COUNTS)}")
            continue
        lo, hi = STYLE_COUNTS[st]
        n = len(pg.get("frames", []))
        if not lo <= n <= hi:
            problems.append(f"page {i} ({st}): {n} frames, needs {lo}" +
                            (f" to {hi}" if hi != lo else ""))
        if st in ("hero", "bleedhero") and not 1 <= len(pg.get("grid", [])) <= 6:
            problems.append(f"page {i} ({st}): needs 1 to 6 grid frames, "
                            f"got {len(pg.get('grid', []))}")
    return spec, problems


def render_spec(spec, src, page, canvas):
    """Turn the spec's pages into rendered sheets. Every entry becomes one
    page except hero/bleedhero, which become two: the hero, its grid facing."""
    from PIL import Image
    pages, notes = [], []
    need = []
    for pg in spec["pages"]:
        need += pg.get("frames", []) + pg.get("grid", [])
    missing = sorted({n for n in need if n not in src})
    if missing:
        sys.exit(f"spec names frames with no master on disk: {missing}")
    ims = {n: Image.open(src[n]).convert("RGB") for n in dict.fromkeys(need)}

    for pg in spec["pages"]:
        st, fr = pg["style"], pg["frames"]
        label = "+".join(map(str, fr))
        if st == "matte":
            pages.append((matted(ims[fr[0]], page), label, "matte"))
        elif st == "bleed":
            full, lost = bleed_page(ims[fr[0]], canvas)
            if full is None:
                pages.append((matted(ims[fr[0]], page), label,
                              f"matte (bleed would lose {lost:.0%})"))
                notes.append(f"frame {fr[0]}: bleed refused at {lost:.0%} crop, matted instead")
            else:
                pages.append((full, label, f"bleed, {lost:.0%} cropped"))
        elif st == "pair":
            pages.append((pair(ims[fr[0]], ims[fr[1]], page), label, "pair"))
        elif st == "stack":
            pages.append((stack(ims[fr[0]], ims[fr[1]], page), label, "stack"))
        elif st == "grid":
            pages.append((montage([ims[n] for n in fr], page), label, f"grid of {len(fr)}"))
        elif st == "hero":
            grid = pg["grid"]
            pages.append((matted(ims[fr[0]], page), label, "hero"))
            pages.append((montage([ims[n] for n in grid], page),
                          "+".join(map(str, grid)), f"grid of {len(grid)} facing {fr[0]}"))
        elif st == "bleedhero":
            grid = pg["grid"]
            full, lost = bleed_page(ims[fr[0]], canvas)
            if full is None:
                pages.append((matted(ims[fr[0]], page), label,
                              f"bleedhero matted (bleed would lose {lost:.0%})"))
                notes.append(f"frame {fr[0]}: bleedhero refused bleed at {lost:.0%} "
                             f"crop, matted instead")
            else:
                pages.append((full, label, f"bleedhero, {lost:.0%} cropped"))
            pages.append((montage([ims[n] for n in grid], page),
                          "+".join(map(str, grid)),
                          f"grid of {len(grid)} facing bled {fr[0]}"))
    return pages, notes


def on_bleed(sheet, canvas):
    """Place a trim-sized sheet on the full bleed canvas. MATTE_ALL means the
    ground extends into the bleed exactly, so the trimmer cuts flat colour."""
    from PIL import Image
    if sheet.size == canvas:
        return sheet
    out = Image.new("RGB", canvas, GROUND)
    out.paste(sheet, ((canvas[0] - sheet.width) // 2,
                      (canvas[1] - sheet.height) // 2))
    return out


def photo_cover(im, canvas, dpi, title, sub):
    """A photographic cover for the Custom Image route. Text sits inside
    Miller's safe inset measured from the TRIM edge, off the fold."""
    from PIL import Image, ImageDraw, ImageFont
    cw, ch = canvas
    scale = max(cw / im.width, ch / im.height)
    w, h = round(im.width * scale), round(im.height * scale)
    art = im.resize((w, h), Image.LANCZOS).crop(
        ((w - cw) // 2, (h - ch) // 2, (w - cw) // 2 + cw, (h - ch) // 2 + ch))

    veil = Image.new("RGB", canvas, INK)
    art = Image.blend(art, veil, COVER_SCRIM)

    d = ImageDraw.Draw(art)
    inset = millers.bleed_px(dpi) + millers.safe_px(dpi)
    big = round(ch * 0.072)
    small = round(ch * 0.021)
    # Avenir Next faces: 7 Regular, 5 Medium, 2 Demi Bold, 0 Bold
    f1 = ImageFont.truetype(FONT, big, index=0)
    f2 = ImageFont.truetype(FONT, small, index=5)
    y = ch - inset - big - round(small * 3.2)
    d.text((inset, y), title, font=f1, fill=GROUND)
    rule_y = y + round(big * 1.28)
    d.line([(inset, rule_y), (inset + round(cw * 0.055), rule_y)],
           fill=ACCENT, width=max(3, round(ch * 0.0045)))
    d.text((inset, rule_y + round(small * 0.9)), sub, font=f2, fill=GROUND)
    return art


def title_page(page, n):
    from PIL import Image, ImageDraw, ImageFont
    out = Image.new("RGB", page, GROUND)
    d = ImageDraw.Draw(out)
    pw, ph = page
    big = round(ph * 0.085)
    small = round(ph * 0.026)
    f1 = ImageFont.truetype(FONT, big, index=7)
    f2 = ImageFont.truetype(FONT, small, index=5)
    t1, t2 = TITLE, SUBTITLE
    w1 = d.textbbox((0, 0), t1, font=f1)[2]
    w2 = d.textbbox((0, 0), t2, font=f2)[2]
    y = round(ph * 0.40)
    d.text(((pw - w1) // 2, y), t1, font=f1, fill=INK)
    rule_y = y + round(big * 1.45)
    d.line([(pw // 2 - round(pw * 0.05), rule_y), (pw // 2 + round(pw * 0.05), rule_y)],
           fill=ACCENT, width=max(2, round(ph * 0.004)))
    d.text(((pw - w2) // 2, rule_y + round(small * 1.1)), t2, font=f2, fill=INK)
    f3 = ImageFont.truetype(FONT, small, index=7)
    cred = "Photographs by Noah Gallagher"
    w3 = d.textbbox((0, 0), cred, font=f3)[2]
    d.text(((pw - w3) // 2, ph - round(ph * 0.10)), cred, font=f3, fill=INK)
    return out


def build(press=False):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    src = sources()

    spec, problems = load_spec()
    if problems:
        sys.exit("book_spec.json has problems, refusing to render:\n  "
                 + "\n  ".join(problems))
    size_key = (spec or {}).get("size", SIZE_KEY)

    if spec:
        seq = [n for pg in spec["pages"] for n in pg.get("frames", [])]
        dropped, seq_from = [], "book_spec.json"
    else:
        seq, dropped, seq_from = lane()
        if not seq:
            sys.exit(f"The sequence is empty ({seq_from}).")
        missing = [n for n in seq if n not in src]
        if missing:
            sys.exit(f"No master on disk for frames {missing}")

    dpi = millers.DPI_PRESS if press else millers.DPI_PREVIEW
    page = millers.trim_px(size_key, dpi)      # where the layout lives
    canvas = millers.page_px(size_key, dpi)    # what the lab receives, bleed included
    os.makedirs(OUTDIR, exist_ok=True)

    # Refuse to print a frame that would arrive soft (Miller's bar: 250 DPI).
    floor = millers.min_pixels_for(size_key)
    soft = []
    for n in dict.fromkeys(seq):
        if n not in src:
            continue
        with Image.open(src[n]) as probe:
            if probe.width < floor[0] and probe.height < floor[1]:
                soft.append(f"frame {n}: {probe.width}x{probe.height}, "
                            f"under {floor[0]}x{floor[1]} for a {size_key} at 250 DPI")

    if spec:
        global COVER_FRAME
        cov = spec.get("cover", {"style": "photo", "frame": COVER_FRAME})
        COVER_FRAME = cov.get("frame") if cov.get("style") == "photo" else None
        pages, notes = render_spec(spec, src, page, canvas)
        return finish(press, seq=seq, dropped=dropped, src=src,
                      page=page, canvas=canvas, dpi=dpi, pages=pages,
                      notes=notes, soft=soft, size_key=size_key, seq_from=seq_from)

    ims = {n: Image.open(src[n]).convert("RGB") for n in seq}
    pages, notes, i = [], [], 0
    while i < len(seq):
        n = seq[i]
        im = ims[n]
        tall = im.height > im.width
        nxt = seq[i + 1] if i + 1 < len(seq) else None
        if n in MONTAGE_SPREADS:
            grid = [m for m in MONTAGE_SPREADS[n] if m in src]
            gone = [m for m in MONTAGE_SPREADS[n] if m not in src]
            if grid:
                pages.append((matted(im, page), str(n), "montage hero"))
                gims = [Image.open(src[m]).convert("RGB") for m in grid]
                pages.append((montage(gims, page), "+".join(map(str, grid)),
                              f"montage, {len(grid)} facing {n}"))
                if gone:
                    notes.append(f"montage for {n} skipped missing frames {gone}")
                i += 1
                continue
            notes.append(f"montage for {n} has no frames on disk {MONTAGE_SPREADS[n]}; "
                         f"it fell back to a plain page")
        if tall and nxt is not None and ims[nxt].height > ims[nxt].width:
            pages.append((pair(im, ims[nxt], page), f"{n} + {nxt}", "paired"))
            i += 2
            continue
        if MATTE_ALL:
            pages.append((matted(im, page), str(n),
                          "matted, portrait" if tall else "matted, landscape"))
            i += 1
            continue
        if tall:
            pages.append((matted(im, page), str(n), "matted, portrait"))
            i += 1
            continue
        full, lost = fit(im, page)
        if full is None:
            pages.append((matted(im, page), str(n), f"matted, would lose {lost:.0%}"))
        else:
            pages.append((full, str(n), f"full bleed, {lost:.0%} cropped"))
            if lost > 0.06:
                notes.append(f"frame {n} loses {lost:.0%} to the page")
        i += 1

    return finish(press, seq=seq, dropped=dropped, src=src,
                  page=page, canvas=canvas, dpi=dpi, pages=pages,
                  notes=notes, soft=soft, size_key=size_key, seq_from=seq_from)


def finish(press, seq, dropped, src, page, canvas, dpi,
           pages, notes, soft, size_key, seq_from):
    """Cover, bleed wrap, lab checks, files. One tail for both paths."""
    from PIL import Image
    if COVER_FRAME is not None and COVER_FRAME in src:
        cim = Image.open(src[COVER_FRAME]).convert("RGB")
        cover = photo_cover(cim, canvas, dpi, TITLE, SUBTITLE)
        cover_note = f"photographic, frame {COVER_FRAME}"
    else:
        cover = on_bleed(title_page(page, len(seq)), canvas)
        cover_note = "typographic"
    sheets = [cover] + [on_bleed(p, canvas) for p, _, _ in pages]

    checks = millers.check_book(len(pages), size_key)

    tag = "press" if press else "preview"
    jdir = os.path.join(OUTDIR, f"{tag}_pages")
    os.makedirs(jdir, exist_ok=True)
    # Cleared first because submit() zips EVERYTHING in it: a shorter book
    # built after a longer one would otherwise ship the longer book's tail.
    for old in os.listdir(jdir):
        if old.endswith(".jpg"):
            os.remove(os.path.join(jdir, old))
    for k, s in enumerate(sheets):
        s.save(os.path.join(jdir, f"page_{k+1:03d}.jpg"), quality=95 if press else 88,
               subsampling=0 if press else 2, dpi=(dpi, dpi))

    if press:
        out = os.path.join(OUTDIR, f"Interlaken_book_press_{size_key}.pdf")
        sheets[0].save(out, save_all=True, append_images=sheets[1:],
                       resolution=dpi, quality=95)
    else:
        # A book reads in spreads; the cover stands alone.
        spreads = [cover]
        rest = [p for p, _, _ in pages]
        for k in range(0, len(rest), 2):
            a = rest[k]
            b = rest[k + 1] if k + 1 < len(rest) else Image.new("RGB", page, GROUND)
            sp = Image.new("RGB", (page[0] * 2, page[1]), GROUND)
            sp.paste(a, (0, 0)); sp.paste(b, (page[0], 0))
            spreads.append(sp)
        out = os.path.join(OUTDIR, f"Interlaken_book_preview_{size_key}.pdf")
        spreads[0].save(out, save_all=True, append_images=spreads[1:],
                        resolution=dpi, quality=88)

    with open(os.path.join(OUTDIR, "sequence_book.txt"), "w") as fh:
        fh.write(f"The book, {len(seq)} frames, {len(pages)} pages, "
                 f"sequence from {seq_from}\n\n")
        for k, (_, label, how) in enumerate(pages, 1):
            fh.write(f"{k:3d}. {label:<12} {how}\n")

    print(f"wrote {out}")
    print(f"  sequence from {seq_from}")
    print(f"  {len(seq)} frames · {len(pages)} pages · {len(sheets)} sheets at {dpi} DPI")
    print(f"  cover: {cover_note}")
    print(f"  lab: Miller's {size_key} Signature Book, "
          f"{canvas[0]}x{canvas[1]} px with {millers.BLEED_IN}in bleed, "
          f"{len(pages)/millers.SIDES_PER_SPREAD:.0f} spreads")
    for c in checks:
        print(f"  LAB CHECK: {c}")
    for s in soft:
        print(f"  RESOLUTION: {s}")
    if millers.SUBMIT_UNIT == "sides":
        print("  submitting as single sides; confirm with Miller's whether this "
              "book wants composed layflat spreads instead (millers.py SUBMIT_UNIT)")
    print(f"  sequence: {OUTDIR}/sequence_book.txt")
    if dropped:
        print(f"  IN THE BOOK, though they also sit in your aside lane: {dropped}")
    for nt in notes:
        print(f"  {nt}")


def submit(cover_route="linen"):
    """Package the press pages the way Miller's order form asks, and print
    the checklist that turns a folder into an ordered book."""
    import zipfile
    build(press=True)
    jdir = os.path.join(OUTDIR, "press_pages")
    pages = sorted(f for f in os.listdir(jdir) if f.endswith(".jpg"))
    zpath = os.path.join(OUTDIR, f"Interlaken_{SIZE_KEY}_press.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as z:
        for f in pages:
            z.write(os.path.join(jdir, f), f)
    mb = os.path.getsize(zpath) / 1e6
    route = millers.COVER_ROUTES[cover_route]
    sides = len(pages) - 1                      # the cover is not a side
    print(f"\n=== READY TO SUBMIT ===")
    print(f"  zip        {zpath}  ({mb:.0f} MB, {len(pages)} files)")
    print(f"  book       Miller's {SIZE_KEY} Signature Book, "
          f"{sides} sides = {sides/millers.SIDES_PER_SPREAD:.0f} spreads")
    print(f"  cover      {cover_route}: {route['how']}")
    if not route["artwork"]:
        print(f"             page_001 in the zip is a cover sheet and is NOT "
              f"used on this route; remove it or order Custom Image instead")
    print(f"\n  1. upload the zip: {millers.DROP_URL}")
    print(f"  2. fill and send:  {millers.ORDER_FORM}")
    print(f"  3. on the form, cover text goes in the foil/deboss fields by position")
    print(f"  4. paper: Matte press, Pearl press, or Deep Matte photographic")
    if millers.SUBMIT_UNIT == "sides":
        print(f"\n  UNCONFIRMED: submitting single sides. If Miller's wants composed")
        print(f"  layflat spreads, set millers.SUBMIT_UNIT and rebuild.")
    return zpath


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--press", action="store_true")
    ap.add_argument("--submit", action="store_true",
                    help="press build, then zip it the way Miller's asks")
    ap.add_argument("--cover", default="linen", choices=list(millers.COVER_ROUTES))
    a = ap.parse_args()
    if a.submit:
        submit(a.cover)
    else:
        build(a.press)
