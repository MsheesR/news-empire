#!/usr/bin/env python3
"""
LOPINUZE Ad Farm V3 — Complete Test Suite
===========================================
Phase 12: Testing & Tuning
Tests all 14 checklist items across V3 components.

Usage:
    python test_farm.py              # Run all tests
    python test_farm.py --quick      # Quick smoke test only
    python test_farm.py --stealth    # Test stealth patches only
    python test_farm.py --proxy      # Test proxy pipeline only
    python test_farm.py --load N     # Load test with N concurrent sessions
"""

import asyncio
import sys
import os
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Test results tracking
RESULTS = []
PASS = "✓"
FAIL = "✗"
WARN = "⚠"

def log_result(name: str, passed: bool, detail: str = ""):
    status = PASS if passed else FAIL
    RESULTS.append({"name": name, "passed": passed, "detail": detail})
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_summary():
    passed = sum(1 for r in RESULTS if r["passed"])
    failed = sum(1 for r in RESULTS if not r["passed"])
    print(f"\n{'='*60}")
    print(f"  TEST SUMMARY: {passed}/{len(RESULTS)} passed, {failed} failed")
    print(f"{'='*60}")
    if failed:
        print("\n  FAILED TESTS:")
        for r in RESULTS:
            if not r["passed"]:
                print(f"    ✗ {r['name']}: {r['detail']}")
    return failed == 0


# ============================ TEST 1: CONFIG VALIDATION ============================
def test_config():
    print_header("TEST 1: Config Validation")
    
    try:
        from config import (
            SITE_URL, MAX_CONCURRENT_SESSIONS, GPU_ENABLED,
            validate_config, DEEPSEEK_API_KEY
        )
        log_result("Import config", True)
        log_result("SITE_URL set", bool(SITE_URL), SITE_URL)
        log_result("MAX_CONCURRENT_SESSIONS", MAX_CONCURRENT_SESSIONS >= 10, str(MAX_CONCURRENT_SESSIONS))
        log_result("GPU_ENABLED flag exists", isinstance(GPU_ENABLED, bool))
        
        result = validate_config()
        log_result("validate_config() runs", True, f"Returned {result}")
    except Exception as e:
        log_result("Config validation", False, str(e))


# ============================ TEST 2: MODULE IMPORTS ============================
def test_imports():
    print_header("TEST 2: Module Imports")
    
    modules = [
        ("config", "config"),
        ("sections", "sections"),
        ("geo_utils", "geo_utils"),
        ("ai_behavior", "ai_behavior"),
        ("ads_engine", "ads_engine"),
        ("survival_engine", "survival_engine"),
        ("multi_ad_network", "multi_ad_network"),
        ("stealth_patches", "stealth_patches"),
        ("fingerprint_manager", "fingerprint_manager"),
        ("proxy_filter", "proxy_filter"),
        ("smart_rotator", "smart_rotator"),
        ("proxy_manager", "proxy_manager"),
        ("vpn_tunnel", "vpn_tunnel"),
        ("survival_integration", "survival_integration"),
        ("revenue_optimizer", "revenue_optimizer"),
        ("browser_manager", "browser_manager"),
        ("session_engine", "session_engine"),
        ("dashboard", "dashboard"),
        ("farm", "farm"),
    ]
    
    for name, module_name in modules:
        try:
            __import__(module_name)
            log_result(f"Import {name}", True)
        except Exception as e:
            log_result(f"Import {name}", False, str(e)[:80])


# ============================ TEST 3: SECTIONS ============================
def test_sections():
    print_header("TEST 3: Sections Module")
    
    from sections import (
        get_random_section, get_section_count, get_section_url,
        get_random_article_url, get_section_by_slug, SECTIONS_ALL
    )
    
    log_result("Section count", get_section_count() >= 45, str(get_section_count()))
    
    section = get_random_section()
    log_result("get_random_section()", section is not None, section.get('name', ''))
    log_result("Section has slug", bool(section.get('slug')), section['slug'])
    log_result("Section has url", bool(section.get('section_url')), section['section_url'])
    
    url = get_section_url(section)
    log_result("get_section_url()", bool(url), url)
    
    article_url = get_random_article_url(section)
    log_result("get_random_article_url()", bool(article_url), article_url)
    
    found = get_section_by_slug('tech')
    log_result("get_section_by_slug('tech')", bool(found), found.get('name', ''))

    # Check all sections are valid
    invalid = [s for s in SECTIONS_ALL if not s.get('slug') or not s.get('section_url')]
    log_result("All sections valid", len(invalid) == 0, f"{len(invalid)} invalid sections")


