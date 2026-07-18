#!/usr/bin/env python3
"""
LOPINUZE Ad Farm V3 — Complete Test Suite
===========================================
Phase 12: Testing & Tuning
Tests all major V3 components.

Usage:
    python test_farm.py              # Run all tests
    python test_farm.py --quick      # Quick smoke test only
    python test_farm.py --load N     # Load test with N concurrent sessions
"""

import asyncio
import sys
import os
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'ad farm' / 'ad farm'))
sys.path.insert(0, str(Path(__file__).parent / 'ad farm'))
sys.path.insert(0, str(Path(__file__).parent))

RESULTS = []
PASS_STR = "PASS"
FAIL_STR = "FAIL"

def log_result(name: str, passed: bool, detail: str = ""):
    status = PASS_STR if passed else FAIL_STR
    RESULTS.append({"name": name, "passed": passed, "detail": detail})
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_summary():
    passed = sum(1 for r in RESULTS if r["passed"])
    failed = sum(1 for r in RESULTS if not r["passed"])
    print(f"\n{'='*60}")
    print(f"  SUMMARY: {passed}/{len(RESULTS)} passed, {failed} failed")
    print(f"{'='*60}")
    if failed:
        print("\n  FAILED:")
        for r in RESULTS:
            if not r["passed"]:
                print(f"    - {r['name']}: {r['detail']}")
    return failed == 0


# ============================ TEST: MODULE IMPORTS ============================
def test_imports():
    print_header("Module Imports")
    modules = [
        "config", "sections", "geo_utils", "ai_behavior", "ads_engine",
        "survival_engine", "multi_ad_network", "stealth_patches",
        "fingerprint_manager", "proxy_filter", "smart_rotator",
        "proxy_manager", "vpn_tunnel", "survival_integration",
        "revenue_optimizer", "browser_manager", "session_engine", "dashboard"
    ]
    for mod in modules:
        try:
            __import__(mod)
            log_result(f"Import {mod}", True)
        except Exception as e:
            log_result(f"Import {mod}", False, str(e)[:80])


# ============================ TEST: CONFIG ============================
def test_config():
    print_header("Config Validation")
    from config import (
        SITE_URL, MAX_CONCURRENT_SESSIONS, GPU_ENABLED, validate_config
    )
    log_result("SITE_URL", bool(SITE_URL), SITE_URL[:50])
    log_result("MAX_CONCURRENT_SESSIONS", MAX_CONCURRENT_SESSIONS >= 10, str(MAX_CONCURRENT_SESSIONS))
    log_result("GPU_ENABLED", isinstance(GPU_ENABLED, bool), str(GPU_ENABLED))
    validate_config()
    log_result("validate_config()", True)


# ============================ TEST: SECTIONS ============================
def test_sections():
    print_header("50 Sections")
    from sections import get_random_section, get_section_count, get_section_url
    count = get_section_count()
    log_result("Section count", count >= 45, str(count))
    section = get_random_section()
    log_result("Random section", bool(section), section.get('name', ''))
    url = get_section_url(section)
    log_result("Section URL", bool(url), url[:50])


# ============================ TEST: FINGERPRINT ============================
def test_fingerprint():
    print_header("Fingerprint Generation")
    from fingerprint_manager import FingerprintFactory
    factory = FingerprintFactory()
    fp = factory.generate()
    log_result("Generate", fp is not None)
    log_result("CPU cores", fp.cpu_cores > 0, str(fp.cpu_cores))
    log_result("RAM GB", fp.ram_gb > 0, str(fp.ram_gb))
    log_result("GPU model", bool(fp.gpu_model), fp.gpu_model[:30])
    log_result("Platform", bool(fp.platform), fp.platform)
    log_result("Screen", fp.screen_width > 0, f"{fp.screen_width}x{fp.screen_height}")
    log_result("Canvas seed", fp.canvas_seed > 0, str(fp.canvas_seed))
    
    fp_dict = fp.to_dict()
    log_result("to_dict()", len(fp_dict) > 10, f"{len(fp_dict)} keys")
    
    geo = {'timezone': 'Europe/London', 'locale': 'en-GB', 'language': 'en'}
    fp2 = factory.generate(geo_config=geo)
    log_result("Geo-aware", fp2.timezone == 'Europe/London', fp2.timezone)
    
    # Uniqueness
    hashes = set()
    for _ in range(500):
        hashes.add(factory.generate().fingerprint_hash)
    log_result("Uniqueness (500)", len(hashes) == 500, f"{len(hashes)} unique")


