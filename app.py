"""
PSA Card Value Finder - Streamlit App
Quick reference for identifying cards worth grading while sorting.
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import html as html_mod
import urllib.parse

st.set_page_config(
    page_title="PSA Card Grading Finder",
    page_icon="🃏",
    layout="wide"
)

DB_PATH = "data/reference.db"
GRADING_COST = 27.99

def get_db():
    if not os.path.exists(DB_PATH):
        st.error("Reference database not found.")
        st.stop()
    return sqlite3.connect(DB_PATH)

# Cache player data so it doesn't reload every keystroke
@st.cache_data(ttl=300)
def get_all_players():
    """Load all players once and cache for 5 minutes"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT player_name, sport FROM key_players WHERE sport != 'soccer' ORDER BY player_name",
        conn
    )
    conn.close()
    # Map to league abbreviations
    league_map = {'football': 'NFL', 'baseball': 'MLB', 'basketball': 'NBA', 'hockey': 'NHL'}
    df['league'] = df['sport'].map(league_map).fillna(df['sport'].str.upper())
    return df

def ebay_search_url(query, sold=True, min_price=None, exclude_auto=False, exclude_graded=False, graded_only=False):
    base = "https://www.ebay.com/sch/i.html"
    
    # Add exclusions to query if needed
    # Note: eBay does substring matching, so -auto is too broad (hits "automatic" etc.)
    # Use -autograph and -autographed instead; keep -auto as well since many sellers
    # abbreviate, but the risk is minimal in the Trading Card Singles category
    if exclude_auto:
        query = f"{query} -autograph -signed -signature -auto"
    if exclude_graded:
        query = f"{query} -PSA -BGS -SGC -CGC -graded -slab"
    if graded_only:
        query = f"{query} (PSA,BGS,SGC,CGC)"
    
    # 261328 = Sports Trading Card Singles category (excludes jerseys, apparel, etc.)
    params = {"_nkw": query, "_sacat": "261328"}
    if sold:
        params["LH_Complete"] = "1"
        params["LH_Sold"] = "1"
    if min_price:
        params["_udlo"] = str(min_price)
    return f"{base}?{urllib.parse.urlencode(params)}"

# Main app
st.title("🃏 PSA Card Grading Finder")
st.markdown("**Find cards worth grading** - Quick reference tool")
st.markdown('<span style="color: #00FF00; font-size: 14px;">Economic Integrity LLC IP - Created 1/29/26</span>', unsafe_allow_html=True)

# Page list for sidebar navigation
PAGES = [
    "CollX Collection",
    "2021 Topps S1",
    "Search",
    "Athletes A-Z",
    "Sets by Year",
    "By Year & Sport",
    "Junk Wax Gems",
    "90s NBA",
    "Parallels & Inserts",
    "Key Sets",
    "Key Players",
    "eBay Listings",
]

# Sidebar
with st.sidebar:
    page = st.selectbox("Navigate", PAGES, index=0)
    st.markdown("---")
    st.header("Quick eBay Lookup")
    quick_search = st.text_input("Search eBay", placeholder="e.g. Ken Griffey Jr 1989 Upper Deck")
    qs_col1, qs_col2 = st.columns(2)
    with qs_col1:
        qs_sold = st.checkbox("Sold only", value=True, key="qs_sold")
    with qs_col2:
        qs_graded = st.checkbox("Graded only", value=False, key="qs_graded")
    if quick_search:
        q = quick_search
        url_sold = ebay_search_url(q, sold=True, exclude_auto=True, graded_only=qs_graded)
        url_active = ebay_search_url(q, sold=False, exclude_auto=True, graded_only=qs_graded)
        if qs_sold:
            st.markdown(f"[🔍 eBay SOLD results]({url_sold})")
        else:
            st.markdown(f"[🛒 eBay ACTIVE listings]({url_active})")
        st.caption(f"[sold]({url_sold}) · [active]({url_active})")
    st.markdown("---")
    st.markdown(f"**Grading Cost:** ${GRADING_COST}")
    st.markdown("Only grade if PSA 8+ condition and $100+ value")