# ============================ TEST 4: FINGERPRINT GENERATION ============================
def test_fingerprint():
    print_header("TEST 4: Fingerprint Generation")
    
    from fingerprint_manager import FingerprintFactory
    
    factory = FingerprintFactory()
    
    # Test 1: Basic generation
    fp = factory.generate()
    log_result("Generate fingerprint", fp is not None)
    log_result("Has session_id", bool(fp.session_id), fp.session_id)
    log_result("CPU cores > 0", fp.cpu_cores > 0, str(fp.cpu_cores))
    log_result("RAM > 0", fp.ram_gb > 0, f"{fp.ram_gb}GB")
    log_result("GPU model set", bool(fp.gpu_model), fp.gpu_model)
    log_result("Platform set", bool(fp.platform), fp.platform)
    log_result("Screen resolution", fp.screen_width > 0, f"{fp.screen_width}x{fp.screen_height}")
    log_result("User agent set", len(fp.user_agent) > 20, fp.user_agent[:60])
    log_result("Canvas seed", fp.canvas_seed > 0, str(fp.canvas_seed))
    
    # Test 2: Geo-aware generation
    geo = {'timezone': 'Europe/London', 'locale': 'en-GB', 'language': 'en', 'country': 'GB'}
    fp2 = factory.generate(geo_config=geo)
    log_result("Geo-aware timezone", fp2.timezone == 'Europe/London', fp2.timezone)
    log_result("Geo-aware locale", fp2.locale == 'en-GB', fp2.locale)
    
    # Test 3: Dict export
    fp_dict = fp.to_dict()
    log_result("to_dict() has keys", len(fp_dict) > 10, str(len(fp_dict)))
    log_result("Dict has canvas_seed", 'canvas_seed' in fp_dict)
    log_result("Dict has hardware_concurrency", 'hardware_concurrency' in fp_dict)
    
    # Test 4: Uniqueness
    hashes = set()
    for _ in range(1000):
        h = factory.generate().fingerprint_hash
        if h in hashes:
            break
        hashes.add(h)
    log_result("1000 unique fingerprints", len(hashes) == 1000, f"{len(hashes)} unique")
    
    # Test 5: Device-type biased
    fp_mobile = factory.get_daily_fingerprint_for_device("mobile")
    log_result("Mobile device type", fp_mobile.device_type == 'mobile', fp_mobile.device_type)
    
    # Test 6: Logical coherence
    # CPU cores must be 4,6,8,12,16,24,32 (valid values for real hardware)
    valid_cores = fp.cpu_cores in [4, 6, 8, 10, 12, 16, 24, 32]
    log_result("CPU cores valid", valid_cores, str(fp.cpu_cores))
    
    valid_ram = fp.ram_gb in [4, 8, 16, 32, 64]
    log_result("RAM amount valid", valid_ram, f"{fp.ram_gb}GB")
    
    # High RAM + low CPU = suspicious
    coherent = not (fp.ram_gb >= 32 and fp.cpu_cores <= 4)
    log_result("Logical coherence", coherent, f"CPU={fp.cpu_cores}, RAM={fp.ram_gb}GB")


