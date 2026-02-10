# Configure Ollama for Card Grading

## ✅ Ollama is Installed! Now Let's Set It Up

---

## Step 1: Pull the Vision Model

Open **PowerShell** (regular, not admin) and run:

```powershell
ollama pull llava
```

This downloads the LLaVA vision model (~4-5 GB). It will take 5-10 minutes depending on your internet speed.

**Alternative (better quality, larger):**
```powershell
ollama pull llama3.2-vision
```
(~7GB, better quality but slower)

---

## Step 2: Verify Installation

After the model downloads, verify it works:

```powershell
ollama list
```

You should see:
```
NAME              ID              SIZE    MODIFIED
llava:latest      abc123...       4.7 GB  2 minutes ago
```

---

## Step 3: Test the Model

Test that vision analysis works:

```powershell
ollama run llava "Describe this image" --image path/to/test/image.jpg
```

Or just test the model loads:
```powershell
ollama run llava "Hello"
```

---

## Step 4: Configure Settings (Optional)

### **Model Location** (Current: `C:\Users\IP\.ollama\models`)
- ✅ **Keep default** - This is fine
- Or change if you want models on a different drive
- **Note:** Models can be large (4-7GB each), make sure you have space

### **Context Length** (Current: 4k)
- ✅ **4k is fine** for card grading (single image analysis)
- Increase to **8k or 16k** if you want longer conversations
- **32k+** only needed for very long documents

### **Airplane Mode** (Currently OFF)
- ✅ **Keep OFF** for now (allows cloud models if needed)
- Turn **ON** if you want 100% local-only (no cloud access)
- For card grading, **OFF is fine** - you're using local models anyway

### **Expose to Network** (Currently OFF)
- ✅ **Keep OFF** unless you need to access Ollama from other devices
- Turn **ON** only if you want to use Ollama from another computer/phone
- For local card grading, **OFF is fine**

---

## Step 5: Install Python Package

Now install the Python package to use Ollama in your code:

```powershell
cd "c:\Users\IP\Desktop\PSA"
pip install ollama
```

---

## Step 6: Test Python Integration

Test that Python can talk to Ollama:

```powershell
python -c "import ollama; print(ollama.list())"
```

Should show your models list.

---

## Step 7: Test Card Grading Module

Test your card grading module:

```powershell
python card_grading.py
```

Should show:
```
✅ Ollama is available
✅ Vision model ready: llava
```

---

## Step 8: Use in Streamlit App

Start your Streamlit app:

```powershell
python -m streamlit run app.py
```

Navigate to the **"🧙‍♂️ CARD GRADER"** tab and upload card images!

---

## Troubleshooting

### **"Model not found"**
```powershell
ollama pull llava
```

### **"Ollama not running"**
- Check system tray for Ollama icon
- Or run: `ollama serve` in PowerShell
- Ollama should auto-start, but sometimes needs manual start

### **Python can't connect**
- Make sure Ollama is running (check system tray)
- Try: `ollama list` in PowerShell first
- Restart terminal after installing `pip install ollama`

### **Slow analysis**
- First run is slower (model loading)
- Subsequent runs are faster
- Consider `llava` (smaller) instead of `llama3.2-vision` (larger)

---

## Quick Reference Commands

```powershell
# List models
ollama list

# Pull vision model
ollama pull llava

# Run model
ollama run llava "Describe this image" --image card.jpg

# Check version
ollama --version

# Stop Ollama
ollama stop

# Start Ollama (if not running)
ollama serve
```

---

## Next Steps

1. ✅ Pull vision model: `ollama pull llava`
2. ✅ Install Python package: `pip install ollama`
3. ✅ Test: `python card_grading.py`
4. ✅ Use in Streamlit app: Upload cards in "CARD GRADER" tab

**You're ready to grade cards for free!** 🎉
