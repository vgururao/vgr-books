#!/usr/bin/env python3
"""
build_catalog.py — Generate docs/index.html, book detail pages, and series pages from registry.json.

URL structure:
  /                         — catalog
  /{slug}/                  — book detail page (generated)
  /{slug}/read/{entry}      — online reading experience (synced by sync.py)
  /series/{series-slug}/    — series home (generated, for series with >= 2 visible volumes)

Catalog section order is controlled by CATALOG_SECTIONS below.

Usage:
    python3 build_catalog.py            # generate all pages
    python3 build_catalog.py --dry-run  # print catalog HTML to stdout only
"""

import datetime
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
PUBLISHING_DIR = SCRIPT_DIR.parent
DOCS_DIR = SCRIPT_DIR / "docs"
REGISTRY = SCRIPT_DIR / "registry.json"
BLURBS_FILE = SCRIPT_DIR / "blurbs.md"
CATALOG_FILE = DOCS_DIR / "index.html"
PLACEHOLDER_THUMB = "thumbnails/coming-soon.svg"
THUMBNAIL_CONVENTIONS = ["cover.svg", "cover.jpg", "cover.png", "thumbnail.jpg", "thumbnail.png"]

BASE_URL = "https://books.venkateshrao.com"
SOCIAL_DIR = DOCS_DIR / "social"

# ---------------------------------------------------------------------------
# Catalog section order — edit this to reorder the catalog.
# Each inner list is one section (rendered as series block or plain grid).
# Books not listed here are appended as a final standalone section.
# ---------------------------------------------------------------------------
CATALOG_SECTIONS = [
    ["configurancy-tempo", "gervais-principle", "be-slightly-evil"],
    ["artofgig-vol1", "artofgig-vol2", "artofgig-vol3"],
    ["breakingsmart", "twitterbook", "crash-early-crash-often"],
    ["rust-age-vol1", "rust-age-vol2", "rust-age-vol3", "rust-age-vol4"],
    ["breaking-smart-newsletter", "mediocratopia"],
]

SERIES_PAGE_MIN_VOLUMES = 2

# Books tagged "ribbonfarm" regardless of series
RIBBONFARM_IDS = {
    "rust-age-vol1", "rust-age-vol2", "rust-age-vol3", "rust-age-vol4",
    "gervais-principle", "crash-early-crash-often",
}

# Ordered tag list for the filter dropdown (only shown if books exist for that tag)
TAG_ORDER = ["ribbonfarm", "art-of-gig", "rust-age", "configurancy"]
TAG_LABELS = {
    "ribbonfarm":   "Ribbonfarm",
    "art-of-gig":   "Art of Gig",
    "rust-age":     "Rust Age",
    "configurancy": "Configurancy",
}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# ---------------------------------------------------------------------------
# Blurb loading — reads blurbs.md, overrides registry.json blurb fields
# ---------------------------------------------------------------------------

def load_blurbs() -> dict:
    """Parse blurbs.md → {book_id: blurb_text}. Returns empty dict if file absent."""
    if not BLURBS_FILE.exists():
        return {}
    blurbs: dict = {}
    current_id: Optional[str] = None
    current_lines: list = []

    def _flush():
        if current_id and current_lines:
            blurbs[current_id] = " ".join(" ".join(current_lines).split())

    for line in BLURBS_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            _flush()
            # ID is the first whitespace-delimited token after "## "
            header = line[3:].strip()
            current_id = header.split()[0] if header else None
            current_lines = []
        elif current_id is not None:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and stripped != "---":
                current_lines.append(stripped)
    _flush()
    return blurbs


def get_tags(book: dict) -> list:
    """Return list of tag slugs for a book (series tag + explicit collection tags)."""
    tags = []
    if book.get("series"):
        tags.append(slugify(book["series"]))
    if book["id"] in RIBBONFARM_IDS:
        tags.append("ribbonfarm")
    return tags


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


def get_slug(book: dict) -> str:
    online = (book.get("editions") or {}).get("online") or {}
    return online.get("slug") or book["id"]


