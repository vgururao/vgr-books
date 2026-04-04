# VGR Books — To-Do List

Items to resolve in future sessions. Edit `registry.json` for data changes, `blurbs.md` for descriptions.

---

## Cover Images Needed

Drop images in `inbox/` (see `inbox/README.md`), then resize with PIL and run `python3 build_catalog.py` + `python3 generate_social_cards.py`.

| Book | id | Notes |
|------|----|-------|
| The Gervais Principle | `gervais-principle` | Current thumb is passable but could be better |
| Be Slightly Evil | `be-slightly-evil` | Current thumb is passable but could be better |
| Configurancy: Tempo | `configurancy-tempo` | Current thumb is passable but could be better |
| Rust Age Vol 1–4 | `rust-age-vol*` | Placeholder-style thumbs — get proper cover images |
| Crash Early, Crash Often | `crash-early-crash-often` | Same |
| Breaking Smart Newsletter | `breaking-smart-newsletter` | Same |

---

## Site Polish

- [ ] **Nav bar** — add strip linking to venkateshrao.com, ribbonfarm.com, contraptions, artofgig.com — add to `page_html` template in `build_catalog.py`
- [ ] **Site metadata** — review `<title>`, `<meta description>`, footer copy in `build_catalog.py` template; add intro paragraph below masthead on catalog page
- [ ] **Blurb review** — edit `blurbs.md` to improve any catalog descriptions; run `python3 build_catalog.py` to rebuild
- [ ] **Social card quality** — review `docs/social/` cards once better cover images are in place; re-run `generate_social_cards.py`
- [ ] **Catalog sort order** — review `sort_order` values in `registry.json` (current: AoG 10–30, Twitter 40, BS 50, Mediocratopia 60, Rust Age 81–84, CECO 85, Tempo 90, BSN 160)

---

## Site Absorption (legacy redirects)

- [ ] **artofgig.com** → redirect to `books.venkateshrao.com/artofgig-vol3/` (series page or vol3 detail)
- [ ] **venkateshrao.com/twitter-book/** → redirect to `books.venkateshrao.com/twitterbook/`
- [ ] **breakingsmart.com** → redirect to `books.venkateshrao.com/breakingsmart/`; shut down WordPress instance

---

## Dashboard Evolution

- [ ] Update `Dashboard/build.py` to read stage/editions/ISBNs from `registry.json` for richer production view
- [ ] Deprecate `display:` flag in `status.md` files (registry.json is now authoritative)
- [ ] Consider moving dashboard to `books.venkateshrao.com/dashboard/` with passphrase gate

---

## Art of Gig Vol. 1 and Vol. 2

- [ ] Vol. 1 and Vol. 2 are buy-only (no online edition) — consider adding online editions if source HTML is available in `../artofgig/`

---

## Transmittal Automation

- [ ] Build script to POST to editor transmittal form when book moves to beta — needs credentials for `jdbb-prod.exe.xyz/vgr/`

---

## Workflow Reminder

After adding or updating a book:
```bash
# Edit registry.json and/or blurbs.md
python3 build_catalog.py          # regenerate all HTML + sitemap/llms.txt
python3 generate_social_cards.py  # regenerate social card images
git add docs/ registry.json blurbs.md
git commit -m "..." && git push
```
