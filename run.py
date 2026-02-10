"""
PSA Card Value Finder - Main Entry Point
Run this to scrape data and/or start the lookup app.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
    print("Done!\n")

def run_scraper(sport="basketball", delay=1.0):
    """Run the PSA scraper."""
    from scraper.psa_scraper import PSAPriceGuideScraper
    
    scraper = PSAPriceGuideScraper()
    
    print(f"Starting scrape for {sport}...")
    print("This will take a while - there are hundreds of sets to scrape.")
    print("You can stop with Ctrl+C and resume later (progress is saved).\n")
    
    scraper.scrape_all_sets(sport=sport, delay=delay)
    
    # Export high value cards
    scraper.export_high_value_csv()
    
    stats = scraper.get_stats()
    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"Total cards: {stats['total_cards']:,}")
    print(f"Cards worth $100+ at PSA 9: {stats['cards_psa9_100plus']:,}")
    print(f"Cards worth $100+ at PSA 10: {stats['cards_psa10_100plus']:,}")
    print(f"\nHigh-value cards exported to: data/high_value_cards.csv")

def run_app():
    """Start the Streamlit app."""
    print("Starting lookup app...")
    print("Open http://localhost:8501 in your browser\n")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='PSA Card Value Finder')
    parser.add_argument('command', choices=['scrape', 'app', 'both'],
                        help='scrape = download PSA data, app = run lookup interface, both = scrape then run app')
    parser.add_argument('--sport', default='basketball',
                        help='Sport to scrape: baseball, basketball, football, hockey, soccer, or all')
    parser.add_argument('--delay', type=float, default=1.0,
                        help='Delay between requests (be nice to PSA servers)')
    
    args = parser.parse_args()
    
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("="*60)
    print("PSA CARD VALUE FINDER")
    print("Find the needles in your haystack")
    print("="*60 + "\n")
    
    if args.command in ['scrape', 'both']:
        install_requirements()
        run_scraper(sport=args.sport, delay=args.delay)
        
    if args.command in ['app', 'both']:
        run_app()


if __name__ == "__main__":
    main()
