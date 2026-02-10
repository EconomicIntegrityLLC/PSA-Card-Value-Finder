# Open Source Python Packages for Card Grading & Pricing

## 🖼️ Image Analysis & Computer Vision

### Core Libraries (Free, Well-Maintained)

#### **OpenCV (cv2)**
- **Purpose:** Image processing, card detection, edge detection, corner analysis
- **Install:** `pip install opencv-python`
- **Use Cases:**
  - Detect card boundaries in photos
  - Analyze corners for rounding/whitening
  - Measure centering (pixel-level precision)
  - Edge detection for wear/chips
  - Surface defect detection
- **GitHub:** https://github.com/opencv/opencv
- **License:** Apache 2.0
- **Status:** ✅ Actively maintained, industry standard

#### **Pillow (PIL)**
- **Purpose:** Image manipulation, resizing, format conversion
- **Install:** `pip install pillow`
- **Use Cases:**
  - Resize card images for analysis
  - Convert formats (JPG, PNG, etc.)
  - Crop images to card boundaries
  - Basic image enhancement
- **GitHub:** https://github.com/python-pillow/Pillow
- **License:** PIL License (open source)
- **Status:** ✅ Actively maintained

#### **scikit-image**
- **Purpose:** Advanced image processing algorithms
- **Install:** `pip install scikit-image`
- **Use Cases:**
  - Advanced edge detection
  - Texture analysis (surface defects)
  - Color analysis
  - Image segmentation
- **GitHub:** https://github.com/scikit-image/scikit-image
- **License:** BSD
- **Status:** ✅ Actively maintained

#### **imagehash**
- **Purpose:** Perceptual hashing for duplicate detection
- **Install:** `pip install imagehash`
- **Use Cases:**
  - Detect duplicate cards
  - Find similar cards in collection
  - Card identification via hash matching
- **GitHub:** https://github.com/JohannesBuchner/imagehash
- **License:** BSD
- **Status:** ✅ Actively maintained

---

## 🎯 Card Grading Projects (Complete Solutions)

### **CardScryer**
- **GitHub:** https://github.com/blakebjorn/CardScryer
- **Stars:** ~30 ⭐
- **Language:** Python
- **Dependencies:** OpenCV, PIL, imagehash, pandas
- **Features:**
  - Computer vision card classification
  - Appraisal/valuation
  - Card identification
- **License:** Check repo
- **Status:** ✅ Active project

### **mint_condition**
- **GitHub:** https://github.com/rthorst/mint_condition
- **Stars:** ~59 ⭐
- **Language:** Python
- **Features:**
  - Automatic sports card grading
  - API + Frontend included
  - Web scraping for training data
  - ResNet-18 CNN model
- **License:** Check repo
- **Status:** ✅ Active project
- **Note:** Trained on 90,000+ eBay graded cards

### **trading_card_grading_capstone**
- **GitHub:** https://github.com/BrianMillerS/trading_card_grading_capstone
- **Language:** Python
- **Features:**
  - CNN-based grading (ResNet-50)
  - Baseball card focused
  - Data processing pipeline
  - Model training code included
- **License:** Check repo
- **Status:** ✅ Academic project

### **card_board**
- **GitHub:** https://github.com/jmcrawford45/card_board
- **Language:** Python
- **License:** Apache 2.0
- **Features:**
  - Reads and grades collectible cards
  - Documentation included
  - Example implementations
- **Status:** ✅ Active

### **KYC (Know Your Cards)**
- **GitHub:** https://github.com/u-siri-ous/KYC
- **Language:** Python
- **License:** AGPL-3.0
- **Features:**
  - Card grader
  - Classifier
  - Game cards focus
- **Status:** ✅ Active

---

## 💰 Pricing & Value Lookup

### **eBay API Wrappers**

#### **ebaysdk-python**
- **Purpose:** Official eBay API wrapper
- **Install:** `pip install ebaysdk`
- **GitHub:** https://github.com/timotheus/ebaysdk-python
- **License:** Apache 2.0
- **Use Cases:**
  - Search sold listings
  - Get pricing data
  - Requires eBay API keys (free tier available)
- **Status:** ✅ Maintained

#### **python-ebay-api**
- **Purpose:** Alternative eBay API wrapper
- **Install:** `pip install python-ebay-api`
- **GitHub:** Various forks available
- **Use Cases:** Similar to ebaysdk
- **Status:** ⚠️ Check specific fork

### **Price Scraping Projects**

#### **trading_card_price_scraper**
- **GitHub:** https://github.com/synderis/trading_card_price_scraper
- **Language:** Python
- **Features:**
  - Full-stack scraper
  - Backend + Frontend
  - Price data collection
- **License:** Check repo
- **Status:** ✅ Active
- **Note:** Scraping may violate ToS - use responsibly

#### **eBay-Fun**
- **GitHub:** https://github.com/LucasMolander/eBay-Fun
- **Language:** Python
- **License:** MIT
- **Features:**
  - Find underpriced cards
  - True price detection
  - Buy-it-now scanner
- **Status:** ✅ Active

#### **cardbytes**
- **GitHub:** https://github.com/jon-gerhartz/cardbytes
- **Language:** Python/Flask
- **Features:**
  - Portfolio tracking
  - eBay API integration
  - Price tracking
- **Status:** ✅ Active

### **130Point Alternatives (Scraping)**

**Note:** 130Point doesn't have a public API, but you can scrape it (check ToS)

#### **beautifulsoup4** (You already have this)
- **Purpose:** Web scraping
- **Install:** `pip install beautifulsoup4`
- **Use Cases:**
  - Scrape 130Point.com
  - Scrape eBay sold listings
  - Extract pricing data
