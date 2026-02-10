"""Parse 2021 Panini Select Football CSV - extract base tiers (empty SEQUENCE only)."""
import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "panini-checklists-csv-files", "2021 Panini Select (Football).csv")
OUT_PATH = os.path.join(BASE_DIR, "data", "panini_select_2021_football.py")

def main():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        all_cards = []
        for row in r:
            cs = row.get("CARD SET", "")
            seq = row.get("SEQUENCE", "").strip()
            if seq:
                continue
            athlete = row.get("ATHLETE", "").strip().replace('""', '"')
            team = row.get("TEAM", "").strip()
            card_num = row.get("CARD NUMBER", "").strip()
            if cs == "Base Premier Level":
                all_cards.append((card_num, athlete, team, "Premier", ""))
            elif cs == "Base Club Level":
                all_cards.append((card_num, athlete, team, "Club", ""))
            elif cs == "Base Field Level":
                all_cards.append((card_num, athlete, team, "Field", ""))

    tier_order = {"Premier": 0, "Club": 1, "Field": 2}
    all_cards.sort(key=lambda x: (tier_order[x[3]], int(x[0])))

    lines = [
        '"""',
        "2021 Panini Select Football — Base (300 cards)",
        "Three tiers: Premier (101-200), Club (201-300), Field (301-400)",
        "Source: panini-checklists-csv-files (rows with empty SEQUENCE = base cards)",
        '"""',
        "",
        "BASE_SET = [",
    ]
    for c in all_cards:
        lines.append(f'    ("{c[0]}", "{c[1]}", "{c[2]}", "{c[3]}", "{c[4]}"),')
    lines.extend([
        "]",
        "",
        "ALL_CARDS = BASE_SET",
        "PREFIX_INFO = {",
        '    "Premier": ("Premier Level (101-200)", "Base", "Higher-end base tier"),',
        '    "Club": ("Club Level (201-300)", "Base", "Mid-tier base"),',
        '    "Field": ("Field Level (301-400)", "Base", "Standard base tier"),',
        "}",
    ])

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {OUT_PATH} — {len(all_cards)} cards")

if __name__ == "__main__":
    main()
