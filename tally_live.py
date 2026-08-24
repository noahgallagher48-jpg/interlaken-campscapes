#!/usr/bin/env python3
"""Tallies the LIVE favorites vote (favorites.html, deployed 2026-08-04, question
added 2026-08-17) for the Sep 8 call with Drea. Supersedes tally_ballots.py,
which parsed the retired "INTERLAKEN BALLOT v2" format and reads zero of the
real ballots.

Ballots arrive as Web3Forms emails, subject "Interlaken favorites: <name>",
body lines like:

    name : Sheryl Rubin
    connection : Board
    email : srubin@wi.rr.com
    what_it_brings_back : shabbat peace
    bridge_with_people : 23, 60
    bridge_without_people : 14, 16
    landscapes : 1, 20, 24, 40, 87, 101
    shabbat : 42, 45, 52, 53, 54, 76, 99
    the_rest : 3, 97, 148, 153, 182, 185, 193, 196

Each ballot is appended verbatim to the private dashboard repo at
docs/interlaken_ballots.txt under a header line "=== <sender> <date>".
Keeping that file current is a session job: search Gmail for
subject:"Interlaken favorites", append any ballot not yet on file.

Usage:
    python3 tally_live.py                          # reads the dashboard file
    python3 tally_live.py path/to/ballots.txt
    python3 tally_live.py --html _work/tally.html  # call-ready page w/ thumbnails

Rules: one ballot per voter (keyed by email, else by name); a later ballot from
the same voter replaces the earlier one and is noted. Picks outside a section's
frame list are flagged, never silently dropped. Vote counts are per frame per
section. The quotes table is verbatim, in arrival order.
"""
import json, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BALLOTS_DEFAULT = os.path.expanduser("~/Abba_Photo/dashboard/docs/interlaken_ballots.txt")
LIVE_THUMB = "https://www.abba-photo.com/interlaken-campscapes/img/thumb/"
LIVE_PRESENT = "https://www.abba-photo.com/interlaken-campscapes/img/present/"

SECTIONS = [
    ("bridge_with_people",    "The bridge, with people",    2),
    ("bridge_without_people", "The bridge, without people", 2),
    ("landscapes",            "Landscapes, nobody in them", 6),
    ("shabbat",               "Shabbat",                    7),
    ("the_rest",              "The rest",                   8),
]

def survey_frames():
    """The allowed frame numbers per section, taken from build_vote.py so the
    tally can never drift from the ballot."""
    src = open(os.path.join(HERE, "build_vote.py")).read()
    m = re.search(r"SURVEY = \[(.*?)\n\]", src, re.S)
    blocks = re.findall(r'"k": "(\w+)".*?"frames": \[(.*?)\]', m.group(1), re.S)
    keymap = {"bp": "bridge_with_people", "bn": "bridge_without_people",
              "ls": "landscapes", "sh": "shabbat", "rest": "the_rest"}
    return {keymap[k]: set(int(x) for x in re.findall(r"\d+", nums))
            for k, nums in blocks}

def frame_files():
    out = {}
    for f in json.load(open(os.path.join(HERE, "frames.json"))):
        m = re.match(r"CILWEB1-(\d+)$", f["id"])
        out[int(m.group(1)) if m else 1] = f["file"]  # bare CILWEB1 is frame 1, per build_vote.by_num
    return out

def parse(path):
    ballots, cur = [], None
    for raw in open(path):
        line = raw.rstrip("\n")
        if line.startswith("==="):
            cur = {"_header": line.lstrip("= ").strip()}
            ballots.append(cur)
            continue
        if cur is None or " : " not in line and ":" not in line:
            continue
        key, _, val = line.partition(":")
        cur[key.strip()] = val.strip()
    # The 8/24 pipeline verification submitted a real ballot through the real
    # form, deliberately named so it can never count. Anything test-named is
    # dropped here, loudly, so the Sep 8 numbers are only the community's.
    kept = []
    for b in ballots:
        label = (b.get("name", "") + " " + b.get("_header", "")).upper()
        if "PIPELINE TEST" in label or "DISCARD" in label:
            print(f"  excluded test ballot: {b.get('name') or b.get('_header')}")
            continue
        kept.append(b)
    return kept

