#!/usr/bin/env python3
"""
Werkt content/manifest.json bij: een lijst van alle itemmappen in content/.

Gebruik:
  - Dubbelklik op update-manifest.bat (Windows), of
  - Draai in een terminal:  python content/build-manifest.py

Elke submap van content/ die een index.html bevat, komt in de lijst.
Mappen die met . of _ beginnen worden overgeslagen.
"""
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent

def main():
    folders = sorted(
        p.name for p in BASE.iterdir()
        if p.is_dir()
        and not p.name.startswith((".", "_"))
        and (p / "index.html").exists()
    )
    (BASE / "manifest.json").write_text(
        json.dumps(folders, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"manifest.json bijgewerkt: {len(folders)} item(s)")
    for name in folders:
        print("  -", name)

if __name__ == "__main__":
    main()
