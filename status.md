# Status: Online Books

## Project
- **Title:** Venkat Rao Online Books
- **URL:** https://books.venkateshrao.com (TBD — domain not yet pointed)
- **Type:** Aggregated static site — all online books in one place
- **Status:** in-progress

## Outputs
| Format | Status | Notes |
|--------|--------|-------|
| Site   | in-progress | Structure, index, and scripts created; hosting not yet decided; books not yet synced |
| Ebook  | n/a | Individual books tracked separately |
| Print  | n/a | Individual books tracked separately |

## Books
| Slug | Book | Sync Status |
|------|------|-------------|
| artofgig-vol3/ | Art of Gig Vol 3: The Yakverse Chronicles | not synced |
| twitterbook/ | vgr: The Twitter Years (2007–22) | not synced |
| breakingsmart/ | Breaking Smart: How Software is Eating the World | not synced |

## Instructions for Agents
After each work session, update this file:
1. Change the **Status** field
2. Update the Outputs table
3. Update the sync status column for each book
4. Add dated session notes at the bottom

## Session Notes

### 2026-02-28
- Created online-books/ project (git repo, main branch)
- Created CLAUDE.md, status.md, .gitignore, sync.py, deploy.sh
- Created docs/index.html (main library page) and docs/style.css
- Created placeholder dirs for artofgig-vol3/, twitterbook/, breakingsmart/
- Created deploy_to_online_books.sh in artofgig/, vgrtwitterbook/, BreakingSmart/
- Updated CLAUDE.md in each source project to document new deploy pathway
- Next: choose hosting platform, run initial sync, configure CNAME
