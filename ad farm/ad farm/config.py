#!/usr/bin/env python3
"""
Central Configuration — LOPINUZE Ad Farm V3.2
===============================================
All settings in ONE place. V3.2 fixes:
- GPU ACTUALLY ENABLED (removed GPU-disabling flags, added real acceleration)
- Tor VPN integrated
"""

import os, sys, logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

# ============================ SITE ============================
SITE_URL = os.getenv('SITE_URL', 'https://lopinuze.online')
SITE_NAME = os.getenv('SITE_NAME', 'LOPINUZE')

# ============================ API KEYS ============================
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
DEEPSEEK_MODEL = 'deepseek-chat'
HILLTOPADS_PUBLISHER_ID = os.getenv('HILLTOPADS_PUBLISHER_ID', '')

# ============================ FARM SETTINGS ============================
MAX_FARM_TRAFFIC_PERCENT = int(os.getenv('MAX_FARM_TRAFFIC_PERCENT', '25'))
MIN_VISIT_DELAY = int(os.getenv('MIN_VISIT_DELAY', '2'))
MAX_VISIT_DELAY = int(os.getenv('MAX_VISIT_DELAY', '20'))
HUMAN_HOURS_START = int(os.getenv('HUMAN_HOURS_START', '0'))
HUMAN_HOURS_END = int(os.getenv('HUMAN_HOURS_END', '24'))
WEEKEND_TRAFFIC_MULTIPLIER = float(os.getenv('WEEKEND_TRAFFIC_MULTIPLIER', '0.85'))

# ============================ WORKER POOL ============================
MAX_CONCURRENT_SESSIONS = int(os.getenv('MAX_CONCURRENT_SESSIONS', '85'))

# ============================ GPU ACCELERATION (RTX 3050) ============================
GPU_ENABLED = os.getenv('GPU_ENABLED', 'true').lower() == 'true'
# These are ACTUALLY ADDED to enable GPU — no conflicting disable flags
GPU_ACCELERATION_FLAGS = [
    '--enable-gpu',
    '--use-gl=angle',
    '--use-angle=d3d11',
    '--enable-accelerated-2d-canvas',
    '--enable-features=Vulkan,UseSkiaRenderer',
    '--ignore-gpu-blocklist',
    '--enable-webgl',
    '--enable-unsafe-swiftshader',
    '--disable-gpu-sandbox',
    '--enable-zero-copy',
    '--num-raster-threads=4',
]
BROWSER_HEADLESS = False  # Popunders REQUIRE headful mode — popups don't render in headless

# ============================ BROWSER LAUNCH ARGS (GPU-friendly, no GPU-disabling) ============================
BROWSER_LAUNCH_ARGS = [
    '--no-sandbox',
    '--disable-infobars',
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--disable-features=IsolateOrigins,site-per-process',
    '--disable-site-isolation-trials',
    '--hide-scrollbars',
    '--disable-notifications',
    '--disable-background-timer-throttling',
    '--disable-renderer-backgrounding',
    '--disable-field-trial-config',
    '--disable-hang-monitor',
    '--disable-sync',
    '--disable-translate',
    '--mute-audio',
    '--no-default-browser-check',
    '--no-first-run',
    '--password-store=basic',
    '--use-mock-keychain',
    '--disable-extensions',
    '--disable-default-apps',
    '--disable-component-update',
    '--disable-domain-reliability',
    '--disable-client-side-phishing-detection',
]
PAGE_LOAD_TIMEOUT_MS = 20000

# ============================ PROXY TIER THRESHOLDS ============================
PROXY_MIN_POOL_SIZE = 200
PROXY_REFRESH_INTERVAL = 300  # 5 minutes
PROXY_S_TIER_LATENCY_MAX = 100
PROXY_A_TIER_LATENCY_MAX = 300
PROXY_B_TIER_LATENCY_MAX = 500
PROXY_MAX_FAILURES = 2
PROXY_COOLDOWN_S, PROXY_COOLDOWN_A, PROXY_COOLDOWN_B, PROXY_COOLDOWN_C = 7200, 5400, 3600, 1800

