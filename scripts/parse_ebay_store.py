"""
Parse Card Investors Lounge eBay store listings into structured CSV.
Extracts player, variant, price, and metadata from listing titles.
"""

import csv
import re
import json
from pathlib import Path

PLAYER_KEYWORDS = [
    "Anthony Edwards", "LeBron James", "Nikola Jokic", "Stephen Curry",
    "Shohei Ohtani", "Aaron Judge", "Victor Wembanyama", "Luka Doncic",
    "Tom Brady", "Mike Trout", "Ken Griffey Jr.", "Giannis Antetokounmpo",
    "Patrick Mahomes", "Caitlin Clark", "Jayson Tatum", "Kylian Mbappe",
    "Lionel Messi", "Bryce Harper", "Justin Herbert", "Ja Morant",
    "Lamelo Ball", "LaMelo Ball", "Kevin Durant", "Kyrie Irving",
    "Shai Gilgeous-Alexander", "Tyrese Maxey", "Drake Maye",
    "Gunnar Henderson", "Kevin Garnett", "Larry Bird", "Roblox",
    "Jalen Hurts", "Conor McGregor", "Fernando Tatis Jr.",
    "Corbin Carroll", "Paul Skenes", "Hyeseong Kim", "Crocs",
    "Jared McCain", "Bryce Young", "Yao Ming", "Francisco Lindor",
    "Kawhi Leonard", "Bo Bichette", "Jarren Duran", "Nick Kurtz",
]

SPORT_HINTS = {
    "NBA": "Basketball", "Lakers": "Basketball", "Warriors": "Basketball",
    "Nuggets": "Basketball", "Timberwolves": "Basketball", "T-Wolves": "Basketball",
    "Mavericks": "Basketball", "Celtics": "Basketball", "Bucks": "Basketball",
    "Hornets": "Basketball", "Spurs": "Basketball", "Thunder": "Basketball",
    "Suns": "Basketball", "Clippers": "Basketball", "76ers": "Basketball",
    "Yankees": "Baseball", "Dodgers": "Baseball", "Angels": "Baseball",
    "Mariners": "Baseball", "Phillies": "Baseball", "Orioles": "Baseball",
    "MLB": "Baseball", "Topps": "Baseball",
    "Chiefs": "Football", "Patriots": "Football", "Buccaneers": "Football",
    "Eagles": "Football", "Chargers": "Football", "NFL": "Football",
    "FIFA": "Soccer", "World Cup": "Soccer", "France": "Soccer",
    "Real Madrid": "Soccer",
}

LISTINGS = []


def detect_player(title):
    for player in sorted(PLAYER_KEYWORDS, key=len, reverse=True):
        if player.lower() in title.lower():
            return player
    return ""


def detect_sport(title):
    for hint, sport in SPORT_HINTS.items():
        if hint.lower() in title.lower():
            return sport
    return "Unknown"


def detect_variant(title):
    variants = ["Refractor", "Prizm", "Holo", "Chrome", "Art Card", "Art Print",
                 "Rookie", "RC", "Display", "Jam Masters", "Revolution",
                 "Clear", "Ice", "Silver", "Gold", "Red", "Blue", "Green",
                 "Purple", "Pink", "Black", "Orange", "SSP", "SP"]
    found = []
    for v in variants:
        if v.lower() in title.lower():
            found.append(v)
    return " / ".join(found[:3]) if found else "Base"


def detect_brand(title):
    brands = ["Topps", "Panini", "Bowman", "Donruss", "Prizm", "Select",
              "Mosaic", "Optic", "Hoops", "Chronicles", "Fleer"]
    for b in brands:
        if b.lower() in title.lower():
            return b
    return ""


def parse_price(price_str):
    match = re.search(r'\$(\d+\.?\d*)', price_str.replace(",", ""))
    return float(match.group(1)) if match else 0.0


