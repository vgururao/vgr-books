# CLAUDE.md — Online Books

## Project Overview

**online-books** hosts all of Venkatesh Rao's free online books at [books.venkateshrao.com](https://books.venkateshrao.com).

Each book is a subfolder under `docs/`, synced from its source project:

| Slug | Source Project | Entry Point |
|------|----------------|-------------|
| `artofgig-vol3/` | `../artofgig/docs/` | `vol3_cover.html` |
| `twitterbook/` | `../vgrtwitterbook/book/` | `index.html` |
| `breakingsmart/` | `../BreakingSmart/docs/` | `index.html` |

The main index at `docs/index.html` is the library landing page. Each book's subdirectory contains a full copy of that book's static site, synced (not independently edited) from its source project.

---

## Local Development

```bash
# 1. Sync all books from source projects (first time, or after source changes)
python3 sync.py

# 2. Start local server
bash serve.sh          # serves on http://localhost:8080
bash serve.sh 9000     # or a custom port
```

The site is a plain static site — no build step. Relative paths within each book's subdir work as-is.

---

## Sync Workflow

Book content is synced from source projects using `sync.py`. Source projects maintain their own build pipelines; syncing is a separate step.

```bash
# Sync all books
python3 sync.py

# Sync a specific book
python3 sync.py artofgig-vol3
python3 sync.py twitterbook
python3 sync.py breakingsmart
```

After syncing, commit and push to deploy:

```bash
git add docs/ && git commit -m "Sync books" && git push
```

---

## Per-Book Deploy Scripts

Each source project has a `deploy_to_online_books.sh` that handles building + syncing in one step:

| Project | Script |
|---------|--------|
| Art of Gig Vol 3 | `../artofgig/deploy_to_online_books.sh` |
| Twitter Book | `../vgrtwitterbook/deploy_to_online_books.sh` |
| Breaking Smart | `../BreakingSmart/deploy_to_online_books.sh` |

Old single-project deploys remain active until the new site is ready.

---

## Hosting (TBD)

Options under evaluation:

| Option | Notes |
|--------|-------|
| **GitHub Pages** | Auto-deploy from `docs/` on push; free; zero config |
| **Vercel** | `vercel --prod`; good for future dynamic features |
| **Netlify** | `netlify deploy --prod --dir docs`; good redirect rule support |
| **Cloudflare Pages** | `wrangler pages deploy docs`; fastest CDN; powerful rules engine |

Custom domain: `books.venkateshrao.com` — DNS CNAME once hosting is chosen. Add `docs/CNAME` for GitHub Pages.

### Redirect Strategy (when DNS is cut over)

Old deployments stay active until books.venkateshrao.com is live. Once ready:

| Old URL | New URL |
|---------|---------|
| `artofgig.com` | `books.venkateshrao.com/artofgig-vol3/` |
| `venkateshrao.com/twitter-book/*` | `books.venkateshrao.com/twitterbook/*` |
| `breakingsmart.com` | `books.venkateshrao.com/breakingsmart/` |

Redirect rules live in hosting config (`_redirects` for Netlify, Cloudflare page rules, etc.) or as HTML `<meta refresh>` pages in the old repos.

---

## Structure

```
online-books/
├── CLAUDE.md           ← this file
├── status.md
├── .gitignore
├── sync.py             ← syncs all book source dirs into docs/<slug>/
├── deploy.sh           ← stub; update when hosting is chosen
└── docs/               ← site root (GitHub Pages source)
    ├── index.html      ← main library page (SACRED — never auto-overwrite)
    ├── style.css       ← library styles (SACRED — never auto-overwrite)
    ├── CNAME           ← add when domain is configured
    ├── artofgig-vol3/  ← synced from ../artofgig/docs/
    ├── twitterbook/    ← synced from ../vgrtwitterbook/book/
    └── breakingsmart/  ← synced from ../BreakingSmart/docs/
```

---

## File Rules

| File | Rule |
|------|------|
| `docs/index.html` | **SACRED** — never auto-overwrite. Hand-crafted library page. |
| `docs/style.css` | **SACRED** — never auto-overwrite. Hand-crafted library styles. |
| `docs/artofgig-vol3/**` | Synced by `sync.py` — never hand-edit (edit source project instead) |
| `docs/twitterbook/**` | Synced by `sync.py` — never hand-edit (edit source project instead) |
| `docs/breakingsmart/**` | Synced by `sync.py` — never hand-edit (edit source project instead) |

---

## Adding Future Books

1. Add an entry to the `BOOKS` dict in `sync.py`
2. Add a card to `docs/index.html`
3. Create a `deploy_to_online_books.sh` in the source project
4. Run `python3 sync.py <new-slug>` to populate the directory
5. Commit and push

---

## Reading Experience Consistency

Individual books use their own styles (hand-crafted `style.css` + shared `book-nav.css` from `online_book_builder/`). The main library index uses its own `style.css`.

Future improvement: add a "← All books" link to each book's nav header, pointing back to `https://books.venkateshrao.com`. This requires changes to each book's nav generation scripts.

---

## After Each Work Session

Update `status.md`, then:

```bash
python3 ../Dashboard/build.py
```
