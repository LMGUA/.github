#!/usr/bin/env python3
"""Build the six 244 × 52 community buttons from reusable vector sources.

Normal builds use source/community-button-labels.json and never open font files.
Use --refresh-text to regenerate label outlines from local PingFang SC Semibold
and Inter Semibold. Font files are read locally and are never copied or embedded.
The X, Discord and LMGUA logo paths are preserved, only positioned and coloured.
"""
from argparse import ArgumentParser
from copy import deepcopy
from html import escape
import json
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree as ET

from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

ROOT = Path(__file__).resolve().parents[1]
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
INK, WHITE, RED = "#111114", "#FFFFFF", "#E5222B"
WIDTH, HEIGHT, FONT_SIZE = 244, 52, 16
LABELS = {
    "x-zh": "邵艾伦 Alan", "x-en": "Alan Shao",
    "discord-zh": "加入 Discord", "discord-en": "Join Discord",
    "website-zh": "官方网站", "website-en": "Official website",
    "arrow": "↗",
}


def xml_svg(body, width, height, title):
    return (f'<svg xmlns="{NS}" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">'
            f'<title id="title">{escape(title)}</title>{body}</svg>\n')


def parse_transform(value):
    result = Transform()
    for name, arguments in re.findall(r"([a-zA-Z]+)\(([^)]*)\)", value):
        values = [float(item) for item in re.split(r"[\s,]+", arguments.strip())]
        if name == "translate":
            result = result.translate(values[0], values[1] if len(values) == 2 else 0)
        elif name == "scale":
            result = result.scale(values[0], values[1] if len(values) == 2 else values[0])
        elif name == "matrix":
            result = result.transform(tuple(values))
        else:
            raise ValueError(f"Unsupported transform: {name}")
    return result


def geometry_bounds(element):
    bounds = BoundsPen(None)

    def visit(node, inherited=Transform()):
        combined = inherited.transform(parse_transform(node.get("transform", "")))
        if node.tag.split("}")[-1] == "path":
            parse_path(node.get("d", ""), TransformPen(bounds, combined))
        for child in node:
            visit(child, combined)

    visit(element)
    return bounds.bounds


def load_chinese_font(path=None, number=0):
    from fontTools.ttLib import TTCollection, TTFont
    if path:
        return TTFont(path, fontNumber=number)
    candidates = sorted(Path("/System/Library/AssetsV2/com_apple_MobileAsset_Font7")
                        .glob("*/AssetData/PingFang.ttc"))
    candidates += [Path("/System/Library/Fonts/PingFang.ttc")]
    for candidate in candidates:
        if not candidate.is_file():
            continue
        collection = TTCollection(candidate, lazy=True)
        try:
            for index, font in enumerate(collection.fonts):
                names = [record.toUnicode() for record in font["name"].names
                         if record.nameID == 6]
                if "PingFangSC-Semibold" in names:
                    return TTFont(candidate, fontNumber=index)
        finally:
            collection.close()
    raise FileNotFoundError("Pass --chinese-font and --font-number for a local font.")


def outline_labels(args):
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    chinese = load_chinese_font(args.chinese_font, args.font_number)
    latin_path = args.latin_font or ROOT.parent / "lmgua-brand/source/fonts/Inter.ttf"
    latin = instantiateVariableFont(TTFont(latin_path), {"wght": 600, "opsz": 32})
    output = {"font_size": FONT_SIZE, "weight": 600,
              "fonts": ["PingFang SC Semibold", "Inter Semibold"], "labels": {}}
    for key, text in LABELS.items():
        pen, cursor = SVGPathPen(None), 0
        for character in text:
            font = latin if ord(character) in latin.getBestCmap() else chinese
            pen.glyphSet = font.getGlyphSet()
            glyph = pen.glyphSet[font.getBestCmap()[ord(character)]]
            scale = FONT_SIZE / font["head"].unitsPerEm
            glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, 0)))
            cursor += glyph.width * scale
        path = pen.getCommands()
        bounds = BoundsPen(None)
        parse_path(path, bounds)
        output["labels"][key] = {"text": text, "path": path,
                                  "bounds": bounds.bounds, "advance": cursor}
    chinese.close()
    latin.close()
    source = ROOT / "source/community-button-labels.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")


