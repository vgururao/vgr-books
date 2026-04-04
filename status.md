# Status: VGR Books

## Project
- **Title:** VGR Books
- **Source:** books.venkateshrao.com (unified catalog, GitHub Pages)
- **Type:** Aggregated static site — all online books in one place
- **Status:** live

## Outputs
| Format | Status | Notes |
|--------|--------|-------|
| Site   | live | books.venkateshrao.com; 15 book cards; GitHub Pages; Namecheap CNAME |
| Ebook  | n/a | Individual books tracked separately |
| Print  | n/a | Individual books tracked separately |

## Books
| Slug | Book | Sync Status |
|------|------|-------------|
| artofgig-vol3/ | Art of Gig Vol 3: The Yakverse Chronicles | synced ✓ |
| twitterbook/ | vgr: The Twitter Years (2007–22) | synced ✓ |
| breakingsmart/ | Breaking Smart: How Software is Eating the World | synced ✓ |
| mediocratopia/ | Mediocratopia | synced ✓ |

## Instructions for Agents
After each work session, update this file:
1. Change the **Status** field
2. Update the Outputs table
3. Update the sync status column for each book
4. Add dated session notes at the bottom

## Session Notes

### 2026-04-03 (session 2)
- Tag filter dropdown: All / Ribbonfarm / Art of Gig / Rust Age / Configurancy
- RIBBONFARM_IDS set: rust-age-vol1–4, gervais-principle, crash-early-crash-often
- Filter hides cards + empty sections; repicks featured book from filtered pool
- Featured section: warmer parchment bg, "Featured Book" label in Georgia bold
- "Catalog" header + top border rule above filter bar
- HTTPS cert provisioned and enforced for books.venkateshrao.com (Let's Encrypt, expires 2026-07-02)
- Buy links audit: all 15 active links upgraded http → https; verified all resolve (200 OK)
- CLAUDE.md, TODO.md, memory updated for session close

### 2026-04-03
- Deployed to GitHub Pages at books.venkateshrao.com (CNAME via Namecheap, repo vgururao/vgr-books)
- Major catalog redesign: 5-column compact grid, featured book (random JS pick), flat rows (no series section headers)
- URL structure established: /{slug}/ = detail page, /{slug}/read/ = reading experience, /series/{slug}/ = series page
- "More in this series" section on individual book detail pages (replaces series section headers)
- CATALOG_SECTIONS list in build_catalog.py for explicit catalog ordering
- Series pages generated at /series/{slug}/
- Thumbnail pipeline: PIL resize to 400px wide; inbox/ drop zone; fixed 6 thumbnail paths after read/ migration
- Masthead redesign: beige background, left-justified, back link above h1 with separator line
- Cover thumbnails added for: Be Slightly Evil, Gervais Principle, Configurancy Tempo (resized from inbox)
- Created ARCHITECTURE.md — reference guide for other projects on how to link, embed, find thumbnails/blurbs

### 2026-04-02
- Major architecture refactor: renamed project online-books → vgr-books (master production registry)
- Created `registry.json` — single source of truth for all 22 books: stages, editions, ISBNs, buy links, transmittal, catalog display
- Rewrote `build_catalog.py` to read from registry.json (replaces catalog_meta.json + status.md display flags)
- Updated CLAUDE.md for vgr-books, manuscripts/, Publishing/, Dashboard/, artofgig/, vgrtwitterbook/, BreakingSmart/, Configurancy/, Ribbonfarm Archives/, online_book_builder/
- Created manuscripts/CLAUDE.md, vgr-books/inbox/README.md, vgr-books/TODO.md
- Renamed deploy_to_online_books.sh → deploy_to_vgr_books.sh in all 3 source projects
- Added thumbnails: gervais-principle.png (from gpthumb.png), be-slightly-evil.png (from bsethumb.png)
- Added thumbnails for Rust Age vol1–4 and Crash Early Crash Often from source folders
- Populated all buy links from ribbonfarm.com/books/ and ribbonfarm.com/tempo/
- Catalog now generates 15 book cards
- Remaining cover quality issues: Gervais Principle, Be Slightly Evil, Configurancy Tempo (user to drop better images in inbox/)



### 2026-03-01 (session 2)
- Added book_meta.json system: Dashboard/build.py now writes {title, status, thumbnail} to every project folder on each build
- Thumbnail discovery order: standard conventions → collateral/ (flat then recursive, preferring cover/front names) → root *cover* glob → subdirectory collateral trees (for multi-volume projects)
- Newsletter cover found: BreakingSmartNewsletterEbook/ebookcovernewsletter300dpi.jpg
- Tempo cover found: Configurancy/Tempo/collateral/TempoCollateral/Delivered/frontSmall.jpg
- build_catalog.py updated: for slug-less entries, reads book_meta.json thumbnail from source project and copies to docs/thumbnails/<id>.<ext>
- docs/thumbnails/ now has: coming-soon.svg, breaking-smart-newsletter.jpg, configurancy-tempo.jpg
- Updated 7 CLAUDE.md files with book_meta.json documentation
- Updated Dashboard/CLAUDE.md with thumbnail discovery order docs

### 2026-03-01
- Implemented Dashboard → Catalog integration (the plan from catalog integration session)
- Added `**display:** on/off` field to status.md format: per-project (flat books) or per-subsection (volumes/editions)
- Created `catalog_meta.json` — hand-maintained catalog registry with title, blurb, thumbnail, buy links, sort order, and status_md pointer for 17 candidate books
- Created `build_catalog.py` — reads catalog_meta.json + status.md display flags, generates docs/index.html
- Created `docs/thumbnails/coming-soon.svg` — placeholder for books without cover art
- Updated `Dashboard/build.py`: added display field parsing + "Catalog" column (● on, ○ off, — unset)
- Updated `Dashboard/CLAUDE.md` with display field docs
- Updated `online-books/CLAUDE.md`: docs/index.html now GENERATED, catalog system documented
- Interview results — display: on set for 8 books:
  - Art of Gig Vol. 1, Vol. 2, Vol. 3 (artofgig/status.md, per-subsection)
  - vgr: The Twitter Years (vgrtwitterbook/status.md)
  - Breaking Smart (BreakingSmart/status.md, "Static Site (active)" subsection)
  - Mediocratopia (Ribbonfarm Archives/Mediocratopia/status.md)
  - Configurancy: Tempo only (Configurancy/status.md, "Tempo" subsection)
  - Breaking Smart Newsletter (BreakingSmartNewsletterEbook/status.md)
- Generated docs/index.html with 8 book cards

### 2026-02-28 (session 2)
- Added Mediocratopia as 4th book: generate_site.py run, synced to docs/mediocratopia/, catalog card added
- All 4 books now synced; catalog index.html shows full book collection with buy links and read-online links
- Documented canonical source principle: once Vellum editing begins, edited .docx is the canonical source for online builds
- Action items documented in CLAUDE.md: (1) docx-driven site rebuild for Mediocratopia; (2) dashboard integration for auto-generated catalog

### 2026-02-28
- Created online-books/ project (git repo, main branch)
- Created CLAUDE.md, status.md, .gitignore, sync.py, deploy.sh
- Created docs/index.html (main library page) and docs/style.css
- Synced all 3 existing books (artofgig-vol3, twitterbook, breakingsmart) to docs/
- Created deploy_to_online_books.sh in artofgig/, vgrtwitterbook/, BreakingSmart/
- Updated CLAUDE.md in each source project to document new deploy pathway
- Next: choose hosting platform, configure CNAME
