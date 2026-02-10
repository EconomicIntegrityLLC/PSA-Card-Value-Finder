"""
eBay Listing Generator for Trading Cards
Fills ALL eBay item specifics - no Ollama required.
Uses reference DB for value context. You provide card details.
"""

import sqlite3
import os
from typing import Dict, Optional, List
from pathlib import Path

DB_PATH = "data/reference.db"
EBAY_TITLE_MAX = 80

# eBay 2025/2026 Item Specifics - Sports Trading Card Singles
# Condition descriptors per eBay (ungraded cards)
CONDITION_OPTIONS = [
    "Near Mint or Better",  # Minor chipping on corners/edges
    "Excellent",           # Moderate corner wear, slightly rough edges
    "Very Good",            # Rounding on corners, moderate chipping
    "Poor",                 # Major damage, missing corners
]

# Sport mapping for eBay
SPORT_EBAY = {
    "football": "Football",
    "baseball": "Baseball",
    "basketball": "Basketball",
    "hockey": "Ice Hockey",
}

# Brand options (common)
BRANDS = ["Topps", "Panini", "Upper Deck", "Donruss", "Fleer", "Score", "Bowman", "Leaf", "Stadium Club", "Fleer Ultra", "Hoops", "O-Pee-Chee", "Sportflics", "SkyBox", "Sports Illustrated", "Other"]


def _truncate_title(title: str, max_len: int = EBAY_TITLE_MAX) -> str:
    if len(title) <= max_len:
        return title
    return title[:max_len].rsplit(' ', 1)[0][:max_len]


def _lookup_reference(player: str, set_name: str, year: int, sport: str) -> Dict:
    """Check if card is in our valuable reference - adds listing boost context."""
    result = {"key_player": False, "tier1_set": False, "tier2_set": False, "notes": ""}
    if not os.path.exists(DB_PATH):
        return result

    with sqlite3.connect(DB_PATH) as conn:
        if player:
            row = conn.execute(
                "SELECT 1 FROM key_players WHERE LOWER(player_name) = LOWER(?)",
                (player.strip(),)
            ).fetchone()
            result["key_player"] = bool(row)

        # Match set (flexible - "1986 Fleer" matches "1986 Fleer Basketball")
        set_lower = (set_name or "").lower()
        for row in conn.execute("SELECT set_name, tier, notes, key_cards FROM valuable_sets"):
            db_set, tier, notes, key_cards = row
            if db_set.lower() in set_lower or set_lower in db_set.lower():
                if tier == 1:
                    result["tier1_set"] = True
                    result["notes"] = notes or ""
                else:
                    result["tier2_set"] = True
                    result["notes"] = key_cards or ""
                break

    return result


