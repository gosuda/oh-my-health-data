# SEO image generation

- `static/og/home.svg` / `static/og/home.png`: home-page share card, 1200 × 630.
- `static/og/sources.svg` / `static/og/sources.png`: sources-page share card, 1200 × 630.
- The generator also writes `static/favicon.svg`, `static/logo.png` (512 × 512),
  `static/apple-touch-icon.png` (180 × 180), and `static/favicon-48.png` (48 × 48).

Edit `scripts/generate_seo_images.py` to change copy or layout. It uses the
existing Noto Sans KR and Barlow Condensed files in `node_modules`, then converts
all letters into SVG paths. The SVG and PNG outputs have no system-font or
external-image dependency. Icon geometry follows `src/lib/Mark.svelte`.

The generator is an optional authoring tool; the website build serves the
checked-in files without running Python or loading an image library.

## Regenerate SVG and PNG

Requires Python 3, Node.js, fonttools with WOFF2 support, and sharp. Install these
authoring tools outside the repository; they are not application dependencies.

```sh
npm ci
python3 -m venv /tmp/oh-my-health-data-seo-tools
/tmp/oh-my-health-data-seo-tools/bin/pip install 'fonttools[woff]==4.66.1'
npm install --prefix /tmp/oh-my-health-data-seo-tools sharp@0.35.5
/tmp/oh-my-health-data-seo-tools/bin/python scripts/generate_seo_images.py \
  --sharp-module /tmp/oh-my-health-data-seo-tools/node_modules/sharp
```

To render the existing SVGs without fontTools or the font-source packages:

```sh
python3 scripts/generate_seo_images.py --raster-only \
  --sharp-module /tmp/oh-my-health-data-seo-tools/node_modules/sharp
```

Use sharp's SVG renderer: some ImageMagick SVG builds misrender the transforms
and strokes used in these cards.
