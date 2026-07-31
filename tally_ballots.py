#!/usr/bin/env python3
"""Tallies Interlaken ballots into a marquee ranking.

Ballots arrive by email with subject "Interlaken picks", each body carrying the
machine-readable block the delivery page builds:

    INTERLAKEN BALLOT v2

    sig: havcil-74
    sig: havcil-95
    fa: havcil-46
    ...
    Name: Drea

Save each ballot as a .txt file (or paste several into one file; ballots are
split on the header line) in a folder, then:

    python3 tally_ballots.py ballots/

Output: per-set ranking by vote count, each voter counted once per frame, then
the forty-two the votes elect: the top 12 from the scape sets (sig + fa) and the
top 30 from the story sets (dev + pub + day), the split the signature layout
runs on. v1 marquee ballots tally the same way. Names are read from the Name:
line when present so the report can say who has voted.
"""
import collections
import glob
import os
import re
import sys

HEADER = re.compile(r"INTERLAKEN BALLOT v[12]")
SCAPE = {"sig", "fa"}
GROUPS = {"sig": "Signature Campscape", "fa": "Fine Art",
          "dev": "Development / Campaign", "pub": "Publication-Ready",
          "day": "Daily / Social"}


def parse(text):
    """Yield (voter, {group: [ids]}) per ballot found in the text."""
    chunks = HEADER.split(text)[1:]
    for chunk in chunks:
        votes = collections.defaultdict(list)
        name = ""
        for line in chunk.splitlines():
            m = re.match(r"\s*(sig|fa|dev|pub|day)\s*:\s*(\S+)", line)
            if m:
                votes[m.group(1)].append(m.group(2))
                continue
            n = re.match(r"\s*Name\s*:\s*(.+)", line)
            if n and not name:
                name = n.group(1).strip()
        if votes:
            yield name or "unnamed", votes


def main(folder):
    tally = collections.defaultdict(collections.Counter)  # group -> frame -> votes
    voters = []
    seen = set()
    for path in sorted(glob.glob(os.path.join(folder, "*.txt"))):
        for name, votes in parse(open(path, encoding="utf-8", errors="replace").read()):
            key = (name, tuple(sorted((g, tuple(v)) for g, v in votes.items())))
            if key in seen:            # the same ballot pasted twice
                continue
            seen.add(key)
            voters.append(name)
            for g, ids in votes.items():
                for fid in set(ids):   # one voter, one vote per frame
                    tally[g][fid] += 1

    if not voters:
        sys.exit(f"no ballots found in {folder}")

    print(f"ballots: {len(voters)}  ({', '.join(voters)})\n")
    combined = collections.Counter()
    for g in GROUPS:
        if not tally[g]:
            continue
        print(GROUPS[g])
        for fid, n in tally[g].most_common():
            marks = "#" * n
            print(f"  {n:>2}  {fid:<14} {marks}")
            combined[fid] += n
        print()
    print("Marquee, all sets combined")
    for fid, n in combined.most_common(15):
        print(f"  {n:>2}  {fid}")

    scape = collections.Counter()
    story = collections.Counter()
    for g, counts in tally.items():
        (scape if g in SCAPE else story).update(counts)
    print("\nThe forty-two the votes elect")
    print(f"  scapes, top 12 of {len(scape)} voted")
    for fid, n in scape.most_common(12):
        print(f"  {n:>2}  {fid}")
    print(f"  story, top 30 of {len(story)} voted")
    for fid, n in story.most_common(30):
        print(f"  {n:>2}  {fid}")
    short = (12 - min(12, len(scape))) + (30 - min(30, len(story)))
    if short:
        print(f"  ({short} slots unfilled by votes so far; ties and gaps are Noah's call)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ballots")
