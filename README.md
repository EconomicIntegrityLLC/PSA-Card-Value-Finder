# PSA Card Grading Finder

**Economic Integrity LLC IP - Created 1/29/26**

A tool to help identify sports cards worth grading from your collection. Quickly look up athletes and check eBay sold prices for PSA graded cards worth $100+.

---

## Features

- **Athletes A-Z** - 1,700+ athletes across NFL, MLB, NBA, NHL with instant eBay lookup
- **Live Search** - Type to filter athletes in real-time
- **Your Collection** - Import your CollX export to find valuable cards you own
- **Key Sets & Keywords** - Reference guide for valuable sets and parallels

---

## Quick Start

### 1. Install Python Dependencies

```bash
cd c:\Users\IP\Desktop\PSA
pip install streamlit pandas
```

### 2. Run the App

```bash
python -m streamlit run app.py
```

### 3. Open in Browser

The app will automatically open, or go to: **http://localhost:8501**

---

## One-Line Launch (Copy & Paste)

```powershell
cd "c:\Users\IP\Desktop\PSA" && python -m streamlit run app.py
```

---

## Optional: Load Your Collection

If you have a CollX CSV export:

1. Place your CSV file in the `data/` folder
2. Run: `python update_from_collection.py`
3. Your cards will appear in the "YOUR CARDS" tab

---

## How to Use

1. **Athletes A-Z Tab** - Start typing a name to filter. Click any name to search eBay for PSA graded cards sold $100+ (excludes autographs)

2. **Search Tab** - Build custom eBay searches with player, year, set, and grade

3. **Key Sets Tab** - Reference for premium sets worth grading

4. **Keywords Tab** - Parallels and insert types that indicate value

---

## Tips

- Only grade cards in **PSA 8+ condition**
- Only grade if the card sells for **$100+ graded** (grading costs ~$28)
- Focus on **rookies** and **numbered parallels**
- Check recent eBay SOLD prices, not listings

---

## Files

- `app.py` - Main Streamlit application
- `data/reference.db` - SQLite database with athletes and sets
- `data/grade_worthy_reference.py` - Reference data builder

---

**Economic Integrity LLC IP - Created 1/29/26**
