#!/usr/bin/env python3
"""
build_catalog.py — Generate docs/index.html, book detail pages, and series pages from registry.json.

URL structure:
  /                         — catalog
  /{slug}/                  — book detail page (generated)
  /{slug}/read/{entry}      — online reading experience (synced by sync.py)
  /series/{series-slug}/    — series home (generated, for series with >= 2 visible volumes)

Usage:
    python3 build_catalog.py            # generate all pages
    python3 build_catalog.py --dry-run  # print catalog HTML to stdout only
"""

import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
PUBLISHING_DIR = SCRIPT_DIR.parent
DOCS_DIR = SCRIPT_DIR / "docs"
REGISTRY = SCRIPT_DIR / "registry.json"
CATALOG_FILE = DOCS_DIR / "index.html"
PLACEHOLDER_THUMB = "thumbnails/coming-soon.svg"
THUMBNAIL_CONVENTIONS = ["cover.svg", "cover.jpg", "cover.png", "thumbnail.jpg", "thumbnail.png"]
SERIES_PAGE_MIN_VOLUMES = 2


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


def get_slug(book: dict) -> str:
    """
    Top-level URL slug for this book. For online books, uses editions.online.slug.
    For buy-only books, falls back to book id.
    """
    online = (book.get("editions") or {}).get("online") or {}
    return online.get("slug") or book["id"]


# ---------------------------------------------------------------------------
# Thumbnail resolution (preserved from prior version)
# ---------------------------------------------------------------------------

def _book_meta_thumbnail(book: dict) -> Optional[Path]:
    status_md_rel = book.get("status_md")
    if not status_md_rel:
        return None
    project_dir = PUBLISHING_DIR / Path(status_md_rel).parent
    meta_file = project_dir / "book_meta.json"
    if not meta_file.exists():
        return None
    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        thumb_rel = meta.get("thumbnail")
        if not thumb_rel:
            return None
        thumb_src = project_dir / thumb_rel
        return thumb_src if thumb_src.exists() else None
    except (json.JSONDecodeError, OSError):
        return None


def resolve_thumbnail(book: dict) -> str:
    """Returns thumbnail path relative to docs/."""
    book_id = book["id"]
    slug = get_slug(book)
    online = (book.get("editions") or {}).get("online") or {}
    has_online = bool(online.get("slug"))

    if book.get("thumbnail"):
        if (DOCS_DIR / book["thumbnail"]).exists():
            return book["thumbnail"]

    if not has_online:
        thumb_path = _book_meta_thumbnail(book)
        if thumb_path:
            dest_name = f"{book_id}{thumb_path.suffix}"
            dest_path = DOCS_DIR / "thumbnails" / dest_name
            if not dest_path.exists():
                shutil.copy2(str(thumb_path), str(dest_path))
            return f"thumbnails/{dest_name}"

    # Convention files now live in docs/{slug}/read/ (synced content)
    if has_online:
        read_dir = DOCS_DIR / slug / "read"
        for name in THUMBNAIL_CONVENTIONS:
            if (read_dir / name).exists():
                return f"{slug}/read/{name}"

    return PLACEHOLDER_THUMB


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------

