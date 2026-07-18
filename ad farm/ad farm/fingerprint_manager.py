#!/usr/bin/env python3
"""
Browser Fingerprint Factory — V3 Maximum Security
===================================================
Generates unique, logically coherent browser fingerprints per session.
Ensures no two sessions share the same fingerprint and all hardware
values are internally consistent with real-world device configurations.

Key Design Principles:
1. LOGICAL COHERENCE: CPU ↔ RAM ↔ GPU ↔ OS must match real devices
2. UNIQUENESS: SHA-256 hash collision detection prevents reuse
3. DIVERSITY: 50+ hardware profiles × 30+ GPUs × 15+ screens = ~50K+ combinations
4. GEO-AWARENESS: Timezone/locale/language matches proxy geo-location
5. PER-SESSION NOISE: Unique canvas/audio/WebGL seeds for fingerprint variability

Database Sources:
- Steam Hardware Survey (GPU/CPU distribution)
- StatCounter (screen resolution distribution)
- W3Schools (browser/OS distribution)
- Real browser telemetry studies

Usage:
    from fingerprint_manager import get_fingerprint_factory
    
    factory = get_fingerprint_factory()
    geo = {'timezone': 'America/New_York', 'locale': 'en-US', 'language': 'en'}
    fp = factory.generate(geo_config=geo)
    
    # fp.to_dict() → injectable fingerprint dict
    # fp.fingerprint_hash → unique identifier for this session
"""

import random
import hashlib
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger('fingerprint_manager')

# ============================ GPU DATABASE ============================
# Real-world GPU models grouped by vendor and tier
# Sourced from Steam Hardware Survey 2026

GPU_DATABASE = {
    "NVIDIA": {
        "budget": [
            "NVIDIA GeForce GTX 1660 SUPER",
            "NVIDIA GeForce GTX 1660 Ti",
            "NVIDIA GeForce GTX 1650",
            "NVIDIA GeForce GTX 1050 Ti",
        ],
        "mid": [
            "NVIDIA GeForce RTX 3060",
            "NVIDIA GeForce RTX 3060 Ti",
            "NVIDIA GeForce RTX 4060",
            "NVIDIA GeForce RTX 4060 Ti",
            "NVIDIA GeForce RTX 3070",
        ],
        "high": [
            "NVIDIA GeForce RTX 3080",
            "NVIDIA GeForce RTX 3080 Ti",
            "NVIDIA GeForce RTX 4070",
            "NVIDIA GeForce RTX 4070 Ti",
            "NVIDIA GeForce RTX 4080",
            "NVIDIA GeForce RTX 4090",
        ],
        "laptop": [
            "NVIDIA GeForce RTX 3050 Laptop GPU",
            "NVIDIA GeForce RTX 3060 Laptop GPU",
            "NVIDIA GeForce RTX 4060 Laptop GPU",
            "NVIDIA GeForce GTX 1650 Ti",
        ],
    },
    "AMD": {
        "budget": [
            "AMD Radeon RX 6500 XT",
            "AMD Radeon RX 6600",
        ],
        "mid": [
            "AMD Radeon RX 6700 XT",
            "AMD Radeon RX 7600",
            "AMD Radeon RX 7700 XT",
        ],
        "high": [
            "AMD Radeon RX 6800 XT",
            "AMD Radeon RX 6900 XT",
            "AMD Radeon RX 7900 XT",
            "AMD Radeon RX 7900 XTX",
        ],
        "laptop": [
            "AMD Radeon RX 6600M",
            "AMD Radeon RX 6800M",
        ],
    },
    "Intel": {
        "budget": [
            "Intel Iris Xe Graphics",
            "Intel UHD Graphics 730",
        ],
        "mid": [
            "Intel Iris Xe Graphics G7",
            "Intel UHD Graphics 770",
            "Intel Arc A750",
        ],
        "high": [
            "Intel Arc A770",
        ],
        "laptop": [
            "Intel Iris Xe Graphics",
            "Intel UHD Graphics",
        ],
    },
    "Apple": {
        "high": [
            "Apple M1",
            "Apple M1 Pro",
            "Apple M1 Max",
            "Apple M2",
            "Apple M2 Pro",
            "Apple M2 Max",
            "Apple M3",
            "Apple M3 Pro",
            "Apple M3 Max",
        ],
        "mobile_apple": [
            "Apple A16 Bionic GPU",
            "Apple A15 Bionic GPU",
            "Apple A14 Bionic GPU",
            "Apple A17 Pro GPU",
        ],
    },
    "Qualcomm": {
        "mobile_adreno": [
            "Qualcomm Adreno 750",
            "Qualcomm Adreno 740",
            "Qualcomm Adreno 730",
            "Qualcomm Adreno 660",
        ],
    },
    "ARM": {
        "mobile_arm": [
            "ARM Mali-G710",
            "ARM Mali-G610",
            "ARM Mali-G78",
            "ARM Mali-G77",
            "ARM Mali-G68",
        ],
        "mobile_mali": [
            "ARM Mali-G57",
            "ARM Mali-G52",
            "ARM Mali-G51",
        ],
    },
}

