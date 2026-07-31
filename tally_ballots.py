#!/usr/bin/env python3
"""Tallies Interlaken ballots into a marquee ranking.

Ballots arrive by email with subject "Interlaken picks", each body carrying the
machine-readable block the delivery page builds:

    INTERLAKEN BALLOT v1

    sig: havcil-74
    sig: havcil-95
    fa: havcil-46
    ...
    Name: Drea

Save each ballot as a .txt file (or paste several into one file; ballots are
split on the header line) in a folder, then:

    python3 tally_ballots.py ballots/

Output: per-set ranking by vote count, each voter counted once per frame, and a
combined marquee list. Names are read from the Name: line when present so the
report can say who has voted, which is what the follow-up nudge needs.
"""
import collections
import glob
import os
import re
import sys

HEADER = "INTERLAKEN BALLOT v1"
GROUPS = {"sig": "Signature Campscape", "fa": "Fine Art",
          "dev": "Development / Campaign", "pub": "Publication-Ready",
          "day": "Daily / Social"}


def parse(text):
    """Yield (voter, {group: [ids]}) per ballot found in the text."""
    chunks = text.split(HEADER)[1:]
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


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ballots")