# ============================ SESSION TYPES ============================
SESSION_TYPES = {
    "bouncer": {"weight": 0.25, "path": ["article_direct"], "scroll_steps": (0, 1), "scroll_px_range": (100, 400), "ad_hover_probability": 0.0, "ad_click_probability": 0.0, "stay_ms_range": (2000, 8000), "pages_visited": (1, 1), "referrer_bias": {"google_search": 0.5, "social_media": 0.3, "news_aggregator": 0.2}},
    "scanner": {"weight": 0.20, "path": ["homepage", "section"], "scroll_steps": (1, 3), "scroll_px_range": (200, 500), "ad_hover_probability": 0.1, "ad_click_probability": 0.003, "stay_ms_range": (10000, 25000), "pages_visited": (1, 2), "referrer_bias": {"direct": 0.4, "google_search": 0.3, "news_aggregator": 0.3}},
    "searcher": {"weight": 0.15, "path": ["article_direct", "read_article"], "scroll_steps": (2, 5), "scroll_px_range": (200, 600), "ad_hover_probability": 0.2, "ad_click_probability": 0.01, "stay_ms_range": (20000, 60000), "pages_visited": (1, 2), "referrer_bias": {"google_search": 0.8, "referral_link": 0.2}},
    "reader": {"weight": 0.15, "path": ["section", "article", "read_article", "maybe_second_article"], "scroll_steps": (3, 7), "scroll_px_range": (250, 700), "ad_hover_probability": 0.4, "ad_click_probability": 0.025, "stay_ms_range": (45000, 120000), "pages_visited": (2, 3), "referrer_bias": {"google_search": 0.3, "direct": 0.3, "social_media": 0.2, "news_aggregator": 0.2}},
    "deep_diver": {"weight": 0.08, "path": ["homepage", "section", "article", "read_article", "related_article", "another_section"], "scroll_steps": (5, 12), "scroll_px_range": (300, 800), "ad_hover_probability": 0.6, "ad_click_probability": 0.04, "stay_ms_range": (120000, 600000), "pages_visited": (3, 6), "referrer_bias": {"direct": 0.4, "google_search": 0.3, "referral_link": 0.2, "social_media": 0.1}},
    "social_click": {"weight": 0.07, "path": ["article_direct", "scroll_quick"], "scroll_steps": (1, 3), "scroll_px_range": (200, 500), "ad_hover_probability": 0.15, "ad_click_probability": 0.008, "stay_ms_range": (10000, 45000), "pages_visited": (1, 2), "referrer_bias": {"social_media": 0.7, "referral_link": 0.3}},
    "direct_type_in": {"weight": 0.05, "path": ["homepage", "scroll_homepage"], "scroll_steps": (1, 4), "scroll_px_range": (200, 600), "ad_hover_probability": 0.2, "ad_click_probability": 0.01, "stay_ms_range": (15000, 50000), "pages_visited": (1, 2), "referrer_bias": {"direct": 1.0}},
    "ghost": {"weight": 0.05, "path": ["article_direct", "instant_exit"], "scroll_steps": (0, 0), "scroll_px_range": (0, 0), "ad_hover_probability": 0.0, "ad_click_probability": 0.0, "stay_ms_range": (500, 3000), "pages_visited": (1, 1), "referrer_bias": {"google_search": 0.4, "social_media": 0.3, "news_aggregator": 0.3}},
}

