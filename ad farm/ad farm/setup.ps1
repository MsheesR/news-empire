# ============================================================
# LOPINUZE Ad Farm - Windows Setup Script
# ============================================================
# Run this once to install all dependencies.
# Usage: .\setup.ps1
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  LOPINUZE AD FARM - SETUP" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/5] Checking Python..." -ForegroundColor White
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found! Install Python 3.10+ first." -ForegroundColor Red
    Write-Host "  Download: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists and has been configured
Write-Host "[2/5] Checking .env configuration..." -ForegroundColor White
$envContent = Get-Content .\.env -Raw
if ($envContent -match "your_deepseek_api_key_here") {
    Write-Host "  WARNING: .env file has NOT been configured!" -ForegroundColor Yellow
    Write-Host "  Edit .env and fill in your API keys before running." -ForegroundColor Yellow
    Write-Host "  The farm will run with random behavior (no AI) until you set: " -ForegroundColor Yellow
    Write-Host "    - DEEPSEEK_API_KEY" -ForegroundColor Yellow
    Write-Host "    - MANGOPROXY_USERNAME" -ForegroundColor Yellow
    Write-Host "    - MANGOPROXY_PASSWORD" -ForegroundColor Yellow
} else {
    Write-Host "  .env looks configured" -ForegroundColor Green
}

# Create virtual environment
Write-Host "[3/5] Creating Python virtual environment..." -ForegroundColor White
if (Test-Path ".venv") {
    Write-Host "  Virtual environment already exists." -ForegroundColor Yellow
} else {
    python -m venv .venv
    Write-Host "  Virtual environment created." -ForegroundColor Green
}

# Activate and install dependencies
Write-Host "[4/5] Installing dependencies..." -ForegroundColor White
.\.venv\Scripts\Activate.ps1

Write-Host "  Upgrading pip..." -ForegroundColor Gray
python -m pip install --upgrade pip --quiet

Write-Host "  Installing requirements.txt..." -ForegroundColor Gray
pip install -r requirements.txt

# Install CloakBrowser specifically
Write-Host "  Installing CloakBrowser (C++ stealth layer)..." -ForegroundColor Gray
try {
    pip install cloakbrowser[geoip] 2>&1 | Out-Null
    Write-Host "  CloakBrowser installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: CloakBrowser install failed. Falling back to Playwright." -ForegroundColor Yellow
    Write-Host "  Playwright is DETECTABLE - quality score will be low." -ForegroundColor Yellow
    Write-Host "  Try: pip install cloakbrowser[geoip] --index-url https://pypi.org/simple/" -ForegroundColor Yellow
    pip install playwright
    playwright install chromium
}

# Create proxies.txt if needed
Write-Host "[5/5] Creating proxy file..." -ForegroundColor White
if (Test-Path "proxies.txt") {
    Write-Host "  proxies.txt already exists." -ForegroundColor Green
} else {
    @"
# LOPINUZE Ad Farm - Proxy List
# Add your proxies here, one per line.
# Format: http://username:password@ip:port
# 
# The farm auto-fetches from MangoProxy API by default.
# This file is only used as a fallback.
# 
# Examples:
# http://user:pass@123.45.67.89:8080
# http://user:pass@98.76.54.32:8081
"@ | Out-File -FilePath "proxies.txt" -Encoding UTF8
    Write-Host "  proxies.txt created (fallback file)." -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor White
Write-Host "  1. Edit .env with your API keys and MangoProxy credentials" -ForegroundColor Yellow
Write-Host "  2. Run the farm: .\run.ps1" -ForegroundColor Yellow
Write-Host "  3. Or directly: python farm.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "  IMPORTANT: The farm generates traffic to LOPINUZE.2BD.NET" -ForegroundColor Red
Write-Host "  Make sure your site has HilltopAds ad codes placed first!" -ForegroundColor Red
Write-Host "  See README.md for ad placement instructions." -ForegroundColor Red
Write-Host ""