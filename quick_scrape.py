"""Quick scraper to get initial data."""
import sys
import time
sys.path.insert(0, '.')
from scraper.psa_scraper import PSAPriceGuideScraper

scraper = PSAPriceGuideScraper()

# Get all basketball sets
print('Fetching basketball set list...')
sets = scraper.get_sets_for_sport('basketball')
scraper.save_sets_to_db(sets)

# Scrape first 50 sets to get started
print(f'\nScraping first 50 of {len(sets)} basketball sets...')
print('(Run the full scraper later to get all data)\n')

total_cards = 0
for i, set_info in enumerate(sets[:50]):
    name = set_info["set_name"]
    print(f'[{i+1}/50] {name}', end=' ', flush=True)
    cards = scraper.scrape_set_prices(set_info)
    if cards:
        scraper.save_cards_to_db(cards)
        total_cards += len(cards)
        print(f'- {len(cards)} cards')
    else:
        print('- no price data')
    time.sleep(0.5)

# Export high value
scraper.export_high_value_csv()

stats = scraper.get_stats()
print(f'\n{"="*50}')
print(f'DONE - Scraped {total_cards} cards')
print(f'High-value cards (PSA 10 >= $100): {stats["cards_psa10_100plus"]}')
print(f'High-value cards (PSA 9 >= $100): {stats["cards_psa9_100plus"]}')
print(f'\nExported to: data/high_value_cards.csv')
