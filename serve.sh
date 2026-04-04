#!/usr/bin/env bash
set -euo pipefail

# Local development server for books.venkateshrao.com
#
# Before first run, sync book content from source projects:
#   python3 sync.py
#
# Then serve:
#   bash serve.sh

PORT="${1:-8080}"
DOCS="$(cd "$(dirname "$0")/docs" && pwd)"

echo "=== VGR Books — local dev server ==="
echo ""
echo "Serving: $DOCS"
echo "Open:    http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop."
echo ""

cd "$DOCS"
python3 -m http.server "$PORT"
