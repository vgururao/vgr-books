# Status: Online Books

## Project
- **Title:** Venkat Rao Online Books
- **URL:** https://books.venkateshrao.com (TBD — domain not yet pointed)
- **Type:** Aggregated static site — all online books in one place
- **Status:** in-progress

## Outputs
| Format | Status | Notes |
|--------|--------|-------|
| Site   | in-progress | 4 books synced; hosting not yet configured; domain not yet pointed |
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
