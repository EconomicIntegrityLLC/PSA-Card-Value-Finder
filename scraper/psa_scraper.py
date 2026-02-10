"""
PSA Price Guide Scraper
Scrapes REAL price data from PSA's price guide to find cards worth grading.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import sqlite3

# Configuration
BASE_URL = "https://www.psacard.com"
PRICE_GUIDE_URL = f"{BASE_URL}/priceguide"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

# Sport categories from PSA's site
SPORT_CATEGORIES = {
    "baseball": {"id": 13, "url_part": "baseball-card-values"},
    "basketball": {"id": 3, "url_part": "basketball-card-values"},
    "football": {"id": 5, "url_part": "football-card-values"},
    "hockey": {"id": 1, "url_part": "hockey-card-values"},
    "soccer": {"id": 17, "url_part": "soccer-card-values"},
    "boxing": {"id": 4, "url_part": "boxing-card-values"},
    "golf": {"id": 6, "url_part": "golf-card-values"},
    "racing": {"id": 10, "url_part": "racing-card-values"},
}


class PSAPriceGuideScraper:
    """Scrapes PSA price guide for card values."""
    
    def __init__(self, data_dir: str = "data", db_path: str = "data/psa_cards.db"):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.data_dir = data_dir
        self.db_path = db_path
        os.makedirs(data_dir, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sport TEXT,
                    year INTEGER,
                    set_name TEXT,
                    set_id TEXT,
                    card_number TEXT,
                    player TEXT,
                    psa_1 REAL, psa_2 REAL, psa_3 REAL, psa_4 REAL,
                    psa_5 REAL, psa_6 REAL, psa_7 REAL, psa_8 REAL,
                    psa_9 REAL, psa_10 REAL,
                    last_updated TEXT,
                    UNIQUE(sport, set_id, card_number, player)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sport TEXT,
                    set_name TEXT,
                    set_id TEXT UNIQUE,
                    url TEXT,
                    scraped INTEGER DEFAULT 0,
                    card_count INTEGER DEFAULT 0,
                    last_updated TEXT
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_cards_psa10 ON cards(psa_10)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_cards_psa9 ON cards(psa_9)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_cards_player ON cards(player)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_cards_sport ON cards(sport)')
            conn.commit()
            
    def _request(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retries."""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    wait = (attempt + 1) * 15
                    print(f"  Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"  HTTP {response.status_code}")
            except Exception as e:
                print(f"  Request error: {e}")
                time.sleep(2)
        return None
    
    def get_sets_for_sport(self, sport: str) -> List[Dict[str, Any]]:
        """Get all card sets for a sport from the price guide."""
        if sport not in SPORT_CATEGORIES:
            print(f"Unknown sport: {sport}")
            return []
            
        cat = SPORT_CATEGORIES[sport]
        url = f"{PRICE_GUIDE_URL}/{cat['url_part']}/{cat['id']}"
        
        print(f"Fetching sets for {sport} from {url}")
        response = self._request(url)
        
        if not response:
            return []
            
        soup = BeautifulSoup(response.text, 'lxml')
        sets = []
        
        # Find all set links in the table
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            # Match pattern like /priceguide/basketball-card-values/1986-fleer/1718
            match = re.search(rf'/priceguide/{cat["url_part"]}/([^/]+)/(\d+)', href)
            if match:
                set_slug = match.group(1)
                set_id = match.group(2)
                set_name = link.get_text(strip=True)
                
                if set_name and not set_name.isdigit():
                    sets.append({
                        "sport": sport,
                        "set_name": set_name,
                        "set_id": set_id,
                        "url": BASE_URL + href
                    })
                    
        # Deduplicate
        seen = set()
        unique_sets = []
        for s in sets:
            key = s['set_id']
            if key not in seen:
                seen.add(key)
                unique_sets.append(s)
                
        print(f"  Found {len(unique_sets)} sets")
        return unique_sets
    
    def save_sets_to_db(self, sets: List[Dict[str, Any]]):
        """Save set list to database."""
        with sqlite3.connect(self.db_path) as conn:
            for s in sets:
                conn.execute('''
                    INSERT OR IGNORE INTO sets (sport, set_name, set_id, url, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                ''', (s['sport'], s['set_name'], s['set_id'], s['url'], 
                      datetime.now().isoformat()))
            conn.commit()
            
    def scrape_set_prices(self, set_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape all card prices from a specific set."""
        url = set_info['url']
        response = self._request(url)
        
        if not response:
            return []
            
        soup = BeautifulSoup(response.text, 'lxml')
        cards = []
        
        # Find the price table
        table = soup.find('table', class_='table')
        if not table:
            # Try alternate table structure
            table = soup.find('table')
            
        if not table:
            return []
            
        # Get headers
        headers = []
        header_row = table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                headers.append(th.get_text(strip=True).lower())
                
        # Parse rows
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
                
            card_data = {
                "sport": set_info['sport'],
                "set_name": set_info['set_name'],
                "set_id": set_info['set_id'],
            }
            
            for i, cell in enumerate(cells):
                if i < len(headers):
                    header = headers[i]
                    value = cell.get_text(strip=True)
                    
                    # Parse price values
                    if header in ['psa 1', 'psa 2', 'psa 3', 'psa 4', 'psa 5', 
                                  'psa 6', 'psa 7', 'psa 8', 'psa 9', 'psa 10',
                                  '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                        # Clean price value
                        price = self._parse_price(value)
                        grade = header.replace('psa ', '').strip()
                        card_data[f'psa_{grade}'] = price
                    elif header in ['#', 'number', 'card #', 'card']:
                        card_data['card_number'] = value
                    elif header in ['name', 'player', 'description', 'subject']:
                        card_data['player'] = value
                        
            # Extract year from set name if possible
            year_match = re.search(r'(\d{4})', set_info['set_name'])
            if year_match:
                card_data['year'] = int(year_match.group(1))
                
            if card_data.get('player') or card_data.get('card_number'):
                cards.append(card_data)
                
        return cards
    
    def _parse_price(self, value: str) -> Optional[float]:
        """Parse price string to float."""
        if not value or value == '-' or value == 'N/A':
            return None
        # Remove $, commas, +/- indicators
        cleaned = re.sub(r'[,$+\-]', '', value).strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
            
    def save_cards_to_db(self, cards: List[Dict[str, Any]]):
        """Save cards to database."""
        with sqlite3.connect(self.db_path) as conn:
            for card in cards:
                try:
                    conn.execute('''
                        INSERT OR REPLACE INTO cards 
                        (sport, year, set_name, set_id, card_number, player,
                         psa_1, psa_2, psa_3, psa_4, psa_5, psa_6, psa_7, psa_8, psa_9, psa_10,
                         last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        card.get('sport'),
                        card.get('year'),
                        card.get('set_name'),
                        card.get('set_id'),
                        card.get('card_number'),
                        card.get('player'),
                        card.get('psa_1'),
                        card.get('psa_2'),
                        card.get('psa_3'),
                        card.get('psa_4'),
                        card.get('psa_5'),
                        card.get('psa_6'),
                        card.get('psa_7'),
                        card.get('psa_8'),
                        card.get('psa_9'),
                        card.get('psa_10'),
                        datetime.now().isoformat()
                    ))
                except Exception as e:
                    print(f"  DB error: {e}")
            conn.commit()
            
    def scrape_all_sets(self, sport: str = "all", delay: float = 1.0):
        """Scrape all sets for specified sport(s)."""
        sports = list(SPORT_CATEGORIES.keys()) if sport == "all" else [sport]
        
        for sport_name in sports:
            print(f"\n{'='*60}")
            print(f"SCRAPING {sport_name.upper()}")
            print(f"{'='*60}")
            
            # Get all sets
            sets = self.get_sets_for_sport(sport_name)
            self.save_sets_to_db(sets)
            
            # Scrape each set
            total_cards = 0
            for i, set_info in enumerate(sets):
                print(f"\n[{i+1}/{len(sets)}] {set_info['set_name']}")
                
                cards = self.scrape_set_prices(set_info)
                
                if cards:
                    self.save_cards_to_db(cards)
                    total_cards += len(cards)
                    
                    # Mark set as scraped
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute('''
                            UPDATE sets SET scraped = 1, card_count = ? 
                            WHERE set_id = ?
                        ''', (len(cards), set_info['set_id']))
                        conn.commit()
                        
                    print(f"  Saved {len(cards)} cards")
                else:
                    print(f"  No cards found")
                    
                time.sleep(delay)
                
            print(f"\n{sport_name}: Scraped {total_cards} total cards from {len(sets)} sets")
            
    def get_high_value_cards(self, min_psa9: float = 100, min_psa10: float = 100) -> pd.DataFrame:
        """Get all cards worth at least min value at PSA 9 or PSA 10."""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query('''
                SELECT * FROM cards 
                WHERE psa_9 >= ? OR psa_10 >= ?
                ORDER BY psa_10 DESC, psa_9 DESC
            ''', conn, params=(min_psa9, min_psa10))
        return df
        
    def export_high_value_csv(self, output_path: str = "data/high_value_cards.csv", 
                               min_value: float = 100):
        """Export high-value cards to CSV for easy reference."""
        df = self.get_high_value_cards(min_psa9=min_value, min_psa10=min_value)
        
        if df.empty:
            print("No high-value cards found yet. Run scraper first.")
            return
            
        # Add useful calculated columns
        df['grading_cost'] = 27.99
        df['profit_psa9'] = df['psa_9'].fillna(0) - 27.99
        df['profit_psa10'] = df['psa_10'].fillna(0) - 27.99
        
        # Sort by potential profit
        df = df.sort_values('profit_psa10', ascending=False)
        
        df.to_csv(output_path, index=False)
        print(f"Exported {len(df)} high-value cards to {output_path}")
        return df
        
    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            stats['total_cards'] = conn.execute('SELECT COUNT(*) FROM cards').fetchone()[0]
            stats['total_sets'] = conn.execute('SELECT COUNT(*) FROM sets').fetchone()[0]
            stats['scraped_sets'] = conn.execute('SELECT COUNT(*) FROM sets WHERE scraped=1').fetchone()[0]
            
            # High value counts
            stats['cards_psa9_100plus'] = conn.execute(
                'SELECT COUNT(*) FROM cards WHERE psa_9 >= 100'
            ).fetchone()[0]
            stats['cards_psa10_100plus'] = conn.execute(
                'SELECT COUNT(*) FROM cards WHERE psa_10 >= 100'
            ).fetchone()[0]
            
            # By sport
            cursor = conn.execute('''
                SELECT sport, COUNT(*) FROM cards GROUP BY sport
            ''')
            stats['by_sport'] = dict(cursor.fetchall())
            
        return stats


def main():
    """Main entry point for scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(description='PSA Price Guide Scraper')
    parser.add_argument('--sport', default='all', 
                        help='Sport to scrape (baseball, basketball, football, hockey, soccer, or all)')
    parser.add_argument('--delay', type=float, default=1.0,
                        help='Delay between requests in seconds')
    parser.add_argument('--export', action='store_true',
                        help='Export high-value cards to CSV after scraping')
    parser.add_argument('--min-value', type=float, default=100,
                        help='Minimum PSA 9/10 value to include in export')
    
    args = parser.parse_args()
    
    scraper = PSAPriceGuideScraper()
    
    print("PSA Price Guide Scraper")
    print("="*60)
    
    # Show current stats
    stats = scraper.get_stats()
    print(f"Current database: {stats['total_cards']} cards, {stats['scraped_sets']}/{stats['total_sets']} sets scraped")
    print(f"High-value cards: {stats['cards_psa9_100plus']} (PSA 9 $100+), {stats['cards_psa10_100plus']} (PSA 10 $100+)")
    
    if stats['total_cards'] == 0 or args.sport != 'skip':
        print(f"\nStarting scrape for: {args.sport}")
        scraper.scrape_all_sets(sport=args.sport, delay=args.delay)
        
    if args.export:
        scraper.export_high_value_csv(min_value=args.min_value)
        
    # Final stats
    stats = scraper.get_stats()
    print(f"\nFinal stats: {stats['total_cards']} cards, {stats['cards_psa10_100plus']} worth $100+ at PSA 10")


if __name__ == "__main__":
    main()
