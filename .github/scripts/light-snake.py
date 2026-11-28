#!/usr/bin/env python3
"""Recolor a snake-and-commits "green" SVG from its dark palette to a light one.

snake-and-commits ships dark themes only, so this rewrites the generated SVG
in place: contribution levels take GitHub's light ramp, the snake keeps its
dark-head-to-light-tail fade, and label/counter colours are adjusted.

Usage: python3 light-snake.py dist/snake-light.svg
"""
import re
import sys

LEVEL = {
    "#161b22": "#ebedf0",  # empty cell
    "#0e4429": "#9be9a8",  # level 1
    "#006d32": "#40c463",  # level 2
    "#26a641": "#30a14e",  # level 3
    "#39d353": "#216e39",  # level 4
}
SNAKE = {
    "#b7ffd0": "#0a3d1c",  # head, darkest
    "#8affc1": "#116329",  # newest segment
    "#39d353": "#1a7f37",  # body
    "#26a641": "#3fa35f",
    "#006d32": "#8bd3a1",  # oldest segment, lightest
}
AMBIGUOUS = {"#006d32", "#26a641", "#39d353"}
LABEL, COUNTER = "#7d8590", "#39d353"
ENTRY = re.compile(r"(\d+(?:\.\d+)?)%\s*\{\s*fill:#([0-9a-fA-F]{6})\s*;?\s\}")
RECT = re.compile(r'(<rect[^>]*?)\bfill="#([0-9a-fA-F]{6})"')


def map_entry(m):
    pct, color = float(m.group(1)), "#" + m.group(2).lower()
    if color in AMBIGUOUS:
        # at 0% the level colours describe the cell's own level; later frames are the snake
        out = LEVEL[color] if pct == 0.0 else SNAKE[color]
    elif color in SNAKE:
        out = SNAKE[color]
    elif color in LEVEL:
        out = LEVEL[color]
    else:
        raise SystemExit(f"unexpected colour {color} at {pct}%")
    return f"{m.group(1)}% {{ fill:{out}; }}"


def map_rect(m):
    color = "#" + m.group(2).lower()
    if color not in LEVEL:
        raise SystemExit(f"unexpected rect colour {color}")
    return f'{m.group(1)}fill="{LEVEL[color]}"'


def main(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    out, seen = [], 0
    for line in lines:
        if line.lstrip().startswith("@keyframes"):
            line = ENTRY.sub(map_entry, line)
            seen += 1
        elif "<rect" in line:
            line = RECT.sub(map_rect, line)
        elif ".lab {" in line:
            line = line.replace(f"fill:{LABEL};", "fill:#57606a;")
        elif ".cnt {" in line:
            line = line.replace(f"fill:{COUNTER};", "fill:#1a7f37;")
        out.append(line)
    text = "\n".join(out)
    if seen < 300:
        raise SystemExit(f"only {seen} keyframes recoloured")
    left = set(re.findall("#[0-9a-fA-F]{6}", text)) & (set(LEVEL) | set(SNAKE))
    if left:
        raise SystemExit(f"leftover dark colours: {sorted(left)}")
    open(path, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main(sys.argv[1])