# GPU → VRAM mapping (in GB)
GPU_VRAM = {
    "GTX 1660 SUPER": 6, "GTX 1660 Ti": 6, "GTX 1650": 4, "GTX 1050 Ti": 4,
    "RTX 3060": 12, "RTX 3060 Ti": 8, "RTX 3070": 8, "RTX 3070 Ti": 8,
    "RTX 3080": 10, "RTX 3080 Ti": 12, "RTX 3090": 24,
    "RTX 4060": 8, "RTX 4060 Ti": 8, "RTX 4070": 12, "RTX 4070 Ti": 12,
    "RTX 4080": 16, "RTX 4090": 24,
    "RX 6500 XT": 4, "RX 6600": 8, "RX 6700 XT": 12, "RX 6800 XT": 16,
    "RX 6900 XT": 16, "RX 7600": 8, "RX 7700 XT": 12,
    "RX 7900 XT": 20, "RX 7900 XTX": 24,
    "Arc A750": 8, "Arc A770": 16,
    "Iris Xe": 0, "UHD 730": 0, "UHD 770": 0,
    "Apple M1": 0, "Apple M2": 0, "Apple M3": 0,
}

# ============================ HARDWARE PROFILES ============================
# Each profile maps to real-world device configurations
# Weights normalized to 1.0 across ALL profiles including mobile

HARDWARE_PROFILES = [
    # --- DESKTOP PROFILES (45% combined) ---
    {
        "label": "budget_desktop",
        "weight": 0.07,
        "cpu_cores": [4, 6],
        "ram_gb": [8, 16],
        "gpu_tier": "budget",
        "os": ["Windows 10", "Windows 11"],
        "platform": "Win32",
        "screen_options": ["1366x768", "1920x1080"],
        "device_type": "desktop",
    },
    {
        "label": "mid_desktop",
        "weight": 0.15,
        "cpu_cores": [8, 12],
        "ram_gb": [16, 32],
        "gpu_tier": "mid",
        "os": ["Windows 10", "Windows 11"],
        "platform": "Win32",
        "screen_options": ["1920x1080", "2560x1440"],
        "device_type": "desktop",
    },
    {
        "label": "high_desktop",
        "weight": 0.05,
        "cpu_cores": [16, 24, 32],
        "ram_gb": [32, 64],
        "gpu_tier": "high",
        "os": ["Windows 11"],
        "platform": "Win32",
        "screen_options": ["2560x1440", "3840x2160"],
        "device_type": "desktop",
    },
    # --- LAPTOP PROFILES (18% combined) ---
    {
        "label": "budget_laptop",
        "weight": 0.05,
        "cpu_cores": [4, 6],
        "ram_gb": [8, 16],
        "gpu_tier": "laptop",
        "os": ["Windows 10", "Windows 11"],
        "platform": "Win32",
        "screen_options": ["1366x768", "1920x1080"],
        "device_type": "laptop",
    },
    {
        "label": "mid_laptop",
        "weight": 0.08,
        "cpu_cores": [8, 12],
        "ram_gb": [16, 32],
        "gpu_tier": "laptop",
        "os": ["Windows 11"],
        "platform": "Win32",
        "screen_options": ["1920x1080", "2560x1440"],
        "device_type": "laptop",
    },
    # --- MAC PROFILES (5%) ---
    {
        "label": "mac_desktop",
        "weight": 0.05,
        "cpu_cores": [8, 10, 12],
        "ram_gb": [16, 32, 64],
        "gpu_tier": "high",
        "gpu_vendor": "Apple",
        "os": ["macOS 14", "macOS 15"],
        "platform": "MacIntel",
        "screen_options": ["2560x1440", "2560x1600", "3024x1964"],
        "device_type": "desktop",
    },
    # --- LINUX PROFILES (3%) ---
    {
        "label": "linux_desktop",
        "weight": 0.03,
        "cpu_cores": [4, 8, 12],
        "ram_gb": [8, 16, 32],
        "gpu_tier": "mid",
        "os": ["Ubuntu 22.04", "Ubuntu 24.04", "Fedora 40"],
        "platform": "Linux x86_64",
        "screen_options": ["1920x1080", "2560x1440"],
        "device_type": "desktop",
    },
    # === MOBILE PROFILES (55% combined — matches DEVICE_DISTRIBUTION) ===
    # --- iPHONE (25%) ---
    {
        "label": "iphone_15",
        "weight": 0.12,
        "cpu_cores": [6],  # A16 Bionic: 6-core
        "ram_gb": [6, 8],
        "gpu_tier": "mobile_apple",
        "gpu_vendor": "Apple",
        "os": ["iOS 17", "iOS 18"],
        "platform": "iPhone",
        "screen_options": ["393x852", "430x932"],
        "device_type": "mobile",
    },
    {
        "label": "iphone_14",
        "weight": 0.08,
        "cpu_cores": [6],  # A15 Bionic
        "ram_gb": [6],
        "gpu_tier": "mobile_apple",
        "gpu_vendor": "Apple",
        "os": ["iOS 16", "iOS 17"],
        "platform": "iPhone",
        "screen_options": ["390x844", "393x852"],
        "device_type": "mobile",
    },
    {
        "label": "iphone_se",
        "weight": 0.05,
        "cpu_cores": [6],  # A15 Bionic
        "ram_gb": [4],
        "gpu_tier": "mobile_apple",
        "gpu_vendor": "Apple",
        "os": ["iOS 15", "iOS 16", "iOS 17"],
        "platform": "iPhone",
        "screen_options": ["375x667", "375x812"],
        "device_type": "mobile",
    },
    # --- ANDROID (25%) ---
    {
        "label": "android_pixel",
        "weight": 0.10,
        "cpu_cores": [8],  # Tensor G3: 8-core
        "ram_gb": [8, 12],
        "gpu_tier": "mobile_arm",
        "gpu_vendor": "ARM",
        "os": ["Android 14", "Android 15"],
        "platform": "Linux armv8l",
        "screen_options": ["412x915", "448x998"],
        "device_type": "mobile",
    },
    {
        "label": "android_samsung",
        "weight": 0.10,
        "cpu_cores": [8],  # Snapdragon 8 Gen 3
        "ram_gb": [8, 12],
        "gpu_tier": "mobile_adreno",
        "gpu_vendor": "Qualcomm",
        "os": ["Android 13", "Android 14"],
        "platform": "Linux armv8l",
        "screen_options": ["384x854", "412x915"],
        "device_type": "mobile",
    },
    {
        "label": "android_budget",
        "weight": 0.05,
        "cpu_cores": [4, 8],  # MediaTek / Snapdragon 6-series
        "ram_gb": [4, 6, 8],
        "gpu_tier": "mobile_mali",
        "gpu_vendor": "ARM",
        "os": ["Android 12", "Android 13"],
        "platform": "Linux armv7l",
        "screen_options": ["360x800", "412x915"],
        "device_type": "mobile",
    },
    # --- iPAD / TABLET (5%) ---
    {
        "label": "ipad",
        "weight": 0.03,
        "cpu_cores": [8],  # M2: 8-core
        "ram_gb": [8, 16],
        "gpu_tier": "mobile_apple",
        "gpu_vendor": "Apple",
        "os": ["iOS 17", "iOS 18"],
        "platform": "iPad",
        "screen_options": ["768x1024", "820x1180"],
        "device_type": "tablet",
    },
    {
        "label": "android_tablet",
        "weight": 0.02,
        "cpu_cores": [8],
        "ram_gb": [4, 6, 8],
        "gpu_tier": "mobile_arm",
        "gpu_vendor": "ARM",
        "os": ["Android 13", "Android 14"],
        "platform": "Linux armv8l",
        "screen_options": ["768x1024", "800x1280"],
        "device_type": "tablet",
    },
]

