# Fix Ollama Installation Error - "Access is denied"

## Problem
Error: "Access is denied" when installing Ollama to `C:\Program Files\Ollama\`

## Solutions (Try in Order)

### Solution 1: Run as Administrator (Most Common Fix)

1. **Close the current installer** (click Cancel)

2. **Right-click the Ollama installer** (.exe file)

3. **Select "Run as administrator"**

4. **Click "Yes"** when Windows asks for permission

5. **Try installing again**

This fixes 90% of "Access is denied" errors.

---

### Solution 2: Check if Ollama is Already Installed

The error mentions `unins000.exe` (uninstaller), which suggests Ollama might already be partially installed.

**Check:**
1. Press `Win + R`
2. Type: `appwiz.cpl`
3. Press Enter
4. Look for "Ollama" in the list
5. If found, **uninstall it first**, then reinstall

**Or check manually:**
- Go to `C:\Program Files\Ollama\`
- If folder exists, delete it (may need admin rights)
- Then reinstall

---

### Solution 3: Install to Different Location

If Program Files is blocked:

1. **Cancel current installation**

2. **Run installer as Administrator**

3. **When prompted for install location**, change to:
   ```
   C:\Users\IP\AppData\Local\Ollama
   ```
   or
   ```
   C:\Ollama
   ```

4. **Complete installation**

---

### Solution 4: Check Antivirus/Security Software

Sometimes antivirus blocks installations:

1. **Temporarily disable** antivirus/Windows Defender
2. **Try installing again**
3. **Re-enable** antivirus after installation

**Or add exception:**
- Add Ollama installer to antivirus exceptions
- Add `C:\Program Files\Ollama\` to exceptions

---

### Solution 5: Manual Cleanup (If Previous Install Failed)

1. **Close installer**

2. **Open PowerShell as Administrator:**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

3. **Run these commands:**
   ```powershell
   # Stop Ollama if running
   Stop-Process -Name ollama -Force -ErrorAction SilentlyContinue
   
   # Remove folder if it exists
   Remove-Item "C:\Program Files\Ollama" -Recurse -Force -ErrorAction SilentlyContinue
   
   # Remove from user folder
   Remove-Item "$env:USERPROFILE\.ollama" -Recurse -Force -ErrorAction SilentlyContinue
   ```

4. **Restart computer** (optional but helps)

5. **Download fresh installer** from https://ollama.com

6. **Run as Administrator** and install

---

### Solution 6: Use Portable Version (Alternative)

If installation keeps failing:

1. **Download Ollama** from https://ollama.com

2. **Extract to a folder** you have full access to:
   ```
   C:\Users\IP\Desktop\Ollama
   ```

3. **Run from there** (may need to add to PATH manually)

---

## Quick Fix Checklist

- [ ] Run installer as Administrator
- [ ] Check if Ollama already installed (uninstall first)
- [ ] Try different install location
- [ ] Temporarily disable antivirus
- [ ] Clean up previous failed install
- [ ] Restart computer
- [ ] Download fresh installer

---

## After Successful Installation

Once installed, verify it works:

1. **Open PowerShell** (regular, not admin)

2. **Test Ollama:**
   ```powershell
   ollama --version
   ```

3. **Should show version number** (e.g., "ollama version is 0.15.5")

4. **If error**, Ollama might not be in PATH - restart terminal or computer

---

## Still Having Issues?

**Common causes:**
- Windows User Account Control (UAC) blocking
- Antivirus blocking
- Previous failed install leaving locked files
- Insufficient disk space
- Corrupted installer download

**Try:**
1. Restart computer
2. Download fresh installer
3. Run as Administrator
4. Install to `C:\Ollama` instead of Program Files

---

## Once Installed Successfully

After Ollama is installed:

1. **Pull vision model:**
   ```powershell
   ollama pull llava
   ```

2. **Test it:**
   ```powershell
   ollama list
   ```

3. **Should show:** `llava` in the list

Then you can use the card grading feature!
