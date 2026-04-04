#!/usr/bin/env python3
"""Generate 1200x630 social card PNG images for books.venkateshrao.com."""

import sys
import textwrap
from pathlib import Path

# Import shared helpers from build_catalog
sys.path.insert(0, str(Path(__file__).parent))
from build_catalog import (
    load_blurbs, resolve_thumbnail, get_slug, slugify,
    DOCS_DIR, REGISTRY, SOCIAL_DIR, BASE_URL,
    _make_catalog_groups, CATALOG_SECTIONS, SERIES_PAGE_MIN_VOLUMES,
)

import json
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
BG     = (252, 249, 244)
TEXT   = (28, 20, 8)
MUTED  = (122, 106, 82)
ACCENT = (92, 58, 16)
BORDER = (224, 213, 192)
WHITE  = (255, 255, 255)

CARD_W = 1200
CARD_H = 630

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_DIR = Path("/System/Library/Fonts/Supplemental")

def _load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    # fallback to default
    return ImageFont.load_default()

font_title_lg = _load_font("Georgia Bold.ttf", 52)
font_title_md = _load_font("Georgia Bold.ttf", 42)
font_body     = _load_font("Georgia.ttf", 22)
font_label    = _load_font("Georgia.ttf", 18)

# ---------------------------------------------------------------------------
# Cover loader
# ---------------------------------------------------------------------------