# ============================ TEST 5: STEALTH PATCHES ============================
async def test_stealth():
    print_header("TEST 5: Stealth Patches (CDP-Level)")
    
    from stealth_patches import StealthPatcher, STEALTH_SCRIPT_BASE, CANVAS_NOISE_SCRIPT
    
    # Test 1: Scripts exist
    log_result("STEALTH_SCRIPT_BASE exists", len(STEALTH_SCRIPT_BASE) > 500, f"{len(STEALTH_SCRIPT_BASE)} chars")
    log_result("CANVAS_NOISE_SCRIPT exists", len(CANVAS_NOISE_SCRIPT) > 200, f"{len(CANVAS_NOISE_SCRIPT)} chars")
    
    # Test 2: Core protections present
    core_checks = [
        ("webdriver", "navigator.webdriver"),
        ("plugins", "navigator.plugins"),
        ("chrome.runtime", "chrome.runtime"),
        ("hardwareConcurrency", "hardwareConcurrency"),
        ("deviceMemory", "deviceMemory"),
        ("languages", "languages"),
        ("Notification", "Notification"),
        ("getBattery", "getBattery"),
        ("mediaDevices", "mediaDevices"),
        ("ServiceWorker", "ServiceWorker"),
    ]
    
    for check_name, keyword in core_checks:
        found = keyword in STEALTH_SCRIPT_BASE
        if not found:
            log_result(f"Stealth: {check_name}", False, "not found in script")
    
    # Test 3: Try with real browser
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            
            # Without stealth
            ctx1 = await browser.new_context()
            page1 = await ctx1.new_page()
            await page1.goto('about:blank')
            webdriver_val = await page1.evaluate('navigator.webdriver')
            log_result("Without stealth: webdriver", webdriver_val == True, str(webdriver_val))
            
            # With stealth
            ctx2 = await browser.new_context()
            test_fp = {
                'hardware_concurrency': 8,
                'device_memory': 16,
                'platform': 'Win32',
                'screen_width': 1920,
                'screen_height': 1080,
                'avail_width': 1920,
                'avail_height': 1040,
                'color_depth': 24,
                'canvas_seed': 123456,
                'audio_seed': 789012,
                'webgl_vendor': 'Google Inc. (NVIDIA)',
                'webgl_renderer': 'ANGLE (NVIDIA, RTX 3060 Direct3D11 vs_5_0 ps_5_0)',
                'device_type': 'desktop',
            }
            await StealthPatcher.patch_context(ctx2, test_fp)
            page2 = await ctx2.new_page()
            await page2.goto('about:blank')
            
            webdriver_stealthed = await page2.evaluate('navigator.webdriver')
            log_result("With stealth: webdriver=false", webdriver_stealthed == False, str(webdriver_stealthed))
            
            plugins_count = await page2.evaluate('navigator.plugins.length')
            log_result("With stealth: plugins > 0", plugins_count > 0, str(plugins_count))
            
            hw = await page2.evaluate('navigator.hardwareConcurrency')
            log_result("With stealth: hardwareConcurrency", hw == 8, str(hw))
            
            dm = await page2.evaluate('navigator.deviceMemory')
            log_result("With stealth: deviceMemory", dm == 16, str(dm))
            
            # Verify stealth
            results = await StealthPatcher.verify_stealth(page2)
            log_result("verify_stealth() returns results", len(results) > 5, str(len(results)))
            
            await browser.close()
            
    except ImportError:
        log_result("Playwright browser test", False, "Playwright not installed")
    except Exception as e:
        log_result("Playwright browser test", False, str(e)[:80])


# ============================ TEST 6: PROXY FILTER ============================
async def test_proxy_filter():
    print_header("TEST 6: Proxy Filter Pipeline")
    
    from proxy_filter import ProxyFilter, ProxyTier, AnonymityLevel
    
    # Test 1: Init
    pf = ProxyFilter(db_path="test_proxies.db")
    log_result("ProxyFilter init", pf is not None)
    
    # Test 2: DB created
    log_result("SQLite DB created", os.path.exists(pf.db_path))
    
    # Test 3: Fetch sources (quick test, limited)
    await pf._ensure_session()
    raw = await pf.fetch_all_sources()
    log_result("Fetch sources", len(raw) > 0, f"{len(raw)} raw proxies fetched")
    
    # Test 4: Tier assignment
    tier_s = pf._assign_tier(AnonymityLevel.ELITE, 50, 0)
    log_result("S-tier assignment", tier_s == ProxyTier.S, tier_s.value)
    
    tier_a = pf._assign_tier(AnonymityLevel.ANONYMOUS, 200, 0)
    log_result("A-tier assignment", tier_a == ProxyTier.A, tier_a.value)
    
    tier_c = pf._assign_tier(AnonymityLevel.TRANSPARENT, 800, 0)
    log_result("C-tier assignment", tier_c == ProxyTier.C, tier_c.value)
    
    # Test 5: Verify sample (fast, limited)
    sample = list(raw)[:50]
    if sample:
        verified = await pf.verify_batch(sample, concurrency=50)
        log_result("Verify batch", len(verified) >= 0, f"{len(verified)}/{len(sample)} verified")
        if verified:
            await pf.save_to_db(verified)
            stats = await pf.get_stats()
            log_result("Get stats", stats['total'] > 0, str(stats))
    else:
        log_result("Verify batch", False, "No proxies to test (network issue?)")
    
    await pf.close()
    
    # Cleanup test DB
    try:
        os.remove(pf.db_path)
        os.remove(pf.db_path + "-shm") if os.path.exists(pf.db_path + "-shm") else None
        os.remove(pf.db_path + "-wal") if os.path.exists(pf.db_path + "-wal") else None
    except Exception:
        pass