def page_html(*, title: str, body: str, root_url: str, description: str = "") -> str:
    """
    Complete HTML page.
    root_url: path from this page back to docs/ root.
      ""     for catalog (docs/index.html)
      "../"  for detail pages (docs/{slug}/index.html)
      "../../" for series pages (docs/series/{slug}/index.html)
    """
    css = root_url + "style.css"
    desc = description or "Books by Venkatesh Rao."
    home = root_url if root_url else "."
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{_esc(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="description" content="{_esc(desc)}"/>
<meta property="og:title" content="{_esc(title)}"/>
<meta property="og:description" content="{_esc(desc)}"/>
<meta property="og:type" content="website"/>
<link rel="stylesheet" href="{css}"/>
</head>
<body>
<header class="site-header">
  <h1><a class="site-title-link" href="{home}">Books by Venkatesh Rao</a></h1>
  <p class="byline"><a href="https://venkateshrao.com">venkateshrao.com</a></p>
</header>
<div class="main-wrapper">
{body}
</div>
<footer class="site-footer">
  <p>Copyright &copy; Venkatesh Rao &mdash; <a href="{home}">All Books</a></p>
</footer>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Shared: buy link helpers
# ---------------------------------------------------------------------------

def _get_buy_links(book: dict) -> tuple:
    """Returns (buy_print_url, buy_ebook_url) falling back to legacy editions."""
    editions = book.get("editions") or {}
    ebook_ed = editions.get("ebook") or {}
    print_ed = editions.get("print") or {}
    buy_ebook = ebook_ed.get("buy_link") if ebook_ed else None
    buy_print = print_ed.get("buy_link") if print_ed else None

    for leg in (book.get("legacy_editions") or []):
        leg_eds = leg.get("editions") or {}
        if not buy_ebook:
            for key in ("ebook", "ebook_kindle"):
                le = leg_eds.get(key)
                if le and le.get("buy_link"):
                    buy_ebook = le["buy_link"]
                    break
        if not buy_print:
            lp = leg_eds.get("print")
            if lp and lp.get("buy_link"):
                buy_print = lp["buy_link"]

    return buy_print, buy_ebook


def _get_read_info(book: dict) -> tuple:
    """Returns (slug, entry_point) if book has an online edition, else (None, None)."""
    online = (book.get("editions") or {}).get("online") or {}
    slug = online.get("slug")
    if not slug:
        return None, None
    entry = online.get("entry_point") or "index.html"
    return slug, entry


# ---------------------------------------------------------------------------
# Book card (catalog and series pages)
# ---------------------------------------------------------------------------

def render_card(book: dict, thumbnail_rel: str, detail_url: str, root_url: str = "") -> str:
    title = book["title"]
    blurb = book.get("blurb") or ""
    series = book.get("series")
    label = book.get("label")

    series_label_html = ""
    if series or label:
        parts = []
        if series:
            parts.append(_esc(series))
        if label:
            parts.append(_esc(label))
        series_label_html = (
            f'\n        <div class="book-series-label">'
            f'{"&thinsp;&middot;&thinsp;".join(parts)}'
            f"</div>"
        )

    thumb = root_url + thumbnail_rel
    cover_html = (
        f'<a class="book-cover-link" href="{detail_url}">\n'
        f'          <img class="book-cover" src="{thumb}" alt="{_esc(title)}"/>\n'
        f"        </a>"
    )
    title_html = f'<h2 class="book-title"><a href="{detail_url}">{_esc(title)}</a></h2>'

    # Links
    slug, entry = _get_read_info(book)
    buy_print, buy_ebook = _get_buy_links(book)
    links = []
    if slug:
        read_url = f"{root_url}{slug}/read/{entry}"
        links.append(f'<a class="read-link" href="{read_url}">Read online &rarr;</a>')
    if buy_print:
        links.append(f'<a class="buy-link" href="{_esc(buy_print)}">Buy Print</a>')
    if buy_ebook:
        links.append(f'<a class="buy-link" href="{_esc(buy_ebook)}">Buy Ebook</a>')
    if not links:
        links.append('<span class="edition-soon">Coming soon</span>')
    links_html = (
        '<div class="book-links">\n          '
        + "\n          ".join(links)
        + "\n        </div>"
    )

    return f"""\
      <article class="book-card">
        {cover_html}
        <div class="book-info">{series_label_html}
          {title_html}
          <p class="book-desc">{_esc(blurb)}</p>
          {links_html}
        </div>
      </article>"""


# ---------------------------------------------------------------------------
# Detail page  (lives at docs/{slug}/index.html)
# ---------------------------------------------------------------------------

def render_detail_page(book: dict, thumbnail_rel: str) -> str:
    ROOT = "../"   # docs/{slug}/ → docs/
    title = book["title"]
    blurb = book.get("blurb") or ""
    series = book.get("series")
    label = book.get("label")

    # Breadcrumb
    crumbs = [f'<a href="{ROOT}">All Books</a>']
    series_slug = None
    if series:
        series_slug = slugify(series)
        crumbs.append(f'<a href="{ROOT}series/{series_slug}/">{_esc(series)}</a>')
    crumbs.append(_esc(title))
    breadcrumb = (
        f'<nav class="breadcrumb" aria-label="Breadcrumb">'
        f'{" &rsaquo; ".join(crumbs)}'
        f"</nav>"
    )

    # Series label
    series_label_html = ""
    if series or label:
        parts = []
        if series:
            parts.append(_esc(series))
        if label:
            parts.append(_esc(label))
        series_label_html = (
            f'<div class="book-series-label">'
            f'{"&thinsp;&middot;&thinsp;".join(parts)}'
            f"</div>"
        )

    # Cover: thumbnail_rel is relative to docs/, so prefix with ROOT="../"
    thumb = ROOT + thumbnail_rel

    # Links — reading is in the sibling read/ dir, not via root
    slug, entry = _get_read_info(book)
    buy_print, buy_ebook = _get_buy_links(book)
    links = []
    if slug and entry:
        links.append(f'<a class="read-link" href="read/{entry}">Read online &rarr;</a>')
    if buy_print:
        links.append(f'<a class="buy-link" href="{_esc(buy_print)}">Buy Print</a>')
    if buy_ebook:
        links.append(f'<a class="buy-link" href="{_esc(buy_ebook)}">Buy Ebook</a>')
    if not links:
        links.append('<span class="edition-soon">Coming soon</span>')
    links_html = (
        '<div class="book-links">\n        '
        + "\n        ".join(links)
        + "\n      </div>"
    )

    # Series back link
    series_link_html = ""
    if series and series_slug:
        series_link_html = (
            f'<p class="series-back-link">'
            f'Part of the <a href="{ROOT}series/{series_slug}/">{_esc(series)}</a> series'
            f"</p>"
        )

    body = f"""\
  {breadcrumb}
  <div class="book-detail">
    <div class="book-detail-cover">
      <img src="{thumb}" alt="{_esc(title)}"/>
    </div>
    <div class="book-detail-info">
      {series_label_html}
      <h1 class="book-detail-title">{_esc(title)}</h1>
      <p class="book-detail-desc">{_esc(blurb)}</p>
      {links_html}
      {series_link_html}
    </div>
  </div>"""

    page_title = f"{title} — {series} {label}" if (series and label) else title
    return page_html(title=page_title, body=body, root_url=ROOT, description=blurb)


# ---------------------------------------------------------------------------
# Series page  (lives at docs/series/{series-slug}/index.html)
# ---------------------------------------------------------------------------

def render_series_page(series_name: str, series_desc: str, volumes: list, thumbs: dict) -> str:
    ROOT = "../../"   # docs/series/{slug}/ → docs/

    breadcrumb = (
        f'<nav class="breadcrumb" aria-label="Breadcrumb">'
        f'<a href="{ROOT}">All Books</a> &rsaquo; {_esc(series_name)}'
        f"</nav>"
    )

    cards = []
    for book in volumes:
        book_slug = get_slug(book)
        detail_url = f"{ROOT}{book_slug}/"
        cards.append(render_card(book, thumbs[book["id"]], detail_url, root_url=ROOT))
    grid_html = "\n\n".join(cards)

    body = f"""\
  {breadcrumb}
  <div class="series-intro">
    <h1 class="series-intro-name">{_esc(series_name)}</h1>
    <p class="series-intro-desc">{_esc(series_desc)}</p>
  </div>
  <div class="book-grid">
{grid_html}
  </div>"""

    return page_html(
        title=f"{series_name} — Books by Venkatesh Rao",
        body=body,
        root_url=ROOT,
        description=series_desc,
    )


# ---------------------------------------------------------------------------
# Catalog  (docs/index.html)
# ---------------------------------------------------------------------------

def render_catalog_body(groups: list, thumbs: dict) -> str:
    sections = []

    for group in groups:
        if group["type"] == "series":
            cards = []
            for book in group["books"]:
                book_slug = get_slug(book)
                detail_url = f"{book_slug}/"
                cards.append(render_card(book, thumbs[book["id"]], detail_url, root_url=""))
            grid = "\n\n".join(cards)

            view_link = ""
            if group.get("has_series_page"):
                view_link = (
                    f' <a class="series-view-link" href="series/{group["slug"]}/">'
                    f"View all &rarr;</a>"
                )

            sections.append(f"""\
  <section class="book-series">
    <div class="series-header">
      <div class="series-name">{_esc(group["name"])}{view_link}</div>
      <div class="series-desc">{_esc(group["desc"])}</div>
    </div>
    <div class="book-grid">
{grid}
    </div>
  </section>""")

        else:  # standalone
            cards = []
            for book in group["books"]:
                book_slug = get_slug(book)
                detail_url = f"{book_slug}/"
                cards.append(render_card(book, thumbs[book["id"]], detail_url, root_url=""))
            grid = "\n\n".join(cards)
            sections.append(f"""\
  <div class="book-grid standalone-grid">
{grid}
  </div>""")

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def build(dry_run: bool = False) -> str:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))

    # Filter to visible books
    visible = [
        book for book in data["books"]
        if any(
            ed.get("display") is True
            for ed in (book.get("editions") or {}).values()
            if ed
        )
    ]
    visible.sort(key=lambda b: b.get("sort_order", 9999))

    # Resolve all thumbnails up front
    thumbs = {book["id"]: resolve_thumbnail(book) for book in visible}

    # Group by series (preserving sort order) and standalone
    series_map: dict = defaultdict(list)
    standalone = []
    seen_series: list = []
    for book in visible:
        s = book.get("series")
        if s:
            series_map[s].append(book)
            if s not in seen_series:
                seen_series.append(s)
        else:
            standalone.append(book)

    series_with_page = {
        name for name, vols in series_map.items()
        if len(vols) >= SERIES_PAGE_MIN_VOLUMES
    }

    # Build catalog groups
    groups = []
    for series_name in seen_series:
        vols = series_map[series_name]
        groups.append({
            "type": "series",
            "name": series_name,
            "slug": slugify(series_name),
            "desc": vols[0].get("series_desc") or "",
            "books": vols,
            "has_series_page": series_name in series_with_page,
        })
    if standalone:
        groups.append({"type": "standalone", "books": standalone})

    # --- Catalog ---
    catalog_body = render_catalog_body(groups, thumbs)
    catalog_html = page_html(
        title="Books by Venkatesh Rao",
        body=catalog_body,
        root_url="",
        description="Books by Venkatesh Rao — some available free to read online.",
    )

    if dry_run:
        return catalog_html

    CATALOG_FILE.write_text(catalog_html, encoding="utf-8")
    card_count = catalog_html.count('class="book-card"')
    print(f"Catalog → {CATALOG_FILE} ({card_count} cards)")

    # --- Detail pages (docs/{slug}/index.html) ---
    for book in visible:
        book_slug = get_slug(book)
        slug_dir = DOCS_DIR / book_slug
        slug_dir.mkdir(exist_ok=True)
        (slug_dir / "index.html").write_text(
            render_detail_page(book, thumbs[book["id"]]), encoding="utf-8"
        )
    print(f"Detail pages → docs/{{slug}}/ ({len(visible)} books)")

    # --- Series pages (docs/series/{slug}/index.html) ---
    series_dir = DOCS_DIR / "series"
    series_dir.mkdir(exist_ok=True)
    for series_name in series_with_page:
        vols = series_map[series_name]
        series_slug = slugify(series_name)
        series_desc = vols[0].get("series_desc") or ""
        slug_dir = series_dir / series_slug
        slug_dir.mkdir(exist_ok=True)
        (slug_dir / "index.html").write_text(
            render_series_page(series_name, series_desc, vols, thumbs), encoding="utf-8"
        )
    print(f"Series pages → docs/series/ ({len(series_with_page)} series)")

    return catalog_html


def main():
    dry_run = "--dry-run" in sys.argv
    html = build(dry_run=dry_run)
    if dry_run:
        print(html)


if __name__ == "__main__":
    main()
