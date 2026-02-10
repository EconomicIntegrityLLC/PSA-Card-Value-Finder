# Android Studio Emulator Setup Guide for CollX

## Quick Setup Steps

### 1. Download Android Studio
- Go to: https://developer.android.com/studio
- Download Android Studio (includes the emulator)
- File size: ~1GB download, ~3GB installed

### 2. Install Android Studio
- Run the installer
- Choose "Standard" installation
- Let it download SDK components (this takes 10-20 minutes)
- **Important**: Make sure "Android Virtual Device (AVD)" is checked during installation

### 3. Create Your Virtual Device
1. Open Android Studio
2. Click **More Actions** → **Virtual Device Manager** (or View → Tool Windows → Device Manager)
3. Click **Create Device**
4. Select **Phone** → **Pixel 7** (or any recent Pixel model)
5. Click **Next**
6. Select **Android 13** or **Android 14** (API 33 or 34) - download if needed
7. Click **Next** → **Finish**

### 4. Configure for Photo Uploads
1. In Virtual Device Manager, click the **▼** next to your device
2. Click **Edit** (pencil icon)
3. Under **Advanced Settings**:
   - **RAM**: Set to 4096 MB (4GB) or higher if you have 16GB+ RAM
   - **VM heap**: 512 MB
   - **Internal Storage**: 2048 MB minimum
4. Click **Finish**

### 5. Start the Emulator
- Click the **▶ Play** button next to your device
- First boot takes 2-3 minutes (subsequent boots are faster)

### 6. Install CollX App
1. Once emulator is running, open **Play Store** in the emulator
2. Sign in with your Google account
3. Search for **"CollX"** or **"CollX: Sports Card Scanner"**
4. Install the app

### 7. Import Photos for CollX
**Method 1: Drag & Drop (Easiest)**
- Drag photos from Windows Explorer directly into the emulator window
- Photos will appear in the emulator's Gallery/Photos app
- Open CollX and select photos from Gallery

**Method 2: Using Camera Import**
1. In Android Studio, click the **...** menu in the emulator toolbar
2. Go to **Camera** tab
3. Click **Import** and select your card photos
4. In CollX, use camera feature - it will use the imported photos

**Method 3: ADB Push (Advanced)**
- Open PowerShell in the emulator's platform-tools folder
- Run: `adb push "C:\path\to\your\photo.jpg" /sdcard/Download/`
- Photos appear in Downloads folder

## System Requirements
- **RAM**: 16GB recommended (8GB minimum)
- **Storage**: 16GB free space
- **OS**: Windows 10/11 (64-bit)
- **CPU**: Modern processor (Intel i5/i7 or AMD Ryzen)

## Tips for Best Performance
1. **Enable Hardware Acceleration**: 
   - Check BIOS settings for Intel VT-x or AMD-V (virtualization)
   - Windows: Enable "Virtual Machine Platform" in Windows Features

2. **Allocate Resources**:
   - Close other heavy applications
   - Give emulator 4-8GB RAM if you have 16GB+ total

3. **Photo Workflow**:
   - Take photos with your phone camera (better quality)
   - Transfer to PC via USB/cloud
   - Import into emulator
   - Upload via CollX

## Troubleshooting

**Emulator is slow:**
- Increase RAM allocation
- Enable hardware acceleration
- Close other programs

**Can't find Play Store:**
- Make sure you selected a Google Play system image (not AOSP)
- Recreate device with Google Play image

**Photos won't import:**
- Try drag & drop method first
- Check file format (JPG/PNG work best)
- Use ADB push method as backup

## Quick Reference
- **Start Emulator**: Virtual Device Manager → Click Play button
- **Import Photos**: Drag & drop into emulator window
- **CollX App**: Install from Play Store in emulator
