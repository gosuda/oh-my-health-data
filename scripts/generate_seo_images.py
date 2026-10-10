#!/usr/bin/env python3
"""Generate checked-in social cards and brand icons without runtime dependencies.

Build tools: Python 3, fonttools[woff] 4.66.1, Node.js, and sharp 0.35.5.
Fonts come from the project's existing, lockfile-pinned @fontsource packages.

    python3 -m venv /tmp/oh-my-health-data-seo-tools
    /tmp/oh-my-health-data-seo-tools/bin/pip install 'fonttools[woff]==4.66.1'
    npm install --prefix /tmp/oh-my-health-data-seo-tools sharp@0.35.5
    npm ci
    /tmp/oh-my-health-data-seo-tools/bin/python scripts/generate_seo_images.py \
        --sharp-module /tmp/oh-my-health-data-seo-tools/node_modules/sharp

Every SVG contains outlined text, not embedded fonts or raster images. Rendering
the checked-in SVGs again requires only Node.js and sharp, not fontTools or
installed fonts: add `--raster-only` to the generator command.
Nothing from this script runs as part of the website build or in the browser.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
OG = STATIC / "og"
INK = "#1c211c"
PAPER = "#f3f1e8"
LIME = "#e5ff36"


class OutlinedFonts:
    """Use the same font files as the site, with no OS font lookup."""

    def __init__(self) -> None:
        from fontTools.ttLib import TTFont

        self.font_loader = TTFont
        self.fonts = {}
        self.glyph_sets = {}
        self.korean_dir = ROOT / "node_modules/@fontsource-variable/noto-sans-kr"
        css = (self.korean_dir / "index.css").read_text()
        self.faces = []
        for block in re.findall(r"@font-face\s*\{(.*?)\}", css, re.S):
            source = re.search(r"url\(\./([^)]+)\)", block)
            ranges = re.search(r"unicode-range:\s*([^;]+)", block)
            if not source or not ranges:
                continue
            intervals = []
            for item in ranges.group(1).split(","):
                first, _, last = item.strip()[2:].partition("-")
                intervals.append((int(first, 16), int(last or first, 16)))
            self.faces.append((self.korean_dir / source.group(1), intervals))
        self.latin = ROOT / (
            "node_modules/@fontsource/barlow-condensed/files/"
            "barlow-condensed-latin-700-normal.woff2"
        )

    def get_glyph(self, char: str, weight: int, latin: bool):
        code = ord(char)
        path = self.latin if latin else next(
            (path for path, intervals in self.faces if any(a <= code <= b for a, b in intervals)),
            None,
        )
        if path is None:
            raise ValueError(f"No font-source subset for {char!r}")
        if path not in self.fonts:
            self.fonts[path] = self.font_loader(path)
        font = self.fonts[path]
        name = font.getBestCmap().get(code)
        if name is None:
            raise ValueError(f"Missing glyph {char!r} in {path}")
        key = (path, weight)
        if key not in self.glyph_sets:
            location = {"wght": weight} if "fvar" in font else None
            self.glyph_sets[key] = font.getGlyphSet(location=location)
        glyph_set = self.glyph_sets[key]
        return glyph_set, glyph_set[name], font["head"].unitsPerEm

    def text(self, value: str, x: float, y: float, size: float, color: str,
             weight: int = 800, latin: bool = False, max_width: float | None = None) -> str:
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen

        glyphs = [self.get_glyph(char, weight, latin) for char in value]
        text_width = sum(glyph.width * size / upm for _, glyph, upm in glyphs)
        if max_width is not None and text_width > max_width:
            raise ValueError(f"Text overflows ({text_width:.1f} > {max_width}): {value}")
        paths = []
        cursor = x
        for glyph_set, glyph, upm in glyphs:
            scale = size / upm
            pen = SVGPathPen(glyph_set, ntos=lambda n: f"{n:.3f}".rstrip("0").rstrip(".") or "0")
            glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, y)))
            if pen.getCommands():
                paths.append(pen.getCommands())
            cursor += glyph.width * scale
        return f'<g aria-label="{html.escape(value, quote=True)}" fill="{color}"><path d="{"".join(paths)}"/></g>'


def mark(x: float, y: float, size: float, color: str = INK) -> str:
    # Geometry matches src/lib/Mark.svelte, including its paper-coloured centre.
    return f'''<g transform="translate({x} {y}) scale({size / 48})">
      <path d="M24 3V45M3 24H45M9 9L39 39M9 39L39 9" stroke="{color}" stroke-width="7" fill="none"/>
      <path d="M19 19H29V29H19Z" fill="{PAPER}"/>
    </g>'''


def svg_document(body: str, title: str, width: int = 1200, height: int = 630) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">
  <title id="title">{html.escape(title)}</title>
  {body}
</svg>
'''


def footer(fonts: OutlinedFonts, dark: bool) -> str:
    foreground = PAPER if dark else INK
    return (
        f'<path d="M64 518H1136" stroke="{foreground}" stroke-opacity=".3"/>'
        + mark(64, 549, 34, LIME if dark else INK)
        + fonts.text("Oh My Health Data", 112, 579, 37, foreground, latin=True)
        + fonts.text("gosuda", 1046, 579, 31, foreground, latin=True, max_width=90)
    )


def home_card(fonts: OutlinedFonts) -> str:
    body = f'<path fill="{INK}" d="M0 0H1200V630H0Z"/>'
    body += f'<rect x="64" y="50" width="265" height="42" fill="{LIME}"/>'
    body += fonts.text("병무청 건강정보 캠페인", 80, 79, 22, INK, 700, max_width=240)
    body += fonts.text("oh-my-health-data.com", 858, 80, 27, PAPER, latin=True, max_width=278)
    for text, baseline, color in [
        ("병무청 신검,", 220, PAPER),
        ("내 기록도", 318, PAPER),
        ("연구에 쓰일까?", 416, LIME),
    ]:
        body += fonts.text(text, 64, baseline, 83, color, 900, max_width=728)

    # A symbolic record, without personal values, official seals, or data claims.
    body += f'<rect x="827" y="142" width="278" height="338" fill="{LIME}" transform="rotate(7 966 311)"/>'
    body += '<g transform="rotate(-5 974 317)">'
    body += f'<rect x="813" y="143" width="290" height="338" fill="{PAPER}"/>'
    body += f'<circle cx="838" cy="168" r="5" fill="{INK}"/><circle cx="1078" cy="168" r="5" fill="{INK}"/>'
    body += fonts.text("MY RECORD", 838, 216, 31, INK, latin=True)
    body += f'<path d="M838 234H1078" stroke="{INK}" stroke-width="2"/>'
    for label, baseline in [("검사 기록", 284), ("연구 활용", 340), ("보존 기준", 396)]:
        body += fonts.text(label, 838, baseline, 27, INK, 800)
        body += f'<path d="M838 {baseline+17}H1078" stroke="{INK}" stroke-opacity=".25"/>'
    body += mark(1045, 431, 29)
    body += '</g>'
    body += footer(fonts, True)
    return svg_document(body, "병무청 신검, 내 기록도 연구에 쓰일까? — Oh My Health Data")


def sources_card(fonts: OutlinedFonts) -> str:
    body = f'<path fill="{PAPER}" d="M0 0H1200V630H0Z"/>'
    body += f'<rect x="64" y="50" width="202" height="42" fill="{INK}"/>'
    body += fonts.text("공식 자료 모음", 80, 79, 22, PAPER, 700, max_width=172)
    body += fonts.text("oh-my-health-data.com", 858, 80, 27, INK, latin=True, max_width=278)
    body += fonts.text("병무청 건강정보", 64, 237, 82, INK, 900, max_width=730)
    body += f'<rect x="60" y="265" width="425" height="106" fill="{LIME}"/>'
    body += fonts.text("공식 근거", 73, 346, 82, INK, 900, max_width=402)
    body += fonts.text("연구 제공 · 보존기간 · 정보주체의 권리", 64, 433, 25, INK, 600, max_width=740)

    body += f'<rect x="850" y="157" width="268" height="322" fill="{LIME}" transform="rotate(7 984 318)"/>'
    body += '<g transform="rotate(-5 980 308)">'
    body += f'<rect x="824" y="143" width="278" height="336" fill="{INK}"/>'
    body += fonts.text("SOURCE FILE", 849, 207, 31, LIME, latin=True)
    body += f'<path d="M849 228H1077" stroke="{PAPER}" stroke-opacity=".5"/>'
    for label, baseline in [("병무청", 281), ("공공데이터", 339), ("법령 · 규정", 397)]:
        body += fonts.text(label, 849, baseline, 27, PAPER, 800)
        body += f'<path d="M849 {baseline+18}H1077" stroke="{PAPER}" stroke-opacity=".3"/>'
    body += mark(1045, 431, 29, LIME)
    body += '</g>'
    body += footer(fonts, False)
    return svg_document(body, "병무청 건강정보 공식 근거 — Oh My Health Data")


def write_sources() -> None:
    fonts = OutlinedFonts()
    OG.mkdir(parents=True, exist_ok=True)
    (OG / "home.svg").write_text(home_card(fonts), encoding="utf-8")
    (OG / "sources.svg").write_text(sources_card(fonts), encoding="utf-8")
    # The same source is used for all favicon/logo sizes.
    icon = svg_document(
        f'<path fill="{LIME}" d="M0 0H64V64H0Z"/>' + mark(8, 8, 48),
        "Oh My Health Data", 64, 64,
    )
    (STATIC / "favicon.svg").write_text(icon, encoding="utf-8")


def render_pngs(sharp_module: str) -> None:
    node = shutil.which("node")
    if node is None:
        raise SystemExit("Install Node.js to render the outlined SVGs using sharp.")
    targets = [
        (OG / "home.svg", OG / "home.png", 1200, 630),
        (OG / "sources.svg", OG / "sources.png", 1200, 630),
        (STATIC / "favicon.svg", STATIC / "logo.png", 512, 512),
        (STATIC / "favicon.svg", STATIC / "apple-touch-icon.png", 180, 180),
        (STATIC / "favicon.svg", STATIC / "favicon-48.png", 48, 48),
    ]
    jobs = [
        {
            "source": str(source), "output": str(output), "width": width, "height": height,
            # Render oversized before downsampling for clean small curves and stems.
            "density": round(max(144, width / (64 if source.name == "favicon.svg" else 1200) * 144)),
        }
        for source, output, width, height in targets
    ]
    renderer = """
const sharp = require(process.argv[1]);
(async () => {
  for (const job of JSON.parse(process.argv[2])) {
    await sharp(job.source, { density: job.density })
      .resize(job.width, job.height, { fit: 'fill' })
      .removeAlpha()
      .png({ compressionLevel: 9, adaptiveFiltering: false })
      .toFile(job.output);
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    subprocess.run([node, "-e", renderer, sharp_module, json.dumps(jobs)], check=True)
    for _, output, _, _ in targets:
        print(output.relative_to(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raster-only", action="store_true", help="Render existing outlined SVGs; no font dependencies.")
    parser.add_argument("--sharp-module", default="sharp", help="Node-resolvable sharp package name or absolute package path.")
    args = parser.parse_args()
    if not args.raster_only:
        write_sources()
    render_pngs(args.sharp_module)


if __name__ == "__main__":
    main()