# ---------------------------------------------------------------------------
# Thumbnail resolution
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

    if has_online:
        read_dir = DOCS_DIR / slug / "read"
        for name in THUMBNAIL_CONVENTIONS:
            if (read_dir / name).exists():
                return f"{slug}/read/{name}"

    return PLACEHOLDER_THUMB


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------

def page_html(*, title: str, body: str, root_url: str, description: str = "",
              canonical_url: str = "", og_image: str = "",
              extra_head: str = "", extra_body_end: str = "") -> str:
    css = root_url + "style.css"
    desc = description or "Books by Venkatesh Rao."
    home = root_url if root_url else "."

    social_tags = ""
    if og_image:
        social_tags += f'\n<meta property="og:image" content="{_esc(og_image)}"/>'
        social_tags += '\n<meta property="og:image:width" content="1200"/>'
        social_tags += '\n<meta property="og:image:height" content="630"/>'
    if canonical_url:
        social_tags += f'\n<meta property="og:url" content="{_esc(canonical_url)}"/>'
        social_tags += f'\n<link rel="canonical" href="{_esc(canonical_url)}"/>'
    if og_image or canonical_url:
        social_tags += f'\n<meta name="twitter:card" content="summary_large_image"/>'
        social_tags += f'\n<meta name="twitter:title" content="{_esc(title)}"/>'
        social_tags += f'\n<meta name="twitter:description" content="{_esc(desc)}"/>'
    if og_image:
        social_tags += f'\n<meta name="twitter:image" content="{_esc(og_image)}"/>'

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
<meta property="og:type" content="website"/>{social_tags}
<link rel="stylesheet" href="{css}"/>{extra_head}
</head>
<body>
<header class="site-header">
  <div class="site-header-inner">
    <a class="back-link" href="https://venkateshrao.com">&larr; venkateshrao.com</a>
    <h1><a class="site-title-link" href="{home}">Books by Venkatesh Rao</a></h1>
  </div>
</header>
<div class="main-wrapper">
{body}
</div>
<footer class="site-footer">
  <p>Copyright &copy; Venkatesh Rao &mdash; <a href="{home}">All Books</a></p>
