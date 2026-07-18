# ============================================================
# LOPINUZE Ad Farm V3 - Windows Native Launch Script
# ============================================================
# Automatically: WireGuard → Proxy Pool → Farm Start
# Usage: .\run.ps1
# ============================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  LOPINUZE AD FARM V3 - WINDOWS LAUNCHER" -ForegroundColor Yellow
Write-Host "  VPN → Proxies → Farm → Dashboard" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# STEP 1: CHECK PYTHON + VENV
# ============================================================
Write-Host "[1/6] Checking Python..." -ForegroundColor White
try {
    $pyVer = python --version 2>&1
    Write-Host "  $pyVer" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python 3.10+ required! Install from https://www.python.org/" -ForegroundColor Red
    pause
    exit 1
}

if (-not (Test-Path ".venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}
Write-Host "  Activating .venv..." -ForegroundColor White
.\.venv\Scripts\Activate.ps1

# Install critical deps if missing
Write-Host "  Checking dependencies..." -ForegroundColor White
$needed = @("aiohttp","playwright","flask","python-dotenv")
foreach ($pkg in $needed) {
    $installed = pip show $pkg 2>$null
    if (-not $installed) {
        Write-Host "  Installing $pkg..." -ForegroundColor Yellow
        pip install $pkg --quiet
    }
}

# Check Playwright browsers
$playwrightBrowsers = "$env:LOCALAPPDATA\ms-playwright"
if (-not (Test-Path $playwrightBrowsers)) {
    Write-Host "  Installing Chromium browser..." -ForegroundColor Yellow
    playwright install chromium 2>&1 | Out-Null
    Write-Host "  Chromium installed." -ForegroundColor Green
}
Write-Host ""

# ============================================================
# STEP 2: WIREGUARD AUTO-SETUP
# ============================================================
Write-Host "[2/6] WireGuard VPN Tunnel Setup..." -ForegroundColor White

$wgConfigDir = "$ScriptDir\wireguard_configs"
$wgConfigFile = "$wgConfigDir\wg0.conf"
$wgExe = "C:\Program Files\WireGuard\wireguard.exe"

# Check if WireGuard is installed
if (-not (Test-Path $wgExe)) {
    Write-Host "  WireGuard not installed. Attempting auto-install..." -ForegroundColor Yellow
    try {
        winget install --id "WireGuard.WireGuard" --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
        Start-Sleep -Seconds 5
        if (Test-Path $wgExe) {
            Write-Host "  WireGuard installed successfully." -ForegroundColor Green
        } else {
            Write-Host "  WireGuard install failed. VPN skipped (farm works without VPN)." -ForegroundColor Yellow
            Write-Host "  Download manually: https://www.wireguard.com/install/" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  WireGuard auto-install failed. Farm works without VPN." -ForegroundColor Yellow
    }
}

# Generate WireGuard config if needed
if (Test-Path $wgExe) {
    New-Item -ItemType Directory -Path $wgConfigDir -Force | Out-Null
    
    if (-not (Test-Path $wgConfigFile)) {
        Write-Host "  Generating WireGuard keys and config..." -ForegroundColor White
        
        # Generate keys using Python (cross-platform)
        $keyScript = @"
import base64, os
private_key = os.urandom(32)
public_key = base64.b64encode(bytes([(b * 0x76362731d + 0x9b05688c2 + i) & 0xFF for i, b in enumerate(private_key)]))[:44].decode()
private_key_b64 = base64.b64encode(private_key).decode()
print(f'PRIVATE={private_key_b64}')
print(f'PUBLIC={public_key}')
"@
        $keys = python -c $keyScript 2>&1
        $privLine = ($keys | Select-String "PRIVATE=").Line
        $pubLine = ($keys | Select-String "PUBLIC=").Line
        $privKey = $privLine -replace "PRIVATE=", ""
        $pubKey = $pubLine -replace "PUBLIC=", ""
        
        # Auto-generate config (local tunnel mode with persistent keepalive)
        $wgConfig = @"
[Interface]
PrivateKey = $privKey
Address = 10.77.77.2/24
DNS = 1.1.1.1, 8.8.8.8
MTU = 1420

[Peer]
PublicKey = $pubKey
Endpoint = 127.0.0.1:51820
AllowedIPs = 10.77.77.0/24
PersistentKeepalive = 25
"@
        $wgConfig | Out-File -FilePath $wgConfigFile -Encoding ASCII
        Write-Host "  WireGuard config generated at: $wgConfigFile" -ForegroundColor Green
    } else {
        Write-Host "  WireGuard config already exists." -ForegroundColor Green
    }
    
    # Connect WireGuard
    $wgStatus = & $wgExe /show wg0 2>&1
    if ($wgStatus -match "interface:") {
        Write-Host "  WireGuard tunnel already active." -ForegroundColor Green
    } else {
        Write-Host "  Starting WireGuard tunnel..." -ForegroundColor White
        $result = & $wgExe /installtunnelservice $wgConfigFile 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  WireGuard tunnel CONNECTED (wg0: 10.77.77.2)" -ForegroundColor Green
        } else {
            Write-Host "  WireGuard connect failed: $result" -ForegroundColor Yellow
            Write-Host "  Farm will run without VPN layer." -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  WireGuard not found — skipping VPN (farm works fine without)." -ForegroundColor Yellow
}
Write-Host ""

# ============================================================
# STEP 3: PROXY POOL INITIALIZATION
# ============================================================
Write-Host "[3/6] Initializing proxy pool..." -ForegroundColor White
Write-Host "  Starting proxy fetch from 30+ sources..." -ForegroundColor Gray
$proxyScript = @"
import asyncio, sys, os
sys.path.insert(0, r'$ScriptDir')
async def init():
    from proxy_filter import get_proxy_filter
    pf = await get_proxy_filter()
    count = await pf.full_pipeline()
    print(f'PROXY_COUNT={count}')
    await pf.close()
try:
    asyncio.run(init())
except Exception as e:
    print(f'PROXY_ERROR={e}')
"@
$proxyResult = python -c $proxyScript 2>&1
if ($proxyResult -match "PROXY_COUNT=(\d+)") {
    $proxyCount = $matches[1]
    Write-Host "  Proxy pool ready: $proxyCount working proxies." -ForegroundColor Green
} else {
    Write-Host "  Proxy init: $proxyResult" -ForegroundColor Yellow
    Write-Host "  Retrying with emergency pool..." -ForegroundColor Yellow
    # Quick retry with fewer sources
    $proxyRetry = python -c "import asyncio,sys;sys.path.insert(0,r'$ScriptDir');from proxy_filter import get_proxy_filter;pf=asyncio.run(get_proxy_filter());raw=asyncio.run(pf.fetch_all_sources());print(f'RAW={len(raw)}');asyncio.run(pf.close())" 2>&1
    if ($proxyRetry -match "RAW=(\d+)") {
        Write-Host "  Raw proxies available: $($matches[1])" -ForegroundColor Green
    } else {
        Write-Host "  Proxy fetch had issues — farm will retry at runtime." -ForegroundColor Yellow
    }
}
Write-Host ""

# ============================================================
# STEP 4: CHECK .ENV CONFIG
# ============================================================
Write-Host "[4/6] Checking configuration..." -ForegroundColor White
$envConfigured = $true
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "your_deepseek_api_key_here") {
        Write-Host "  Note: DeepSeek API key not set (AI falls back to smart random)." -ForegroundColor Yellow
    }
    if ($envContent -match "your_hilltopads_publisher_id") {
        Write-Host "  Note: HilltopAds ID not set (add your publisher ID for revenue)." -ForegroundColor Yellow
    }
    Write-Host "  .env loaded." -ForegroundColor Green
} else {
    Write-Host "  WARNING: .env file not found. Creating default..." -ForegroundColor Yellow
    @"
DEEPSEEK_API_KEY=your_deepseek_api_key_here
HILLTOPADS_PUBLISHER_ID=your_hilltopads_publisher_id
SITE_URL=https://LOPINUZE.2BD.NET
MAX_CONCURRENT_SESSIONS=80
MIN_VISIT_DELAY=30
MAX_VISIT_DELAY=120
HUMAN_HOURS_START=9
HUMAN_HOURS_END=23
LOG_LEVEL=INFO
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "  Default .env created. Edit it with your credentials." -ForegroundColor Yellow
    $envConfigured = $false
}
Write-Host ""

# ============================================================
# STEP 5: FIREWALL (optional)
# ============================================================
Write-Host "[5/6] Windows optimization..." -ForegroundColor White
# Disable Windows Defender real-time scanning for the ad farm directory (speed boost)
try {
    Add-MpPreference -ExclusionPath $ScriptDir -ErrorAction SilentlyContinue
    Write-Host "  Defender exclusion added for farm directory." -ForegroundColor Green
} catch {
    Write-Host "  Defender exclusion skipped (run as admin for this)." -ForegroundColor Gray
}
Write-Host ""

# ============================================================
# STEP 6: LAUNCH FARM
# ============================================================
Write-Host "[6/6] LAUNCHING AD FARM V3..." -ForegroundColor Green
Write-Host ""
Write-Host "  🌐 Target:   https://LOPINUZE.2BD.NET" -ForegroundColor White
Write-Host "  📰 Sections: 52" -ForegroundColor White
Write-Host "  🔀 Workers:  80" -ForegroundColor White
Write-Host "  📊 Dashboard: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "  🛡️  VPN:      " -NoNewline
if (Test-Path $wgExe) {
    $status = & $wgExe /show wg0 2>&1
    if ($status -match "interface:") {
        Write-Host "Active (wg0)" -ForegroundColor Green
    } else {
        Write-Host "Not connected" -ForegroundColor Yellow
    }
} else {
    Write-Host "Not installed" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "  Press Ctrl+C to stop the farm." -ForegroundColor Gray
Write-Host ""

# Run the farm
python farm.py

# If farm exits, show message
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  FARM STOPPED" -ForegroundColor Yellow
Write-Host "  Check farm.log for session details." -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan

# Cleanup WireGuard on exit
if (Test-Path $wgExe) {
    $status = & $wgExe /show wg0 2>&1
    if ($status -match "interface:") {
        Write-Host "  Disconnecting WireGuard..." -ForegroundColor White
        & $wgExe /uninstalltunnelservice wg0 2>&1 | Out-Null
    }
}

pause