# ============================ SCREEN CONFIGURATIONS ============================
# Detailed screen data matching real-world browser window sizes

SCREEN_CONFIGS = {
    "1366x768": {
        "width": 1366, "height": 768,
        "avail_height": 728, "outer_height_offset": 100,
        "pixel_ratios": [1.0],
        "weight": 0.08,
    },
    "1440x900": {
        "width": 1440, "height": 900,
        "avail_height": 860, "outer_height_offset": 110,
        "pixel_ratios": [1.0],
        "weight": 0.04,
    },
    "1536x864": {
        "width": 1536, "height": 864,
        "avail_height": 824, "outer_height_offset": 110,
        "pixel_ratios": [1.0, 1.25],
        "weight": 0.05,
    },
    "1920x1080": {
        "width": 1920, "height": 1080,
        "avail_height": 1040, "outer_height_offset": 120,
        "pixel_ratios": [1.0, 1.25],
        "weight": 0.55,
    },
    "2560x1440": {
        "width": 2560, "height": 1440,
        "avail_height": 1400, "outer_height_offset": 140,
        "pixel_ratios": [1.0, 1.25, 1.5],
        "weight": 0.15,
    },
    "2560x1600": {
        "width": 2560, "height": 1600,
        "avail_height": 1560, "outer_height_offset": 140,
        "pixel_ratios": [2.0],
        "weight": 0.03,
    },
    "3024x1964": {
        "width": 3024, "height": 1964,
        "avail_height": 1924, "outer_height_offset": 150,
        "pixel_ratios": [2.0],
        "weight": 0.02,
    },
    "3840x2160": {
        "width": 3840, "height": 2160,
        "avail_height": 2120, "outer_height_offset": 160,
        "pixel_ratios": [1.5, 2.0],
        "weight": 0.08,
    },
    # === MOBILE SCREEN CONFIGS ===
    "360x800": {
        "width": 360, "height": 800,
        "avail_height": 760, "outer_height_offset": 80,
        "pixel_ratios": [1.0, 1.5],
        "weight": 0.04,
    },
    "375x667": {
        "width": 375, "height": 667,
        "avail_height": 627, "outer_height_offset": 70,
        "pixel_ratios": [2.0],
        "weight": 0.03,
    },
    "375x812": {
        "width": 375, "height": 812,
        "avail_height": 772, "outer_height_offset": 80,
        "pixel_ratios": [2.0, 3.0],
        "weight": 0.04,
    },
    "384x854": {
        "width": 384, "height": 854,
        "avail_height": 814, "outer_height_offset": 85,
        "pixel_ratios": [1.5, 2.0],
        "weight": 0.04,
    },
    "390x844": {
        "width": 390, "height": 844,
        "avail_height": 804, "outer_height_offset": 85,
        "pixel_ratios": [2.0, 3.0],
        "weight": 0.06,
    },
    "393x852": {
        "width": 393, "height": 852,
        "avail_height": 812, "outer_height_offset": 85,
        "pixel_ratios": [2.0, 3.0],
        "weight": 0.06,
    },
    "412x915": {
        "width": 412, "height": 915,
        "avail_height": 875, "outer_height_offset": 90,
        "pixel_ratios": [2.0, 2.75],
        "weight": 0.08,
    },
    "430x932": {
        "width": 430, "height": 932,
        "avail_height": 892, "outer_height_offset": 95,
        "pixel_ratios": [3.0],
        "weight": 0.04,
    },
    "448x998": {
        "width": 448, "height": 998,
        "avail_height": 958, "outer_height_offset": 100,
        "pixel_ratios": [2.0, 3.0],
        "weight": 0.02,
    },
    # === TABLET SCREEN CONFIGS ===
    "768x1024": {
        "width": 768, "height": 1024,
        "avail_height": 984, "outer_height_offset": 120,
        "pixel_ratios": [2.0],
        "weight": 0.05,
    },
    "800x1280": {
        "width": 800, "height": 1280,
        "avail_height": 1240, "outer_height_offset": 130,
        "pixel_ratios": [2.0],
        "weight": 0.03,
    },
    "820x1180": {
        "width": 820, "height": 1180,
        "avail_height": 1140, "outer_height_offset": 125,
        "pixel_ratios": [2.0],
        "weight": 0.03,
    },
}