</footer>
{extra_body_end}
</body>
</html>"""


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _get_buy_links(book: dict) -> tuple:
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
    online = (book.get("editions") or {}).get("online") or {}
    slug = online.get("slug")
    if not slug:
        return None, None
    return slug, online.get("entry_point") or "index.html"


def _series_label_parts(book: dict) -> list:
    parts = []
    if book.get("series"):
        parts.append(_esc(book["series"]))
    if book.get("label"):
        parts.append(_esc(book["label"]))
    return parts


# ---------------------------------------------------------------------------
# Book card  (catalog and series pages — compact, no blurb)
# ---------------------------------------------------------------------------

def render_card(book: dict, thumbnail_rel: str, detail_url: str, root_url: str = "") -> str:
    title = book["title"]
    parts = _series_label_parts(book)

    series_label_html = ""
    if parts:
        series_label_html = (
            f'<div class="book-series-label">'
            f'{"&thinsp;&middot;&thinsp;".join(parts)}'
            f"</div>"
        )

    thumb = root_url + thumbnail_rel
    cover_html = (
        f'<a class="book-cover-link" href="{detail_url}">'
        f'<img class="book-cover" src="{thumb}" alt="{_esc(title)}"/>'
        f"</a>"
    )
    title_html = f'<h2 class="book-title"><a href="{detail_url}">{_esc(title)}</a></h2>'

    slug, entry = _get_read_info(book)
    buy_print, buy_ebook = _get_buy_links(book)
    links = []
    if slug:
        links.append(f'<a class="read-link" href="{root_url}{slug}/read/{entry}">Read &rarr;</a>')
    if buy_print:
        links.append(f'<a class="buy-link" href="{_esc(buy_print)}">Print</a>')
    if buy_ebook:
        links.append(f'<a class="buy-link" href="{_esc(buy_ebook)}">Ebook</a>')
    if not links:
        links.append('<span class="edition-soon">Soon</span>')

    links_html = (
        '<div class="book-links">'
        + "".join(links)
        + "</div>"
    )

    tags_attr = " ".join(get_tags(book))
    return f"""\
      <article class="book-card" data-tags="{tags_attr}">
        {cover_html}
        <div class="book-info">
          {series_label_html}
          {title_html}
          {links_html}
        </div>
      </article>"""


# ---------------------------------------------------------------------------
# Detail page
# ---------------------------------------------------------------------------

def render_detail_page(book: dict, thumbnail_rel: str, series_volumes: list = None) -> str:
    ROOT = "../"
    title = book["title"]
    blurb = book.get("blurb") or ""
    series = book.get("series")
    label = book.get("label")

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

    parts = _series_label_parts(book)
    series_label_html = ""
    if parts:
        series_label_html = (
            f'<div class="book-series-label">'
            f'{"&thinsp;&middot;&thinsp;".join(parts)}'
            f"</div>"
        )

    thumb = ROOT + thumbnail_rel
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

    # "More in this series" section
    more_series_html = ""
    others = [v for v in (series_volumes or []) if v["id"] != book["id"]]
    if others:
        other_cards = []
        for v in others:
            v_slug = get_slug(v)
            v_thumb = ROOT + (v.get("_thumb_rel") or PLACEHOLDER_THUMB)
            other_cards.append(render_card(v, v.get("_thumb_rel") or PLACEHOLDER_THUMB,
                                           f"{ROOT}{v_slug}/", root_url=ROOT))
        series_url = f"{ROOT}series/{series_slug}/" if series_slug else None
        view_all = (f'<a class="series-view-link" href="{series_url}">View full series &rarr;</a>'
                    if series_url else "")
        more_series_html = f"""\
  <div class="more-in-series">
    <div class="more-in-series-header">
      <span class="more-in-series-title">More in {_esc(series)}</span>
      {view_all}
    </div>
    <div class="book-grid">
{"".join(other_cards)}
    </div>
  </div>"""

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
    </div>
  </div>
  {more_series_html}"""

    page_title = f"{title} — {series} {label}" if (series and label) else title
    canonical = f"{BASE_URL}/{get_slug(book)}/"
    og_image = f"{BASE_URL}/social/{book['id']}.png"
    return page_html(title=page_title, body=body, root_url=ROOT, description=blurb,
                     canonical_url=canonical, og_image=og_image)


# ---------------------------------------------------------------------------
# Series page
# ---------------------------------------------------------------------------

def render_series_page(series_name: str, series_desc: str, volumes: list, thumbs: dict) -> str:
    ROOT = "../../"
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

    canonical = f"{BASE_URL}/series/{slugify(series_name)}/"
    og_image = f"{BASE_URL}/social/series-{slugify(series_name)}.png"
    return page_html(
        title=f"{series_name} — Books by Venkatesh Rao",
        body=body, root_url=ROOT, description=series_desc,
        canonical_url=canonical, og_image=og_image,
    )


# ---------------------------------------------------------------------------
# Featured book (JS random pick)
# ---------------------------------------------------------------------------