- **Status:** ✅ Actively maintained

#### **selenium**
- **Purpose:** Browser automation for JavaScript-heavy sites
- **Install:** `pip install selenium`
- **Use Cases:**
  - Scrape dynamic sites
  - Handle JavaScript-rendered content
  - More robust than BeautifulSoup for modern sites
- **Status:** ✅ Actively maintained

---

## 🤖 Machine Learning / AI

### **TensorFlow / PyTorch**
- **Purpose:** Deep learning for custom grading models
- **Install:** `pip install tensorflow` or `pip install torch`
- **Use Cases:**
  - Train custom card grading models
  - Transfer learning from pre-trained models
  - CNN for condition assessment
- **Status:** ✅ Industry standard

### **scikit-learn**
- **Purpose:** Traditional ML algorithms
- **Install:** `pip install scikit-learn`
- **Use Cases:**
  - Classification models
  - Regression for price prediction
  - Feature extraction
- **Status:** ✅ Actively maintained

### **Ollama** (You're already using this!)
- **Purpose:** Local AI models (vision + text)
- **Install:** `pip install ollama`
- **Use Cases:**
  - Card image analysis
  - Condition assessment
  - Card identification
- **Status:** ✅ Actively maintained
- **Cost:** FREE (runs locally)

---

## 📊 Data Processing

### **pandas** (You already have this)
- **Purpose:** Data manipulation, CSV handling
- **Use Cases:**
  - Process card collections
  - Analyze pricing data
  - Export results

### **numpy**
- **Purpose:** Numerical computing
- **Install:** `pip install numpy`
- **Use Cases:**
  - Image array manipulation
  - Mathematical operations on images
  - Statistical analysis

---

## 🔍 OCR & Text Recognition

### **pytesseract**
- **Purpose:** Extract text from card images
- **Install:** `pip install pytesseract`
- **Use Cases:**
  - Read card text (player names, years)
  - Extract set names
  - Read PSA slab labels
- **GitHub:** https://github.com/madmaze/pytesseract
- **Status:** ✅ Active
- **Note:** Requires Tesseract OCR installed separately

### **easyocr**
- **Purpose:** Easy-to-use OCR
- **Install:** `pip install easyocr`
- **Use Cases:**
  - Text extraction from cards
  - No separate installation needed
- **Status:** ✅ Active

---

## 🎨 Image Enhancement

### **opencv-contrib-python**
- **Purpose:** Extended OpenCV features
- **Install:** `pip install opencv-contrib-python`
- **Use Cases:**
  - Advanced image processing
  - Additional algorithms
- **Status:** ✅ Active

### **imgaug**
- **Purpose:** Image augmentation for training
- **Install:** `pip install imgaug`
- **Use Cases:**
  - Augment training data
  - Improve model robustness
- **Status:** ✅ Active

---

## 📦 Complete Package Recommendations

### **For Card Grading (Image Analysis)**
```python
pip install opencv-python pillow scikit-image imagehash numpy
```

### **For Price Lookup (Web Scraping)**
```python
pip install beautifulsoup4 requests selenium lxml
```

### **For ML/AI Grading**
```python
pip install tensorflow torch scikit-learn
# OR use Ollama (free, local):
pip install ollama
```

### **For Complete Solution**
```python
pip install opencv-python pillow beautifulsoup4 requests pandas numpy ollama
```

---

## 🚀 Quick Integration Ideas

### **1. Add OpenCV for Precise Centering**
```python
import cv2
import numpy as np

def measure_centering(image_path):
    """Measure card centering with pixel precision"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect card edges
    edges = cv2.Canny(gray, 50, 150)
    # Calculate border widths
    # Return centering score
```

### **2. Add Price Scraping**
```python
from bs4 import BeautifulSoup
import requests

def get_130point_price(player, year, set_name):
    """Scrape 130Point for pricing (check ToS first!)"""
    # Implementation here
    pass
```

### **3. Add Card Detection**
```python
import cv2

def detect_card_in_image(image_path):
    """Find card boundaries in photo"""
    img = cv2.imread(image_path)
    # Use contour detection
    # Return card bounding box
```

---

## ⚠️ Important Notes

### **Legal/Ethical Considerations**
- **Web Scraping:** Always check Terms of Service
- **eBay API:** Use official API when possible (free tier available)
- **130Point:** No public API - scraping may violate ToS
- **Rate Limiting:** Be respectful, don't overload servers

### **Best Practices**
- Use official APIs when available
- Respect robots.txt
- Add delays between requests
- Cache results to avoid repeated requests
- Consider using proxies for large-scale scraping

---

## 📚 Learning Resources

### **OpenCV Tutorials**
- Official docs: https://docs.opencv.org/
- PyImageSearch: https://www.pyimagesearch.com/

### **Card Grading Research**
- RoboFlow blog: "Using Computer Vision to Make Card Grading Faster"
- Academic papers on automated card grading

### **eBay API**
- Official docs: https://developer.ebay.com/
- Free sandbox available for testing

---

## 🎯 Recommended Stack for Your Project

Based on what you're building:

```python
# Core (you have these)
streamlit pandas beautifulsoup4 requests

# Add for image analysis
opencv-python pillow scikit-image

# Add for AI (free, local)
ollama

# Optional: Advanced ML
# tensorflow  # Only if training custom models
# pytesseract  # Only if you need OCR
```

**Total Cost: $0** (all open source, free)

---

## 🔗 Quick Links

- **OpenCV:** https://opencv.org/
- **Pillow:** https://pillow.readthedocs.io/
- **Ollama:** https://ollama.com/
- **eBay API:** https://developer.ebay.com/
- **130Point:** https://130point.com/ (no API, web only)
