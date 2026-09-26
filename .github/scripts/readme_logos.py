"""Render the README's framework logos from the store's own marks.

The marks under frameworks/ are monochrome by contract, which GitHub would
draw black and lose on a dark theme. This paints each one in its declared
colour on a white tile, so the README reads the same in either theme.

Run from the repo root after adding or changing a mark:
    python3 .github/scripts/readme_logos.py
"""

import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / ".github" / "logos"

TILE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">\
<rect x="0.5" y="0.5" width="63" height="63" rx="14" fill="#ffffff" stroke="#e4e4e7"/>\
<svg x="13" y="13" width="38" height="38" viewBox="{viewbox}" fill="{color}">{body}</svg></svg>
"""


def render(mark: str, color: str) -> str:
    root = re.match(r'\s*<svg[^>]*viewBox="([^"]+)"[^>]*>(.*)</svg>\s*$', mark, re.S)
    if not root:
        sys.exit("mark has no <svg viewBox=...> root")
    return TILE.format(viewbox=root.group(1), color=color, body=root.group(2))


def main() -> None:
    index = json.loads((ROOT / "frameworks" / "index.json").read_text())
    OUT.mkdir(exist_ok=True)
    for entry in index["frameworks"]:
        name = entry["name"]
        mark = ROOT / "frameworks" / f"{name}.svg"
        if not mark.exists():
            sys.exit(f"{name} has no frameworks/{name}.svg, and the README table shows every framework's mark")
        definition = yaml.safe_load((ROOT / "frameworks" / name / f"{entry['latest']}.yaml").read_text())
        color = definition.get("color")
        if not color:
            sys.exit(f"{name}@{entry['latest']} declares no color:")
        (OUT / f"{name}.svg").write_text(render(mark.read_text(), color))
        print(f"wrote .github/logos/{name}.svg")


if __name__ == "__main__":
    main()