def parse_store_text(text_block):
    """Parse the raw eBay store text dump into structured listings."""
    lines = text_block.strip().split("\n")
    listings = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line or line.startswith("Shop on eBay") or line.startswith("Sponsored"):
            i += 1
            continue

        if ("ENCASED" in line or "Encased" in line or "encased" in line or
            "MINT" in line or "Investment" in line or "Refractor" in line or
            "Rookie" in line or "RC" in line or "Prizm" in line or
            "Art Card" in line):

            title = line.replace("NEW LOW PRICE", "").replace("New Listing", "").strip()
            if title.startswith("Opens in a new"):
                i += 1
                continue

            player = detect_player(title)
            sport = detect_sport(title)
            variant = detect_variant(title)
            brand = detect_brand(title)

            price = 0.0
            watchers = 0
            condition = "Pre-Owned"

            for j in range(1, min(8, len(lines) - i)):
                next_line = lines[i + j].strip() if (i + j) < len(lines) else ""
                if "$" in next_line and price == 0:
                    price = parse_price(next_line)
                if "watcher" in next_line.lower():
                    wm = re.search(r'(\d+)\s*watcher', next_line.lower())
                    if wm:
                        watchers = int(wm.group(1))

            if player and price > 0:
                listings.append({
                    "title": title,
                    "player": player,
                    "sport": sport,
                    "variant": variant,
                    "brand": brand,
                    "price": price,
                    "original_price": "",
                    "condition": condition,
                    "watchers": watchers,
                    "status": "Active",
                })

        i += 1

    seen = set()
    unique = []
    for l in listings:
        key = l["title"][:60]
        if key not in seen:
            seen.add(key)
            unique.append(l)

    return unique