if page == "CollX Collection":
    st.header("📦 My CollX Collection — Full Searchable Checklist")
    st.caption("Your entire CollX export. Search by **player**, **card #**, **team**, **year**, **brand**, or **set**. eBay links: Sold, No Autos.")

    # ── Load CSV data (cached) ────────────────────────────────────────
    @st.cache_data(ttl=600)
    def load_collx_csv():
        csv_path = os.path.join(os.path.dirname(__file__), "collx-photos-master.csv")
        df = pd.read_csv(csv_path, dtype=str).fillna("")
        # Strip whitespace from all columns
        for col in df.columns:
            df[col] = df[col].str.strip()
        return df

    collx_df = load_collx_csv()

    # ── Search bar ────────────────────────────────────────────────────
    collx_search = st.text_input(
        "🔍 Search your collection",
        placeholder="e.g. Ken Griffey, Bowman Chrome, Yankees, 1989, RC...",
        key="collx_search"
    ).strip()

    # ── Filter options ────────────────────────────────────────────────
    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
    with col_f1:
        all_categories = sorted(collx_df[collx_df['category'] != '']['category'].unique().tolist())
        cat_filter = st.selectbox("Sport", ["All"] + all_categories, key="collx_cat")
    with col_f2:
        all_brands = sorted(collx_df[collx_df['brand'] != '']['brand'].unique().tolist())
        brand_filter = st.selectbox("Brand", ["All"] + all_brands, key="collx_brand")
    with col_f3:
        all_years = sorted(collx_df[collx_df['year'] != '']['year'].unique().tolist(), reverse=True)
        year_filter = st.selectbox("Year", ["All"] + all_years, key="collx_year")
    with col_f4:
        show_max_collx = st.selectbox("Show max", [50, 100, 200, 500, 999, 2999], index=1, key="collx_max")
    with col_f5:
        min_price_collx = st.selectbox("Min eBay $", [0, 5, 10, 25, 50], index=0, key="collx_min_price")

    # ── eBay search format ────────────────────────────────────────────
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        COLLX_SEARCH_FMTS = [
            "Year + Set + Player",
            "Year + Brand + Player",
            "Year + Brand + # + Player",
            "Set + Player",
            "Player + Team",
        ]
        collx_search_fmt = st.selectbox("eBay Search Format", COLLX_SEARCH_FMTS, index=0, key="collx_fmt")
    with col_s2:
        collx_sort = st.selectbox("Sort by", [
            "Name A-Z", "Name Z-A", "Year (newest)", "Year (oldest)",
            "Brand A-Z", "Team A-Z", "Card #"
        ], index=0, key="collx_sort")

    # ── Filter logic ──────────────────────────────────────────────────
    filtered = collx_df.copy()

    if collx_search:
        search_lower = collx_search.lower()
        mask = (
            filtered['name'].str.lower().str.contains(search_lower, na=False)
            | filtered['number'].str.lower().str.contains(search_lower, na=False)
            | filtered['team'].str.lower().str.contains(search_lower, na=False)
            | filtered['year'].str.lower().str.contains(search_lower, na=False)
            | filtered['brand'].str.lower().str.contains(search_lower, na=False)
            | filtered['set'].str.lower().str.contains(search_lower, na=False)
            | filtered['flags'].str.lower().str.contains(search_lower, na=False)
            | filtered['category'].str.lower().str.contains(search_lower, na=False)
        )
        filtered = filtered[mask]

    if cat_filter != "All":
        filtered = filtered[filtered['category'] == cat_filter]
    if brand_filter != "All":
        filtered = filtered[filtered['brand'] == brand_filter]
    if year_filter != "All":
        filtered = filtered[filtered['year'] == year_filter]

    # ── Sort ──────────────────────────────────────────────────────────
    sort_map = {
        "Name A-Z": ("name", True),
        "Name Z-A": ("name", False),
        "Year (newest)": ("year", False),
        "Year (oldest)": ("year", True),
        "Brand A-Z": ("brand", True),
        "Team A-Z": ("team", True),
        "Card #": ("number", True),
    }
    sort_col, sort_asc = sort_map[collx_sort]
    filtered = filtered.sort_values(sort_col, ascending=sort_asc, na_position='last')

    total_matches = len(filtered)
    display_df = filtered.head(show_max_collx)

    st.markdown(f"**{total_matches}** cards found" + (f" (showing first {show_max_collx})" if total_matches > show_max_collx else ""))

    # ── Stats bar ─────────────────────────────────────────────────────
    stat1, stat2, stat3, stat4 = st.columns(4)
    with stat1:
        st.metric("Total Cards", len(collx_df))
    with stat2:
        st.metric("Unique Players", collx_df[collx_df['name'] != '']['name'].nunique())
    with stat3:
        st.metric("Brands", collx_df[collx_df['brand'] != '']['brand'].nunique())
    with stat4:
        rc_count = collx_df['flags'].str.contains('RC', case=False, na=False).sum()
        st.metric("Rookies (RC)", rc_count)

    # ── Results table with eBay links ─────────────────────────────────
    if len(display_df) > 0:
        html = ['<table style="width:100%;border-collapse:collapse;font-size:13px;">']
        html.append('<tr style="border-bottom:2px solid #555;text-align:left;">')
        html.append('<th style="padding:4px 8px;">Card #</th>')
        html.append('<th style="padding:4px 8px;">Player</th>')
        html.append('<th style="padding:4px 8px;">Team</th>')
        html.append('<th style="padding:4px 8px;">Year</th>')
        html.append('<th style="padding:4px 8px;">Set / Brand</th>')
        html.append('<th style="padding:4px 8px;">Flags</th>')
        html.append('<th style="padding:4px 8px;">eBay Sold' + (f' ${min_price_collx}+' if min_price_collx else '') + '</th>')
        html.append('</tr>')

        for _, row in display_df.iterrows():
            card_num = html_mod.escape(row['number'])
            player_name = html_mod.escape(row['name'])
            team = html_mod.escape(row['team'])
            year = html_mod.escape(row['year'])
            brand = html_mod.escape(row['brand'])
            set_name = html_mod.escape(row['set'])
            flags = html_mod.escape(row['flags'])
            category = html_mod.escape(row['category'])

            # Build eBay query using RAW (unescaped) values for URL
            raw_name = row['name']
            raw_team = row['team']
            raw_year = row['year']
            raw_brand = row['brand']
            raw_set = row['set']
            raw_num = row['number']

            if collx_search_fmt == "Year + Set + Player":
                ebay_q = f"{raw_year} {raw_set} {raw_name}" if raw_set else f"{raw_year} {raw_brand} {raw_name}"
            elif collx_search_fmt == "Year + Brand + Player":
                ebay_q = f"{raw_year} {raw_brand} {raw_name}"
            elif collx_search_fmt == "Year + Brand + # + Player":
                num_str = f"#{raw_num}" if raw_num else ""
                ebay_q = f"{raw_year} {raw_brand} {num_str} {raw_name}"
            elif collx_search_fmt == "Set + Player":
                ebay_q = f"{raw_set} {raw_name}" if raw_set else f"{raw_brand} {raw_name}"
            else:  # Player + Team
                ebay_q = f"{raw_name} {raw_team}"

            ebay_q = ebay_q.strip()
            if not ebay_q or ebay_q == "":
                continue  # skip rows with no useful data

            mp = min_price_collx if min_price_collx > 0 else None
            url_raw = ebay_search_url(ebay_q, sold=True, min_price=mp, exclude_auto=True, exclude_graded=True)
            url_graded = ebay_search_url(ebay_q, sold=True, min_price=mp, exclude_auto=True, graded_only=True)
            url_all = ebay_search_url(ebay_q, sold=True, min_price=mp, exclude_auto=True)
            url_active = ebay_search_url(ebay_q, sold=False, exclude_auto=True)

            # Row styling
            row_bg = ""
            if flags and "RC" in flags.upper():
                row_bg = ' style="background-color:rgba(0,200,0,0.08);"'
            elif flags and ("SN" in flags.upper() or "SP" in flags.upper()):
                row_bg = ' style="background-color:rgba(255,165,0,0.08);"'

            # Flags display
            flag_display = ""
            if flags:
                flag_display = f'<span style="color:#FF6B6B;font-weight:bold;">{flags}</span>'

            # Truncate long set names
            set_display = set_name if len(set_name) <= 35 else set_name[:32] + "..."

            html.append(f'<tr{row_bg}>')
            html.append(f'<td style="padding:3px 8px;font-weight:bold;">{card_num}</td>')
            html.append(f'<td style="padding:3px 8px;">{player_name}</td>')
            html.append(f'<td style="padding:3px 8px;color:#888;font-size:12px;">{team}</td>')
            html.append(f'<td style="padding:3px 8px;">{year}</td>')
            html.append(f'<td style="padding:3px 8px;font-size:12px;" title="{set_name}">{set_display}</td>')
            html.append(f'<td style="padding:3px 8px;">{flag_display}</td>')
            html.append(f'<td style="padding:3px 8px;white-space:nowrap;">')
            html.append(f'<a href="{url_raw}" target="_blank" title="Raw/Ungraded sold">🃏Raw</a>')
            html.append(f' · <a href="{url_graded}" target="_blank" title="Graded PSA/BGS/SGC sold">🏆Graded</a>')
            html.append(f' · <a href="{url_all}" target="_blank" title="All sold">📋All</a>')
            html.append(f' · <a href="{url_active}" target="_blank" title="Active listings now" style="color:#4CAF50;">🛒Buy</a>')
            html.append('</td></tr>')

        html.append('</table>')
        st.markdown(''.join(html), unsafe_allow_html=True)
    else:
        st.warning("No cards found. Try a different search or filter.")

    # ── Brand breakdown (collapsed) ───────────────────────────────────
    st.markdown("---")
    with st.expander("📊 Collection Breakdown by Brand"):
        brand_counts = collx_df[collx_df['brand'] != ''].groupby('brand').size().sort_values(ascending=False)
        bc_html = ['<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:4px 12px;font-size:13px;">']
        for brand_name, count in brand_counts.items():
            url = ebay_search_url(f"{brand_name} PSA", sold=True, min_price=50, exclude_auto=True)
            bc_html.append(f'<div><a href="{url}" target="_blank"><b>{html_mod.escape(brand_name)}</b></a> ({count})</div>')
        bc_html.append('</div>')
        st.markdown(''.join(bc_html), unsafe_allow_html=True)

    with st.expander("📅 Collection Breakdown by Year"):
        year_counts = collx_df[collx_df['year'] != ''].groupby('year').size().sort_index(ascending=False)
        yc_html = ['<div style="display:grid;grid-template-columns:repeat(8,1fr);gap:4px 8px;font-size:13px;">']
        for yr, count in year_counts.items():
            yc_html.append(f'<div><b>{yr}</b> ({count})</div>')
        yc_html.append('</div>')
        st.markdown(''.join(yc_html), unsafe_allow_html=True)

