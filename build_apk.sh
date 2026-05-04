#!/bin/bash
# JJ Chess AI Assistant - Build APK Script (Linux/WSL)
# This script builds the Android APK using buildozer

set -e

echo "========================================"
echo "   JJ Chess AI - APK Builder"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "buildozer.spec" ]; then
    echo "Error: buildozer.spec not found!"
    echo "Please run this script from the project root."
    exit 1
fi

# Update system and install dependencies
echo "[Step 1] Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv \
    build-essential \
    git \
    wget \
    unzip \
    libpq-dev \
    cmake \
    swig

# Create virtual environment
echo ""
echo "[Step 2] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo ""
echo "[Step 3] Upgrading pip..."
pip install --upgrade pip

# Install Cython first (required for some packages)
echo ""
echo "[Step 4] Installing Cython..."
pip install cython

# Install buildozer
echo ""
echo "[Step 5] Installing buildozer..."
pip install buildozer

# Install Kivy and dependencies
echo ""
echo "[Step 6] Installing Kivy and dependencies..."
pip install kivy Pillow numpy opencv-python mss requests

# Initialize buildozer (downloads Android SDK/NDK)
echo ""
echo "[Step 7] Initializing buildozer..."
buildozer init

# Build the APK
echo ""
echo "[Step 8] Building APK..."
echo "This may take 20-40 minutes for the first build..."
buildozer android debug

echo ""
echo "========================================"
echo "Build completed!"
if [ -f "bin/*.apk" ]; then
    echo "APK found in: bin/"
    ls -la bin/*.apk
else
    echo "APK not found. Check logs above."
fi
echo "========================================"