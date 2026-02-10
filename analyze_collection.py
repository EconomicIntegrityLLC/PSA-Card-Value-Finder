"""
Analyze CollX export and update reference database with your specific sets/players.
"""
import pandas as pd
import sqlite3
import re

# Load your collection
df = pd.read_csv('download_EconomicIntegrity-2026-01-29-023330_collx.csv')

print(f"Total cards in collection: {len(df)}")
print(f"\nBy category:")
print(df['category'].value_counts())

# Get unique sets
unique_sets = df['set'].dropna().unique()
print(f"\nUnique sets: {len(unique_sets)}")

# Get unique players
unique_players = df['name'].dropna().unique()
print(f"Unique players: {len(unique_players)}")

# Find potentially valuable cards based on keywords
valuable_keywords = ['Prizm', 'Silver', 'Gold', 'Refractor', 'Chrome', 'Auto', 'Patch', 
                     '/99', '/75', '/50', '/25', '/10', '/5', '/1', 
                     'Select', 'Optic', 'Mosaic', 'National Treasures',
                     'Contenders', 'SP', 'SSP', 'Rookie', 'RC']

def has_valuable_keyword(row):
    searchable = f"{row.get('set', '')} {row.get('flags', '')} {row.get('name', '')}"
    for kw in valuable_keywords:
        if kw.lower() in searchable.lower():
            return True
    return False

df['potentially_valuable'] = df.apply(has_valuable_keyword, axis=1)
valuable_cards = df[df['potentially_valuable']]

print(f"\nPotentially valuable cards (based on keywords): {len(valuable_cards)}")

# Extract key sets from your collection
key_sets_in_collection = []
for set_name in unique_sets:
    set_lower = set_name.lower()
    # Check if it's a key set type
    if any(kw.lower() in set_lower for kw in ['prizm', 'select', 'optic', 'chrome', 'mosaic', 'contenders', 'national treasures', 'flawless']):
        key_sets_in_collection.append(set_name)

print(f"\nKey sets YOU have ({len(key_sets_in_collection)}):")
for s in sorted(set(key_sets_in_collection))[:50]:
    print(f"  - {s}")

# Extract year from sets
def extract_year(set_name):
    match = re.search(r'(19|20)\d{2}', str(set_name))
    return int(match.group()) if match else None

df['year_extracted'] = df['set'].apply(extract_year)

# Group by sport/category
print("\n" + "="*60)
print("YOUR COLLECTION BREAKDOWN BY SPORT")
print("="*60)

for category in df['category'].unique():
    cat_df = df[df['category'] == category]
    print(f"\n{category.upper()} ({len(cat_df)} cards)")
    
    # Top sets in this category
    top_sets = cat_df['set'].value_counts().head(15)
    print("  Top sets:")
    for set_name, count in top_sets.items():
        print(f"    [{count}] {set_name}")

# Now update the database with YOUR specific sets
print("\n" + "="*60)
print("UPDATING REFERENCE DATABASE WITH YOUR SETS")
print("="*60)

conn = sqlite3.connect('data/reference.db')

# Add your sets as tier 3 (your collection)
conn.execute('''
    CREATE TABLE IF NOT EXISTS your_sets (
        id INTEGER PRIMARY KEY,
        set_name TEXT UNIQUE,
        sport TEXT,
        year INTEGER,
        card_count INTEGER,
        has_valuable_keywords INTEGER
    )
''')

# Add your players
conn.execute('''
    CREATE TABLE IF NOT EXISTS your_players (
        id INTEGER PRIMARY KEY,
        player_name TEXT,
        sport TEXT,
        card_count INTEGER,
        UNIQUE(player_name, sport)
    )
''')

# Insert your sets
for set_name in unique_sets:
    if pd.isna(set_name):
        continue
    set_df = df[df['set'] == set_name]
    sport = set_df['category'].iloc[0] if len(set_df) > 0 else None
    year = extract_year(set_name)
    count = len(set_df)
    has_valuable = 1 if set_name in key_sets_in_collection else 0
    
    try:
        conn.execute('''
            INSERT OR REPLACE INTO your_sets (set_name, sport, year, card_count, has_valuable_keywords)
            VALUES (?, ?, ?, ?, ?)
        ''', (set_name, sport, year, count, has_valuable))
    except:
        pass

# Insert your players  
player_counts = df.groupby(['name', 'category']).size().reset_index(name='count')
for _, row in player_counts.iterrows():
    if pd.isna(row['name']):
        continue
    try:
        conn.execute('''
            INSERT OR REPLACE INTO your_players (player_name, sport, card_count)
            VALUES (?, ?, ?)
        ''', (row['name'], row['category'], row['count']))
    except:
        pass

conn.commit()

# Show key players you have
print("\nKEY PLAYERS IN YOUR COLLECTION (multiple cards):")
top_players = df.groupby(['name', 'category']).size().reset_index(name='count')
top_players = top_players[top_players['count'] >= 3].sort_values('count', ascending=False)

for _, row in top_players.head(40).iterrows():
    print(f"  [{row['count']}] {row['name']} ({row['category']})")

# Find your RC (Rookie Cards)
rookies = df[df['flags'].str.contains('RC', na=False)]
print(f"\n\nROOKIE CARDS IN YOUR COLLECTION: {len(rookies)}")
print("Top rookies by count:")
rookie_counts = rookies.groupby('name').size().sort_values(ascending=False)
for name, count in rookie_counts.head(20).items():
    print(f"  [{count}] {name}")

# Find numbered cards
numbered = df[df['flags'].str.contains('SN', na=False)]
print(f"\nNUMBERED/LIMITED CARDS: {len(numbered)}")

conn.close()
print(f"\nDatabase updated with {len(unique_sets)} of your sets and {len(unique_players)} players")