def position_label(record, color, left=None, right=None):
    x0, y0, x1, y1 = record["bounds"]
    x = left - x0 if left is not None else right - x1
    y = HEIGHT / 2 - (y0 + y1) / 2
    return (f'<path fill="{color}" aria-label="{escape(record["text"])}" '
            f'transform="translate({x:.9f} {y:.9f})" d="{record["path"]}"/>')


def position_icon(kind, color):
    filename = ROOT / ("profile/assets/lmgua-mark.svg" if kind == "website"
                       else f"source/icons/{kind}.svg")
    source = ET.parse(filename).getroot()
    icon = ET.Element(f"{{{NS}}}g", {"aria-label": kind})
    for child in source:
        if child.tag.split("}")[-1] not in {"title", "desc", "metadata"}:
            icon.append(deepcopy(child))
    paths = [node.get("d") for node in icon.iter() if node.tag.split("}")[-1] == "path"]
    x0, y0, x1, y1 = geometry_bounds(icon)
    scale = 24 / max(x1 - x0, y1 - y0)
    tx = 30 - (x0 + x1) / 2 * scale
    ty = 26 - (y0 + y1) / 2 * scale
    icon.set("transform", f"matrix({scale:.12f} 0 0 {scale:.12f} {tx:.12f} {ty:.12f})")
    for node in icon.iter():
        if "fill" in node.attrib or node.tag.split("}")[-1] == "path":
            node.set("fill", color)
    assert paths == [node.get("d") for node in icon.iter() if node.tag.split("}")[-1] == "path"]
    return icon


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-text", action="store_true")
    parser.add_argument("--chinese-font", type=Path)
    parser.add_argument("--font-number", type=int, default=0)
    parser.add_argument("--latin-font", type=Path)
    parser.add_argument("--preview", type=Path,
                        default=ROOT.parent / "lmgua-community-buttons-preview.png")
    args = parser.parse_args()
    if (args.chinese_font or args.latin_font) and not args.refresh_text:
        parser.error("Font arguments require --refresh-text")
    if args.refresh_text:
        outline_labels(args)
    labels = json.loads((ROOT / "source/community-button-labels.json").read_text())["labels"]
    assert {key: value["text"] for key, value in labels.items()} == LABELS
    measurements, bodies = {}, {}
    for language in ("zh", "en"):
        for kind in ("x", "discord", "website"):
            key = f"{kind}-{language}"
            background = {"x": INK, "discord": RED, "website": WHITE}[kind]
            foreground = RED if kind == "website" else WHITE
            icon = position_icon(kind, foreground)
            label = position_label(labels[key], foreground, left=56)
            arrow = position_label(labels["arrow"], foreground, right=225)
            parts = [icon, ET.fromstring(label), ET.fromstring(arrow)]
            bounds = [geometry_bounds(part) for part in parts]
            assert all(0 <= x0 < x1 <= WIDTH and 0 <= y0 < y1 <= HEIGHT
                       for x0, y0, x1, y1 in bounds), (key, bounds)
            assert bounds[0][2] + 12 <= bounds[1][0], (key, bounds)
            assert bounds[1][2] + 16 <= bounds[2][0], (key, bounds)
            body = (f'<rect x="1" y="1" width="242" height="50" rx="6" '
                    f'fill="{background}" stroke="{RED}" stroke-width="2"/>')
            body += ET.tostring(icon, encoding="unicode") + label + arrow
            destination = ROOT / f"profile/assets/community-{key}.svg"
            destination.write_text(xml_svg(body, WIDTH, HEIGHT, LABELS[key]))
            measurements[key] = {"icon": bounds[0], "label": bounds[1], "arrow": bounds[2]}
            bodies[key] = body
    # Chinese row on light, English row on dark: both retain the same geometry.
    preview = '<path fill="#FFFFFF" d="M0 0H804V88H0Z"/>'
    preview += '<path fill="#111114" d="M0 88H804V176H0Z"/>'
    for row, language in enumerate(("zh", "en")):
        for column, kind in enumerate(("x", "discord", "website")):
            preview += (f'<g transform="translate({24 + column * 256} {18 + row * 88})">'
                        f'{bodies[f"{kind}-{language}"]}</g>')
    args.preview.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsvg-convert", "--output", str(args.preview)],
                   input=xml_svg(preview, 804, 176, "LMGUA community buttons").encode(), check=True)
    print(json.dumps({"dimensions": [WIDTH, HEIGHT], "bounds": measurements,
                      "preview": str(args.preview)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
