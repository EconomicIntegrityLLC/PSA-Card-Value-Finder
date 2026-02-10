# Free Card Grading Setup Guide

This guide will help you set up **completely free** card grading using Ollama (runs locally, no API costs).

## Step 1: Install Ollama

1. **Download Ollama:**
   - Go to: https://ollama.com
   - Download for Windows
   - Install it

2. **Start Ollama:**
   - Ollama runs in the background after installation
   - You should see an Ollama icon in your system tray

## Step 2: Install Vision Model

Open PowerShell or Command Prompt and run:

```powershell
ollama pull llava
```

This downloads the LLaVA vision model (about 4-5 GB). It's free and runs locally.

**Alternative models (larger, potentially better):**
```powershell
ollama pull llama3.2-vision  # ~7GB, better quality
```

## Step 3: Install Python Package

```powershell
cd "c:\Users\IP\Desktop\PSA"
pip install ollama pillow
```

## Step 4: Test It Works

```powershell
python card_grading.py
```

You should see:
```
✅ Ollama is available
✅ Vision model ready: llava
```

## Step 5: Use in Streamlit App

The card grading module is ready! You can now:

1. **Add a new tab** to your `app.py` for card grading
2. **Upload card images** (up to 10 at a time)
3. **Get instant analysis** with tier assignments

## How It Works

- **TIER 1** 🚨: $1000+ graded potential → PAUSE ALL
- **TIER 2** 🟨: $10+ raw OR $100-999 graded → HOLD
- **TIER 3** 🟩: Everything else → BULK

The system analyzes:
- Card identification (player, year, set, rookie status)
- Condition (centering, corners, edges, surface)
- Grade ceiling (realistic PSA grade estimate)
- Market value estimates
- Whether back check is needed

## Troubleshooting

**"Ollama not found":**
- Make sure Ollama is installed and running
- Check system tray for Ollama icon
- Try: `ollama list` in terminal

**"Model not found":**
- Run: `ollama pull llava`
- Wait for download to complete (may take 5-10 minutes)

**Slow analysis:**
- First run is slower (model loading)
- Subsequent analyses are faster
- Consider using `llava` (smaller) instead of `llama3.2-vision` (larger)

## Cost: $0

Everything runs locally on your computer. No API costs, no subscriptions, no limits.
