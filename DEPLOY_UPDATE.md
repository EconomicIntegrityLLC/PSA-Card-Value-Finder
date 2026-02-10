# Deployment Update — Checklist Expansion

**Date:** Feb 10, 2026

---

## Summary of Changes

### 1. New checklist pages (6 total)

| Page | Cards | Source |
|------|-------|--------|
| 2026 Topps S1 | 350 base | `data/topps_2026_s1.py` |
| 2025 Prizm Football | 400 (300 base + 100 rookies) | `data/panini_prizm_2025_football.py` |
| 2021 Prizm Football | 330 base | `data/panini_prizm_2021_football.py` |
| 2021 Mosaic Football | 200 base | `data/panini_mosaic_2021_football.py` |
| 2021 Select Football | 300 base (3 tiers) | `data/panini_select_2021_football.py` |
| 2020 Prizm Basketball | 300 base | `data/panini_prizm_2020_basketball.py` |

### 2. Files modified

- **app.py** — Added 6 new pages, sidebar nav, Home page table, filters, search, eBay links

### 3. Files added

- `data/topps_2026_s1.py`
- `data/panini_prizm_2025_football.py` (full 400-card checklist, rookies 331–400 from CSV)
- `data/panini_prizm_2021_football.py`
- `data/panini_mosaic_2021_football.py`
- `data/panini_select_2021_football.py`
- `data/panini_prizm_2020_basketball.py`
- `scripts/parse_panini_csv.py` — Parse Prizm/Mosaic/Basketball CSVs
- `scripts/parse_select_2021.py` — Parse 2021 Select CSV (handles tiered structure)

### 4. Excluded from repo (large, not needed at runtime)

- `panini-checklists-csv-files/` — Raw CSV checklists. Added to `.gitignore`. Data is in the `.py` files; scripts in `scripts/` can regenerate from CSVs if needed.

---

## Git commands for push

```bash
cd c:\Users\IP\Desktop\PSA

# Stage all changes
git add app.py .gitignore
git add data/topps_2026_s1.py
git add data/panini_prizm_2025_football.py
git add data/panini_prizm_2021_football.py
git add data/panini_mosaic_2021_football.py
git add data/panini_select_2021_football.py
git add data/panini_prizm_2020_basketball.py
git add scripts/parse_panini_csv.py
git add scripts/parse_select_2021.py
git add DEPLOY_UPDATE.md

# Commit
git commit -m "Add 6 checklist pages: 2026 Topps S1, 2025/2021 Prizm, 2021 Mosaic/Select, 2020 Prizm Basketball

- 2026 Topps S1: 350-card base checklist
- 2025 Prizm Football: 400 cards (300 base + 100 rookies, full checklist from CSV)
- 2021 Prizm Football: 330 base
- 2021 Mosaic Football: 200 base
- 2021 Select Football: 300 base (Premier/Club/Field tiers)
- 2020 Prizm Basketball: 300 base
- CSV parse scripts for future checklist updates
- All pages: search, filters, eBay Raw/Graded/All links"

# Push
git push origin master
```

---

## Streamlit Cloud redeploy

If the app is already on **Streamlit Community Cloud**:

1. Push the changes to your GitHub repo (commands above).
2. Open [share.streamlit.io](https://share.streamlit.io) and sign in.
3. Open your app.
4. Streamlit Cloud will detect the push and redeploy automatically.
5. If it doesn’t, click **"Reboot app"** or **"Redeploy"** in the app dashboard.

### App configuration

- **Main file:** `app.py`
- **Python version:** 3.9+ (default)
- **Requirements:** `requirements.txt` (streamlit, pandas, requests)

No extra config is needed for these changes.

---

## One-line push (after testing)

```powershell
cd c:\Users\IP\Desktop\PSA && git add app.py .gitignore data/topps_2026_s1.py data/panini_prizm_2025_football.py data/panini_prizm_2021_football.py data/panini_mosaic_2021_football.py data/panini_select_2021_football.py data/panini_prizm_2020_basketball.py scripts/parse_panini_csv.py scripts/parse_select_2021.py DEPLOY_UPDATE.md && git commit -m "Add 6 checklist pages: Topps 2026, Prizm/Mosaic/Select 2021, Prizm 2025/2020" && git push origin master
```

---

## Verify locally before push

```powershell
cd c:\Users\IP\Desktop\PSA
python -m streamlit run app.py
```

Then open **http://localhost:8501** and check:

- Sidebar → Navigate → 2026 Topps S1, 2025 Prizm Football, 2021 Prizm Football, 2021 Mosaic Football, 2021 Select Football, 2020 Prizm Basketball
- Search, filters, and eBay links work on each page
