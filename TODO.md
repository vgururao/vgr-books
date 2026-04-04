# VGR Books — To-Do List

Items to resolve in future sessions. Add buy links directly to `registry.json` when available.

## Buy Links Needed

All buy links resolved. ✓

## Cover Images Needed

Drop images in `inbox/` named `{id}.jpg` (see `inbox/README.md`).

| Book | id | Notes |
|------|----|-------|
| The Gervais Principle | `gervais-principle` | Current thumb is poor quality — source better version |
| Be Slightly Evil | `be-slightly-evil` | Current thumb is poor quality — source better version |
| Configurancy: Tempo | `configurancy-tempo` | Current thumb is poor quality — source better version |

## Catalog Display Polish

- [ ] Review `sort_order` values in `registry.json` — decide final display order (current: AoG 10–30, Twitter 40, BS 50, Mediocratopia 60, Rust Age 81–84, CECO 85, Tempo 90, BSN 160)
- [ ] Layout improvements: series grouping/headers, hero row for featured books, better coming-soon card treatment — edit `docs/style.css`
- [ ] Site metadata: update `<title>`, `<meta description>`, OG tags, H1 byline, footer, add intro paragraph — all in HTML template in `build_catalog.py`
- [ ] Add nav strip linking to venkateshrao.com, ribbonfarm.com, contraptions, artofgig.com — add to `build_catalog.py` template

## Dashboard Evolution

- [ ] Update `Dashboard/build.py` to read stage/editions/ISBNs from `registry.json` for richer production view
- [ ] Deprecate `display:` flag in status.md files (registry.json is now authoritative)

## Art of Gig Vol. 1 and Vol. 2

- [ ] Vol. 1 and Vol. 2 are ebook-only (no online edition) — confirm buy links are correct in registry.json
- [ ] Consider adding Vol. 1+2 online editions if source HTML is available

## Hosting

- Choose hosting platform (GitHub Pages / Vercel / Netlify / Cloudflare Pages)
- Configure DNS: `books.venkateshrao.com` CNAME
- Add `docs/CNAME` (GitHub Pages) or equivalent
- Set up redirect rules for old domains → new URLs

## Site Absorption (from consolidation plan)

- [ ] Phase 1: Absorb artofgig.com → redirect to books.venkateshrao.com/artofgig/
- [ ] Phase 2: Retire venkateshrao.com/twitter-book/ redirect
- [ ] Phase 3: Cut DNS breakingsmart.com → books.venkateshrao.com/breakingsmart/; shut down WordPress
- [ ] Phase 5: Ribbonfarm Archives — decide which series get online editions and prioritize pipeline

## Dashboard Deployment

- [ ] Move dashboard from venkateshrao.com/pubdashboard/ → books.venkateshrao.com/dashboard/
  - Update `Dashboard/publish.py`: change target from `vgururao.github.io/pubdashboard/` to vgr-books `docs/dashboard/`
  - Add password protection (HTTP Basic Auth via hosting platform config, or lightweight JS passphrase gate)
  - Update live URL reference in `Dashboard/CLAUDE.md` and `Dashboard/publish.py`
  - Do this after hosting platform is chosen (see Hosting section above)

## Transmittal Automation

- Build script to POST to editor transmittal form when book moves to beta
- Needs: credentials/session for jdbb-prod.exe.xyz/vgr/
- Wire to stage change in registry.json