def render_featured_js(visible: list, thumbs: dict) -> str:
    """Generate the featured-book section with embedded JS for random selection."""
    books_data = []
    for book in visible:
        slug = get_slug(book)
        slug_read, entry = _get_read_info(book)
        buy_print, buy_ebook = _get_buy_links(book)
        parts = []
        if book.get("series"):
            parts.append(book["series"])
        if book.get("label"):
            parts.append(book["label"])
        books_data.append({
            "title": book["title"],
            "label": " · ".join(parts) if parts else "",
            "blurb": book.get("blurb") or "",
            "detail": f"{slug}/",
            "thumb": thumbs[book["id"]],
            "tags": get_tags(book),
            "read": f"{slug}/read/{entry}" if slug_read else None,
            "buyPrint": buy_print,
            "buyEbook": buy_ebook,
        })

    books_json = json.dumps(books_data, ensure_ascii=False)

    return f"""\
<section class="featured-section" id="featured-section">
  <div class="featured-tag">Featured Book</div>
  <div class="featured-book" id="featured-book">
    <div class="featured-cover-wrap"><div class="featured-cover-placeholder"></div></div>
    <div class="featured-info"><p class="book-detail-desc" style="color:var(--muted)">Loading&hellip;</p></div>
  </div>
</section>
<script>
var __catalogBooks = {books_json};
function __renderFeatured(b) {{
  var links = '';
  if (b.read)     links += '<a class="read-link" href="' + b.read + '">Read online &rarr;</a>';
  if (b.buyPrint) links += '<a class="buy-link" href="' + b.buyPrint + '">Buy Print</a>';
  if (b.buyEbook) links += '<a class="buy-link" href="' + b.buyEbook + '">Buy Ebook</a>';
  var label = b.label ? '<div class="book-series-label">' + b.label + '</div>' : '';
  document.getElementById('featured-book').innerHTML =
    '<a class="featured-cover-wrap" href="' + b.detail + '">' +
      '<img class="featured-cover" src="' + b.thumb + '" alt="' + b.title.replace(/"/g,'&quot;') + '"/>' +
    '</a>' +
    '<div class="featured-info">' +
      label +
      '<h2 class="featured-title"><a href="' + b.detail + '">' + b.title + '</a></h2>' +
      '<p class="featured-desc">' + b.blurb + '</p>' +
      '<div class="book-links">' + links + '</div>' +
    '</div>';
}}
function __pickFeatured(tag) {{
  var pool = (tag === 'all') ? __catalogBooks :
    __catalogBooks.filter(function(b) {{ return b.tags && b.tags.indexOf(tag) !== -1; }});
  if (!pool.length) return;
  __renderFeatured(pool[Math.floor(Math.random() * pool.length)]);
}}
__pickFeatured('all');
</script>"""


# ---------------------------------------------------------------------------
# Filter bar (catalog page only)
# ---------------------------------------------------------------------------

def render_filter_bar(available_tags: list) -> str:
    """Render the tag filter dropdown + JS. available_tags is a list of tag slugs."""
    if not available_tags:
        return ""
    options = ['<option value="all">All books</option>']
    for tag in available_tags:
        label = TAG_LABELS.get(tag, tag.replace("-", " ").title())
        options.append(f'<option value="{tag}">{label}</option>')
    options_html = "\n    ".join(options)
    return f"""\
<div class="catalog-header">
  <h2 class="catalog-title">Catalog</h2>
  <div class="filter-bar">
    <label for="tag-filter">Filter</label>
    <select class="filter-select" id="tag-filter">
      {options_html}
    </select>
  </div>
</div>
<script>
(function() {{
  var sel = document.getElementById('tag-filter');
  if (!sel) return;
  sel.addEventListener('change', function() {{
    var tag = this.value;
    // Show/hide cards
    document.querySelectorAll('.book-card').forEach(function(c) {{
      var tags = (c.dataset.tags || '').split(' ').filter(Boolean);
      c.style.display = (tag === 'all' || tags.indexOf(tag) !== -1) ? '' : 'none';
    }});
    // Show/hide empty sections
    document.querySelectorAll('.book-section').forEach(function(s) {{
      var anyVisible = Array.from(s.querySelectorAll('.book-card')).some(function(c) {{
        return c.style.display !== 'none';
      }});
      s.style.display = anyVisible ? '' : 'none';
    }});
    // Update featured book
    if (typeof __pickFeatured === 'function') __pickFeatured(tag);
  }});
}})();
</script>"""


# ---------------------------------------------------------------------------
# Catalog body
# ---------------------------------------------------------------------------

