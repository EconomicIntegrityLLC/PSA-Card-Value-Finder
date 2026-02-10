# Legal Open Source Packages for Card Grading & Pricing

## ✅ 100% Legal Options (No ToS Violations)

---

## 🖼️ Image Analysis (All Legal)

### **OpenCV (cv2)**
- ✅ **Legal:** Yes - Image processing library
- **Install:** `pip install opencv-python`
- **Use:** Card detection, corner analysis, centering measurement
- **License:** Apache 2.0 (open source)
- **Cost:** FREE

### **Pillow (PIL)**
- ✅ **Legal:** Yes - Image manipulation library
- **Install:** `pip install pillow` (you already have this)
- **Use:** Resize, crop, format conversion
- **License:** PIL License (open source)
- **Cost:** FREE

### **scikit-image**
- ✅ **Legal:** Yes - Scientific image processing
- **Install:** `pip install scikit-image`
- **Use:** Advanced edge detection, texture analysis
- **License:** BSD (open source)
- **Cost:** FREE

### **imagehash**
- ✅ **Legal:** Yes - Perceptual hashing library
- **Install:** `pip install imagehash`
- **Use:** Duplicate detection, card matching
- **License:** BSD (open source)
- **Cost:** FREE

---

## 🤖 AI/ML (All Legal)

### **Ollama**
- ✅ **Legal:** Yes - Local AI models
- **Install:** `pip install ollama` (you already have this)
- **Use:** Card image analysis, condition assessment
- **License:** MIT (open source)
- **Cost:** FREE (runs locally)

### **TensorFlow / PyTorch**
- ✅ **Legal:** Yes - Machine learning frameworks
- **Install:** `pip install tensorflow` or `pip install torch`
- **Use:** Train custom grading models
- **License:** Apache 2.0 (open source)
- **Cost:** FREE

### **scikit-learn**
- ✅ **Legal:** Yes - Traditional ML algorithms
- **Install:** `pip install scikit-learn`
- **Use:** Classification, regression, feature extraction
- **License:** BSD (open source)
- **Cost:** FREE

---

## 💰 Pricing APIs (Official, Legal)

### **eBay API (Official)**
- ✅ **Legal:** Yes - Official API from eBay
- **Install:** `pip install ebaysdk`
- **Use:** Search sold listings, get pricing data
- **Requirements:**
  - Free API keys from eBay Developer Program
  - Sign up: https://developer.ebay.com/
  - Free tier: 5,000 calls/day
- **License:** eBay's API terms (legal to use)
- **Cost:** FREE (up to 5,000 calls/day)

**Setup:**
1. Go to https://developer.ebay.com/
2. Create free account
3. Get API keys (App ID, Dev ID, Cert ID)
4. Use ebaysdk to make requests

**Example:**
```python
from ebaysdk.finding import Connection as Finding

api = Finding(appid='YOUR_APP_ID', config_file=None)
response = api.execute('findCompletedItems', {
    'keywords': 'LeBron James PSA 10',
    'itemFilter': [{'name': 'SoldItemsOnly', 'value': 'True'}]
})
```

### **PSA Public API (Official)**
- ✅ **Legal:** Yes - Official PSA API
- **Use:** Look up PSA certification details
- **Requirements:**
  - PSA account
  - OAuth 2 authentication
- **Docs:** https://www.psacard.com/publicapi
- **Cost:** FREE (with PSA account)

### **PokemonPriceTracker PSA API**
- ✅ **Legal:** Yes - Third-party PSA data API
- **Use:** PSA pricing, population reports, ROI analysis
- **Requirements:**
  - Account signup
  - API subscription ($19-49/month)
- **Note:** Paid service, but legal/legitimate
- **Cost:** $19-49/month (not free, but legal)

---

## 📊 Data Processing (All Legal)

### **pandas**
- ✅ **Legal:** Yes - Data manipulation
- **Install:** Already in your requirements
- **Use:** Process collections, analyze data
- **License:** BSD (open source)
- **Cost:** FREE

### **numpy**
- ✅ **Legal:** Yes - Numerical computing
- **Install:** `pip install numpy`
- **Use:** Image arrays, mathematical operations
- **License:** BSD (open source)
- **Cost:** FREE

---

## 🔍 OCR (All Legal)

### **pytesseract**
- ✅ **Legal:** Yes - OCR library
- **Install:** `pip install pytesseract`
- **Use:** Extract text from card images
- **Requirements:** Tesseract OCR (separate install)
- **License:** Apache 2.0 (open source)
- **Cost:** FREE

### **easyocr**
- ✅ **Legal:** Yes - Easy OCR
- **Install:** `pip install easyocr`
- **Use:** Text extraction (no separate install needed)
- **License:** Apache 2.0 (open source)
- **Cost:** FREE

---

## 🚫 What to AVOID (Legal Issues)