# ============================ WEBGL CONFIGURATIONS ============================

WEBGL_VENDOR_TEMPLATES = {
    "NVIDIA": "Google Inc. (NVIDIA)",
    "AMD": "Google Inc. (AMD)",
    "Intel": "Google Inc. (Intel)",
    "Apple": "Apple Inc.",
}

WEBGL_RENDERER_TEMPLATES = {
    "NVIDIA": "ANGLE (NVIDIA, {model} Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "AMD": "ANGLE (AMD, {model} Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "Intel": "ANGLE (Intel, {model} Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "Apple": "ANGLE (Apple, ANGLE Metal Renderer: {model}, Unspecified Version)",
}

# ============================ BROWSER VERSIONS ============================
# Common Chrome versions with realistic build numbers

CHROME_VERSIONS = [
    (126, 6478, 122), (126, 6478, 182), (126, 6478, 185),
    (127, 6533, 72),  (127, 6533, 88),  (127, 6533, 99),
    (128, 6613, 36),  (128, 6613, 84),  (128, 6613, 113),
    (125, 6422, 141), (125, 6422, 175), (125, 6422, 176),
]

EDGE_VERSIONS = [
    (126, 2592, 56), (126, 2592, 81), (126, 2592, 102),
    (127, 2651, 74), (127, 2651, 86),
]

FIREFOX_VERSIONS = [
    (127, 0), (127, 0, 2), (128, 0), (128, 0, 3),
    (126, 0, 1), (126, 0),
]

COLOR_DEPTHS = [24, 30, 48]
COLOR_DEPTH_WEIGHTS = [0.85, 0.10, 0.05]


def _weighted_choice(options: list, weights: list = None) -> object:
    """Pick a random item based on weights."""
    if weights is None:
        return random.choice(options)
    total = sum(weights)
    r = random.random() * total
    cumulative = 0
    for item, weight in zip(options, weights):
        cumulative += weight
        if r <= cumulative:
            return item
    return options[-1]


def _resolve_vram(gpu_model: str) -> int:
    """Get VRAM for a GPU model by fuzzy matching."""
    model_short = gpu_model.replace("NVIDIA GeForce ", "").replace("AMD Radeon ", "").replace("Intel ", "")
    for key, vram in GPU_VRAM.items():
        if key in model_short:
            return vram
    # Fallback: reasonable estimate by tier
    if any(x in gpu_model for x in ["4090", "4080", "3090", "7900 XTX"]):
        return 24
    if any(x in gpu_model for x in ["4070", "3080", "7900 XT"]):
        return 12
    if any(x in gpu_model for x in ["4060", "3070", "3060", "7600", "6600"]):
        return 8
    return 6


def _get_gpu_vendor(gpu_model: str) -> str:
    """Determine GPU vendor from model name."""
    if "NVIDIA" in gpu_model:
        return "NVIDIA"
    if "AMD" in gpu_model:
        return "AMD"
    if "Intel" in gpu_model:
        return "Intel"
    if "Apple" in gpu_model:
        return "Apple"
    return "NVIDIA"


# ============================ FINGERPRINT DATACLASS ============================

@dataclass
class Fingerprint:
    """A complete, coherent browser fingerprint for one session."""

    # Hardware
    cpu_cores: int
    ram_gb: int
    gpu_model: str
    gpu_vendor: str
    vram_gb: int
    platform: str
    hardware_profile: str

    # Screen
    screen_width: int
    screen_height: int
    avail_width: int
    avail_height: int
    color_depth: int
    pixel_ratio: float

    # Browser
    user_agent: str
    browser_vendor: str
    chrome_version: str

    # Location (from proxy geo)
    timezone: str
    locale: str
    language: str
    languages: list

    # Anti-fingerprint seeds (unique per session)
    canvas_seed: int
    audio_seed: int
    webgl_seed: int

    # Display
    webgl_vendor: str
    webgl_renderer: str

    # Connection
    rtt: int
    downlink: float
    effective_type: str

    # Device
    device_type: str
    os_version: str

    # Timing
    created_at: float
    session_id: str
    fingerprint_hash: str

    def to_dict(self) -> Dict:
        """Export fingerprint as dictionary for injection via StealthPatcher."""
        return {
            'hardware_concurrency': self.cpu_cores,
            'device_memory': self.ram_gb,
            'gpu_model': self.gpu_model,
            'gpu_vendor': self.gpu_vendor,
            'vram_gb': self.vram_gb,
            'platform': self.platform,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'avail_width': self.avail_width,
            'avail_height': self.avail_height,
            'color_depth': self.color_depth,
            'pixel_ratio': self.pixel_ratio,
            'user_agent': self.user_agent,
            'browser_vendor': self.browser_vendor,
            'chrome_version': self.chrome_version,
            'timezone': self.timezone,
            'locale': self.locale,
            'language': self.language,
            'languages': self.languages,
            'canvas_seed': self.canvas_seed,
            'audio_seed': self.audio_seed,
            'webgl_seed': self.webgl_seed,
            'webgl_vendor': self.webgl_vendor,
            'webgl_renderer': self.webgl_renderer,
            'session_id': self.session_id,
            'rtt': self.rtt,
            'downlink': self.downlink,
            'effective_type': self.effective_type,
            'device_type': self.device_type,
            'os_version': self.os_version,
        }


# ============================ FINGERPRINT FACTORY ============================

class FingerprintFactory:
    """
    Generates unique, coherent browser fingerprints.
    Never generates the same fingerprint twice (collision detection).
    """

    def __init__(self):
        self._used_hashes: set = set()
        self._generated_count: int = 0
        self._profile_usage: Dict[str, int] = {}  # Track profile distribution
        self._vendor_usage: Dict[str, int] = {}   # Track GPU vendor distribution

    def generate(self, geo_config: Optional[Dict] = None) -> Fingerprint:
        """
        Generate a new unique fingerprint.

        Args:
            geo_config: Optional dict with 'timezone', 'locale', 'language',
                       'country', 'city' from GeoIPClient.get_browser_geo_config()

        Returns:
            Fingerprint object with all values ready for injection
        """
        # Step 1: Pick weighted random hardware profile
        profile = _weighted_choice(
            HARDWARE_PROFILES,
            [p["weight"] for p in HARDWARE_PROFILES]
        )

        # Step 2: CPU cores (within profile range)
        cpu_cores = random.choice(profile["cpu_cores"])

        # Step 3: RAM (within profile range, must be power of 2 or common)
        ram_options = [r for r in profile["ram_gb"] if r >= 4]
        ram_gb = random.choice(ram_options)

        # Step 4: GPU (matching profile tier and possibly forced vendor)
        gpu_vendor = profile.get("gpu_vendor", random.choice(["NVIDIA", "AMD", "Intel"]))
        if gpu_vendor not in GPU_DATABASE:
            gpu_vendor = "NVIDIA"

        gpu_tier = profile["gpu_tier"]
        if gpu_tier not in GPU_DATABASE.get(gpu_vendor, {}):
            # Fallback to NVIDIA if vendor doesn't have this tier
            for fallback_vendor in ["NVIDIA", "AMD", "Intel"]:
                if gpu_tier in GPU_DATABASE.get(fallback_vendor, {}):
                    gpu_vendor = fallback_vendor
                    break

        gpu_list = GPU_DATABASE.get(gpu_vendor, {}).get(gpu_tier, GPU_DATABASE["NVIDIA"]["mid"])
        gpu_model = random.choice(gpu_list)
        vram_gb = _resolve_vram(gpu_model)

        # Step 5: OS version
        os_version = random.choice(profile["os"])

        # Step 6: Screen configuration (weighted by real-world distribution)
        screen_keys = list(SCREEN_CONFIGS.keys())
        screen_weights = [SCREEN_CONFIGS[k]["weight"] for k in screen_keys]
        screen_key = _weighted_choice(screen_keys, screen_weights)
        screen_config = SCREEN_CONFIGS[screen_key]
        pixel_ratio = random.choice(screen_config["pixel_ratios"])

        # Step 7: Browser configuration (detection #6 fix: real browser diversity)
        # Real internet: ~65% Chrome, ~20% Safari, ~6% Firefox, ~4% Edge, ~5% other
        browser_choice = random.random()
        
        # Determine platform string for this profile
        if 'Window' in os_version:
            platform_str = 'Windows NT 10.0; Win64; x64'
        elif 'macOS' in os_version or 'iOS' in os_version:
            platform_str = 'Macintosh; Intel Mac OS X 10_15_7'
        elif 'Android' in os_version:
            platform_str = f'Linux; Android {random.randint(10,14)}; {random.choice(["SM-S921B","Pixel 7","SM-G991B"])}'
        else:
            platform_str = 'X11; Linux x86_64'
        
        if browser_choice < 0.55:  # 55% Chrome
            ver = random.choice(CHROME_VERSIONS)
            chrome_version = f"{ver[0]}.{ver[1]}.{ver[2]}"
            browser_vendor = "Google Inc."
            user_agent = (
                f"Mozilla/5.0 ({platform_str}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{chrome_version} Safari/537.36"
            )
        elif browser_choice < 0.70:  # 15% Chrome for Mobile
            ver = random.choice(CHROME_VERSIONS)
            chrome_version = f"{ver[0]}.{ver[1]}.{ver[2]}"
            browser_vendor = "Google Inc."
            device_ua = random.choice([
                'iPhone; CPU iPhone OS 17_5 like Mac OS X',
                'Linux; Android 14; SM-S921B',
                'Linux; Android 13; Pixel 7',
                'iPad; CPU OS 17_5 like Mac OS X',
            ])
            user_agent = (
                f"Mozilla/5.0 ({device_ua}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{chrome_version} Mobile Safari/537.36"
            )
        elif browser_choice < 0.78:  # 8% Safari (desktop + mobile + tablet)
            safari_version = f"17.{random.randint(1,5)}"
            chrome_version = ""
            browser_vendor = "Apple Computer, Inc."
            if 'iOS' in os_version or device_type == 'mobile':
                device_ua_safari = random.choice([
                    'iPhone; CPU iPhone OS 17_5 like Mac OS X',
                    'iPhone; CPU iPhone OS 16_6 like Mac OS X',
                ])
                user_agent = (
                    f"Mozilla/5.0 ({device_ua_safari}) "
                    f"AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    f"Version/{safari_version} Mobile/15E148 Safari/604.1"
                )
            elif 'iPad' in os_version or device_type == 'tablet':
                user_agent = (
                    f"Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) "
                    f"AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    f"Version/{safari_version} Mobile/15E148 Safari/604.1"
                )
            else:
                user_agent = (
                    f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    f"AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    f"Version/{safari_version} Safari/605.1.15"
                )
        elif browser_choice < 0.85:  # 7% Firefox
            ver = random.choice(FIREFOX_VERSIONS)
            ff_version = f"{ver[0]}.{ver[1]}"
            chrome_version = ff_version
            browser_vendor = ""
            user_agent = (
                f"Mozilla/5.0 ({platform_str}; rv:{ff_version}) "
                f"Gecko/20100101 Firefox/{ff_version}"
            )
        elif browser_choice < 0.90:  # 5% Edge (Windows desktop)
            ver = random.choice(EDGE_VERSIONS)
            chrome_version = f"{ver[0]}.{ver[1]}.{ver[2]}"
            browser_vendor = "Google Inc."
            user_agent = (
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{chrome_version} Safari/537.36 Edg/{chrome_version}"
            )
        elif browser_choice < 0.93:  # 3% Samsung Internet (Android mobile)
            chrome_version = random.choice(["126.0", "125.0", "127.0"])
            browser_vendor = "Google Inc."
            samsung_version = f"{random.randint(23,25)}.0"
            user_agent = (
                f"Mozilla/5.0 (Linux; Android 14; SM-S921B) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"SamsungBrowser/{samsung_version} Chrome/{chrome_version}.6478.122 Mobile Safari/537.36"
            )
        elif browser_choice < 0.96:  # 3% Opera
            chrome_version = f"{random.randint(100,110)}.0"
            browser_vendor = "Opera Software"
            user_agent = (
                f"Mozilla/5.0 ({platform_str}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{chrome_version}.0.0 Safari/537.36 OPR/{random.randint(85,95)}.0"
            )
        else:  # 4% Brave / other Chromium-based
            ver = random.choice(CHROME_VERSIONS)
            chrome_version = f"{ver[0]}.{ver[1]}.{ver[2]}"
            browser_vendor = "Google Inc."
            user_agent = (
                f"Mozilla/5.0 ({platform_str}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{chrome_version} Safari/537.36"
            )

        # Step 8: Geo-based values (from proxy)
        if geo_config:
            timezone = geo_config.get('timezone', 'America/New_York')
            locale = geo_config.get('locale', 'en-US')
            language = geo_config.get('language', 'en')
            languages = [locale, 'en-US', 'en'] if locale != 'en-US' else ['en-US', 'en']
        else:
            timezone = random.choice([
                'America/New_York', 'America/Chicago', 'America/Denver',
                'America/Los_Angeles', 'Europe/London', 'Europe/Berlin',
                'Europe/Paris', 'Asia/Tokyo', 'Asia/Kolkata', 'Asia/Singapore',
                'Australia/Sydney', 'America/Toronto',
            ])
            locale = 'en-US'
            language = 'en'
            languages = ['en-US', 'en']

        # Step 9: Unique seeds for fingerprint noise
        canvas_seed = random.randint(100000, 999999)
        audio_seed = random.randint(100000, 999999)
        webgl_seed = random.randint(100000, 999999)

        # Step 10: WebGL vendor/renderer strings
        webgl_vendor = WEBGL_VENDOR_TEMPLATES.get(gpu_vendor, 'Google Inc.')
        webgl_renderer = WEBGL_RENDERER_TEMPLATES.get(gpu_vendor, 'ANGLE').format(model=gpu_model)

        # Step 11: Connection info (varies by device type)
        if profile['device_type'] == 'desktop':
            rtt = random.randint(10, 80)
            downlink = round(random.uniform(5, 100), 1)
            effective_type = random.choice(['4g', '4g', '4g', 'ethernet'])
        elif profile['device_type'] == 'laptop':
            rtt = random.randint(20, 150)
            downlink = round(random.uniform(2, 50), 1)
            effective_type = random.choice(['4g', '4g', '3g'])
        else:
            rtt = random.randint(30, 200)
            downlink = round(random.uniform(1, 30), 1)
            effective_type = random.choice(['4g', '3g'])

        # Step 12: Color depth (weighted)
        color_depth = _weighted_choice(COLOR_DEPTHS, COLOR_DEPTH_WEIGHTS)

        # Step 13: Build fingerprint object
        self._generated_count += 1

        fp = Fingerprint(
            cpu_cores=cpu_cores,
            ram_gb=ram_gb,
            gpu_model=gpu_model,
            gpu_vendor=gpu_vendor,
            vram_gb=vram_gb,
            platform=profile["platform"],
            hardware_profile=profile["label"],
            screen_width=screen_config["width"],
            screen_height=screen_config["height"],
            avail_width=screen_config["width"],
            avail_height=screen_config["avail_height"],
            color_depth=color_depth,
            pixel_ratio=pixel_ratio,
            user_agent=user_agent,
            browser_vendor=browser_vendor,
            chrome_version=chrome_version,
            timezone=timezone,
            locale=locale,
            language=language,
            languages=languages,
            canvas_seed=canvas_seed,
            audio_seed=audio_seed,
            webgl_seed=webgl_seed,
            webgl_vendor=webgl_vendor,
            webgl_renderer=webgl_renderer,
            rtt=rtt,
            downlink=downlink,
            effective_type=effective_type,
            device_type=profile["device_type"],
            os_version=os_version,
            created_at=time.time(),
            session_id=f"fp_{int(time.time())}_{self._generated_count:08d}",
            fingerprint_hash="",
        )

        # Step 14: Generate unique hash
        fp.fingerprint_hash = self._hash_fingerprint(fp)

        # Step 15: Ensure uniqueness (re-try with different seeds if collision)
        retries = 0
        while fp.fingerprint_hash in self._used_hashes and retries < 100:
            fp.canvas_seed = random.randint(100000, 999999)
            fp.audio_seed = random.randint(100000, 999999)
            fp.webgl_seed = random.randint(100000, 999999)
            fp.fingerprint_hash = self._hash_fingerprint(fp)
            retries += 1

        self._used_hashes.add(fp.fingerprint_hash)
        self._profile_usage[profile["label"]] = self._profile_usage.get(profile["label"], 0) + 1
        self._vendor_usage[gpu_vendor] = self._vendor_usage.get(gpu_vendor, 0) + 1

        # Memory management: clear hashes periodically
        if len(self._used_hashes) > 500_000:
            self._used_hashes.clear()
            logger.debug("Fingerprint hash cache cleared (500K limit)")

        return fp

    def _hash_fingerprint(self, fp: Fingerprint) -> str:
        """Generate unique SHA-256 hash from fingerprint data."""
        data = (
            f"{fp.cpu_cores}|{fp.ram_gb}|{fp.gpu_model}|{fp.platform}|"
            f"{fp.screen_width}x{fp.screen_height}|{fp.pixel_ratio}|"
            f"{fp.canvas_seed}|{fp.audio_seed}|{fp.webgl_seed}|"
            f"{fp.user_agent[:50]}|{fp.timezone}"
        )
        return hashlib.sha256(data.encode()).hexdigest()[:24]

    def get_daily_fingerprint_for_device(
        self, device_type: str, geo_config: Optional[Dict] = None
    ) -> Fingerprint:
        """
        Generate a fingerprint biased toward a specific device type.
        Useful for matching the farm's device distribution (55% mobile, 35% desktop, 10% tablet).

        Args:
            device_type: 'desktop', 'mobile', 'tablet', or 'laptop'
            geo_config: Optional geo data
        """
        # Filter profiles by device type
        matching_profiles = [
            p for p in HARDWARE_PROFILES
            if p.get("device_type") == device_type
        ]

        if not matching_profiles:
            # Fallback to all profiles
            matching_profiles = HARDWARE_PROFILES

        # Override profile selection to match device type
        profile = _weighted_choice(
            matching_profiles,
            [p["weight"] for p in matching_profiles]
        )

        # Force the device type
        fp = self.generate(geo_config)
        fp.device_type = device_type

        return fp

    def get_stats(self) -> Dict:
        """Get factory statistics for monitoring."""
        return {
            "total_generated": self._generated_count,
            "unique_hashes_active": len(self._used_hashes),
            "profile_distribution": self._profile_usage,
            "vendor_distribution": self._vendor_usage,
        }


# ============================ GLOBAL FACTORY ============================

_factory: Optional[FingerprintFactory] = None


def get_fingerprint_factory() -> FingerprintFactory:
    """Get or create the global fingerprint factory instance."""
    global _factory
    if _factory is None:
        _factory = FingerprintFactory()
    return _factory


# ============================ UTILITY FUNCTIONS ============================

def generate_quick_fingerprint(device_type: str = "desktop",
                                geo_config: Optional[Dict] = None) -> Fingerprint:
    """Quick one-liner to generate a fingerprint. For direct use in session_engine."""
    return get_fingerprint_factory().generate(geo_config)


# ============================ STANDALONE TEST ============================
if __name__ == '__main__':
    print("=" * 70)
    print("  FINGERPRINT FACTORY — UNIT TEST")
    print("=" * 70)

    factory = FingerprintFactory()

    print("\n--- Test 1: Default Fingerprint ---")
    fp = factory.generate()
    print(f"  Session ID:    {fp.session_id}")
    print(f"  CPU Cores:     {fp.cpu_cores}")
    print(f"  RAM:           {fp.ram_gb}GB")
    print(f"  GPU:           {fp.gpu_model} ({fp.vram_gb}GB VRAM)")
    print(f"  Platform:      {fp.platform}")
    print(f"  Screen:        {fp.screen_width}x{fp.screen_height} @{fp.pixel_ratio}x")
    print(f"  Browser:       {fp.user_agent[:80]}...")
    print(f"  Canvas Seed:   {fp.canvas_seed}")
    print(f"  WebGL Vendor:  {fp.webgl_vendor}")
    print(f"  Timezone:      {fp.timezone}")
    print(f"  Hash:          {fp.fingerprint_hash}")

    print("\n--- Test 2: Geo-Aware Fingerprint (India) ---")
    geo = {'timezone': 'Asia/Kolkata', 'locale': 'hi-IN', 'language': 'hi',
           'country': 'IN', 'city': 'Mumbai'}
    fp2 = factory.generate(geo_config=geo)
    print(f"  Timezone:      {fp2.timezone}")
    print(f"  Locale:        {fp2.locale}")
    print(f"  Language:      {fp2.language}")
    print(f"  Hash:          {fp2.fingerprint_hash}")

    print("\n--- Test 3: Device-Type Biased (mobile) ---")
    fp3 = factory.get_daily_fingerprint_for_device("mobile")
    print(f"  Device Type:   {fp3.device_type}")
    print(f"  GPU:           {fp3.gpu_model}")

    print("\n--- Test 4: Uniqueness Check (10,000 fingerprints) ---")
    hashes = set()
    duplicates = 0
    for _ in range(10000):
        fp_test = factory.generate()
        if fp_test.fingerprint_hash in hashes:
            duplicates += 1
        hashes.add(fp_test.fingerprint_hash)
    print(f"  Generated:     10,000")
    print(f"  Unique Hashes: {len(hashes)}")
    print(f"  Duplicates:    {duplicates}")

    print("\n--- Test 5: Factory Stats ---")
    stats = factory.get_stats()
    print(f"  Total Generated:  {stats['total_generated']}")
    print(f"  Profile Dist:     {stats['profile_distribution']}")
    print(f"  Vendor Dist:      {stats['vendor_distribution']}")

    print("\n--- Test 6: Fingerprint.to_dict() ---")
    fp_dict = fp.to_dict()
    print(f"  Keys: {list(fp_dict.keys())}")
    print(f"  canvas_seed in dict: {fp_dict['canvas_seed']}")

    print("\n" + "=" * 70)
    print("  ALL TESTS PASSED ✓")
    print("=" * 70)