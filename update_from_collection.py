"""Update reference database with user's specific collection data."""
import pandas as pd
import sqlite3
import re

# Load collection
df = pd.read_csv('download_EconomicIntegrity-2026-01-29-023330_collx.csv')

conn = sqlite3.connect('data/reference.db')

# Create tables for user's specific data
conn.execute('DROP TABLE IF EXISTS your_sets')
conn.execute('DROP TABLE IF EXISTS your_players')
conn.execute('DROP TABLE IF EXISTS your_valuable')

conn.execute('''
    CREATE TABLE your_sets (
        id INTEGER PRIMARY KEY,
        set_name TEXT,
        sport TEXT,
        year INTEGER,
        card_count INTEGER,
        priority INTEGER DEFAULT 0
    )
''')

conn.execute('''
    CREATE TABLE your_players (
        id INTEGER PRIMARY KEY,
        player_name TEXT,
        sport TEXT,
        card_count INTEGER
    )
''')

conn.execute('''
    CREATE TABLE your_valuable (
        id INTEGER PRIMARY KEY,
        set_name TEXT,
        player TEXT,
        card_number TEXT,
        sport TEXT,
        year INTEGER,
        flags TEXT,
        reason TEXT
    )
''')

# Priority keywords - sets with these are more likely valuable
HIGH_PRIORITY = ['Prizm', 'Select', 'Optic', 'Chrome', 'Mosaic', 'National Treasures', 
                 'Contenders', 'Spectra', 'Immaculate', 'Flawless']
MEDIUM_PRIORITY = ['Bowman', 'Topps Chrome', 'Finest', 'Revolution', 'Certified']

def get_priority(set_name):
    if pd.isna(set_name):
        return 0
    for kw in HIGH_PRIORITY:
        if kw.lower() in set_name.lower():
            return 3
    for kw in MEDIUM_PRIORITY:
        if kw.lower() in set_name.lower():
            return 2
    return 1

def extract_year(s):
    match = re.search(r'(19|20)\d{2}', str(s))
    return int(match.group()) if match else None

# Insert sets with priority
set_counts = df.groupby(['set', 'category']).size().reset_index(name='count')
for _, row in set_counts.iterrows():
    if pd.isna(row['set']):
        continue
    priority = get_priority(row['set'])
    year = extract_year(row['set'])
    conn.execute('''
        INSERT INTO your_sets (set_name, sport, year, card_count, priority)
        VALUES (?, ?, ?, ?, ?)
    ''', (row['set'], row['category'], year, row['count'], priority))

# Insert players
player_counts = df.groupby(['name', 'category']).size().reset_index(name='count')
for _, row in player_counts.iterrows():
    if pd.isna(row['name']):
        continue
    conn.execute('''
        INSERT INTO your_players (player_name, sport, card_count)
        VALUES (?, ?, ?)
    ''', (row['name'], row['category'], row['count']))

# Find potentially valuable cards
valuable_flags = ['RC', 'AUTO', 'MEM', 'SP', 'SSP']
valuable_set_keywords = ['Prizm', 'Silver', 'Gold', 'Refractor', 'Holo', 'Mojo', 
                         '/99', '/75', '/50', '/25', '/10', '/5', '/1', 
                         'Numbered', 'SN', 'Auto', 'Patch']

for _, row in df.iterrows():
    reasons = []
    flags = str(row.get('flags', ''))
    set_name = str(row.get('set', ''))
    
    # Check flags
    if 'RC' in flags:
        reasons.append('Rookie Card')
    if 'SN' in flags:
        reasons.append('Serial Numbered')
    if 'AUTO' in flags:
        reasons.append('Autograph')
    if 'MEM' in flags:
        reasons.append('Memorabilia')
        
    # Check set name for valuable keywords
    for kw in valuable_set_keywords:
        if kw.lower() in set_name.lower():
            reasons.append(f'Set: {kw}')
            break
            
    if reasons:
        conn.execute('''
            INSERT INTO your_valuable (set_name, player, card_number, sport, year, flags, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (row.get('set'), row.get('name'), row.get('number'), 
              row.get('category'), extract_year(row.get('set')),
              flags, ', '.join(reasons)))

conn.commit()

# Print summary
print("="*60)
print("YOUR COLLECTION - CARDS TO CHECK")
print("="*60)

# High priority sets in your collection
print("\n[HIGH PRIORITY] SETS YOU HAVE (Prizm, Select, Optic, Chrome):")
cursor = conn.execute('''
    SELECT set_name, sport, card_count FROM your_sets 
    WHERE priority = 3 ORDER BY card_count DESC LIMIT 30
''')
for row in cursor:
    print(f"  [{row[2]}] {row[0]} ({row[1]})")

# Rookies
print("\n[ROOKIES] IN YOUR COLLECTION:")
cursor = conn.execute('''
    SELECT player, set_name, sport FROM your_valuable 
    WHERE reason LIKE '%Rookie%' 
    GROUP BY player ORDER BY COUNT(*) DESC LIMIT 30
''')
for row in cursor:
    print(f"  {row[0]} - {row[1]} ({row[2]})")

# Numbered cards
print("\n[NUMBERED] LIMITED CARDS:")
cursor = conn.execute('''
    SELECT player, set_name, flags FROM your_valuable 
    WHERE reason LIKE '%Numbered%' LIMIT 20
''')
for row in cursor:
    print(f"  {row[0]} - {row[1]} ({row[2]})")

# Count valuable
cursor = conn.execute('SELECT COUNT(*) FROM your_valuable')
total_valuable = cursor.fetchone()[0]
print(f"\n\nTOTAL POTENTIALLY VALUABLE CARDS: {total_valuable}")

conn.close()
print("\nDatabase updated! Restart the app to see your collection data.")