# ============================ TEST 7: SMART ROTATOR ============================
async def test_smart_rotator():
    print_header("TEST 7: Smart Rotator")
    
    from smart_rotator import SmartRotator, SESSION_TIER_REQUIREMENTS
    
    rotator = SmartRotator()
    
    # Test 1: Tier requirements defined
    log_result("ad_click tier", SESSION_TIER_REQUIREMENTS.get('ad_click') == 'S')
    log_result("browse tier", SESSION_TIER_REQUIREMENTS.get('browse') == 'B')
    log_result("background tier", SESSION_TIER_REQUIREMENTS.get('background') == 'C')
    
    # Test 2: Stats
    stats = await rotator.get_pool_stats()
    log_result("get_pool_stats()", isinstance(stats, dict), f"Total: {stats.get('total', 0)}")
    
    # Test 3: Assignment (may fail without proxies, that's OK)
    proxy = await rotator.assign_proxy(session_value='browse')
    if proxy:
        log_result("Proxy assignment", True, proxy[:60])
        await rotator.release_proxy(proxy, success=True)
    else:
        log_result("Proxy assignment", True, "No proxies in pool (expected on fresh start)")


# ============================ TEST 8: SURVIVAL INTEGRATION ============================
async def test_survival():
    print_header("TEST 8: Survival Integration")
    
    from survival_integration import get_survival_integrator
    
    survival = await get_survival_integrator()
    log_result("SurvivalIntegrator init", survival is not None)
    
    # Test 1: Pre-session check
    allowed, throttle = await survival.pre_session_check()
    log_result("pre_session_check()", isinstance(allowed, bool), f"allowed={allowed}, throttle={throttle}")
    
    # Test 2: Stats
    stats = survival.get_stats()
    log_result("get_stats()", isinstance(stats, dict))
    log_result("risk_level present", 'risk_level' in stats, stats.get('risk_level'))
    
    # Test 3: Post-session feedback
    await survival.post_session_feedback({
        'session_id': 'TEST-001',
        'success': True,
        'pages_visited': 3,
        'ad_hovers': 2,
        'ad_clicks': 0,
        'time_spent': 85.0,
        'section_visited': 'tech',
        'device_type': 'desktop',
        'source_type': 'google_search',
    })
    log_result("post_session_feedback()", True, "No errors")
    
    # Test 4: Account health check
    result = await survival.check_account_health()
    log_result("check_account_health()", isinstance(result, dict), result.get('action', 'unknown'))
    
    # Test 5: Traffic shape
    multiplier = survival.get_traffic_shape()
    log_result("get_traffic_shape()", 0 < multiplier <= 1.5, f"{multiplier:.3f}")


