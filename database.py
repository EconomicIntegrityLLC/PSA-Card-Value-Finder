"""
SQLite database for storing and querying high-value card data.
"""

import sqlite3
import pandas as pd
import os
from typing import Optional, List, Dict, Any
from datetime import datetime


class CardDatabase:
    """SQLite database for PSA card values."""
    
    def __init__(self, db_path: str = "data/psa_cards.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Main cards table - stores high-value card reference data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year INTEGER,
                    set_name TEXT,
                    player TEXT,
                    card_number TEXT,
                    sport TEXT,
                    psa_8_value REAL,
                    psa_9_value REAL,
                    psa_10_value REAL,
                    raw_value REAL,
                    grading_cost REAL DEFAULT 27.99,
                    grade_premium REAL,
                    last_updated TEXT,
                    source TEXT,
                    notes TEXT,
                    UNIQUE(year, set_name, player, card_number)
                )
            ''')
            
            # Auction results table - stores actual sale data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auction_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id INTEGER,
                    sale_date TEXT,
                    grade TEXT,
                    price REAL,
                    auction_house TEXT,
                    sale_type TEXT,
                    cert_number TEXT,
                    source_url TEXT,
                    FOREIGN KEY (card_id) REFERENCES cards(id)
                )
            ''')
            
            # Create indexes for fast lookups
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_player ON cards(player)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_year ON cards(year)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sport ON cards(sport)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_set ON cards(set_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_value ON cards(psa_10_value)')
            
            # Full-text search index
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS cards_fts USING fts5(
                    player, set_name, sport, card_number,
                    content='cards',
                    content_rowid='id'
                )
            ''')
            
            conn.commit()
            
    def load_from_csv(self, csv_path: str, source: str = "csv_import"):
        """Load card data from a CSV file."""
        df = pd.read_csv(csv_path)
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Map to our schema
        column_mapping = {
            'psa_9_value': 'psa_9_value',
            'psa_10_value': 'psa_10_value',
            'psa9': 'psa_9_value',
            'psa10': 'psa_10_value',
            'psa_9': 'psa_9_value',
            'psa_10': 'psa_10_value',
        }
        
        df = df.rename(columns=column_mapping)
        
        # Add metadata
        df['last_updated'] = datetime.now().isoformat()
        df['source'] = source
        
        # Calculate grade premium if not present
        if 'grade_premium' not in df.columns and 'psa_10_value' in df.columns and 'psa_9_value' in df.columns:
            df['grade_premium'] = df['psa_10_value'] / df['psa_9_value'].replace(0, 1)
            
        # Insert into database
        with sqlite3.connect(self.db_path) as conn:
            for _, row in df.iterrows():
                try:
                    conn.execute('''
                        INSERT OR REPLACE INTO cards 
                        (year, set_name, player, card_number, sport, 
                         psa_8_value, psa_9_value, psa_10_value, 
                         grade_premium, last_updated, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('year'),
                        row.get('set_name'),
                        row.get('player'),
                        row.get('card_number'),
                        row.get('sport'),
                        row.get('psa_8_value'),
                        row.get('psa_9_value'),
                        row.get('psa_10_value'),
                        row.get('grade_premium'),
                        row.get('last_updated'),
                        row.get('source')
                    ))
                except Exception as e:
                    print(f"Error inserting row: {e}")
                    
            conn.commit()
            
        # Rebuild FTS index
        self._rebuild_fts()
        
        print(f"Loaded {len(df)} cards from {csv_path}")
        
    def _rebuild_fts(self):
        """Rebuild full-text search index."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cards_fts")
            conn.execute('''
                INSERT INTO cards_fts(rowid, player, set_name, sport, card_number)
                SELECT id, player, set_name, sport, card_number FROM cards
            ''')
            conn.commit()
            
    def search(self, query: str, limit: int = 100) -> pd.DataFrame:
        """Full-text search for cards."""
        with sqlite3.connect(self.db_path) as conn:
            # Use FTS for the search
            sql = '''
                SELECT c.* FROM cards c
                JOIN cards_fts fts ON c.id = fts.rowid
                WHERE cards_fts MATCH ?
                ORDER BY c.psa_10_value DESC
                LIMIT ?
            '''
            return pd.read_sql_query(sql, conn, params=(query, limit))
            
    def search_player(self, player_name: str) -> pd.DataFrame:
        """Search by player name (partial match)."""
        with sqlite3.connect(self.db_path) as conn:
            sql = '''
                SELECT * FROM cards 
                WHERE player LIKE ? 
                ORDER BY psa_10_value DESC
            '''
            return pd.read_sql_query(sql, conn, params=(f'%{player_name}%',))
            
    def search_by_year(self, year: int) -> pd.DataFrame:
        """Get all high-value cards from a specific year."""
        with sqlite3.connect(self.db_path) as conn:
            sql = '''
                SELECT * FROM cards 
                WHERE year = ?
                ORDER BY psa_10_value DESC
            '''
            return pd.read_sql_query(sql, conn, params=(year,))
            
    def search_by_set(self, set_name: str) -> pd.DataFrame:
        """Search by set name (partial match)."""
        with sqlite3.connect(self.db_path) as conn:
            sql = '''
                SELECT * FROM cards 
                WHERE set_name LIKE ?
                ORDER BY psa_10_value DESC
            '''
            return pd.read_sql_query(sql, conn, params=(f'%{set_name}%',))
            
    def search_by_sport(self, sport: str) -> pd.DataFrame:
        """Get all high-value cards for a sport."""
        with sqlite3.connect(self.db_path) as conn:
            sql = '''
                SELECT * FROM cards 
                WHERE sport = ?
                ORDER BY psa_10_value DESC
            '''
            return pd.read_sql_query(sql, conn, params=(sport.lower(),))
            
    def get_top_cards(self, sport: str = None, limit: int = 100, min_value: float = 100) -> pd.DataFrame:
        """Get top cards by PSA 10 value."""
        with sqlite3.connect(self.db_path) as conn:
            if sport:
                sql = '''
                    SELECT * FROM cards 
                    WHERE sport = ? AND psa_10_value >= ?
                    ORDER BY psa_10_value DESC
                    LIMIT ?
                '''
                params = (sport.lower(), min_value, limit)
            else:
                sql = '''
                    SELECT * FROM cards 
                    WHERE psa_10_value >= ?
                    ORDER BY psa_10_value DESC
                    LIMIT ?
                '''
                params = (min_value, limit)
            return pd.read_sql_query(sql, conn, params=params)
            
    def get_all_sets(self) -> List[str]:
        """Get list of all unique set names."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT DISTINCT set_name FROM cards ORDER BY set_name')
            return [row[0] for row in cursor.fetchall()]
            
    def get_all_players(self) -> List[str]:
        """Get list of all unique player names."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT DISTINCT player FROM cards ORDER BY player')
            return [row[0] for row in cursor.fetchall()]
            
    def get_years_range(self) -> tuple:
        """Get min and max years in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT MIN(year), MAX(year) FROM cards')
            return cursor.fetchone()
            
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            stats['total_cards'] = conn.execute('SELECT COUNT(*) FROM cards').fetchone()[0]
            stats['total_sports'] = conn.execute('SELECT COUNT(DISTINCT sport) FROM cards').fetchone()[0]
            stats['total_sets'] = conn.execute('SELECT COUNT(DISTINCT set_name) FROM cards').fetchone()[0]
            stats['total_players'] = conn.execute('SELECT COUNT(DISTINCT player) FROM cards').fetchone()[0]
            
            # Cards by sport
            cursor = conn.execute('''
                SELECT sport, COUNT(*) as count 
                FROM cards 
                GROUP BY sport 
                ORDER BY count DESC
            ''')
            stats['by_sport'] = dict(cursor.fetchall())
            
            # Value ranges
            cursor = conn.execute('''
                SELECT 
                    MIN(psa_10_value) as min_value,
                    MAX(psa_10_value) as max_value,
                    AVG(psa_10_value) as avg_value
                FROM cards
            ''')
            row = cursor.fetchone()
            stats['min_psa10'] = row[0]
            stats['max_psa10'] = row[1]
            stats['avg_psa10'] = row[2]
            
            return stats
            
    def advanced_search(
        self,
        player: str = None,
        year_min: int = None,
        year_max: int = None,
        set_name: str = None,
        sport: str = None,
        min_psa9: float = None,
        min_psa10: float = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """Advanced search with multiple filters."""
        
        conditions = []
        params = []
        
        if player:
            conditions.append("player LIKE ?")
            params.append(f"%{player}%")
            
        if year_min:
            conditions.append("year >= ?")
            params.append(year_min)
            
        if year_max:
            conditions.append("year <= ?")
            params.append(year_max)
            
        if set_name:
            conditions.append("set_name LIKE ?")
            params.append(f"%{set_name}%")
            
        if sport:
            conditions.append("sport = ?")
            params.append(sport.lower())
            
        if min_psa9:
            conditions.append("psa_9_value >= ?")
            params.append(min_psa9)
            
        if min_psa10:
            conditions.append("psa_10_value >= ?")
            params.append(min_psa10)
            
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f'''
            SELECT * FROM cards 
            WHERE {where_clause}
            ORDER BY psa_10_value DESC
            LIMIT ?
        '''
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(sql, conn, params=params)


if __name__ == "__main__":
    # Test the database
    db = CardDatabase()
    
    # Load seed data if available
    seed_path = "data/seed_database.csv"
    if os.path.exists(seed_path):
        db.load_from_csv(seed_path, source="seed_data")
        
    # Print stats
    stats = db.get_stats()
    print(f"\nDatabase Statistics:")
    print(f"  Total cards: {stats['total_cards']}")
    print(f"  Sports: {stats['total_sports']}")
    print(f"  Sets: {stats['total_sets']}")
    print(f"  Players: {stats['total_players']}")
    print(f"\nBy Sport: {stats['by_sport']}")
