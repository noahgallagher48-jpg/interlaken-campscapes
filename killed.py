"""The kill list. One import, one job: a frame removed once never comes back.

Why this exists: culls were being applied by hand-editing sections.json, so a
later restore or rebuild could quietly put a pulled frame back on the page. That
happened on 2026-08-14 with eight frames. `_work/killed.json` is now the single
record, and every builder filters through `strip()` at load, so sections.json can
say anything and the killed frames still will not render.

To kill a frame: add it to `_work/killed.json` with a reason. Never just delete
it from sections.json.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def killed():
    """The set of frame numbers permanently out."""
    p = os.path.join(HERE, "_work", "killed.json")
    if not os.path.exists(p):
        return set()
    return {int(k) for k in json.load(open(p))["killed"]}


def strip(sections):
    """Filter a sections.json structure, dropping killed frames and any group or
    section left empty. Returns the filtered structure."""
    K = killed()
    out = []
    for name, groups in sections:
        g2 = [[gn, [n for n in ns if n not in K]] for gn, ns in groups]
        g2 = [g for g in g2 if g[1]]
        if g2:
            out.append([name, g2])
    return out


def check(sections, label="build"):
    """Loud failure if a killed frame reached the page anyway."""
    K = killed()
    bad = sorted({n for _, gs in sections for _, ns in gs for n in ns} & K)
    if bad:
        raise SystemExit(f"{label}: killed frames present after filtering: {bad}")