def build_full_listing(
    player: str,
    year: int,
    set_name: str,
    brand: str,
    sport: str,
    card_number: str = "",
    team: str = "",
    is_rookie: bool = False,
    is_graded: bool = False,
    grade: str = "",
    cert_number: str = "",
    condition: str = "Near Mint or Better",
    variety: str = "Base",  # Base, Refractor, Silver Prizm, Holo, etc.
    features: str = "",    # Serial Numbered, Autograph, etc.
    description_extra: str = "",
    suggested_price: str = "",
) -> Dict:
    """
    Build a complete eBay listing with ALL item specifics filled.
    """
    sport_ebay = SPORT_EBAY.get(sport.lower(), sport.title())
    ref = _lookup_reference(player, set_name, year, sport)

    # Build title (eBay format: Year Brand Player Set [Rookie] [Grade])
    title_parts = []
    if year:
        title_parts.append(str(year))
    if brand and brand != "Other":
        title_parts.append(brand)
    if set_name and set_name.lower() != (brand or "").lower():
        title_parts.append(set_name)
    if player:
        title_parts.append(player)
    if is_rookie:
        title_parts.append("Rookie")
    if is_graded and grade:
        title_parts.append(grade)
    if card_number and card_number != "N/A":
        title_parts.append(f"#{card_number}")

    title = " ".join(str(p) for p in title_parts if p)
    title = _truncate_title(title)

    # Build description
    set_display = f"{year} {brand}" if (set_name and set_name.lower() == (brand or "").lower()) else f"{year} {brand} {set_name}"
    desc_lines = [
        f"{set_display} {'Rookie ' if is_rookie else ''}Card.",
        f"Player: {player}." if player else "",
        f"Card #: {card_number}." if card_number else "",
        f"Team: {team}." if team else "",
        f"Condition: {condition}." if not is_graded else f"Graded: {grade}. Cert: {cert_number}." if cert_number else f"Graded: {grade}.",
        "Ships securely in top loader and rigid mailer." if not is_graded else "Ships in card saver/sleeve.",
    ]
    if ref["key_player"] or ref["tier1_set"] or ref["tier2_set"]:
        desc_lines.append("")
        if ref["notes"]:
            desc_lines.append(f"Note: {ref['notes']}")
    if description_extra:
        desc_lines.append("")
        desc_lines.append(description_extra.strip())

    description = "\n".join(l for l in desc_lines if l).strip()

    # Item specifics (all fields eBay needs)
    item_specs = {
        "Year": str(year) if year else "",
        "Brand": brand if brand in BRANDS else "Other",
        "Sport": sport_ebay,
        "Player": player or "",
        "Card Number": card_number or "N/A",
        "Team": team or "N/A",
        "Season": str(year) if year else "",
        "Rookie": "Yes" if is_rookie else "No",
        "Graded": "Yes" if is_graded else "No",
        "Grade": grade if is_graded else "",
        "Certification Number": cert_number if is_graded else "",
        "Condition": condition if not is_graded else "",
        "Variety": variety or "Base",
        "Features": features or "",
    }

    # Keywords for search
    keywords = [str(year), brand, set_name, player, sport_ebay]
    if is_rookie:
        keywords.append("Rookie")
    if variety and variety != "Base":
        keywords.append(variety)
    if is_graded and grade:
        keywords.append(grade)
    if team:
        keywords.append(team)
    keywords = ", ".join(k for k in keywords if k)

    return {
        "title": title,
        "description": description,
        "item_specs": {k: v for k, v in item_specs.items() if v},
        "suggested_price": suggested_price or "Check sold listings",
        "category": "Sports Trading Card Singles",
        "category_id": "261328",
        "keywords": keywords,
        "value_context": ref,
    }


def format_for_copy(listing: Dict) -> str:
    """Output listing as copy-paste ready text."""
    lines = [
        "=" * 60,
        "EBAY LISTING - COPY EACH FIELD IN",
        "=" * 60,
        "",
        "TITLE (80 char max):",
        listing["title"],
        "",
        "DESCRIPTION:",
        listing["description"],
        "",
        "--- ITEM SPECIFICS ---",
    ]
    for k, v in listing["item_specs"].items():
        if v:
            lines.append(f"  {k}: {v}")
    lines.extend([
        "",
        "SUGGESTED PRICE:",
        listing["suggested_price"],
        "",
        "CATEGORY:",
        listing["category"],
        "",
        "KEYWORDS:",
        listing["keywords"],
        "",
        "=" * 60,
    ])
    return "\n".join(lines)


def format_for_csv_row(listing: Dict) -> Dict:
    """Format for CSV/bulk upload (eBay file format compatible)."""
    s = listing["item_specs"]
    return {
        "Title": listing["title"],
        "Description": listing["description"],
        "Price": listing["suggested_price"],
        "Category": listing["category_id"],
        "Year": s.get("Year", ""),
        "Brand": s.get("Brand", ""),
        "Sport": s.get("Sport", ""),
        "Player": s.get("Player", ""),
        "Card Number": s.get("Card Number", ""),
        "Team": s.get("Team", ""),
        "Season": s.get("Season", ""),
        "Rookie": s.get("Rookie", ""),
        "Graded": s.get("Graded", ""),
        "Grade": s.get("Grade", ""),
        "Certification Number": s.get("Certification Number", ""),
        "Condition": s.get("Condition", ""),
        "Variety": s.get("Variety", ""),
        "Features": s.get("Features", ""),
    }


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    # Example
    listing = build_full_listing(
        player="Mark Brunell",
        year=1995,
        set_name="Sports Illustrated Kids",
        brand="Sports Illustrated",
        sport="football",
        card_number="",
        team="Jacksonville Jaguars",
        is_rookie=True,
        is_graded=False,
        condition="Near Mint or Better",
        variety="Base",
        suggested_price="$3-$8",
    )
    print(format_for_copy(listing))