# Hardcoded inventory from store scrape data
STORE_INVENTORY = [
    {"title": "Stephen Curry Rare Refractor Display MVP Warriors Collectible MINT ENCASED", "player": "Stephen Curry", "sport": "Basketball", "variant": "Refractor / Display", "brand": "Panini", "price": 65.50, "watchers": 16},
    {"title": "LeBron James RARE REFRACTOR SSP Investment Card Lakers MVP MINT ENCASED", "player": "LeBron James", "sport": "Basketball", "variant": "Refractor / SSP", "brand": "Panini", "price": 44.50, "watchers": 42},
    {"title": "50/50 Shohei Ohtani RARE Refractor SSP Investment Card Dodgers 50/50 ENCASED", "player": "Shohei Ohtani", "sport": "Baseball", "variant": "Refractor / SSP", "brand": "Topps", "price": 55.50, "watchers": 161},
    {"title": "Anthony Edwards RARE ROOKIE RC DIAMOND REFRACTOR SSP INVESTMENT CARD ENCASED", "player": "Anthony Edwards", "sport": "Basketball", "variant": "Rookie / RC / Refractor / SSP", "brand": "Panini", "price": 125.00, "watchers": 56},
    {"title": "Anthony Edwards RARE ROOKIE RC DIAMOND REFRACTOR SSP INVESTMENT CARD ENCASED (Asia Red)", "player": "Anthony Edwards", "sport": "Basketball", "variant": "Rookie / RC / Refractor / SSP / Red", "brand": "Panini", "price": 150.00, "watchers": 10},
    {"title": "Tom Brady RARE Display Clear Investment Card MVP Buccaneers Encased", "player": "Tom Brady", "sport": "Football", "variant": "Clear / Display", "brand": "Panini", "price": 55.50, "watchers": 27},
    {"title": "Stephen Curry 2016 NBA Art Card MVP Warriors Collectible MINT ENCASED", "player": "Stephen Curry", "sport": "Basketball", "variant": "Art Card", "brand": "Panini", "price": 65.50, "watchers": 34},
    {"title": "Nikola Jokic RARE REFRACTOR PRIZM INVESTMENT CARD DENVER NUGGETS MINT ENCASED", "player": "Nikola Jokic", "sport": "Basketball", "variant": "Refractor / Prizm", "brand": "Panini", "price": 65.00, "watchers": 0},
    {"title": "Victor Wembanyama RARE Refractor Investment Card Topps MINT ENCASED", "player": "Victor Wembanyama", "sport": "Basketball", "variant": "Refractor", "brand": "Topps", "price": 65.00, "watchers": 12},
    {"title": "Anthony Edwards RARE DISPLAY REFRACTOR SSP INVESTMENT CARD T-Wolves MVP ENCASED", "player": "Anthony Edwards", "sport": "Basketball", "variant": "Display / Refractor / SSP", "brand": "Panini", "price": 44.50, "watchers": 19},
    {"title": "50/50 Shohei Ohtani RARE Topps Refractor Investment Card Dodgers 50/50 ENCASED", "player": "Shohei Ohtani", "sport": "Baseball", "variant": "Refractor", "brand": "Topps", "price": 55.50, "watchers": 0},
    {"title": "Stephen Curry RARE RED REFRACTOR SSP PANINI WARRIORS MINT Encased", "player": "Stephen Curry", "sport": "Basketball", "variant": "Red / Refractor / SSP", "brand": "Panini", "price": 45.50, "watchers": 30},
    {"title": "Victor Wembanyama RARE Jam Masters Refractor Investment Card Panini ENCASED", "player": "Victor Wembanyama", "sport": "Basketball", "variant": "Jam Masters / Refractor", "brand": "Panini", "price": 54.50, "watchers": 19},
    {"title": "Victor Wembanyama RARE Refractor Investment Card Panini ROTY MINT ENCASED", "player": "Victor Wembanyama", "sport": "Basketball", "variant": "Refractor", "brand": "Panini", "price": 54.50, "watchers": 28},
    {"title": "Anthony Edwards RARE HOLO REFRACTOR SSP INVESTMENT CARD PANINI MVP MINT ENCASED", "player": "Anthony Edwards", "sport": "Basketball", "variant": "Holo / Refractor / SSP", "brand": "Panini", "price": 44.50, "watchers": 40},
    {"title": "LeBron James RARE Refractor Prizm SSP Investment Card Lakers MVP MINT ENCASED", "player": "LeBron James", "sport": "Basketball", "variant": "Refractor / Prizm / SSP", "brand": "Panini", "price": 55.50, "watchers": 0},
    {"title": "Shohei Ohtani RARE Display Refractor Investment Card Topps Dodgers 50/50 ENCASED", "player": "Shohei Ohtani", "sport": "Baseball", "variant": "Display / Refractor", "brand": "Topps", "price": 55.50, "watchers": 0},
    {"title": "Anthony Edwards RARE ROOKIE RC HOLO FOIL REFRACTOR SSP INVESTMENT CARD ENCASED", "player": "Anthony Edwards", "sport": "Basketball", "variant": "Rookie / RC / Holo / Refractor / SSP", "brand": "Panini", "price": 48.50, "watchers": 32},
    {"title": "Shohei Ohtani RARE Refractor SSP Investment Card Topps Dodgers 50/50 ENCASED", "player": "Shohei Ohtani", "sport": "Baseball", "variant": "Refractor / SSP", "brand": "Topps", "price": 45.50, "watchers": 0},
    {"title": "Nikola Jokic RARE PINK PRIZM REFRACTOR INVESTMENT CARD PANINI NUGGETS ENCASED", "player": "Nikola Jokic", "sport": "Basketball", "variant": "Pink / Prizm / Refractor", "brand": "Panini", "price": 45.00, "watchers": 0},
    {"title": "Luka Doncic RARE REFRACTOR INVESTMENT CARD SSP MAVERICKS MVP MINT ENCASED", "player": "Luka Doncic", "sport": "Basketball", "variant": "Refractor / SSP", "brand": "Panini", "price": 55.50, "watchers": 19},
    {"title": "LeBron James Rare JAM MASTERS Refractor Los Angeles Lakers NBA MVP Mint Encased", "player": "LeBron James", "sport": "Basketball", "variant": "Jam Masters / Refractor", "brand": "Panini", "price": 44.50, "watchers": 20},
    {"title": "Luka Doncic RARE REFRACTOR INVESTMENT CARD SSP MAVERICKS MVP MINT ENCASED (2)", "player": "Luka Doncic", "sport": "Basketball", "variant": "Refractor / SSP", "brand": "Panini", "price": 44.50, "watchers": 15},
    {"title": "LeBron James Art Card RARE MVP NBA Cavaliers Encased", "player": "LeBron James", "sport": "Basketball", "variant": "Art Card", "brand": "Panini", "price": 65.50, "watchers": 36},
    {"title": "Stephen Curry 2016 NBA Art Card Rare Orange Refractor Warriors MINT ENCASED", "player": "Stephen Curry", "sport": "Basketball", "variant": "Art Card / Orange / Refractor", "brand": "Panini", "price": 95.50, "watchers": 3},
    {"title": "Anthony Edwards RARE REFRACTOR SSP INVESTMENT CARD T-Wolves MVP MINT ENCASED", "player": "Anthony Edwards", "sport": "Basketball", "variant": "Refractor / SSP", "brand": "Panini", "price": 48.50, "watchers": 85},
    {"title": "Giannis Antetokounmpo RARE Purple Refractor Investment Card Panini Bucks ENCASED", "player": "Giannis Antetokounmpo", "sport": "Basketball", "variant": "Purple / Refractor", "brand": "Panini", "price": 47.50, "watchers": 25},
    {"title": "Mike Trout Blueprint Topps Rare Refractor Angels Encased", "player": "Mike Trout", "sport": "Baseball", "variant": "Refractor", "brand": "Topps", "price": 44.50, "watchers": 21},
    {"title": "Nikola Jokic Encased Black Refractor NBA Investment Card Nuggets MVP DISPLAY", "player": "Nikola Jokic", "sport": "Basketball", "variant": "Black / Refractor / Display", "brand": "Panini", "price": 55.00, "watchers": 0},
    {"title": "LeBron James RARE Refractor MVP NBA LA Lakers Beautiful Encased", "player": "LeBron James", "sport": "Basketball", "variant": "Refractor", "brand": "Panini", "price": 65.50, "watchers": 16},
    {"title": "40/40 Shohei Ohtani RARE Topps Refractor Investment Card 40/40 ENCASED", "player": "Shohei Ohtani", "sport": "Baseball", "variant": "Refractor", "brand": "Topps", "price": 65.00, "watchers": 0},
    {"title": "Nikola Jokic Encased Investment Card NBA Nuggets MINT DISPLAY", "player": "Nikola Jokic", "sport": "Basketball", "variant": "Display", "brand": "Panini", "price": 42.50, "watchers": 16},
    {"title": "Shohei Ohtani 50/50 Dodgers Display Card Encased Rare Collectible", "player": "Shohei Ohtani", "sport": "Baseball", "variant": "Display", "brand": "Topps", "price": 50.50, "watchers": 21},
    {"title": "Aaron Judge RARE Mini Refractor Chrome SP Yankees MVP MINT ENCASED", "player": "Aaron Judge", "sport": "Baseball", "variant": "Refractor / Chrome / SP", "brand": "Topps", "price": 55.50, "watchers": 0},
    {"title": "LeBron James RARE Ice Refractor Lakers MVP MINT ENCASED Investment", "player": "LeBron James", "sport": "Basketball", "variant": "Ice / Refractor", "brand": "Panini", "price": 55.00, "watchers": 0},
    {"title": "Anthony Edwards RARE HOLO REFRACTOR INVESTMENT CARD PANINI MVP MINT ENCASED (2)", "player": "Anthony Edwards", "sport": "Basketball", "variant": "Holo / Refractor", "brand": "Panini", "price": 44.50, "watchers": 0},
    {"title": "Nikola Jokic RARE REFRACTOR SSP INVESTMENT CARD Denver Nuggets MVP MINT ENCASED", "player": "Nikola Jokic", "sport": "Basketball", "variant": "Refractor / SSP", "brand": "Panini", "price": 53.50, "watchers": 0},
    {"title": "Stephen Curry RARE Red Refractor Investment Card Panini Warriors MINT ENCASED", "player": "Stephen Curry", "sport": "Basketball", "variant": "Red / Refractor", "brand": "Panini", "price": 55.50, "watchers": 0},
    {"title": "2025 Anthony Edwards RARE LIMITED STOCK LEGEND INVESTMENT CARD Topps MVP ENCASED", "player": "Anthony Edwards", "sport": "Basketball", "variant": "SP", "brand": "Topps", "price": 44.50, "watchers": 11},
    {"title": "Nikola Jokic RARE REFRACTOR PRIZM INVESTMENT CARD SSP NUGGETS MVP MINT ENCASED", "player": "Nikola Jokic", "sport": "Basketball", "variant": "Refractor / Prizm / SSP", "brand": "Panini", "price": 55.50, "watchers": 0},
    {"title": "40/40 Shohei Ohtani RARE Topps Refractor Investment Card Dodgers 40/40 ENCASED", "player": "Shohei Ohtani", "sport": "Baseball", "variant": "Refractor", "brand": "Topps", "price": 55.50, "watchers": 6},
    {"title": "Stephen Curry RARE Black Display Refractor SSP Panini Warriors MINT ENCASED", "player": "Stephen Curry", "sport": "Basketball", "variant": "Black / Display / Refractor / SSP", "brand": "Panini", "price": 55.50, "watchers": 0},
    {"title": "Nikola Jokic RARE REFRACTOR SSP INVESTMENT CARD Denver Nuggets MVP ENCASED (top)", "player": "Nikola Jokic", "sport": "Basketball", "variant": "Refractor / SSP", "brand": "Panini", "price": 48.50, "watchers": 69},
    {"title": "Aaron Judge RARE Refractor SSP Investment Card Topps New York Yankees ENCASED", "player": "Aaron Judge", "sport": "Baseball", "variant": "Refractor / SSP", "brand": "Topps", "price": 48.50, "watchers": 0},
    {"title": "Historic 2025 Shohei Ohtani RARE Refractor Investment Card Dodgers 50/50 ENCASED", "player": "Shohei Ohtani", "sport": "Baseball", "variant": "Refractor", "brand": "Topps", "price": 55.50, "watchers": 0},
    {"title": "Nikola Jokic RARE REFRACTOR PRIZM INVESTMENT CARD SSP NUGGETS MVP (30 watch)", "player": "Nikola Jokic", "sport": "Basketball", "variant": "Refractor / Prizm / SSP", "brand": "Panini", "price": 44.50, "watchers": 30},
    {"title": "LeBron James Rare Refractor SSP Lakers MVP Encased Mint Investment", "player": "LeBron James", "sport": "Basketball", "variant": "Refractor / SSP", "brand": "Panini", "price": 44.50, "watchers": 0},
    {"title": "Anthony Edwards RARE WHITE BEAUTIFUL INVESTMENT CARD MVP Antman ENCASED", "player": "Anthony Edwards", "sport": "Basketball", "variant": "SP", "brand": "Panini", "price": 44.50, "watchers": 6},
    {"title": "Ken Griffey Jr. RARE REFRACTOR TOPPS CHROME INVESTMENT CARD MARINERS ENCASED", "player": "Ken Griffey Jr.", "sport": "Baseball", "variant": "Refractor / Chrome", "brand": "Topps", "price": 95.00, "watchers": 0},
    {"title": "2025 Panini Caitlin Clark Rare Iowa Hawkeyes Refractor Investment Card Encased", "player": "Caitlin Clark", "sport": "Basketball", "variant": "Refractor", "brand": "Panini", "price": 45.50, "watchers": 0},
    {"title": "Aaron Judge RARE Mini Display Refractor Chrome SP Yankees MINT ENCASED", "player": "Aaron Judge", "sport": "Baseball", "variant": "Refractor / Chrome / SP / Display", "brand": "Topps", "price": 65.00, "watchers": 0},
    {"title": "Nikola Jokic RARE Clear Refractor SSP Panini Nuggets MVP ENCASED", "player": "Nikola Jokic", "sport": "Basketball", "variant": "Clear / Refractor / SSP", "brand": "Panini", "price": 45.50, "watchers": 15},
    {"title": "Shohei Ohtani RARE ART PRINT INVESTMENT CARD TOPPS 50/50 MVP MINT ENCASED", "player": "Shohei Ohtani", "sport": "Baseball", "variant": "Art Print", "brand": "Topps", "price": 65.00, "watchers": 0},
    {"title": "Nikola Jokic Encased Green Refractor Investment Card NBA Nuggets MINT DISPLAY", "player": "Nikola Jokic", "sport": "Basketball", "variant": "Green / Refractor / Display", "brand": "Panini", "price": 65.00, "watchers": 0},
    {"title": "Stephen Curry 2016 NBA Art Card MVP Warriors MINT ENCASED (2)", "player": "Stephen Curry", "sport": "Basketball", "variant": "Art Card", "brand": "Panini", "price": 65.50, "watchers": 0},
    {"title": "LEBRON JAMES REFRACTOR SP Number 23 LAKERS LEGEND Beautiful Card ENCASED", "player": "LeBron James", "sport": "Basketball", "variant": "Refractor / SP", "brand": "Panini", "price": 65.00, "watchers": 0},
    {"title": "Nikola Jokic Encased NBA Investment Card Nuggets MVP MINT DISPLAY (19 watch)", "player": "Nikola Jokic", "sport": "Basketball", "variant": "Display", "brand": "Panini", "price": 48.50, "watchers": 19},
    {"title": "Tom Brady RARE Blue Refractor SSP Investment Card Pats ENCASED", "player": "Tom Brady", "sport": "Football", "variant": "Blue / Refractor / SSP", "brand": "Panini", "price": 55.50, "watchers": 13},
    {"title": "Anthony Edwards GOLD Revolution Refractor SSP Timberwolves Encased", "player": "Anthony Edwards", "sport": "Basketball", "variant": "Gold / Revolution / Refractor / SSP", "brand": "Panini", "price": 75.50, "watchers": 27},
]

