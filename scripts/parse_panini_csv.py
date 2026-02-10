"""
Parse Panini CSV checklists and output Python data format for app.
Usage: python scripts/parse_panini_csv.py
"""
import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, "panini-checklists-csv-files")
DATA_DIR = os.path.join(BASE_DIR, "data")

def parse_csv(path, card_set_filter, sport=None, year=None):
    """Extract rows where CARD SET matches filter. Returns list of (card_num, athlete, team, card_type, notes)."""
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("CARD SET") != card_set_filter:
                continue
            if sport and row.get("SPORT") != sport:
                continue
            if year and str(row.get("YEAR", "")) != str(year):
                continue
            # Avoid duplicates (e.g. parallels with SEQUENCE) - take first occurrence only
            card_num = row.get("CARD NUMBER", "").strip()
            athlete = row.get("ATHLETE", "").strip().replace('""', '"')
            team = row.get("TEAM", "").strip()
            seq = row.get("SEQUENCE", "").strip()
            if seq:  # Has sequence = parallel, skip
                continue
            if not card_num or not athlete:
                continue
            rows.append((card_num, athlete, team))
    return rows

def write_py_file(path, var_name, cards, card_type, notes_suffix, docstring):
    """Write Python file with ALL_CARDS and PREFIX_INFO."""
    lines = [f'"""', docstring, '"""', ""]
    lines.append(f'{var_name} = [')
    for card_num, athlete, team in cards:
        notes = notes_suffix if "Rookie" in card_type or "RC" in notes_suffix else ""
        lines.append(f'    ("{card_num}", "{athlete}", "{team}", "{card_type}", "{notes}"),')
    lines.append("]")
    lines.append("")
    lines.append("ALL_CARDS = " + var_name)
    lines.append("PREFIX_INFO = {}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    # 2021 Panini Prizm Football - Base only (330 cards)
    csv_path = os.path.join(CSV_DIR, "2021 Panini Prizm (Football).csv")
    if os.path.exists(csv_path):
        base = parse_csv(csv_path, "Base", "Football", 2021)
        out_path = os.path.join(DATA_DIR, "panini_prizm_2021_football.py")
        write_py_file(out_path, "BASE_SET", base, "Base", "",
            "2021 Panini Prizm Football — Base Set (330 cards)\nSource: panini-checklists-csv-files")
        print(f"Wrote {out_path} ({len(base)} cards)")

    # 2021 Panini Mosaic Football - Base only (200 cards)
    csv_path = os.path.join(CSV_DIR, "2021 Panini Mosaic (Football).csv")
    if os.path.exists(csv_path):
        base = parse_csv(csv_path, "Base", "Football", 2021)
        out_path = os.path.join(DATA_DIR, "panini_mosaic_2021_football.py")
        write_py_file(out_path, "BASE_SET", base, "Base", "",
            "2021 Panini Mosaic Football — Base Set (200 cards)\nSource: panini-checklists-csv-files")
        print(f"Wrote {out_path} ({len(base)} cards)")

    # 2020 Panini Prizm Basketball - Base only (300 cards)
    csv_path = os.path.join(CSV_DIR, "2020 Panini Prizm (20-21) (Basketball).csv")
    if os.path.exists(csv_path):
        base = parse_csv(csv_path, "Base", "Basketball", 2020)
        out_path = os.path.join(DATA_DIR, "panini_prizm_2020_basketball.py")
        write_py_file(out_path, "BASE_SET", base, "Base", "",
            "2020-21 Panini Prizm Basketball — Base Set (300 cards)\nSource: panini-checklists-csv-files")
        print(f"Wrote {out_path} ({len(base)} cards)")

if __name__ == "__main__":
    main()