def _make_catalog_groups(visible: list) -> list:
    """
    Order and group visible books according to CATALOG_SECTIONS.
    Returns a list of groups, each a dict with 'books' and optionally series metadata.
    """
    by_id = {book["id"]: book for book in visible}
    used = set()
    groups = []

    for section_ids in CATALOG_SECTIONS:
        section_books = [by_id[bid] for bid in section_ids if bid in by_id]
        if not section_books:
            continue
        used.update(b["id"] for b in section_books)

        # Detect if ALL books share the same series with >= SERIES_PAGE_MIN_VOLUMES
        series_names = {b.get("series") for b in section_books}
        if len(series_names) == 1 and None not in series_names and len(section_books) >= SERIES_PAGE_MIN_VOLUMES:
            series_name = series_names.pop()
            groups.append({
                "type": "series",
                "name": series_name,
                "slug": slugify(series_name),
                "desc": section_books[0].get("series_desc") or "",
                "books": section_books,
            })
        else:
            groups.append({"type": "standalone", "books": section_books})

    # Append any books not covered by CATALOG_SECTIONS
    remainder = [b for b in visible if b["id"] not in used]
    if remainder:
        groups.append({"type": "standalone", "books": remainder})

    return groups


def render_catalog_body(groups: list, thumbs: dict) -> str:
    sections = []
    for group in groups:
        cards = []
        for book in group["books"]:
            book_slug = get_slug(book)
            detail_url = f"{book_slug}/"
            cards.append(render_card(book, thumbs[book["id"]], detail_url, root_url=""))
        grid = "\n\n".join(cards)
        sections.append(f"""\
  <section class="book-section">
    <div class="book-grid">
{grid}
    </div>
  </section>""")

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# SEO files: sitemap, robots.txt, llms.txt
# ---------------------------------------------------------------------------

def generate_sitemap(visible: list, series_groups: list) -> None:
    """Write docs/sitemap.xml."""
    today = datetime.date.today().isoformat()

    urls = []

    # Catalog root
    urls.append(f"""\
  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>""")

    # Book detail pages + optional reading entry points
    for book in visible:
        slug = get_slug(book)
        urls.append(f"""\
  <url>
    <loc>{BASE_URL}/{slug}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""")
        online = (book.get("editions") or {}).get("online") or {}
        if online.get("slug"):
            entry = online.get("entry_point") or "index.html"
            urls.append(f"""\
  <url>
    <loc>{BASE_URL}/{slug}/read/{entry}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.5</priority>
  </url>""")

    # Series pages
    for g in series_groups:
        urls.append(f"""\
  <url>
    <loc>{BASE_URL}/series/{g['slug']}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>""")

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "\n".join(urls) + "\n"
    sitemap += "</urlset>\n"

    (DOCS_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def generate_robots_txt() -> None:
    """Write docs/robots.txt."""
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )
    (DOCS_DIR / "robots.txt").write_text(content, encoding="utf-8")