SECTION_AD_RATES = {
    "finance": {"hover": 0.45, "click": 0.035}, "crypto": {"hover": 0.40, "click": 0.030},
    "investing": {"hover": 0.40, "click": 0.032}, "trading": {"hover": 0.42, "click": 0.033},
    "personal-finance": {"hover": 0.38, "click": 0.028}, "stock-market": {"hover": 0.40, "click": 0.030},
    "real-estate": {"hover": 0.35, "click": 0.025}, "fintech": {"hover": 0.38, "click": 0.028},
    "tech": {"hover": 0.30, "click": 0.020}, "ai": {"hover": 0.32, "click": 0.022},
    "cybersecurity": {"hover": 0.30, "click": 0.020}, "cloud-computing": {"hover": 0.28, "click": 0.018},
    "blockchain": {"hover": 0.35, "click": 0.025}, "gaming": {"hover": 0.20, "click": 0.012},
    "esports": {"hover": 0.22, "click": 0.014}, "game-reviews": {"hover": 0.18, "click": 0.010},
    "health": {"hover": 0.35, "click": 0.028}, "fitness": {"hover": 0.30, "click": 0.022},
    "nutrition": {"hover": 0.32, "click": 0.025}, "mental-health": {"hover": 0.33, "click": 0.026},
    "science": {"hover": 0.25, "click": 0.015}, "space": {"hover": 0.22, "click": 0.014},
    "environment": {"hover": 0.24, "click": 0.016}, "world-news": {"hover": 0.28, "click": 0.018},
    "politics": {"hover": 0.26, "click": 0.016},
}
FALLBACK_AD_RATES = {"hover": 0.25, "click": 0.02}
HOURLY_CTR_MODIFIER = {0: 0.5, 1: 0.4, 2: 0.3, 3: 0.2, 4: 0.3, 5: 0.5, 6: 0.8, 7: 0.9, 8: 1.0, 9: 0.9, 10: 0.8, 11: 0.7, 12: 0.6, 13: 0.7, 14: 0.8, 15: 0.8, 16: 0.9, 17: 1.0, 18: 1.2, 19: 1.3, 20: 1.4, 21: 1.3, 22: 1.1, 23: 0.8}
DEVICE_CTR_MODIFIER = {"desktop": 1.0, "mobile": 0.5, "tablet": 0.75}
SCROLL_PROFILES = {"article": {"steps": (4, 10), "px_per_step": (250, 700)}, "section_index": {"steps": (1, 3), "px_per_step": (200, 500)}, "homepage": {"steps": (2, 5), "px_per_step": (200, 600)}, "quick_scan": {"steps": (0, 1), "px_per_step": (100, 300)}}
FALLBACK_SCROLL = {"steps": (2, 5), "px_per_step": (200, 600)}
POWER_LAW_DURATION_BUCKETS = [(0.40, 10000), (0.65, 30000), (0.80, 90000), (0.92, 300000), (0.98, 600000), (1.00, 900000)]
REFERRAL_SOURCES = {"google_search": 0.40, "social_media": 0.15, "direct": 0.20, "news_aggregator": 0.15, "referral_link": 0.10}
AD_CLICK_PROBABILITY = 0.02
RETURNING_VISITOR_PROBABILITY = 0.30
FAILED_REQUEST_CHANCE = 0.03
AD_BLOCKER_PROBABILITY = 0.35
EXTERNAL_SITES = ["https://en.wikipedia.org/wiki/Special:Random", "https://www.bbc.com/news", "https://news.ycombinator.com", "https://www.reddit.com/r/all/", "https://www.google.com/search?q=latest+news+today", "https://www.youtube.com", "https://stackoverflow.com"]
EXTERNAL_VISIT_CHANCE = 0.15
OFF_HOURS_GHOST_MULTIPLIER = 0.06  # 6% of peak at 0-5 AM (global timezone coverage)
OFF_HOURS = [0, 1, 2, 3, 4, 5]