elif page == "Athletes A-Z":
    st.header("Athletes A-Z - PSA Graded $100+")
    
    # Search box with auto-filter
    search_query = st.text_input("🔍 Search athletes...", placeholder="Type to filter...", key="athlete_search")
    
    # Use cached player data
    players_df = get_all_players()
    
    # Filter based on search
    if search_query:
        filtered_df = players_df[players_df['player_name'].str.lower().str.contains(search_query.lower())]
    else:
        filtered_df = players_df
    
    st.caption(f"**{len(filtered_df)}** athletes | Click = eBay SOLD $100+ (no autos)")
    
    if len(filtered_df) > 0:
        sorted_df = filtered_df.sort_values('player_name')
        html_parts = ['<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px 12px; font-size: 14px;">']
        for _, row in sorted_df.iterrows():
            player = row['player_name']
            league_tag = row['league']
            url = ebay_search_url(f"{player} PSA", sold=True, min_price=100, exclude_auto=True)
            html_parts.append(f'<div><a href="{url}" target="_blank" style="text-decoration:none;">{player}</a> <span style="color:#888;font-size:11px;">{league_tag}</span></div>')
        html_parts.append('</div>')
        st.markdown(''.join(html_parts), unsafe_allow_html=True)

elif page == "Sets by Year":
    st.header("📅 Sets by Year - PSA $100+ Sold")
    st.caption("Click = eBay SOLD $100+, no autos | ⭐ = Premium")
    
    col_search, col_expand = st.columns([3, 1])
    with col_search:
        set_search = st.text_input("🔍 Search sets...", placeholder="e.g. prizm, chrome, bowman...", key="set_search", label_visibility="collapsed")
    with col_expand:
        expand_all = st.checkbox("Expand All", value=False, key="expand_all")
    
    SETS_BY_YEAR = {
        2025: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐", "Panini Select ⭐", "Panini Donruss Optic ⭐"],
        2024: ["Topps", "Topps Chrome ⭐", "Topps Finest ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐", "Panini Select ⭐", "Panini Donruss Optic ⭐", "Panini Mosaic ⭐"],
        2023: ["Topps", "Topps Chrome ⭐", "Topps Finest ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐", "Panini Select ⭐", "Panini Donruss Optic ⭐", "Panini Mosaic ⭐"],
        2022: ["Topps", "Topps Chrome ⭐", "Topps Finest ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐", "Panini Select ⭐", "Panini Donruss Optic ⭐", "Panini Mosaic ⭐"],
        2021: ["Topps", "Topps Chrome ⭐", "Topps Finest ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐", "Panini Select ⭐", "Panini Donruss Optic ⭐", "Panini Mosaic ⭐"],
        2020: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐", "Panini Select ⭐", "Panini Donruss Optic ⭐", "Panini Mosaic ⭐"],
        2019: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐", "Panini Select ⭐", "Panini Donruss Optic ⭐"],
        2018: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐", "Panini Select ⭐", "Panini Donruss Optic ⭐"],
        2017: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐", "Panini Select ⭐"],
        2016: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐"],
        2015: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐"],
        2014: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐"],
        2013: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐"],
        2012: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Panini Prizm ⭐⭐"],
        2011: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐"],
        2010: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐"],
        2009: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck"],
        2008: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck"],
        2007: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck"],
        2006: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck"],
        2005: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck"],
        2004: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck"],
        2003: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck"],
        2002: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck"],
        2001: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck"],
        2000: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck"],
        1999: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck"],
        1998: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Upper Deck SP Authentic ⭐"],
        1997: ["Topps", "Topps Chrome ⭐", "Bowman", "Bowman Chrome ⭐", "Bowman's Best ⭐"],
        1996: ["Topps", "Topps Chrome ⭐", "Bowman's Best ⭐", "Finest ⭐"],
        1995: ["Topps", "Finest ⭐", "Bowman's Best ⭐"],
        1994: ["Topps", "Finest ⭐", "Upper Deck SP ⭐"],
        1993: ["Topps", "Finest ⭐", "Upper Deck SP ⭐", "Stadium Club"],
        1992: ["Topps", "Stadium Club ⭐", "Upper Deck", "Bowman", "Fleer Ultra"],
        1991: ["Topps", "Stadium Club ⭐", "Upper Deck", "Fleer Ultra"],
        1990: ["Topps", "Upper Deck", "Leaf ⭐", "Bowman"],
        1989: ["Topps", "Upper Deck ⭐", "Bowman", "Donruss", "Fleer", "Score"],
        1988: ["Topps", "Donruss", "Fleer", "Score"],
        1987: ["Topps", "Donruss", "Fleer"],
        1986: ["Topps", "Donruss", "Fleer ⭐"],
        1985: ["Topps", "Donruss", "Fleer"],
        1984: ["Topps", "Donruss", "Fleer"],
        1983: ["Topps", "Donruss", "Fleer"],
        1982: ["Topps", "Donruss", "Fleer"],
        1981: ["Topps", "Donruss", "Fleer"],
        1980: ["Topps"],
        1979: ["Topps", "O-Pee-Chee"],
        1978: ["Topps", "O-Pee-Chee"],
        1977: ["Topps", "O-Pee-Chee"],
        1976: ["Topps"],
        1975: ["Topps"],
    }
    
    search_lower = set_search.lower() if set_search else ""
    years_shown = 0
    
    for year in range(2025, 1974, -1):
        if year in SETS_BY_YEAR:
            sets = SETS_BY_YEAR[year]
            if search_lower:
                filtered_sets = [s for s in sets if search_lower in s.lower()]
                if not filtered_sets:
                    continue
                sets = filtered_sets
            
            years_shown += 1
            with st.expander(f"**{year}** ({len(sets)} sets)", expanded=expand_all or bool(search_lower)):
                html_parts = ['<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:2px 10px;font-size:13px;">']
                for set_name in sets:
                    clean_name = set_name.replace(" ⭐⭐", "").replace(" ⭐", "")
                    url = ebay_search_url(f"{year} {clean_name} PSA", sold=True, min_price=100, exclude_auto=True)
                    html_parts.append(f'<div><a href="{url}" target="_blank">{set_name}</a></div>')
                html_parts.append('</div>')
                st.markdown(''.join(html_parts), unsafe_allow_html=True)
    
    # Hockey section
    st.markdown("---")
    st.subheader("🏒 HOCKEY SETS")
    
    hockey_sets = {
        "2020-21 Upper Deck": ["2020-21 Upper Deck Series 1 Hockey", "2020-21 Upper Deck Series 2 Hockey", "2020-21 Upper Deck Extended Series Hockey"],
        "2019-20 Upper Deck": ["2019-20 Upper Deck Series 1 Hockey", "2019-20 Upper Deck Series 2 Hockey", "2019-20 Upper Deck Trilogy Hockey", "2019-20 Upper Deck Artifacts Hockey", "2019-20 Upper Deck Update Hockey", "2019-20 Upper Deck Credentials Hockey"],
        "2018-19 Upper Deck": ["2018-19 SP Hockey", "2018-19 SP Authentic Hockey", "2018-19 Upper Deck Series 1 Hockey", "2018-19 Upper Deck Series 2 Hockey"],
        "SP Hockey": ["2020-21 SP Hockey", "2019-20 SP Hockey", "2018-19 SP Hockey", "2017-18 SP Hockey", "2016-17 SP Hockey", "2015-16 SP Hockey", "2020-21 SP Authentic Hockey", "2019-20 SP Authentic Hockey", "2018-19 SP Authentic Hockey", "2017-18 SP Authentic Hockey"],
        "2009-10 Hockey": ["2009-10 Upper Deck Hockey", "2009-10 O-Pee-Chee Hockey", "2009-10 Upper Deck Series 1 Hockey", "2009-10 Upper Deck Series 2 Hockey"],
        "Vintage Topps Hockey": ["1988 Topps Hockey", "1986 Topps Hockey", "1985 Topps Hockey", "1984 Topps Hockey", "1981 Topps Hockey", "1978 Topps Hockey"],
        "Vintage O-Pee-Chee Hockey": ["1977 O-Pee-Chee Hockey", "1978 O-Pee-Chee Hockey", "1979 O-Pee-Chee Hockey", "1980 O-Pee-Chee Hockey", "1981 O-Pee-Chee Hockey", "1984 O-Pee-Chee Hockey", "1985 O-Pee-Chee Hockey", "1986 O-Pee-Chee Hockey"],
    }
    
    for category, sets in hockey_sets.items():
        with st.expander(f"**{category}** ({len(sets)} sets)", expanded=False):
            html = ['<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:4px 10px;font-size:13px;">']
            for set_name in sets:
                url = ebay_search_url(f"{set_name}", sold=True, min_price=50, exclude_auto=True)
                html.append(f'<div><a href="{url}" target="_blank">{set_name}</a></div>')
            html.append('</div>')
            st.markdown(''.join(html), unsafe_allow_html=True)