def main():
    output = Path(__file__).parent.parent / "data" / "card_investors_lounge_inventory.csv"
    output.parent.mkdir(exist_ok=True)

    for item in STORE_INVENTORY:
        item.setdefault("condition", "Pre-Owned")
        item.setdefault("status", "Active")
        item.setdefault("watchers", 0)

    fieldnames = ["title", "player", "sport", "variant", "brand", "price", "condition", "watchers", "status"]

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(STORE_INVENTORY)

    print(f"Wrote {len(STORE_INVENTORY)} listings to {output}")

    by_player = {}
    for item in STORE_INVENTORY:
        p = item["player"]
        by_player[p] = by_player.get(p, 0) + 1
    print("\nBy player:")
    for p, c in sorted(by_player.items(), key=lambda x: -x[1]):
        print(f"  {p}: {c} listings")

    by_sport = {}
    for item in STORE_INVENTORY:
        s = item["sport"]
        by_sport[s] = by_sport.get(s, 0) + 1
    print("\nBy sport:")
    for s, c in sorted(by_sport.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c} listings")

    total_value = sum(item["price"] for item in STORE_INVENTORY)
    print(f"\nTotal inventory value: ${total_value:,.2f}")
    print(f"Average price: ${total_value/len(STORE_INVENTORY):,.2f}")
    total_watchers = sum(item["watchers"] for item in STORE_INVENTORY)
    print(f"Total watchers: {total_watchers}")


if __name__ == "__main__":
    main()