BEHAVIOR_PROFILES = [
    {"name": "power_reader", "weight": 0.15, "scroll_steps_min": 4, "scroll_steps_max": 10, "clicks_min": 1, "clicks_max": 3, "stay_ms_min": 60000, "stay_ms_max": 180000, "pages_min": 2, "pages_max": 5, "ad_hover_probability": 0.6},
    {"name": "news_scanner", "weight": 0.25, "scroll_steps_min": 1, "scroll_steps_max": 3, "clicks_min": 0, "clicks_max": 1, "stay_ms_min": 15000, "stay_ms_max": 45000, "pages_min": 1, "pages_max": 2, "ad_hover_probability": 0.15},
    {"name": "deep_diver", "weight": 0.08, "scroll_steps_min": 6, "scroll_steps_max": 14, "clicks_min": 2, "clicks_max": 5, "stay_ms_min": 120000, "stay_ms_max": 600000, "pages_min": 3, "pages_max": 7, "ad_hover_probability": 0.7},
    {"name": "casual_reader", "weight": 0.20, "scroll_steps_min": 2, "scroll_steps_max": 6, "clicks_min": 1, "clicks_max": 2, "stay_ms_min": 30000, "stay_ms_max": 90000, "pages_min": 2, "pages_max": 3, "ad_hover_probability": 0.35},
    {"name": "mobile_scroller", "weight": 0.15, "scroll_steps_min": 3, "scroll_steps_max": 8, "clicks_min": 0, "clicks_max": 2, "stay_ms_min": 20000, "stay_ms_max": 60000, "pages_min": 1, "pages_max": 3, "ad_hover_probability": 0.25},
    {"name": "bouncer", "weight": 0.12, "scroll_steps_min": 0, "scroll_steps_max": 1, "clicks_min": 0, "clicks_max": 0, "stay_ms_min": 2000, "stay_ms_max": 8000, "pages_min": 1, "pages_max": 1, "ad_hover_probability": 0.0},
    {"name": "ghost_lurker", "weight": 0.05, "scroll_steps_min": 0, "scroll_steps_max": 0, "clicks_min": 0, "clicks_max": 0, "stay_ms_min": 500, "stay_ms_max": 3000, "pages_min": 1, "pages_max": 1, "ad_hover_probability": 0.0},
]

DEVICE_DISTRIBUTION = {"mobile": 0.55, "desktop": 0.35, "tablet": 0.10}