elif page == "By Year & Sport":
    st.header("📆 BY YEAR & SPORT - PSA/BGS $50+")
    st.caption("Click = eBay SOLD $50+, PSA or Beckett graded, no autos")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        year_sport_search = st.text_input("Filter by year...", placeholder="1986", key="year_sport_search")
    with col2:
        expand_all_sports = st.checkbox("Expand All", key="expand_sports")
    
    sports = ["MLB", "NFL", "NBA", "NHL"]
    years = list(range(1980, 2026))
    
    search_year = year_sport_search.strip() if year_sport_search else ""
    
    for sport in sports:
        if search_year:
            filtered_years = [y for y in years if search_year in str(y)]
            if not filtered_years:
                continue
        else:
            filtered_years = years
        
        with st.expander(f"**{sport}** ({len(filtered_years)} years)", expanded=expand_all_sports or bool(search_year)):
            html = ['<div style="display:grid;grid-template-columns:repeat(8,1fr);gap:4px 8px;font-size:13px;">']
            for year in filtered_years:
                url = ebay_search_url(f"{year} {sport} (PSA, BGS, Beckett)", sold=True, min_price=50, exclude_auto=True)
                html.append(f'<div><a href="{url}" target="_blank">{year}</a></div>')
            html.append('</div>')
            st.markdown(''.join(html), unsafe_allow_html=True)

