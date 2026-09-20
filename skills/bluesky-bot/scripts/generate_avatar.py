#!/usr/bin/env python3
"""Generate original vector bot avatars. No network, account access, or credentials."""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import io
import tempfile
from pathlib import Path

MOTIFS = {
    'house': '<path d="M245 410V735Q245 770 280 770H720Q755 770 755 735V410 M190 440L500 200L810 440"/><path stroke-width="24" d="M360 770V650H640V770 M360 705H640"/>',
    'buoy': '<path d="M410 590L435 280Q500 240 565 280L590 590 M435 280V210H565V280 M355 590H645L610 690H390Z"/><path stroke-width="28" d="M200 760Q275 690 350 760T500 760T650 760T800 760"/>',
    'parcel': '<path d="M270 250H730V730H270Z"/><path stroke-width="28" d="M190 810H810 M190 185V810"/><path stroke-width="20" d="M270 650H730 M645 250V730"/>',
    'bike': '<circle cx="310" cy="645" r="140"/><circle cx="690" cy="645" r="140"/><path stroke-width="28" d="M310 645L420 425L540 645H310 M420 425H620L540 645 M620 425L690 645 M620 425L590 335H675 M380 415H455"/>',
}


def color(value: str) -> str:
    if re.fullmatch(r'#[0-9a-fA-F]{6}', value) is None:
        raise argparse.ArgumentTypeError('Use a six-digit hex color, for example #41B6E6')
    return value.upper()


def svg_art(motif: str, name: str, ink: str, accent: str, background: str, star: bool = False) -> str:
    cx, cy, radius = (500, 245, 75) if motif == 'bike' else (500, 460, 105)
    points = []
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        r = radius if i % 2 == 0 else radius * 3 / 7
        points.append(f'{cx + r * math.cos(angle):.3f},{cy + r * math.sin(angle):.3f}')
    shapes = re.sub(r'<(path|circle)\b', lambda m: m.group(0) + f' stroke="{ink}" fill="none" stroke-linecap="round" stroke-linejoin="round"', MOTIFS[motif])
    shapes = re.sub(r'<(?:path|circle)\b[^>]*>', lambda m: m.group(0) if 'stroke-width=' in m.group(0) else m.group(0).replace('/>', ' stroke-width="48"/>'), shapes)
    desc = f'A {motif} outline' + (' with a six-point civic star' if star else '') + ' on a solid background.'
    star_svg = f'<polygon points="{" ".join(points)}" fill="{accent}"/>' if star else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1000 1000" role="img" aria-labelledby="title description">
<title id="title">{html.escape(name)}</title><desc id="description">{desc}</desc>
<rect width="1000" height="1000" fill="{background}"/>
{shapes}
{star_svg}
</svg>
'''


def preview(name: str, png: bool = False) -> str:
    title = html.escape(name)
    asset = 'avatar.png' if png else 'avatar.svg'
    label = 'PNG upload' if png else 'SVG master'
    rows = ''.join(f'<figure><img src="{asset}" width="{s}" height="{s}" alt="{title} avatar"><figcaption>{s} px</figcaption></figure>' for s in (32, 48, 96, 320))
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} — avatar review</title>
<style>body{{font:16px system-ui;margin:32px;background:#eee;color:#17212b}}h1{{font-size:24px}}section{{padding:24px;display:flex;gap:24px;align-items:center;flex-wrap:wrap;border-radius:12px;margin:20px 0}}.light{{background:#fff}}.dark{{background:#17212b;color:#fff}}figure{{margin:0;text-align:center;max-width:100%}}img{{display:block;border-radius:50%;max-width:100%;height:auto}}figcaption{{margin-top:12px;font-size:13px}}</style>
<h1>{title}</h1><p>Inspect the {label} in circular crops at feed and profile sizes. <a href="avatar.svg">Open SVG master</a>.</p><section class="light">{rows}</section><section class="dark">{rows}</section></html>'''


def export_png(svg_path: Path, png_path: Path) -> None:
    try:
        import cairosvg
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError('--png requires CairoSVG and Pillow; use uv run --with cairosvg --with pillow python SCRIPT ... --png') from exc
    raster = cairosvg.svg2png(url=str(svg_path), output_width=2048, output_height=2048)
    with Image.open(io.BytesIO(raster)) as source:
        source.resize((1024, 1024), Image.Resampling.LANCZOS).save(png_path, optimize=True)
    size = png_path.stat().st_size
    if size > 1_000_000:
        raise RuntimeError(f'PNG is {size} bytes; simplify or re-encode below the profile limit')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--motif', choices=tuple(MOTIFS), default='house')
    parser.add_argument('--name', required=True)
    parser.add_argument('--ink', type=color, default='#41B6E6')
    parser.add_argument('--accent', type=color, default='#E4002B')
    parser.add_argument('--background', type=color, default='#FFFFFF')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--png', action='store_true')
    parser.add_argument('--star', action='store_true', help='Add an optional six-point civic accent')
    parser.add_argument('--force', action='store_true', help='Replace previously generated files in this output directory')
    args = parser.parse_args()
    out = args.out.expanduser().resolve()
    names = ['avatar.svg', 'avatar-preview.html', 'avatar-parameters.json'] + (['avatar.png'] if args.png else [])
    if not args.force and any((out / n).exists() for n in names):
        parser.error('Output files already exist; use another --out or --force to replace them')
    if (out / 'avatar.png').exists() and not args.png:
        parser.error('An avatar.png exists here; use --png to regenerate it with the SVG, or choose a new directory')
    out.mkdir(parents=True, exist_ok=True)
    # Stage all outputs so failed rasterization cannot leave a misleading partial update.
    with tempfile.TemporaryDirectory(prefix='.avatar-', dir=out) as directory:
        stage = Path(directory)
        (stage / 'avatar.svg').write_text(svg_art(args.motif, args.name, args.ink, args.accent, args.background, args.star), encoding='utf-8')
        (stage / 'avatar-preview.html').write_text(preview(args.name, args.png), encoding='utf-8')
        values = {'motif': args.motif, 'name': args.name, 'ink': args.ink, 'accent': args.accent, 'background': args.background, 'star': args.star, 'viewbox': 1000, 'output_pixels': 1024}
        (stage / 'avatar-parameters.json').write_text(json.dumps(values, indent=2) + '\n', encoding='utf-8')
        if args.png:
            try:
                export_png(stage / 'avatar.svg', stage / 'avatar.png')
            except (RuntimeError, OSError) as exc:
                parser.exit(1, f'Avatar export failed: {exc}\n')
        for name in names:
            (stage / name).replace(out / name)
    print(f'Generated {args.motif} avatar in {out}')


if __name__ == '__main__':
    main()