def main():
    args = sys.argv[1:]
    html_out = None
    if "--html" in args:
        i = args.index("--html")
        html_out = args[i + 1]
        args = args[:i] + args[i + 2:]
    path = args[0] if args else BALLOTS_DEFAULT

    allowed = survey_frames()
    files = frame_files()
    raw = parse(path)

    voters, order, notes = {}, [], []
    for b in raw:
        key = (b.get("email") or b.get("name") or b.get("_header", "?")).lower()
        if key in voters:
            notes.append(f"replaced earlier ballot from {b.get('name', key)}")
        else:
            order.append(key)
        voters[key] = b

    counts = {sec: defaultdict(list) for sec, _, _ in SECTIONS}
    quotes = []
    for key in order:
        b = voters[key]
        name = b.get("name") or key
        q = b.get("what_it_brings_back", "").strip()
        if q:
            quotes.append((name, b.get("connection", ""), q))
        for sec, _, quota in SECTIONS:
            picks = [int(x) for x in re.findall(r"\d+", b.get(sec, ""))]
            for n in picks:
                if n not in allowed[sec]:
                    notes.append(f"{name}: pick {n} not in section {sec}, counted anyway")
                counts[sec][n].append(name)
            if picks and len(picks) != quota:
                notes.append(f"{name}: {len(picks)} picks in {sec}, quota is {quota}")

    nv = len(order)
    print(f"BALLOTS: {nv}  (file: {path})")
    for note in notes:
        print(f"  note: {note}")
    print()
    for sec, title, _ in SECTIONS:
        ranked = sorted(counts[sec].items(), key=lambda kv: (-len(kv[1]), kv[0]))
        print(f"{title}")
        for n, who in ranked:
            print(f"  {len(who):>3}  #{n:<4} {files.get(n, '?'):<28} {', '.join(who)}")
        print()
    if quotes:
        print("What it brings back (verbatim):")
        for name, conn, q in quotes:
            print(f'  {name} ({conn}): "{q}"')

    if html_out:
        secs = []
        for sec, title, _ in SECTIONS:
            ranked = sorted(counts[sec].items(), key=lambda kv: (-len(kv[1]), kv[0]))
            cards = "".join(
                f'<figure><a href="{LIVE_PRESENT}{files[n]}" target=_blank>'
                f'<img loading=lazy src="{LIVE_THUMB}{files[n]}" alt="#{n}"></a>'
                f'<figcaption><b>{len(who)}</b> &middot; #{n}</figcaption></figure>'
                for n, who in ranked if n in files)
            secs.append(f"<section><h2>{title}</h2><div class=wall>{cards}</div></section>")
        qrows = "".join(f'<li>&ldquo;{q}&rdquo; <span>{name}, {conn}</span></li>'
                        for name, conn, q in quotes)
        page = f"""<!DOCTYPE html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><meta name=robots content=noindex>
<title>Interlaken favorites &middot; the tally</title><style>
body{{margin:0;background:#161310;color:#EDE7DD;font:15px/1.5 "Avenir Next",Avenir,-apple-system,sans-serif;padding:24px}}
h1{{font-family:Georgia,serif;font-weight:500;margin:0 0 2px}}
.sub{{color:#A29786;font-size:13px;margin-bottom:26px}}
h2{{font-family:Georgia,serif;font-weight:500;font-size:19px;margin:30px 0 10px}}
.wall{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}}
figure{{margin:0}}img{{width:100%;height:auto;border-radius:4px;display:block}}
figcaption{{font-size:12px;color:#A29786;margin-top:3px}}figcaption b{{color:#E2A73E;font-size:14px}}
ul{{list-style:none;padding:0}}li{{margin:8px 0;font-family:Georgia,serif;font-size:16px}}
li span{{color:#A29786;font-family:"Avenir Next",sans-serif;font-size:12.5px;margin-left:8px}}
footer{{margin-top:36px;color:#7A7060;font-size:12px}}</style></head><body>
<h1>Camp Interlaken &middot; the favorites, tallied</h1>
<div class=sub>{nv} ballot{"s" if nv != 1 else ""} &middot; vote open through Sept 7 &middot; ranked by votes, live library thumbnails</div>
{"".join(secs)}
<section><h2>What it brings back, verbatim</h2><ul>{qrows}</ul></section>
<footer>Photographs Noah Gallagher &middot; Abba Photo &middot; internal tally for the Sep 8 review</footer>
</body></html>"""
        open(html_out, "w").write(page)
        print(f"\nwrote {html_out}")

if __name__ == "__main__":
    main()