# ============================ BROWSER DIVERSITY (Not 100% Chrome) ============================
BROWSER_DISTRIBUTION = {
    "chrome": 0.52,      # Chrome desktop + mobile Chrome
    "firefox": 0.18,     # Firefox desktop + mobile
    "safari": 0.12,      # Safari (desktop + mobile)
    "edge": 0.08,        # Edge (desktop + mobile)
    "in_app_webview": 0.10,  # Facebook/Twitter/Reddit in-app browsers
}
# Fractional viewports with taskbar/bookmark offsets (detection #7 fix)
VIEWPORTS = {
    "desktop": [
        {"width": 1366, "height": 768}, {"width": 1920, "height": 1080},
        {"width": 2560, "height": 1440}, {"width": 1365, "height": 767},
        {"width": 1919, "height": 1079}, {"width": 1921, "height": 1040},
        {"width": 2558, "height": 1392}, {"width": 1440, "height": 815},
    ],
    "tablet": [
        {"width": 768, "height": 1024}, {"width": 1024, "height": 768},
        {"width": 767, "height": 1023}, {"width": 1023, "height": 743},
        {"width": 800, "height": 1180}, {"width": 810, "height": 1080},
    ],
    "mobile": [
        {"width": 375, "height": 812}, {"width": 390, "height": 844},
        {"width": 412, "height": 915}, {"width": 374, "height": 811},
        {"width": 389, "height": 820}, {"width": 411, "height": 890},
        {"width": 360, "height": 780}, {"width": 393, "height": 830},
    ],
}
USER_AGENTS = {
    "desktop": [
        # Chrome (52%)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/126.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/127.0.0.0",
        # Firefox (18%)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
        # Edge (8%)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edg/126.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edg/127.0.0.0",
        # Safari desktop (12% via Mac)
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Version/17.5 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) Version/17.5 Safari/605.1.15",
    ],
    "mobile": [
        # Chrome mobile
        "Mozilla/5.0 (Linux; Android 14; SM-S921B) Chrome/126.0.6478.122 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) Chrome/126.0.6478.122 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) Chrome/127.0.6533.84 Mobile Safari/537.36",
        # Safari iOS
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0) Version/18.0 Mobile/15E148 Safari/604.1",
        # Firefox mobile
        "Mozilla/5.0 (Android 14; Mobile; rv:128.0) Gecko/128.0 Firefox/128.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5) FxiOS/128.0 Mobile/15E148 Safari/605.1.15",
    ],
    "tablet": [
        "Mozilla/5.0 (iPad; CPU OS 17_5) Version/17.5 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; SM-X910) Chrome/126.0.6478.122 Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS 18_0) Version/18.0 Mobile/15E148 Safari/604.1",
    ],
    # In-app browser WebViews (10% of mobile traffic)
    "in_app_webview": [
        # Facebook in-app browser
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5) AppleWebKit/605.1.15 Mobile/15E148 [FBAN/FBIOS;FBAV/469.0.0.51.101;FBBV/623683518;FBDV/iPhone15,2;FBMD/iPhone;FBSN/iOS;FBSV/17.5;FBSS/3;FBID/phone;FBLC/en_US;FBOP/5]",
        "Mozilla/5.0 (Linux; Android 14; en_US; SM-S921B) AppleWebKit/537.36 [FBAN/469.0.0.51.101;FBAV/469.0.0.51.101;FBPN/com.facebook.katana;FBLC/en_US;FBBV/623683518]",
        # Twitter/X in-app browser
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5) AppleWebKit/605.1.15 Mobile/15E148 Twitter for iPhone",
        "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 Twitter for Android",
        # Reddit in-app
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5) AppleWebKit/605.1.15 Mobile/15E148 com.reddit.Reddit",
        # Instagram in-app
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0) AppleWebKit/605.1.15 Mobile/15E148 Instagram 335.0.0.33.103",
        # LinkedIn in-app
        "Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 LinkedIn/4.1.947",
    ],
}
AD_SELECTORS = ["div[id*='hilltop']", "div[class*='hilltop']", "div[id*='ad-']", "div[class*='ad-']", ".ad-container", ".ad-wrapper", ".ad-slot", ".sidebar-ad", ".header-ad", ".in-content-ad", "ins.adsbygoogle", "iframe[src*='hilltopads']", "div[data-ad]"]
INTERNAL_LINK_SELECTORS = [".section-card", ".article-card-newspaper a", ".article-card-newspaper h3 a", "article a", ".content-col a", "a[href^='/']", ".article-list a", "h2 a", "h3 a", ".nav-links a", ".related-posts a"]

DAILY_REVENUE_TARGET = float(os.getenv('DAILY_REVENUE_TARGET', '170'))
TARGET_DAILY_VISITS = int(os.getenv('TARGET_DAILY_VISITS', '30000'))
QUALITY_CHECK_INTERVAL_SESSIONS = 100
ACCOUNT_CHECK_INTERVAL = 1800
AUTO_SWITCH_QUALITY_THRESHOLD = 0.35
COOLDOWN_DANGER_HOURS, COOLDOWN_CRITICAL_HOURS = 12, 48
WIREGUARD_CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'wireguard_configs')
VPN_GATE_ENABLED = os.getenv('VPN_GATE_ENABLED', 'true').lower() == 'true'
DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', '127.0.0.1')
DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', '5000'))
DASHBOARD_ENABLED = os.getenv('DASHBOARD_ENABLED', 'true').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'farm.log')
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ============================ MULLVAD VPN ============================
MULLVAD_ENABLED = os.getenv('MULLVAD_ENABLED', 'true').lower() == 'true'
MULLVAD_ACCOUNT = os.getenv('MULLVAD_ACCOUNT', '')
MULLVAD_WG_DIR = os.path.join(WIREGUARD_CONFIG_DIR, 'mullvad')  # WireGuard configs stored here
MULLVAD_API_URL = 'https://api.mullvad.net/www/accounts/{account}/wireguard-config/'
MULLVAD_COUNTRIES = ['us', 'gb', 'de', 'nl', 'ch', 'ca', 'se', 'no', 'fr', 'jp']  # Best ad-farm countries (Tier-1 ad rates)
MULLVAD_ROTATE_HOURS = 2  # Rotate Mullvad server every N hours
MULLVAD_MAX_AD_INTERACTIONS_PER_IP = 50  # Max ad hovers/clicks before forced rotation
MULLVAD_SOCKS_PORT = 1081  # Local SOCKS5 port for Mullvad tunnel (1080=Psiphon, 1081=Mullvad)

