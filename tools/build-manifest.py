#!/usr/bin/env python3
"""
Werkt content.json bij: de lijst van alle content-items (projecten en blogs).

Gebruik:
  - Dubbelklik op tools/update-manifest.bat (Windows), of
  - Draai in een terminal:  python tools/build-manifest.py

Elke map in werk/ met een index.html die <meta name="wotto:type"> bevat,
telt als content-item. Mappen zonder die tag worden overgeslagen.

Een item met een ontbrekende coverfoto is nog niet af en wordt ook
overgeslagen, zodat er nooit een kapot kaartje op de site komt.
"""
import json
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parent.parent
WERK = BASE / "werk"


def check(folder: pathlib.Path):
    """Geeft (klaar_of_niet, reden) terug."""
    index = folder / "index.html"
    if not index.exists():
        return False, None                      # geen pagina: stilletjes overslaan
    try:
        txt = index.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False, None
    if "wotto:type" not in txt:
        return False, None                      # gewone pagina, geen content-item
    m = re.search(r'wotto:cover"\s+content="([^"]+)"', txt)
    cover = m.group(1) if m else "cover.jpg"
    if not (folder / cover).exists():
        return False, "coverfoto %s ontbreekt nog" % cover
    return True, None


def main():
    if not WERK.is_dir():
        raise SystemExit("map werk/ niet gevonden naast tools/")
    folders, skipped = [], []
    for p in sorted(WERK.iterdir()):
        if not p.is_dir() or p.name.startswith((".", "_")):
            continue
        ok, reden = check(p)
        if ok:
            folders.append(p.name)
        elif reden:
            skipped.append((p.name, reden))

    (BASE / "content.json").write_text(
        json.dumps(folders, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"content.json bijgewerkt: {len(folders)} item(s)")
    for name in folders:
        print("  -", name)
    if skipped:
        print("\nNog niet klaar, dus niet op de site gezet:")
        for name, reden in skipped:
            print(f"  - {name}: {reden}")


if __name__ == "__main__":
    main()