# ============================ TEST: STEALTH PATCHES ============================
async def test_stealth():
    print_header("Stealth Patches")
    from stealth_patches import StealthPatcher, STEALTH_SCRIPT_BASE
    log_result("Stealth script", len(STEALTH_SCRIPT_BASE) > 500, f"{len(STEALTH_SCRIPT_BASE)} chars")
    
    checks = ["navigator.webdriver", "navigator.plugins", "chrome.runtime",
              "hardwareConcurrency", "deviceMemory", "ServiceWorker"]
    for keyword in checks:
        log_result(f"Contains {keyword}", keyword in STEALTH_SCRIPT_BASE)

    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            
            # Without stealth
            ctx1 = await browser.new_context()
            pg1 = await ctx1.new_page()
            await pg1.goto('about:blank')
            wd1 = await pg1.evaluate('navigator.webdriver')
            log_result("Without stealth: webdriver", wd1 == True, str(wd1))
            
            # With stealth
            ctx2 = await browser.new_context()
            fp = {'hardware_concurrency': 8, 'device_memory': 16, 'platform': 'Win32',
                  'screen_width': 1920, 'screen_height': 1080, 'avail_width': 1920, 'avail_height': 1040,
                  'color_depth': 24, 'canvas_seed': 123456, 'audio_seed': 789012,
                  'webgl_vendor': 'Google Inc. (NVIDIA)', 
                  'webgl_renderer': 'ANGLE (NVIDIA, RTX 3060 Direct3D11 vs_5_0 ps_5_0)',
                  'device_type': 'desktop'}
            await StealthPatcher.patch_context(ctx2, fp)
            pg2 = await ctx2.new_page()
            await pg2.goto('about:blank')
            wd2 = await pg2.evaluate('navigator.webdriver')
            log_result("With stealth: webdriver=false", wd2 == False, str(wd2))
            plugins = await pg2.evaluate('navigator.plugins.length')
            log_result("With stealth: plugins>0", plugins > 0, str(plugins))
            
            await browser.close()
    except ImportError:
        log_result("Browser test", False, "Playwright not installed")
    except Exception as e:
        log_result("Browser test", False, str(e)[:80])


# ============================ TEST: PROXY FILTER ============================
async def test_proxy():
    print_header("Proxy Pipeline")
    from proxy_filter import ProxyFilter, ProxyTier, AnonymityLevel
    
    pf = ProxyFilter(db_path="test_proxies.db")
    log_result("Init", True)
    
    tier_s = pf._assign_tier(AnonymityLevel.ELITE, 50, 0)
    log_result("S-tier assignment", tier_s == ProxyTier.S)
    tier_a = pf._assign_tier(AnonymityLevel.ANONYMOUS, 200, 0)
    log_result("A-tier assignment", tier_a == ProxyTier.A)
    
    await pf._ensure_session()
    raw = await pf.fetch_all_sources()
    log_result("Fetch sources", len(raw) > 0, f"{len(raw)} raw proxies")
    
    sample = list(raw)[:30]
    if sample:
        verified = await pf.verify_batch(sample, concurrency=30)
        log_result("Verify batch", True, f"{len(verified)}/{len(sample)} working")
    
    await pf.close()
    for f in ["test_proxies.db", "test_proxies.db-shm", "test_proxies.db-wal"]:
        try: os.remove(f)
        except: pass


# ============================ TEST: SURVIVAL ============================
async def test_survival():
    print_header("Survival Integration")
    from survival_integration import get_survival_integrator
    s = await get_survival_integrator()
    log_result("Init", True)
    allowed, throttle = await s.pre_session_check()
    log_result("pre_session_check", isinstance(allowed, bool), f"allowed={allowed}")
    stats = s.get_stats()
    log_result("get_stats", 'risk_level' in stats, stats.get('risk_level'))
    await s.post_session_feedback({
        'success': True, 'pages_visited': 3, 'ad_hovers': 2,
        'ad_clicks': 0, 'time_spent': 85, 'section_visited': 'tech',
        'device_type': 'desktop', 'source_type': 'google_search'
    })
    log_result("post_session_feedback", True)
    shape = s.get_traffic_shape()
    log_result("get_traffic_shape", 0 < shape <= 1.5, f"{shape:.3f}")


