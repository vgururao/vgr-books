# Architecture Overview — vgr-books / books.venkateshrao.com

This document is a reference for other projects in the Publishing ecosystem that need to link to, embed, or display information about VGR books.

---

## Live Site

**[books.venkateshrao.com](https://books.venkateshrao.com)**
GitHub Pages, repo `vgururao/vgr-books`, auto-deploy from `main` branch `/docs`.

---

## Source of Truth

**`registry.json`** is the single authoritative file for all book metadata. Never read `catalog_meta.json` (deprecated) or scrape `docs/index.html` (generated). Parse `registry.json` directly.

---

## URL Patterns

| What | Pattern | Example |
|------|---------|---------|
| Catalog home | `https://books.venkateshrao.com/` | — |
| Book detail page | `https://books.venkateshrao.com/{slug}/` | `.../artofgig-vol3/` |
| Online reading | `https://books.venkateshrao.com/{slug}/read/{entry_point}` | `.../artofgig-vol3/read/vol3_cover.html` |
| Series page | `https://books.venkateshrao.com/series/{series-slug}/` | `.../series/art-of-gig/` |

**Slug** = `editions.online.slug` (if the book has an online edition), otherwise the book's `id`.

**Reading entry point** = `editions.online.entry_point` in `registry.json`.

**Series slug** = series name lowercased with spaces replaced by hyphens (e.g., "Art of Gig" → `art-of-gig`).

---

## Finding a Book's Data

All lookups start from `registry.json` → `books` array.

### Key fields per book

```json
{
  "id": "artofgig-vol3",           // stable identifier, used in file paths
  "title": "The Yakverse Chronicles",
  "series": "Art of Gig",          // null for standalone books
  "series_volume": 3,              // null for standalone books
  "label": "Vol. 3",               // short display label, null if standalone
  "blurb": "Thirteen absurdist...", // 1–2 sentence description for display
  "thumbnail": "artofgig-vol3/read/images/yakverse-cover.png",  // relative to docs/
  "sort_order": 30,                // lower = earlier in catalog
  "stage": "beta",                 // option | alpha | beta | production | published
  "editions": {
    "online": {
      "slug": "artofgig-vol3",
      "entry_point": "vol3_cover.html",
      "display": true
    },
    "ebook":  { "isbn": null,              "buy_link": null,  "display": false },
    "print":  { "isbn": null,              "buy_link": null,  "display": false }
  }
}
```

### Is a book visible in the public catalog?

```python
book_is_visible = any(
    (ed or {}).get("display") == True
    for ed in book["editions"].values()
)
```

---

## Thumbnails

Thumbnail path is stored in `registry.json` → `thumbnail`. It is **relative to `docs/`**.

To construct an absolute URL:
```
https://books.venkateshrao.com/{thumbnail_field_value}
```

Example:
- `"thumbnail": "thumbnails/be-slightly-evil.jpg"` → `https://books.venkateshrao.com/thumbnails/be-slightly-evil.jpg`
- `"thumbnail": "artofgig-vol3/read/images/yakverse-cover.png"` → `https://books.venkateshrao.com/artofgig-vol3/read/images/yakverse-cover.png`

If `thumbnail` is `null`, the fallback is `https://books.venkateshrao.com/thumbnails/coming-soon.svg`.

All thumbnails are sized ~400px wide (2:3 aspect ratio). Prefer these over raw source images for any web display.

---

## Buy Links and Online Reading Links

| Want | Where in registry.json |
|------|------------------------|
| Amazon buy link (ebook) | `editions.ebook.buy_link` |
| Amazon buy link (print) | `editions.print.buy_link` |
| Online reading entry URL | Construct from `editions.online.slug` + `editions.online.entry_point` (see URL Patterns above) |

All buy links go directly to Amazon (amzn.to short links). They may be `null` if not yet published.

---

## Book Detail Page

Every visible book has a generated detail page at `/{slug}/`. It contains:
- Cover thumbnail
- Title, series label, blurb
- "Read Online" button (if online edition exists)
- Buy links (ebook / print)
- "More in this series" grid (for books that are part of a series)

To link to a book from another site, link to its **detail page** (`/{slug}/`), not directly to the reading experience. The detail page is the stable, shareable URL.

---

## Blurbs

`blurb` in `registry.json` is the canonical short description (1–2 sentences). Use this verbatim when referencing a book elsewhere. Do not paraphrase or generate new blurbs — update `registry.json` if the blurb needs to change.

---

## Series

Books in a series share a `series` field value (exact string match). To find all volumes:

```python
series_books = [b for b in registry["books"] if b.get("series") == "Art of Gig"]
series_books.sort(key=lambda b: b.get("series_volume") or 0)
```

Series home page lives at `https://books.venkateshrao.com/series/{series-slug}/`.

The `series_desc` field on each book holds a one-line description of the series as a whole (same value across all volumes).

---

## Catalog Ordering

`sort_order` controls the order books appear in the catalog (lower = earlier). Current assignments:

| Range | Books |
|-------|-------|
| 10–30 | Art of Gig series (vols 1–3) |
| 40 | Twitter Book |
| 50 | Breaking Smart |
| 55–60 | Crash Early Crash Often, Mediocratopia |
| 70–80 | Rust Age series |
| 90–100 | Configurancy series (Tempo, ...) |
| 150–160 | Lower-priority / newsletter books |

---

## Adding a Reference from Another Project

If another project (e.g., venkateshrao.com, ribbonfarm.com, a Substack) wants to display a book card:

1. Read `registry.json` — either by parsing the file directly (if in the same filesystem) or by fetching the raw GitHub URL.
2. Filter to `display: true` books.
3. Use `thumbnail`, `blurb`, `title`, and the detail page URL (`/{slug}/`).
4. For buy links, use `editions.ebook.buy_link` and/or `editions.print.buy_link`.
5. For online reading, construct the URL from `editions.online.slug` + `editions.online.entry_point`.

Raw `registry.json` on GitHub:
```
https://raw.githubusercontent.com/vgururao/vgr-books/main/registry.json
```

---

## Updating Book Data

All updates go into `registry.json` (never `catalog_meta.json`). After editing:

```bash
python3 build_catalog.py   # regenerates all HTML pages
git add docs/ registry.json && git commit -m "Update catalog" && git push
```

GitHub Pages auto-deploys on push; propagation takes ~30–60 seconds.