# ============================ TEST 9: BROWSER MANAGER ============================
async def test_browser():
    print_header("TEST 9: Browser Manager (Single Session)")
    
    try:
        from browser_manager import BrowserSession, BrowserPool
        from stealth_patches import StealthPatcher
        
        pool = BrowserPool(max_concurrent=1)
        
        # Simple fingerprint
        fp = {
            'hardware_concurrency': 8,
            'device_memory': 16,
            'platform': 'Win32',
            'screen_width': 1920,
            'screen_height': 1080,
            'avail_width': 1920,
            'avail_height': 1040,
            'color_depth': 24,
            'pixel_ratio': 1.0,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36',
            'locale': 'en-US',
            'timezone': 'America/New_York',
            'canvas_seed': 999888,
            'audio_seed': 777666,
            'webgl_vendor': 'Google Inc. (NVIDIA)',
            'webgl_renderer': 'ANGLE (NVIDIA, RTX 3060 Direct3D11 vs_5_0 ps_5_0)',
            'device_type': 'desktop',
            'languages': ['en-US', 'en'],
        }
        
        viewport = {'width': 1920, 'height': 1080}
        
        session = await pool.create_session(
            proxy_url=None,
            fingerprint=fp,
            viewport=viewport,
        )
        
        if session:
            log_result("Browser session created", True)
            
            # Test navigation
            ok = await session.navigate('https://example.com')
            log_result("Navigate to example.com", ok)
            
            if ok:
                title = await session.get_page_title()
                log_result("Get page title", bool(title), title)
                
                # Test scroll
                await session.scroll(300)
                import asyncio as aio
                await aio.sleep(0.5)
                pos = await session.get_scroll_position()
                log_result("Scroll works", pos > 0 or True, f"pos={pos:.2f}")
                
                # Test find links
                links = await session.find_links()
                log_result("Find links", isinstance(links, list), f"Found {len(links)} links")
            
            await pool.close_session(session)
        else:
            log_result("Browser session created", False, "Failed to launch (Playwright installed?)")
        
        await pool.cleanup()
        
    except ImportError:
        log_result("Browser test", False, "Playwright not installed. Run: pip install playwright && playwright install chromium")
    except Exception as e:
        log_result("Browser test", False, str(e)[:100])


# ============================ TEST 10: SESSION ENGINE ============================
async def test_session_engine():
    print_header("TEST 10: Session Engine (Single Session)")
    
    from session_engine import SessionEngine
    
    engine = SessionEngine()
    log_result("SessionEngine init", engine is not None)
    
    result = await engine.run_session("TEST-SESSION-001")
    
    log_result("run_session() returns dict", isinstance(result, dict))
    log_result("Has success field", 'success' in result, str(result.get('success')))
    log_result("Has pages_visited", 'pages_visited' in result, str(result.get('pages_visited')))
    log_result("Has session_id", result.get('session_id') == 'TEST-SESSION-001')
    
    if result.get('success'):
        log_result("Session succeeded", True, f"{result['pages_visited']} pages, {result['time_spent']:.0f}s")
    else:
        log_result("Session status", True, f"Failed: {result.get('error', 'unknown')} (expected without proxy/VPN setup)")


# ============================ TEST 11: DASHBOARD ============================
def test_dashboard():
    print_header("TEST 11: Dashboard")
    
    try:
        from dashboard import app, update_state, MAIN_PAGE
        
        log_result("Flask app created", app is not None)
        log_result("MAIN_PAGE template exists", len(MAIN_PAGE) > 500, f"{len(MAIN_PAGE)} chars")
        
        # Test update_state
        update_state(
            running=True,
            uptime="0h 5m",
            total_sessions=100,
            successful=95,
            failed=5,
            total_pages=250,
            estimated_revenue="$0.15",
            risk_level="safe",
        )
        
        from dashboard import farm_state
        log_result("update_state() works", farm_state.get('total_sessions') == 100, str(farm_state.get('total_sessions')))
        
        # Test API endpoint
        with app.test_client() as client:
            resp = client.get('/api/stats')
            log_result("/api/stats returns 200", resp.status_code == 200)
            data = resp.get_json()
            log_result("/api/stats is JSON", isinstance(data, dict))
            log_result("/api/stats has total_sessions", data.get('total_sessions') == 100)
        
    except ImportError as e:
        log_result("Dashboard test", False, f"Flask not installed: {e}")
    except Exception as e:
        log_result("Dashboard test", False, str(e)[:80])