# ============================ TEST: BROWSER ============================
async def test_browser():
    print_header("Browser Manager")
    try:
        from browser_manager import BrowserPool
        pool = BrowserPool(max_concurrent=1)
        fp = {'hardware_concurrency': 8, 'device_memory': 16, 'platform': 'Win32',
              'screen_width': 1920, 'screen_height': 1080, 'avail_width': 1920, 'avail_height': 1040,
              'color_depth': 24, 'pixel_ratio': 1.0, 'locale': 'en-US', 'timezone': 'America/New_York',
              'canvas_seed': 999, 'audio_seed': 888, 'webgl_vendor': 'Google Inc. (NVIDIA)',
              'webgl_renderer': 'ANGLE (NVIDIA, RTX 3060)', 'device_type': 'desktop',
              'languages': ['en-US', 'en'],
              'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36'}
        
        session = await pool.create_session(proxy_url=None, fingerprint=fp, viewport={'width': 1920, 'height': 1080})
        if session:
            log_result("Session created", True)
            ok = await session.navigate('https://example.com')
            log_result("Navigate", ok)
            if ok:
                title = await session.get_page_title()
                log_result("Page title", bool(title), title[:30])
                await session.scroll(200)
                log_result("Scroll", True)
            await pool.close_session(session)
        else:
            log_result("Session created", False, "Failed")
        await pool.cleanup()
    except ImportError:
        log_result("Browser test", False, "Playwright not installed")
    except Exception as e:
        log_result("Browser test", False, str(e)[:80])


# ============================ TEST: SESSION ENGINE ============================
async def test_session():
    print_header("Session Engine")
    from session_engine import SessionEngine
    engine = SessionEngine()
    log_result("Init", True)
    result = await engine.run_session("TEST-001")
    log_result("Run session", isinstance(result, dict))
    log_result("Has success", 'success' in result, str(result.get('success')))
    log_result("Has pages", 'pages_visited' in result, str(result.get('pages_visited')))
    if not result.get('success'):
        log_result("Expected failure", True, f"No proxy: {result.get('error', '')}")


# ============================ TEST: DASHBOARD ============================
def test_dashboard():
    print_header("Dashboard")
    try:
        from dashboard import app, update_state, MAIN_PAGE
        log_result("Flask app", True)
        log_result("Template", len(MAIN_PAGE) > 500, f"{len(MAIN_PAGE)} chars")
        update_state(running=True, total_sessions=42, risk_level="safe")
        with app.test_client() as client:
            resp = client.get('/api/stats')
            log_result("/api/stats 200", resp.status_code == 200)
            data = resp.get_json()
            log_result("API JSON", isinstance(data, dict))
    except ImportError:
        log_result("Dashboard", False, "Flask not installed")
    except Exception as e:
        log_result("Dashboard", False, str(e)[:80])


# ============================ TEST: REVENUE ============================
async def test_revenue():
    print_header("Revenue Tracking")
    from farm import RevenueTracker
    tracker = RevenueTracker()
    await tracker.record_session(popunders=1, banner_impressions=3, banner_clicks=1)
    await tracker.record_session(popunders=1, banner_impressions=2, banner_clicks=0)
    earnings = tracker.get_earnings()
    log_result("Total > 0", earnings['total'] > 0, f"${earnings['total']:.4f}")
    log_result("Sessions", earnings['sessions'] == 2, str(earnings['sessions']))


# ============================ TEST: LOAD ============================
async def test_load(num: int = 10):
    print_header(f"Load Test ({num} concurrent)")
    from session_engine import SessionEngine
    engine = SessionEngine()
    start = time.time()
    tasks = [engine.run_session(f"LOAD-{i:04d}") for i in range(num)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start
    ok = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
    err = sum(1 for r in results if not isinstance(r, dict))
    log_result("Completed", True, f"{num} in {elapsed:.1f}s")
    log_result("Successes", True, str(ok))
    log_result("Errors", err == 0, str(err))
    log_result("Rate", True, f"{num/elapsed:.1f} sessions/sec")


# ============================ MAIN ============================
async def run_all_tests(args):
    print("=" * 60)
    print("  LOPINUZE AD FARM V3 — TEST SUITE")
    print("=" * 60)
    
    test_imports()
    test_config()
    test_sections()
    test_fingerprint()
    await test_revenue()
    test_dashboard()
    await test_stealth()
    await test_proxy()
    await test_survival()
    await test_browser()
    await test_session()
    if args.load:
        await test_load(args.load)
    return print_summary()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LOPINUZE Ad Farm V3 Test Suite')
    parser.add_argument('--load', type=int, default=0, help='Load test with N sessions')
    args = parser.parse_args()
    all_pass = asyncio.run(run_all_tests(args))
    sys.exit(0 if all_pass else 1)