def load_cover(thumbnail_rel: str, w: int, h: int) -> Image.Image:
    """Load and fit a cover image into a w×h box. Returns solid BORDER rect on failure."""
    fallback = Image.new("RGB", (w, h), BORDER)
    if not thumbnail_rel:
        return fallback
    path = DOCS_DIR / thumbnail_rel
    if not path.exists():
        return fallback
    suffix = path.suffix.lower()
    if suffix == ".svg":
        return fallback
    try:
        img = Image.open(str(path)).convert("RGB")
    except Exception:
        return fallback

    # Fit/crop preserving aspect ratio, centered
    img_w, img_h = img.size
    scale = max(w / img_w, h / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    img = img.crop((left, top, left + w, top + h))
    return img


# ---------------------------------------------------------------------------
# Text drawing helpers
# ---------------------------------------------------------------------------

def draw_wrapped(draw: ImageDraw.Draw, text: str, x: int, y: int,
                 font: ImageFont.FreeTypeFont, fill: tuple,
                 max_width_chars: int, line_height: int) -> int:
    """Draw wrapped text, return the y position after the last line."""
    lines = textwrap.wrap(text, width=max_width_chars)
    if not lines:
        lines = [""]
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


# ---------------------------------------------------------------------------
# Book detail card
# ---------------------------------------------------------------------------

def make_book_card(book: dict, thumbnail_rel: str) -> Image.Image:
    img = Image.new("RGB", (CARD_W, CARD_H), BG)
    draw = ImageDraw.Draw(img)

    # Cover image: 380×560 at (30, 35)
    cover_w, cover_h = 380, 560
    cover_x, cover_y = 30, 35
    cover = load_cover(thumbnail_rel, cover_w, cover_h)
    img.paste(cover, (cover_x, cover_y))

    # Thin vertical divider at x=440
    draw.line([(440, 30), (440, 600)], fill=BORDER, width=1)

    # Text block starting at x=470
    tx = 470

    # Author label
    draw.text((tx, 60), "VENKATESH RAO", font=font_label, fill=MUTED)

    # Series · label
    series = book.get("series")
    label = book.get("label")
    series_y = 60 + 26 + 19  # below author label with gap
    if series or label:
        parts = []
        if series:
            parts.append(series)
        if label:
            parts.append(label)
        series_text = " · ".join(parts)
        draw.text((tx, series_y), series_text, font=font_label, fill=MUTED)
        title_y = series_y + 26 + 19
    else:
        title_y = series_y

    # Title
    title = book["title"]
    if len(title) <= 30:
        title_font = font_title_lg
        wrap_chars = 28
        line_h = 58
    else:
        title_font = font_title_md
        wrap_chars = 35
        line_h = 50

    after_title_y = draw_wrapped(draw, title, tx, title_y, title_font, TEXT, wrap_chars, line_h)

    # Blurb
    blurb = book.get("blurb") or ""
    blurb_y = after_title_y + 25
    draw_wrapped(draw, blurb, tx, blurb_y, font_body, MUTED, 55, 32)

    # Footer URL
    draw.text((tx, 585), "books.venkateshrao.com", font=font_label, fill=ACCENT)

    return img


# ---------------------------------------------------------------------------
# Catalog card
# ---------------------------------------------------------------------------

def make_catalog_card(visible: list, thumbs: dict) -> Image.Image:
    img = Image.new("RGB", (CARD_W, CARD_H), BG)
    draw = ImageDraw.Draw(img)

    # 2×2 grid of first 4 books, each cover 240×360
    positions = [(20, 30), (275, 30), (20, 240), (275, 240)]
    cover_w, cover_h = 240, 360
    for i, (cx, cy) in enumerate(positions):
        if i >= len(visible):
            break
        book = visible[i]
        thumb_rel = thumbs[book["id"]]
        cover = load_cover(thumb_rel, cover_w, cover_h)
        img.paste(cover, (cx, cy))

    # Right side text block
    rx = 570
    draw.text((rx, 140), "Books by", font=font_body, fill=MUTED)
    draw.text((rx, 175), "Venkatesh Rao", font=font_title_lg, fill=TEXT)
    draw.text((rx, 260), f"{len(visible)} books", font=font_body, fill=MUTED)
    draw.text((rx, 300), "fiction · essays · longform", font=font_label, fill=MUTED)
    draw.text((rx, 585), "books.venkateshrao.com", font=font_label, fill=ACCENT)

    return img


# ---------------------------------------------------------------------------
# Series card
# ---------------------------------------------------------------------------

def make_series_card(series_name: str, series_desc: str, volumes: list, thumbs: dict) -> Image.Image:
    img = Image.new("RGB", (CARD_W, CARD_H), BG)
    draw = ImageDraw.Draw(img)

    n_covers = min(len(volumes), 4)
    cover_w, cover_h = 210, 315
    gap = 10
    total_cover_area_w = n_covers * cover_w + (n_covers - 1) * gap
    cover_area_right = 30 + total_cover_area_w

    # Center covers vertically
    cover_top = (CARD_H - cover_h) // 2

    for i, book in enumerate(volumes[:4]):
        cx = 30 + i * (cover_w + gap)
        thumb_rel = thumbs.get(book["id"]) or ""
        cover = load_cover(thumb_rel, cover_w, cover_h)
        img.paste(cover, (cx, cover_top))

    # Right side text
    rx = cover_area_right + 40

    # Series name
    after_name_y = draw_wrapped(draw, series_name, rx, 150, font_title_lg, TEXT, 28, 62)

    # Series desc
    desc_y = max(after_name_y + 10, 220)
    draw_wrapped(draw, series_desc, rx, desc_y, font_body, MUTED, 40, 30)

    # Volume count
    draw.text((rx, 350), f"{len(volumes)} volumes", font=font_label, fill=MUTED)

    # Footer URL
    draw.text((rx, 585), "books.venkateshrao.com", font=font_label, fill=ACCENT)

    return img


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import json
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))

    blurbs = load_blurbs()
    for book in data["books"]:
        if book["id"] in blurbs:
            book["blurb"] = blurbs[book["id"]]

    visible = [
        book for book in data["books"]
        if any(
            ed.get("display") is True
            for ed in (book.get("editions") or {}).values()
            if ed
        )
    ]

    thumbs = {book["id"]: resolve_thumbnail(book) for book in visible}
    groups = _make_catalog_groups(visible)
    series_groups = [g for g in groups if g["type"] == "series"]

    SOCIAL_DIR.mkdir(exist_ok=True)

    # --- Book detail cards ---
    for book in visible:
        thumb_rel = thumbs[book["id"]]
        card = make_book_card(book, thumb_rel)
        out_path = SOCIAL_DIR / f"{book['id']}.png"
        card.save(str(out_path), "PNG")
        print(f"Social card → docs/social/{book['id']}.png")

    # --- Catalog card ---
    catalog_card = make_catalog_card(visible, thumbs)
    out_path = SOCIAL_DIR / "catalog.png"
    catalog_card.save(str(out_path), "PNG")
    print(f"Social card → docs/social/catalog.png")

    # --- Series cards ---
    for g in series_groups:
        series_slug = g["slug"]
        series_card = make_series_card(g["name"], g.get("desc") or "", g["books"], thumbs)
        out_path = SOCIAL_DIR / f"series-{series_slug}.png"
        series_card.save(str(out_path), "PNG")
        print(f"Social card → docs/social/series-{series_slug}.png")

    total = len(visible) + 1 + len(series_groups)
    print(f"\nDone. {total} social cards written to docs/social/")


if __name__ == "__main__":
    main()
