#!/usr/bin/env python3
"""Sync book content from source projects into online-books/docs/<slug>/.

Usage:
    python3 sync.py                           # sync all books
    python3 sync.py artofgig-vol3             # sync one book
    python3 sync.py artofgig-vol3 twitterbook # sync multiple books
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

# Source paths relative to the shared Publishing/ parent directory
PUBLISHING = ROOT.parent

BOOKS = {
    "artofgig-vol3": {
        "source": PUBLISHING / "artofgig" / "docs",
        "exclude": ["CNAME"],  # artofgig.com CNAME doesn't belong here
        "description": "Art of Gig Vol 3: The Yakverse Chronicles",
        "url": "/artofgig-vol3/vol3_cover.html",
    },
    "twitterbook": {
        "source": PUBLISHING / "vgrtwitterbook" / "book",
        "exclude": [],
        "description": "vgr: The Twitter Years (2007–22)",
        "url": "/twitterbook/index.html",
    },
    "breakingsmart": {
        "source": PUBLISHING / "BreakingSmart" / "docs",
        "exclude": ["CNAME"],
        "description": "Breaking Smart: How Software is Eating the World",
        "url": "/breakingsmart/index.html",
    },
    "mediocratopia": {
        "source": PUBLISHING / "Ribbonfarm Archives" / "Mediocratopia" / "docs",
        "exclude": [],
        "description": "Mediocratopia",
        "url": "/mediocratopia/index.html",
    },
}


def sync_book(slug, book_info):
    src = book_info["source"]
    dst = DOCS / slug

    if not src.exists():
        print(f"  ERROR: source not found: {src}")
        return 1

    dst.mkdir(parents=True, exist_ok=True)

    cmd = ["rsync", "-av", "--delete", "--exclude=.DS_Store"]
    for excl in book_info["exclude"]:
        cmd += ["--exclude", excl]
    cmd += [str(src) + "/", str(dst) + "/"]

    print(f"\n=== Syncing {slug}: {book_info['description']} ===")
    print(f"  {src}/")
    print(f"  → {dst}/")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    slugs = sys.argv[1:] if len(sys.argv) > 1 else list(BOOKS.keys())
    errors = []

    for slug in slugs:
        if slug not in BOOKS:
            print(f"Unknown book: {slug}. Available: {', '.join(BOOKS)}")
            errors.append(slug)
            continue
        code = sync_book(slug, BOOKS[slug])
        if code != 0:
            errors.append(slug)

    print()
    if errors:
        print(f"Errors syncing: {', '.join(errors)}")
        sys.exit(1)
    else:
        print("All syncs complete.")
        print()
        print("Next steps:")
        print("  git add docs/ && git commit -m 'Sync books' && git push")


if __name__ == "__main__":
    main()
