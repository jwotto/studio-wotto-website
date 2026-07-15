#!/usr/bin/env python3
"""
Werkt content.json bij: de lijst van alle content-items (projecten en blogs).

Gebruik:
  - Dubbelklik op tools/update-manifest.bat (Windows), of
  - Draai in een terminal:  python tools/build-manifest.py

Elke map in werk/ met een index.html die <meta name="wotto:type"> bevat,
telt als content-item. Mappen zonder die tag worden overgeslagen.
"""
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
WERK = BASE / "werk"


def is_content_item(folder: pathlib.Path) -> bool:
    index = folder / "index.html"
    if not index.exists():
        return False
    try:
        return "wotto:type" in index.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False


def main():
    if not WERK.is_dir():
        raise SystemExit("map werk/ niet gevonden naast tools/")
    folders = sorted(
        p.name for p in WERK.iterdir()
        if p.is_dir()
        and not p.name.startswith((".", "_"))
        and is_content_item(p)
    )
    (BASE / "content.json").write_text(
        json.dumps(folders, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"content.json bijgewerkt: {len(folders)} item(s)")
    for name in folders:
        print("  -", name)


if __name__ == "__main__":
    main()