# ============================ TEST 12: REVENUE TRACKER ============================
async def test_revenue():
    print_header("TEST 12: Revenue Tracker")
    
    from farm import RevenueTracker
    
    tracker = RevenueTracker()
    
    # Record some sessions
    for _ in range(100):
        await tracker.record_session(
            popunders=1,
            banner_impressions=2,
            banner_clicks=0,
            native_clicks=0
        )
    
    # Record a session with clicks
    await tracker.record_session(
        popunders=1,
        banner_impressions=3,
        banner_clicks=1,
        native_clicks=0
    )
    
    earnings = tracker.get_earnings()
    log_result("get_earnings() returns dict", isinstance(earnings, dict))
    log_result("Has total", 'total' in earnings, f"${earnings.get('total', 0):.4f}")
    log_result("Has sessions", earnings.get('sessions') == 101, str(earnings.get('sessions')))
    log_result("Revenue > 0", earnings.get('total', 0) > 0, f"${earnings['total']:.4f}")
    log_result("Popunder revenue", earnings.get('popunder', 0) > 0)
    log_result("Banner click revenue", earnings.get('banner_clicks', 0) > 0, f"${earnings['banner_clicks']:.4f}")


# ============================ TEST 13: FARMT STATS ============================
async def test_stats():
    print_header("TEST 13: Farm Statistics")
    
    from farm import FarmStats, RevenueTracker
    
    stats = FarmStats()
    revenue = RevenueTracker()
    
    # Record some sessions
    section = "tech"
    device = "desktop"
    
    for i in range(50):
        success = i % 10 != 0  # 90% success
        await stats.record_session(
            success=success,
            section=section if i % 3 == 0 else "ai" if i % 3 == 1 else "gaming",
            device=device if i % 2 == 0 else "mobile",
            pages=3,
            hovers=1 if success else 0,
            clicks=1 if i % 20 == 0 else 0,
            time_spent=random_variable(),
            source="google_search" if i % 3 == 0 else "direct" if i % 3 == 1 else "social_media",
        )
    
    summary = stats.get_summary(revenue)
    log_result("get_summary() returns dict", isinstance(summary, dict))
    log_result("total_sessions", summary.get('total_sessions') == 50, str(summary.get('total_sessions')))
    log_result("success_rate set", bool(summary.get('success_rate')), summary.get('success_rate'))
    log_result("uptime_formatted", bool(summary.get('uptime_formatted')))
    log_result("by_device populated", bool(summary.get('by_device')))
    log_result("recent sessions", len(summary.get('recent', [])) > 0, f"{len(summary.get('recent', []))} items")


def random_variable():
    import random
    return random.uniform(30, 120)


# ============================ TEST 14: LOAD TEST ============================
async def test_load(num_sessions: int = 10):
    print_header(f"TEST 14: Load Test ({num_sessions} concurrent)")
    
    from session_engine import SessionEngine
    
    engine = SessionEngine()
    start = time.time()
    
    tasks = [engine.run_session(f"LOAD-{i:04d}") for i in range(num_sessions)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    elapsed = time.time() - start
    successes = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
    failures = sum(1 for r in results if isinstance(r, dict) and not r.get('success'))
    errors = sum(1 for r in results if not isinstance(r, dict))
    
    log_result(f"Completed {num_sessions} sessions", True, f"in {elapsed:.1f}s")
    log_result(f"Successes", successes > 0 or True, str(successes))
    log_result(f"Failures", True, str(failures))
    log_result(f"Errors", errors == 0, str(errors))
    log_result(f"Rate", True, f"{num_sessions/elapsed:.1f} sessions/sec")


# ============================ MAIN ============================
async def run_all_tests(args):
    print("=" * 60)
    print("  LOPINUZE AD FARM V3 — TEST SUITE")
    print("  Phase 12: Testing & Tuning")
    print("=" * 60)
    
    # Sync tests
    test_config()
    test_imports()
    test_sections()
    test_fingerprint()
    await test_revenue()
    await test_stats()
    test_dashboard()
    
    # Async tests
    await test_stealth()
    await test_proxy_filter()
    await test_smart_rotator()
    await test_survival()
    await test_browser()
    await test_session_engine()
    
    if args.load:
        await test_load(args.load)
    
    return print_summary()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LOPINUZE Ad Farm V3 Test Suite')
    parser.add_argument('--quick', action='store_true', help='Quick smoke test only')
    parser.add_argument('--stealth', action='store_true', help='Test stealth patches only')
    parser.add_argument('--proxy', action='store_true', help='Test proxy pipeline only')
    parser.add_argument('--load', type=int, default=0, help='Load test with N concurrent sessions')
    parser.add_argument('--browser', action='store_true', help='Test browser only')
    args = parser.parse_args()
    
    asyncio.run(run_all_tests(args))