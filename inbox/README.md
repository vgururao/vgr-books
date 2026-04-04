# Cover Image Inbox

Drop updated cover images here. At the start of the next session, tell Claude to "process the inbox" and it will move them to the right places, update registry.json, and rebuild the catalog.

## Naming convention

Files must be named using the book's `id` from `registry.json`:

| File name | Meaning | Destination |
|-----------|---------|-------------|
| `{id}.jpg` / `{id}.png` | Final or current cover | `docs/thumbnails/{id}.jpg` |
| `{id}-beta.jpg` / `{id}-beta.png` | Working mockup / early draft | `docs/thumbnails/{id}-beta.jpg` |

## Book IDs (for reference)

| id | Title |
|----|-------|
| `artofgig-vol1` | Foundations (Art of Gig Vol. 1) |
| `artofgig-vol2` | Superstructures (Art of Gig Vol. 2) |
| `artofgig-vol3` | The Yakverse Chronicles (Art of Gig Vol. 3) |
| `twitterbook` | vgr: The Twitter Years |
| `breakingsmart` | Breaking Smart |
| `mediocratopia` | Mediocratopia |
| `gervais-principle` | The Gervais Principle |
| `be-slightly-evil` | Be Slightly Evil |
| `configurancy-tempo` | Tempo (Configurancy Vol. 1) |
| `breaking-smart-newsletter` | Breaking Smart Newsletter |

## Image guidelines

- Web-resolution (75–150 dpi) is fine — no 300dpi print files
- JPG or PNG preferred; SVG accepted
- Roughly portrait/cover proportions (e.g. 300×450px or similar)
- Purpose-built thumb crops are ideal if available from the designer