### ❌ **Web Scraping (Generally Not Legal)**
- **130Point.com** - No public API, scraping violates ToS
- **eBay scraping** - Use official API instead
- **Any site without API** - Scraping usually violates ToS

### ❌ **Rate Limiting Bypasses**
- Don't use proxies to bypass rate limits
- Don't use bots to avoid detection
- Don't scrape faster than human speed

### ⚠️ **Gray Area (Use Caution)**
- **BeautifulSoup** - Legal library, but scraping may violate ToS
- **Selenium** - Legal tool, but automation may violate ToS
- **Note:** The tool is legal, but HOW you use it matters

---

## ✅ Recommended Legal Stack

### **For Card Grading (Image Analysis)**
```python
pip install opencv-python pillow scikit-image imagehash numpy
```
**All legal, all free, all open source**

### **For AI Analysis**
```python
pip install ollama
```
**Legal, free, runs locally**

### **For Price Lookup**
```python
pip install ebaysdk
```
**Legal, free (with eBay API keys), official**

### **Complete Legal Stack**
```python
# Your existing
streamlit pandas beautifulsoup4 requests lxml plotly

# Add for image analysis (legal)
opencv-python scikit-image imagehash numpy

# Add for AI (legal, free)
ollama

# Add for pricing (legal, official API)
ebaysdk
```

**Total Cost: $0** (all free, all legal)

---

## 📋 eBay API Setup (Legal Way to Get Prices)

### Step 1: Get API Keys
1. Go to https://developer.ebay.com/
2. Sign up (free)
3. Create app → Get credentials:
   - App ID (Client ID)
   - Dev ID
   - Cert ID (Client Secret)

### Step 2: Install SDK
```powershell
pip install ebaysdk
```

### Step 3: Use in Code
```python
from ebaysdk.finding import Connection as Finding

# Initialize with your App ID
api = Finding(
    appid='YOUR_APP_ID',
    config_file=None
)

# Search sold items
response = api.execute('findCompletedItems', {
    'keywords': 'LeBron James PSA 10',
    'itemFilter': [
        {'name': 'SoldItemsOnly', 'value': 'True'},
        {'name': 'MinPrice', 'value': '100'}
    ]
})

# Parse results
items = response.dict()['searchResult']['item']
for item in items:
    print(f"{item['title']}: ${item['sellingStatus']['currentPrice']['value']}")
```

### Step 4: Rate Limits (Free Tier)
- **5,000 calls per day** (free)
- **More than enough** for personal use
- **Upgrade available** if needed (paid)

---

## 🎯 Legal Alternatives to Scraping

### **Instead of Scraping 130Point:**
1. ✅ Use eBay API (official, legal)
2. ✅ Use PSA API (official, legal)
3. ✅ Manual lookup (slow but legal)
4. ✅ Use PokemonPriceTracker API (paid but legal)

### **Instead of Scraping eBay:**
1. ✅ Use eBay API (official, legal, free tier)
2. ✅ Use ebaysdk Python wrapper (legal)

### **Instead of Scraping PSA:**
1. ✅ Use PSA Public API (official, legal)
2. ✅ Use PokemonPriceTracker API (paid but legal)

---

## 📚 Legal Resources

### **eBay API Documentation**
- Official: https://developer.ebay.com/
- Python SDK: https://github.com/timotheus/ebaysdk-python
- Free tier: 5,000 calls/day

### **PSA API Documentation**
- Official: https://www.psacard.com/publicapi
- Requires: PSA account + OAuth 2

### **Open Source Licenses (All Legal)**
- Apache 2.0: OpenCV, TensorFlow, pytesseract
- BSD: pandas, numpy, scikit-learn, scikit-image
- MIT: Ollama
- PIL License: Pillow

---

## ✅ Summary: 100% Legal Stack

**Image Analysis:**
- ✅ OpenCV
- ✅ Pillow
- ✅ scikit-image
- ✅ imagehash

**AI/ML:**
- ✅ Ollama (free, local)

**Pricing:**
- ✅ eBay API (official, free tier)
- ✅ PSA API (official, free with account)

**Data Processing:**
- ✅ pandas
- ✅ numpy

**All Legal, All Free, All Open Source**

---

## 🚀 Quick Start (Legal Only)

```powershell
# Install legal packages
pip install opencv-python scikit-image imagehash numpy ebaysdk

# You already have:
# streamlit pandas beautifulsoup4 requests lxml plotly ollama pillow
```

**Note:** `beautifulsoup4` and `selenium` are legal libraries, but using them to scrape websites may violate those sites' Terms of Service. Use eBay API instead for pricing data.

---

## 💡 Pro Tip

**Best Legal Approach:**
1. Use **eBay API** for pricing (official, free)
2. Use **OpenCV** for image analysis (legal, free)
3. Use **Ollama** for AI grading (legal, free, local)
4. **Avoid scraping** - use official APIs instead

This gives you everything you need, legally, for free.