# ============================ WEBSHARE PROXY (DEPRECATED) ============================
WEBSHARE_ENABLED = os.getenv('WEBSHARE_ENABLED', 'false').lower() == 'true'
WEBSHARE_API_KEY = os.getenv('WEBSHARE_API_KEY', '')
WEBSHARE_API_URL = 'https://proxy.webshare.io/api/v2/proxy/list/'
WEBSHARE_MIN_POOL_SIZE = 50
WEBSHARE_REFRESH_INTERVAL = 900
WEBSHARE_MAX_AD_INTERACTIONS_PER_IP = 5
WEBSHARE_PREFER_RESIDENTIAL = True

# ============================ MANGOPROXY ISP (Gateway-Based — Budget ISP Rotating Proxies) ============================
# Uses GATEWAY model: connect to MANGOPROXY_HOST:MANGOPROXY_PORT with rotating username credentials.
# Each unique username/session ID gets a fresh ISP exit IP. No API pool needed.
MANGOPROXY_ENABLED = os.getenv('MANGOPROXY_ENABLED', 'true').lower() == 'true'
MANGOPROXY_HOST = os.getenv('MANGOPROXY_HOST', 'p1.mangoproxy.com')
MANGOPROXY_PORT = int(os.getenv('MANGOPROXY_PORT', '8000'))
MANGOPROXY_USERNAME = os.getenv('MANGOPROXY_USERNAME', '')
MANGOPROXY_PASSWORD = os.getenv('MANGOPROXY_PASSWORD', '')
MANGOPROXY_PROTOCOL = os.getenv('MANGOPROXY_PROTOCOL', 'http')
MANGOPROXY_REGION = os.getenv('MANGOPROXY_REGION', 'us')
MANGOPROXY_SESSION_TIME_MIN = int(os.getenv('MANGOPROXY_SESSION_TIME_MIN', '10'))
MANGOPROXY_MAX_AD_INTERACTIONS_PER_IP = int(os.getenv('MANGOPROXY_MAX_AD_INTERACTIONS_PER_IP', '25'))

# ============================ TRAFFIC ROUTING RATIOS ============================
IMPRESSION_SESSION_RATIO = 0.75  # 75% of sessions use scraped proxies (ghost, bouncer, scanner)
REVENUE_SESSION_RATIO = 0.25    # 25% of sessions use MangoProxy+Mullvad (reader, deep_diver, searcher)
MANGOPROXY_MULLVAD_SPLIT = 0.80  # Of revenue sessions: 80% MangoProxy ISP, 20% Mullvad VPN

# ============================ IP REPUTATION CHECK ============================
IP_REPUTATION_CHECK_ENABLED = True
IP_REPUTATION_SERVICES = [
    'http://ip-api.com/json/{ip}?fields=proxy,hosting,mobile,country,countryCode,isp,timezone',
]
IP_REPUTATION_TIMEOUT = 5

# ============================ PER-IP INTERACTION TRACKING ============================
MAX_AD_INTERACTIONS_PER_MANGOPROXY_IP = MANGOPROXY_MAX_AD_INTERACTIONS_PER_IP
MAX_AD_INTERACTIONS_PER_MULLVAD_IP = MULLVAD_MAX_AD_INTERACTIONS_PER_IP
MAX_AD_INTERACTIONS_PER_WEBSHARE_IP = WEBSHARE_MAX_AD_INTERACTIONS_PER_IP
INTERACTION_TRACKING_WINDOW_HOURS = 24