elif page == "Junk Wax Gems":
    st.header("📦 JUNK WAX GEMS (1987-1992)")
    st.caption("The FEW cards from the overproduction era actually worth grading. PSA 10 or bust!")
    
    # MLB
    st.subheader("⚾ MLB - Key Rookies Worth Grading")
    mlb_junk = [
        ("Barry Bonds", "1987 Topps #320"), ("Barry Bonds", "1987 Fleer #604"),
        ("Mark McGwire", "1987 Topps #366"), ("Mark McGwire", "1987 Donruss #46"),
        ("Bo Jackson", "1987 Topps #170"), ("Greg Maddux", "1987 Topps #36"),
        ("Will Clark", "1987 Topps #420"), ("Tom Glavine", "1988 Topps #779"),
        ("Roberto Alomar", "1988 Topps #4"), ("Ken Griffey Jr", "1989 Upper Deck #1"),
        ("Ken Griffey Jr", "1989 Bowman #220"), ("Ken Griffey Jr", "1989 Donruss #33"),
        ("Craig Biggio", "1989 Upper Deck #273"), ("Randy Johnson", "1989 Fleer #381"),
        ("John Smoltz", "1989 Donruss #642"), ("Gary Sheffield", "1989 Upper Deck #13"),
        ("Frank Thomas", "1990 Topps #414"), ("Frank Thomas", "1990 Leaf #300"),
        ("Sammy Sosa", "1990 Leaf #220"), ("Larry Walker", "1990 Topps #757"),
        ("David Justice", "1990 Topps #48"), ("Juan Gonzalez", "1990 Topps #331"),
        ("Chipper Jones", "1991 Topps #333"), ("Ivan Rodriguez", "1991 Topps #101"),
        ("Jeff Bagwell", "1991 Topps #755"), ("Jim Thome", "1991 Topps #353"),
        ("Mike Piazza", "1992 Bowman #461"), ("Manny Ramirez", "1992 Bowman #532"),
        ("Pedro Martinez", "1992 Bowman #82"), ("Mariano Rivera", "1992 Bowman #302"),
    ]
    html = ['<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px 10px;font-size:13px;">']
    for player, card in sorted(mlb_junk, key=lambda x: x[0]):
        url = ebay_search_url(f"{player} {card}", sold=True, min_price=50, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{player} - {card}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)
    
    # NBA
    st.subheader("🏀 NBA - Key Rookies Worth Grading")
    nba_junk = [
        ("Michael Jordan", "1987 Fleer #59"), ("Michael Jordan", "1988 Fleer #17"),
        ("Michael Jordan", "1989 Fleer #21"), ("Michael Jordan", "1990 Fleer #26"),
        ("Scottie Pippen", "1988 Fleer #20"), ("Reggie Miller", "1988 Fleer #57"),
        ("Dennis Rodman", "1989 Hoops #211"), ("David Robinson", "1989 Hoops #138"),
        ("David Robinson", "1989 Fleer #76"), ("Gary Payton", "1990 Hoops #391"),
        ("Shawn Kemp", "1990 Hoops #279"), ("Tim Hardaway", "1990 Hoops #113"),
        ("Dikembe Mutombo", "1991 Hoops #549"), ("Larry Johnson", "1991 Hoops #547"),
        ("Shaquille O'Neal", "1992 Topps #362"), ("Shaquille O'Neal", "1992 Fleer #401"),
        ("Shaquille O'Neal", "1992 Upper Deck #1"), ("Alonzo Mourning", "1992 Topps #393"),
        ("Charles Barkley", "1987 Fleer #9"), ("Patrick Ewing", "1987 Fleer #37"),
        ("Karl Malone", "1987 Fleer #68"), ("John Stockton", "1987 Fleer #115"),
        ("Hakeem Olajuwon", "1987 Fleer #80"), ("Clyde Drexler", "1987 Fleer #30"),
    ]
    html = ['<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px 10px;font-size:13px;">']
    for player, card in sorted(nba_junk, key=lambda x: x[0]):
        url = ebay_search_url(f"{player} {card}", sold=True, min_price=50, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{player} - {card}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)
    
    # NFL
    st.subheader("🏈 NFL - Key Rookies Worth Grading")
    nfl_junk = [
        ("Bo Jackson", "1987 Topps #327"), ("Barry Sanders", "1989 Score #257"),
        ("Barry Sanders", "1989 Topps Traded #83T"), ("Deion Sanders", "1989 Score #246"),
        ("Troy Aikman", "1989 Score #270"), ("Troy Aikman", "1989 Topps Traded #70T"),
        ("Emmitt Smith", "1990 Score #101"), ("Emmitt Smith", "1990 Topps Traded #27T"),
        ("Brett Favre", "1991 Stadium Club #94"), ("Brett Favre", "1991 Ultra #283"),
        ("Junior Seau", "1990 Score #302"), ("Thurman Thomas", "1988 Topps #226"),
        ("Sterling Sharpe", "1988 Topps #392"), ("Tim Brown", "1988 Topps #144"),
        ("Cris Carter", "1988 Topps #119"), ("Michael Irvin", "1989 Score #18"),
        ("Derrick Thomas", "1989 Score #258"), ("Andre Rison", "1989 Score #272"),
        ("Rod Woodson", "1987 Topps #264"), ("Cortez Kennedy", "1990 Score #599"),
    ]
    html = ['<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px 10px;font-size:13px;">']
    for player, card in sorted(nfl_junk, key=lambda x: x[0]):
        url = ebay_search_url(f"{player} {card}", sold=True, min_price=50, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{player} - {card}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)
    
    # NHL
    st.subheader("🏒 NHL - Key Rookies Worth Grading")
    nhl_junk = [
        ("Brett Hull", "1988 Topps #66"), ("Joe Sakic", "1989 O-Pee-Chee #113"),
        ("Jaromir Jagr", "1990 Score #428"), ("Sergei Fedorov", "1990 Score #429"),
        ("Pavel Bure", "1990 Upper Deck #526"), ("Eric Lindros", "1991 Score #440"),
        ("Martin Brodeur", "1991 Upper Deck #146"), ("Dominik Hasek", "1991 Upper Deck #335"),
        ("Teemu Selanne", "1992 Upper Deck #406"), ("Luc Robitaille", "1987 Topps #42"),
        ("Brian Leetch", "1988 Topps #196"), ("Jeremy Roenick", "1989 Topps #111"),
        ("Mike Modano", "1989 Topps #174"), ("Nicklas Lidstrom", "1991 Upper Deck #167"),
    ]
    html = ['<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px 10px;font-size:13px;">']
    for player, card in sorted(nhl_junk, key=lambda x: x[0]):
        url = ebay_search_url(f"{player} {card}", sold=True, min_price=50, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{player} - {card}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)
    
    st.info("💡 **Junk Wax Tip:** Most base cards are worthless. Only PSA 10s of key rookies and stars have value. Centering is everything!")

