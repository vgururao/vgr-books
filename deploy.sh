#!/usr/bin/env bash
set -euo pipefail

# Deploy books.venkateshrao.com
# Hosting: TBD — update this script once a platform is chosen.
#
# Options:
#   GitHub Pages:  git push (auto-deploys from docs/ on main branch)
#   Vercel:        vercel --prod
#   Netlify:       netlify deploy --prod --dir docs
#   Cloudflare:    wrangler pages deploy docs

echo "=== Online Books Deploy ==="
echo ""
echo "Step 1: Sync all books from source projects:"
echo "  python3 sync.py"
echo ""
echo "Step 2: Commit and push:"
echo "  git add docs/ && git commit -m 'Sync books' && git push"
echo ""
echo "Hosting not yet configured. Update this script after choosing a platform."
echo ""
echo "See CLAUDE.md for hosting options and redirect strategy."