COUNTRY_BEHAVIOR = {
    "US": {"ctr_mod": 1.0, "scroll_speed": "medium", "dwell_bias": 1.0, "device_bias": "balanced", "peak_hours": (9, 21), "referrer_preference": {"google_search": 0.35, "social_media": 0.20, "direct": 0.25, "news_aggregator": 0.12, "referral_link": 0.08}},
    "GB": {"ctr_mod": 0.95, "scroll_speed": "medium", "dwell_bias": 1.1, "device_bias": "balanced", "peak_hours": (8, 20), "referrer_preference": {"google_search": 0.40, "social_media": 0.18, "direct": 0.22, "news_aggregator": 0.12, "referral_link": 0.08}},
    "DE": {"ctr_mod": 0.85, "scroll_speed": "slow", "dwell_bias": 1.3, "device_bias": "desktop_heavy", "peak_hours": (8, 19), "referrer_preference": {"google_search": 0.45, "social_media": 0.10, "direct": 0.30, "news_aggregator": 0.10, "referral_link": 0.05}},
    "IN": {"ctr_mod": 0.70, "scroll_speed": "slow", "dwell_bias": 1.1, "device_bias": "mobile_heavy", "peak_hours": (10, 20), "referrer_preference": {"google_search": 0.50, "social_media": 0.20, "direct": 0.15, "news_aggregator": 0.10, "referral_link": 0.05}},
    "JP": {"ctr_mod": 0.90, "scroll_speed": "fast", "dwell_bias": 0.8, "device_bias": "mobile_heavy", "peak_hours": (7, 22), "referrer_preference": {"google_search": 0.30, "social_media": 0.25, "direct": 0.20, "news_aggregator": 0.15, "referral_link": 0.10}},
    "BR": {"ctr_mod": 0.75, "scroll_speed": "medium", "dwell_bias": 1.0, "device_bias": "mobile_heavy", "peak_hours": (10, 22), "referrer_preference": {"google_search": 0.45, "social_media": 0.25, "direct": 0.15, "news_aggregator": 0.08, "referral_link": 0.07}},
    "PK": {"ctr_mod": 0.65, "scroll_speed": "slow", "dwell_bias": 1.2, "device_bias": "mobile_heavy", "peak_hours": (10, 21), "referrer_preference": {"google_search": 0.50, "social_media": 0.20, "direct": 0.15, "news_aggregator": 0.08, "referral_link": 0.07}},
}
FALLBACK_COUNTRY_BEHAVIOR = {"ctr_mod": 0.85, "scroll_speed": "medium", "dwell_bias": 1.0, "device_bias": "balanced", "peak_hours": (9, 21), "referrer_preference": REFERRAL_SOURCES}

# ============================ ARTICLE FRESHNESS BIAS (SEO: Latest Articles First) ============================
# Higher article numbers are assumed to be newer (article-24 = newest, article-1 = oldest).
# This biases traffic toward latest content → Google sees new content has immediate engagement.
ARTICLE_FRESHNESS_BIAS = float(os.getenv('ARTICLE_FRESHNESS_BIAS', '0.75'))  # 75% chance of visiting a "recent" article
RECENT_ARTICLE_THRESHOLD = float(os.getenv('RECENT_ARTICLE_THRESHOLD', '0.5'))  # Top 50% of articles count as "recent"
MIN_ARTICLE_AGE_HOURS = int(os.getenv('MIN_ARTICLE_AGE_HOURS', '2'))  # Don't visit articles newer than 2h (let Google index first)

def validate_config():
    errors = []
    if not DEEPSEEK_API_KEY or 'your_' in DEEPSEEK_API_KEY: errors.append("DEEPSEEK_API_KEY not set (AI falls back to random — OK)")
    if not HILLTOPADS_PUBLISHER_ID or 'your_' in HILLTOPADS_PUBLISHER_ID: logging.getLogger('config').warning("HILLTOPADS_PUBLISHER_ID not set — ad revenue won't work")
    return True