elif page == "90s NBA":
    st.header("🏀 90s NBA STARS")
    st.caption("Click = eBay SOLD $50+, no autos (any grade)")
    
    nba_90s_stars = [
        "Alonzo Mourning", "Anfernee Hardaway", "Charles Barkley", "Christian Laettner",
        "Cliff Robinson", "Clyde Drexler", "David Robinson", "Dikembe Mutombo",
        "Doc Rivers", "Dominique Wilkins", "Gary Payton", "Glen Rice",
        "Hakeem Olajuwon", "Isiah Thomas", "Jason Kidd", "John Stockton",
        "Karl Malone", "Kevin McHale", "Larry Bird", "Latrell Sprewell",
        "Magic Johnson", "Moses Malone", "Mugsy Bogues", "Patrick Ewing",
        "Reggie Miller", "Scottie Pippen", "Shaquille O'Neal", "Shawn Bradley",
        "Shawn Kemp", "Steve Kerr", "Tim Hardaway", "Toni Kukoc", "Vlade Divac",
    ]
    
    html = ['<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px 12px;font-size:14px;">']
    for player in sorted(nba_90s_stars):
        url = ebay_search_url(f"{player}", sold=True, min_price=50, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{player}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)

elif page == "Parallels & Inserts":
    st.header("🌈 Parallels & Inserts - PSA $100+ Sold")
    st.caption("Click = eBay SOLD $100+, no autos")
    
    # Prizm Parallels
    st.subheader("🔷 Prizm Parallels")
    prizm = ["Silver", "Gold", "Green", "Blue", "Red", "Orange", "Purple", "Pink", "Black", "Camo", "Tie Dye", "Disco", "Mojo", "Shimmer"]
    html = ['<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:4px 10px;font-size:13px;">']
    for p in prizm:
        url = ebay_search_url(f"Prizm {p} PSA", sold=True, min_price=100, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{p}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)
    
    # Optic
    st.subheader("🟣 Optic Parallels")
    optic = ["Holo", "Silver", "Blue", "Red", "Orange", "Pink", "Purple", "Gold", "Black", "Shock", "Wave"]
    html = ['<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:4px 10px;font-size:13px;">']
    for p in optic:
        url = ebay_search_url(f"Optic {p} PSA", sold=True, min_price=100, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{p}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)
    
    # Refractors
    st.subheader("💎 Refractors")
    refractors = ["Refractor", "Gold Refractor", "Red Refractor", "Blue Refractor", "Orange Refractor", "Atomic Refractor", "Xfractor", "Superfractor"]
    html = ['<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:4px 10px;font-size:13px;">']
    for p in refractors:
        url = ebay_search_url(f"{p} PSA", sold=True, min_price=100, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{p}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SP/SSP
    st.subheader("🎯 Short Prints & Variations")
    sp_ssp = ["SP Short Print", "SSP Super Short Print", "SP Variation", "Photo Variation", "Image Variation"]
    html = ['<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px 10px;font-size:13px;">']
    for p in sp_ssp:
        url = ebay_search_url(f"{p} PSA", sold=True, min_price=100, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{p}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)
    
    # Numbered
    st.subheader("🔢 Numbered Cards")
    numbered = ["/1 One of One", "/5", "/10", "/25", "/50", "/75", "/99", "/199", "/299", "/499"]
    html = ['<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:4px 10px;font-size:13px;">']
    for p in numbered:
        url = ebay_search_url(f"Numbered {p} PSA", sold=True, min_price=100, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{p}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)
    
    # Premium Inserts
    st.subheader("🔥 Premium Inserts")
    inserts = ["Kaboom", "Downtown", "Color Blast", "Case Hit", "Net Marvels", "Cracked Ice", "Mojo", "Shimmer"]
    html = ['<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:4px 10px;font-size:13px;">']
    for p in inserts:
        url = ebay_search_url(f"{p} PSA", sold=True, min_price=100, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{p}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)
    
    # Premium Sets
    st.subheader("👑 Premium Sets")
    premium = ["National Treasures", "Flawless", "Immaculate", "Exquisite", "Noir", "One", "Spectra", "Obsidian"]
    html = ['<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:4px 10px;font-size:13px;">']
    for p in premium:
        url = ebay_search_url(f"{p} PSA", sold=True, min_price=100, exclude_auto=True)
        html.append(f'<div><a href="{url}" target="_blank">{p}</a></div>')
    html.append('</div>')
    st.markdown(''.join(html), unsafe_allow_html=True)

elif page == "Search":
    st.header("eBay Price Lookup")
    
    col1, col2 = st.columns(2)
    with col1:
        player = st.text_input("Player Name", placeholder="LeBron James")
    with col2:
        year_set = st.text_input("Year/Set", placeholder="2003 Topps Chrome")
    
    col3, col4 = st.columns(2)
    with col3:
        card_num = st.text_input("Card # (optional)", placeholder="111")
    with col4:
        grade = st.selectbox("Grade", ["PSA 10", "PSA 9", "PSA 8", "BGS 9.5", "Any PSA"])
    
    if st.button("🔍 Search eBay Sold", type="primary"):
        query_parts = [p for p in [player, year_set, f"#{card_num}" if card_num else "", 
                                    grade if grade != "Any PSA" else "PSA"] if p]
        if query_parts:
            url = ebay_search_url(" ".join(query_parts), sold=True)
            st.markdown(f"### [Search eBay: {' '.join(query_parts)}]({url})")
    
    st.markdown("---")
    st.markdown("### Quick Links")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("[📊 PSA Price Guide](https://www.psacard.com/priceguide)")
        st.markdown("[🔍 130point Sales](https://130point.com/sales/)")
    with col2:
        st.markdown("[📈 Card Ladder](https://cardladder.com/)")
        st.markdown("[🏷️ COMC](https://www.comc.com/)")

elif page == "Key Sets":
    st.header("Key Sets to Always Check")
    
    with get_db() as conn:
        st.subheader("🔥 TIER 1 - Grade ANY card")
        try:
            tier1 = pd.read_sql_query(
                "SELECT set_name, sport, year, notes FROM valuable_sets WHERE tier=1 ORDER BY sport, year", conn)
            for sport in tier1['sport'].unique():
                with st.expander(f"**{sport.upper()}**"):
                    for _, row in tier1[tier1['sport'] == sport].iterrows():
                        url = ebay_search_url(f"{row['set_name']} PSA 10", sold=True)
                        st.markdown(f"**{row['set_name']}** - {row['notes'] or ''} [eBay]({url})")
        except:
            st.info("Key sets data not loaded.")

elif page == "Key Players":
    st.header("Key Players")
    
    with get_db() as conn:
        try:
            players = pd.read_sql_query("SELECT player_name, sport FROM key_players ORDER BY sport", conn)
            for sport in players['sport'].unique():
                with st.expander(f"**{sport.upper()}**", expanded=True):
                    sport_players = players[players['sport'] == sport]['player_name'].tolist()
                    cols = st.columns(3)
                    for i, p in enumerate(sport_players):
                        url = ebay_search_url(f"{p} PSA 10", sold=True)
                        cols[i % 3].markdown(f"[{p}]({url})")
        except:
            st.info("Key players data not loaded.")

elif page == "eBay Listings":
    st.header("📝 eBay Listing Generator")
    st.markdown("**Fill in card details → get a complete listing with all eBay item specifics.** Uses your reference DB for value context.")

    try:
        from ebay_listing_generator import (
            build_full_listing,
            format_for_copy,
            format_for_csv_row,
            CONDITION_OPTIONS,
            BRANDS,
            SPORT_EBAY,
        )

        with st.form("ebay_listing_form", clear_on_submit=False):
            st.subheader("Card Details")
            col1, col2, col3 = st.columns(3)
            with col1:
                player = st.text_input("Player Name*", placeholder="Mark Brunell")
                year = st.number_input("Year*", min_value=1900, max_value=2026, value=1995)
                set_name = st.text_input("Set Name*", placeholder="Sports Illustrated Kids")
                brand = st.selectbox("Brand", BRANDS, index=BRANDS.index("Topps") if "Topps" in BRANDS else 0)
            with col2:
                sport = st.selectbox("Sport", list(SPORT_EBAY.values()))
                card_number = st.text_input("Card #", placeholder="123 or leave blank")
                team = st.text_input("Team", placeholder="Jacksonville Jaguars")
                is_rookie = st.checkbox("Rookie Card")
            with col3:
                is_graded = st.checkbox("Graded")
                grade = st.text_input("Grade", placeholder="PSA 10", disabled=not is_graded)
                cert_number = st.text_input("Cert #", placeholder="e.g. 12345678", disabled=not is_graded)

            condition = st.selectbox("Condition (ungraded)", CONDITION_OPTIONS, disabled=is_graded)
            variety = st.text_input("Variety/Parallel", placeholder="Base, Refractor, Silver Prizm, Holo...", value="Base")
            features = st.text_input("Features", placeholder="Serial Numbered, Autograph, etc.")
            suggested_price = st.text_input("Suggested Price", placeholder="$5-$15 or leave blank")
            description_extra = st.text_area("Extra description (optional)", placeholder="Additional notes for buyers...")

            submitted = st.form_submit_button("📝 Generate Full Listing")

        if submitted:
            sport_key = next((k for k, v in SPORT_EBAY.items() if v == sport), "football")
            listing = build_full_listing(
                player=player or "Unknown",
                year=int(year),
                set_name=set_name or "Unknown",
                brand=brand,
                sport=sport_key,
                card_number=card_number,
                team=team,
                is_rookie=is_rookie,
                is_graded=is_graded,
                grade=grade if is_graded else "",
                cert_number=cert_number if is_graded else "",
                condition=condition if not is_graded else "Graded",
                variety=variety or "Base",
                features=features,
                description_extra=description_extra,
                suggested_price=suggested_price,
            )

            st.success("✅ Listing generated! Copy each field into eBay.")

            col_a, col_b = st.columns(2)
            with col_a:
                st.text_area("TITLE (80 char max)", listing["title"], height=60, key="ebay_title")
                st.text_area("DESCRIPTION", listing["description"], height=200, key="ebay_desc")
            with col_b:
                st.markdown("**ITEM SPECIFICS**")
                for k, v in listing["item_specs"].items():
                    if v:
                        st.text_input(k, v, key=f"spec_{k.replace(' ', '_')}", disabled=True)
                st.info(f"**Price:** {listing['suggested_price']} | **Category:** {listing['category']}")
                st.caption(f"Keywords: {listing['keywords']}")

            if listing.get("value_context", {}).get("key_player") or listing.get("value_context", {}).get("tier1_set"):
                st.success("🔥 Key player / Tier 1 set - value context added to description!")

            st.download_button("Download .txt", format_for_copy(listing), file_name="ebay_listing.txt", key="dl_ebay")

    except ImportError as e:
        st.error("eBay listing module not available")
        st.code(str(e))

elif page == "2021 Topps S1":
    st.header("⚾ 2021 Topps Series 1 — Full Searchable Checklist")
    st.caption("Search by **player name**, **card number** (e.g. 86B-54), **team**, or **prefix** (e.g. 86B, T52). All eBay links: Sold, No Autos.")

    from data.topps_2021_s1 import ALL_CARDS, PREFIX_INFO

    # ── Search bar ────────────────────────────────────────────────────
    checklist_search = st.text_input(
        "🔍 Search the checklist",
        placeholder="e.g. Randy Johnson, 86B-54, Dodgers, T52, RC...",
        key="checklist_2021_search"
    ).strip()

    # ── Filter options ────────────────────────────────────────────────
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        filter_type = st.selectbox("Card Type", ["All", "Base Only", "Inserts Only", "RC Only"], key="filter_type_2021")
    with col_f2:
        show_max = st.selectbox("Show max results", [50, 100, 200, 330, 999], index=0, key="show_max_2021")
    with col_f3:
        min_price_filter = st.selectbox("Min eBay Price", [5, 10, 25, 50], index=0, key="min_price_2021")
    with col_f4:
        SEARCH_FORMATS = [
            "2021 Topps + Player",
            "2021 Topps S1 + Player",
            "2021 Topps + # + Player",
            "2021 Topps S1 + # + Player",
            "2021 Topps + # + Player + Team",
            "2021 Topps S1 + # + Player + Team",
        ]
        search_fmt = st.selectbox("eBay Search Format", SEARCH_FORMATS, index=2, key="search_fmt_2021")

    # ── Filter logic ──────────────────────────────────────────────────
    results = ALL_CARDS
    search_lower = checklist_search.lower()

    if search_lower:
        results = [
            c for c in results
            if search_lower in c[0].lower()       # card number
            or search_lower in c[1].lower()        # player
            or search_lower in c[2].lower()        # team
            or search_lower in c[3].lower()        # card type
            or search_lower in c[4].lower()        # notes
        ]

    if filter_type == "Base Only":
        results = [c for c in results if c[3] == "Base"]
    elif filter_type == "Inserts Only":
        results = [c for c in results if c[3] != "Base"]
    elif filter_type == "RC Only":
        results = [c for c in results if "RC" in c[4]]

    # ── Sort ──────────────────────────────────────────────────────────
    SORT_OPTIONS = {
        "Card # (default)": lambda c: (c[0].zfill(10) if c[0].isdigit() else c[0]),
        "Player A-Z": lambda c: c[1].lower(),
        "Player Z-A": lambda c: c[1].lower(),
        "Team A-Z": lambda c: c[2].lower(),
        "Type": lambda c: c[3].lower(),
    }
    sort_choice = st.selectbox("Sort by", list(SORT_OPTIONS.keys()), index=0, key="sort_2021")
    reverse_sort = sort_choice == "Player Z-A"
    results = sorted(results, key=SORT_OPTIONS[sort_choice], reverse=reverse_sort)

    total_matches = len(results)
    results = results[:show_max]

    st.markdown(f"**{total_matches}** cards found" + (f" (showing first {show_max})" if total_matches > show_max else ""))

    # ── If search matched a prefix, show prefix info banner ───────────
    prefix_upper = checklist_search.strip().upper()
    if prefix_upper in PREFIX_INFO:
        pinfo = PREFIX_INFO[prefix_upper]
        st.info(f"**{prefix_upper}** = {pinfo[0]} ({pinfo[1]}) — Parallels: {pinfo[2]}")

    # ── Results table with eBay links ─────────────────────────────────
    if results:
        html = ['<table style="width:100%;border-collapse:collapse;font-size:13px;">']
        html.append('<tr style="border-bottom:2px solid #555;text-align:left;">')
        html.append('<th style="padding:4px 8px;">Card #</th>')
        html.append('<th style="padding:4px 8px;">Player</th>')
        html.append('<th style="padding:4px 8px;">Team</th>')
        html.append('<th style="padding:4px 8px;">Type</th>')
        html.append('<th style="padding:4px 8px;">Notes</th>')
        html.append('<th style="padding:4px 8px;">eBay Sold $' + str(min_price_filter) + '+</th>')
        html.append('</tr>')

        for card_num, player_name, team, card_type, notes in results:
            # Build eBay query based on selected search format (use raw values)
            is_base = card_type == "Base" and card_num.isdigit()
            num_str = f"#{card_num}" if is_base else card_num
            s1 = "Series 1 " if "S1" in search_fmt else ""
            if "+ # + Player + Team" in search_fmt:
                ebay_q = f"2021 Topps {s1}{num_str} {player_name} {team}"
            elif "+ # + Player" in search_fmt:
                ebay_q = f"2021 Topps {s1}{num_str} {player_name}"
            elif "S1 + Player" in search_fmt:
                ebay_q = f"2021 Topps Series 1 {player_name}"
            else:  # "2021 Topps + Player"
                ebay_q = f"2021 Topps {player_name}"
            url_raw = ebay_search_url(ebay_q, sold=True, min_price=min_price_filter, exclude_auto=True, exclude_graded=True)
            url_graded = ebay_search_url(ebay_q, sold=True, min_price=min_price_filter, exclude_auto=True, graded_only=True)
            url_all = ebay_search_url(ebay_q, sold=True, min_price=min_price_filter, exclude_auto=True)

            # HTML-escape display values
            e_num = html_mod.escape(card_num)
            e_player = html_mod.escape(player_name)
            e_team = html_mod.escape(team)
            e_type = html_mod.escape(card_type.replace("Insert ", ""))
            e_notes = html_mod.escape(notes)

            # Row styling — green for RC, blue tint for inserts
            row_bg = ""
            if "RC" in notes:
                row_bg = ' style="background-color:rgba(0,200,0,0.08);"'
            elif card_type != "Base":
                row_bg = ' style="background-color:rgba(100,100,255,0.06);"'

            note_display = f'<span style="color:#FF6B6B;font-weight:bold;">{e_notes}</span>' if notes else ""

            html.append(f'<tr{row_bg}>')
            html.append(f'<td style="padding:3px 8px;font-weight:bold;">{e_num}</td>')
            html.append(f'<td style="padding:3px 8px;">{e_player}</td>')
            html.append(f'<td style="padding:3px 8px;color:#888;font-size:12px;">{e_team}</td>')
            html.append(f'<td style="padding:3px 8px;font-size:12px;">{e_type}</td>')
            html.append(f'<td style="padding:3px 8px;">{note_display}</td>')
            html.append(f'<td style="padding:3px 8px;white-space:nowrap;">')
            html.append(f'<a href="{url_raw}" target="_blank" title="Raw/Ungraded">🃏Raw</a>')
            html.append(f' · <a href="{url_graded}" target="_blank" title="Graded PSA/BGS/SGC">🏆Graded</a>')
            html.append(f' · <a href="{url_all}" target="_blank" title="All">📋All</a>')
            html.append('</td></tr>')

        html.append('</table>')
        st.markdown(''.join(html), unsafe_allow_html=True)
    else:
        st.warning("No cards found. Try a different search term.")

    # ── Prefix quick reference (collapsed) ────────────────────────────
    st.markdown("---")
    with st.expander("📋 All Insert Set Prefixes — Quick Reference"):
        pref_html = ['<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px 12px;font-size:13px;">']
        for code, (name, ctype, parallels) in PREFIX_INFO.items():
            url = ebay_search_url(f"2021 Topps {name}", sold=True, min_price=5, exclude_auto=True)
            pref_html.append(f'<div><a href="{url}" target="_blank"><b>{code}</b></a> — {name[:35]} <span style="color:#888;">({ctype})</span></div>')
        pref_html.append('</div>')
        st.markdown(''.join(pref_html), unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
**How to use:** Browse your collection, click eBay links to check real sold prices.
Only grade cards that are PSA 8+ condition AND sell for $100+ graded.
""")
st.markdown('<span style="color: #00FF00; font-size: 14px;">Economic Integrity LLC IP - Created 1/29/26</span>', unsafe_allow_html=True)