def generate_llms_txt(all_books: list, visible: list, series_groups: list) -> None:
    """Write docs/llms.txt in llmstxt.org format."""
    visible_ids = {b["id"] for b in visible}

    # Partition visible books
    online_books = []
    buy_only_books = []
    for book in visible:
        online = (book.get("editions") or {}).get("online") or {}
        if online.get("slug"):
            online_books.append(book)
        else:
            buy_only_books.append(book)

    # Alpha books with a blurb (not visible, but worth mentioning)
    optional_books = [
        b for b in all_books
        if b["id"] not in visible_ids and b.get("blurb")
    ]

    lines = []
    lines.append("# Books by Venkatesh Rao")
    lines.append("")
    lines.append("> A catalog of books by Venkatesh Rao, with free online editions and buy links for print and ebook formats.")
    lines.append("")
    lines.append("Venkatesh Rao ([@vgr](https://venkateshrao.com)) is a writer, consultant, and blogger at [Ribbonfarm](https://www.ribbonfarm.com). He writes about strategy, technology, and the nature of modern life.")
    lines.append("")

    lines.append("## Docs")
    lines.append("")
    lines.append(f"- [Full Catalog]({BASE_URL}/): Browse all books with covers, descriptions, and links.")
    lines.append("")

    if online_books:
        lines.append("## Online Books (free to read)")
        lines.append("")
        for book in online_books:
            slug = get_slug(book)
            blurb = book.get("blurb") or ""
            lines.append(f"- [{book['title']}]({BASE_URL}/{slug}/): {blurb}")
        lines.append("")

    if buy_only_books:
        lines.append("## Buy Only")
        lines.append("")
        for book in buy_only_books:
            slug = get_slug(book)
            blurb = book.get("blurb") or ""
            lines.append(f"- [{book['title']}]({BASE_URL}/{slug}/): {blurb}")
        lines.append("")

    if series_groups:
        lines.append("## Series")
        lines.append("")
        for g in series_groups:
            series_slug = g["slug"]
            series_desc = g.get("desc") or ""
            n = len(g["books"])
            lines.append(f"- [{g['name']}]({BASE_URL}/series/{series_slug}/): {series_desc} — {n} volumes.")
        lines.append("")

    if optional_books:
        lines.append("## Optional")
        lines.append("")
        for book in optional_books:
            blurb = book.get("blurb") or ""
            lines.append(f"- {book['title']}: {blurb}")
        lines.append("")

    (DOCS_DIR / "llms.txt").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def build(dry_run: bool = False) -> str:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))

    # Overlay blurbs from blurbs.md (takes priority over registry.json blurb field)
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

    featured_html = render_featured_js(visible, thumbs)
    catalog_body = render_catalog_body(groups, thumbs)

    # Compute available tags (only tags that have at least one visible book)
    tag_counts: dict = {}
    for book in visible:
        for tag in get_tags(book):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    available_tags = [t for t in TAG_ORDER if t in tag_counts]
    filter_bar_html = render_filter_bar(available_tags)

    full_body = featured_html + "\n\n" + filter_bar_html + "\n\n" + catalog_body

    catalog_html = page_html(
        title="Books by Venkatesh Rao",
        body=full_body,
        root_url="",
        description="A catalog of books by Venkatesh Rao — fiction, essays, and longform writing. Some available free to read online.",
        canonical_url=f"{BASE_URL}/",
        og_image=f"{BASE_URL}/social/catalog.png",
    )

    if dry_run:
        return catalog_html

    SOCIAL_DIR.mkdir(exist_ok=True)
    CATALOG_FILE.write_text(catalog_html, encoding="utf-8")
    card_count = catalog_html.count('class="book-card"')
    print(f"Catalog → {CATALOG_FILE} ({card_count} cards)")

    # Build series map for "More in this series"
    from collections import defaultdict
    series_map = defaultdict(list)
    for book in visible:
        if book.get("series"):
            # Stash resolved thumbnail on book dict for use in render_detail_page
            book["_thumb_rel"] = thumbs[book["id"]]
            series_map[book["series"]].append(book)

    # Detail pages
    for book in visible:
        book_slug = get_slug(book)
        slug_dir = DOCS_DIR / book_slug
        slug_dir.mkdir(exist_ok=True)
        series_vols = series_map.get(book.get("series")) if book.get("series") else None
        (slug_dir / "index.html").write_text(
            render_detail_page(book, thumbs[book["id"]], series_volumes=series_vols),
            encoding="utf-8",
        )
    print(f"Detail pages → docs/{{slug}}/ ({len(visible)} books)")

    # Series pages
    series_dir = DOCS_DIR / "series"
    series_dir.mkdir(exist_ok=True)
    series_groups = [g for g in groups if g["type"] == "series"]
    for g in series_groups:
        slug_dir = series_dir / g["slug"]
        slug_dir.mkdir(exist_ok=True)
        (slug_dir / "index.html").write_text(
            render_series_page(g["name"], g["desc"], g["books"], thumbs), encoding="utf-8"
        )
    print(f"Series pages → docs/series/ ({len(series_groups)} series)")

    # Sitemap, robots, llms.txt
    generate_sitemap(visible, series_groups)
    generate_robots_txt()
    generate_llms_txt(data["books"], visible, series_groups)
    print("Sitemap, robots.txt, llms.txt → docs/")

    return catalog_html


def main():
    dry_run = "--dry-run" in sys.argv
    html = build(dry_run=dry_run)
    if dry_run:
        print(html)


if __name__ == "__main__":
    main()
