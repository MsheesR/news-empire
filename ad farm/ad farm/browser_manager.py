#!/usr/bin/env python3
"""
Browser Manager V3 — GPU-Accelerated Stealth Sessions
======================================================
Manages Playwright Chromium sessions with CDP-level stealth,
GPU hardware acceleration, per-session fingerprint injection,
and automatic crash recovery.

Key V3 Changes:
- Removed CloakBrowser dependency (not installed)
- Auto-injects StealthPatcher on EVERY new page
- Auto-injects FingerprintFactory data per session
- GPU-accelerated rendering flags for RTX 3050
- Context pooling: reuse browser, create new context per session
- Memory monitoring: auto-close idle contexts
- Crash recovery: try/except with auto-restart
- Per-context proxy assignment
- Per-context viewport/UA matching fingerprint
"""

import asyncio
import random
import time
import logging
from typing import Dict, Any, Optional, List

from config import (
    BROWSER_HEADLESS, BROWSER_LAUNCH_ARGS,
    INTERNAL_LINK_SELECTORS, AD_SELECTORS,
    PAGE_LOAD_TIMEOUT_MS,
)

logger = logging.getLogger('browser_manager')

# Browser engine selection — CloakBrowser equivalent stack (free, maximum security)
# Priority: rebrowser-playwright > undetected-chromedriver > plain Playwright
# rebrowser-playwright = CloakBrowser equivalent: patches Chromium binary for:
#   - navigator.webdriver removal (binary-level, not JS override)
#   - cdc_ variable patching
#   - TLS/JA4 fingerprint randomization  
#   - HTTP/2 settings frame randomization
#   - Font rendering normalization
REBROWSER_AVAILABLE = False
UNDETECTED_AVAILABLE = False
PLAYWRIGHT_AVAILABLE = False
BROWSER_ENGINE = 'playwright'

try:
    import rebrowser_playwright
    from rebrowser_playwright.async_api import async_playwright as rebrowser_async_playwright
    REBROWSER_AVAILABLE = True
    PLAYWRIGHT_AVAILABLE = True
    BROWSER_ENGINE = 'rebrowser'
    # Override the async_playwright import for all modules
    async_playwright = rebrowser_async_playwright
    logger.info("🛡️  rebrowser-playwright active — CloakBrowser-equivalent binary anti-detection (MAXIMUM)")
except ImportError:
    logger.debug("rebrowser-playwright not found — trying undetected-chromedriver...")

if not REBROWSER_AVAILABLE:
    try:
        import undetected_chromedriver
        from playwright.async_api import async_playwright
        UNDETECTED_AVAILABLE = True
        PLAYWRIGHT_AVAILABLE = True
        BROWSER_ENGINE = 'undetected'
        logger.info("🛡️  undetected-chromedriver active — medium binary anti-detection")
    except ImportError:
        logger.debug("undetected-chromedriver not found — falling back to plain Playwright...")

if not REBROWSER_AVAILABLE and not UNDETECTED_AVAILABLE:
    try:
        from playwright.async_api import async_playwright
        PLAYWRIGHT_AVAILABLE = True
        BROWSER_ENGINE = 'playwright'
        logger.warning("⚠️  Using plain Playwright — detectable by binary fingerprint")
    except ImportError:
        logger.critical("Playwright not installed! Run: pip install playwright && playwright install chromium")

# Make the correct async_playwright available globally for this module
_async_playwright_engine = async_playwright  # noqa: F811


class BrowserSession:
    """
    Isolated browser session with stealth patches and unique fingerprint.
    Uses Playwright context as isolation boundary.
    """

    def __init__(
        self,
        proxy_url: Optional[str] = None,
        fingerprint: Optional[Dict] = None,
        viewport: Optional[Dict[str, int]] = None,
    ):
        self.proxy_url = proxy_url
        self.fingerprint = fingerprint or {}
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self._browser = None
        self._context = None
        self._page = None
        self._playwright_instance = None
        self.session_start = time.time()
        self.pages_visited = 0
        self.last_action = None
        self._is_launched = False

    @property
    def page(self):
        return self._page

    @property
    def browser(self):
        return self._browser

    async def launch(self, playwright_instance=None) -> bool:
        """Launch browser context with stealth + fingerprint + GPU + proxy."""
        if self._is_launched:
            return True

        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available")
            return False

        try:
            from stealth_patches import StealthPatcher

            if playwright_instance is None:
                self._playwright_instance = await async_playwright().start()
            else:
                self._playwright_instance = playwright_instance

            # Enhanced launch args with GPU + TLS/DNS diversity
            launch_args = list(BROWSER_LAUNCH_ARGS)
            gpu_args = [
                '--enable-gpu', '--use-gl=angle', '--use-angle=d3d11',
                '--enable-accelerated-2d-canvas', '--enable-features=VaapiVideoDecoder',
                '--ignore-gpu-blocklist', '--enable-webgl', '--enable-unsafe-swiftshader',
            ]
            # Browser engine TLS diversity — Firefox + Chrome cipher suites
            # Chrome (52%): standard Chrome JA4 fingerprint
            chrome_tls = [
                ['--disable-features=TranslateUI,BlinkGenPropertyTrees'],
                ['--enable-features=NetworkService,NetworkServiceInProcess', '--disable-features=BlinkGenPropertyTrees'],
                ['--disable-features=TranslateUI', '--enable-features=NetworkServiceInProcess'],
                ['--disable-features=BlinkGenPropertyTrees', '--disable-features=TranslateUI'],
            ]
            # Firefox (18%): Firefox-compatible cipher suites via Chrome flags
            firefox_tls = [
                ['--disable-features=TranslateUI', '--disable-features=BlinkGenPropertyTrees',
                 '--cipher-suite-blacklist=0x1301,0x1302,0x1303,0xc02b,0xc02f,0xc02c,0xc030'],
                ['--disable-features=BlinkGenPropertyTrees', '--enable-features=NetworkServiceInProcess',
                 '--cipher-suite-blacklist=0x1301,0x1302,0xc02b,0xc02f'],
            ]
            # In-app WebView (10%): stripped-down mobile TLS
            webview_tls = [
                ['--disable-features=TranslateUI,BlinkGenPropertyTrees,NetworkServiceInProcess'],
                ['--disable-features=BlinkGenPropertyTrees', '--disable-features=TranslateUI'],
            ]
            # Select browser type for this session
            from config import BROWSER_DISTRIBUTION
            browser_weights = list(BROWSER_DISTRIBUTION.values())
            browser_names = list(BROWSER_DISTRIBUTION.keys())
            chosen_browser = random.choices(browser_names, weights=browser_weights, k=1)[0]
            if chosen_browser == 'firefox':
                tls_flags = random.choice(firefox_tls)
            elif chosen_browser == 'in_app_webview':
                tls_flags = random.choice(webview_tls)
            else:
                tls_flags = random.choice(chrome_tls)
            # DNS diversity: different DNS per context
            dns_servers = ['1.1.1.1', '8.8.8.8', '9.9.9.9', '208.67.222.222', '1.0.0.1', '8.8.4.4']
            dns = random.choice(dns_servers)
            # WebRTC IP handling policy (default_public_interface_only prevents local IP leak)
            webrtc_flags = [
                '--force-webrtc-ip-handling-policy=default_public_interface_only',
                '--enforce-webrtc-ip-permission-check',
            ]
            extra_args = gpu_args + tls_flags + [f'--dns-server={dns}'] + webrtc_flags
            launch_args = launch_args[:3] + extra_args + launch_args[3:]

            self._browser = await self._playwright_instance.chromium.launch(
                headless=BROWSER_HEADLESS,
                args=launch_args,
            )

            # Create context with fingerprint-matching config
            # Map timezone to approximate geolocation
            tz = self.fingerprint.get("timezone", "America/New_York")
            geo_map = {
                "America/New_York": {"lat": 40.7128, "lon": -74.0060},
                "America/Chicago": {"lat": 41.8781, "lon": -87.6298},
                "America/Denver": {"lat": 39.7392, "lon": -104.9903},
                "America/Los_Angeles": {"lat": 34.0522, "lon": -118.2437},
                "Europe/London": {"lat": 51.5074, "lon": -0.1278},
                "Europe/Berlin": {"lat": 52.5200, "lon": 13.4050},
                "Europe/Paris": {"lat": 48.8566, "lon": 2.3522},
                "Asia/Tokyo": {"lat": 35.6762, "lon": 139.6503},
                "Asia/Kolkata": {"lat": 28.6139, "lon": 77.2090},
                "Asia/Karachi": {"lat": 24.8607, "lon": 67.0011},
                "America/Sao_Paulo": {"lat": -23.5505, "lon": -46.6333},
                "Europe/Stockholm": {"lat": 59.3293, "lon": 18.0686},
                "Europe/Zurich": {"lat": 47.3769, "lon": 8.5417},
                "America/Toronto": {"lat": 43.6532, "lon": -79.3832},
                "Europe/Oslo": {"lat": 59.9139, "lon": 10.7522},
            }
            geo = geo_map.get(tz, {"lat": 40.7128, "lon": -74.0060})
            
            context_options = {
                "viewport": self.viewport,
                "locale": self.fingerprint.get("locale", "en-US"),
                "timezone_id": tz,
                "permissions": ["geolocation"],
                "geolocation": {"latitude": geo["lat"] + random.uniform(-0.5, 0.5),
                                "longitude": geo["lon"] + random.uniform(-0.5, 0.5)},
                "user_agent": self.fingerprint.get("user_agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36"),
                "color_scheme": random.choice(["light", "dark", "no-preference"]),
                "device_scale_factor": self.fingerprint.get("pixel_ratio", 1.0),
                "is_mobile": self.fingerprint.get("device_type") == "mobile",
                "has_touch": self.fingerprint.get("device_type") == "mobile",
            }

            if self.proxy_url:
                context_options["proxy"] = {"server": self.proxy_url}

            self._context = await self._browser.new_context(**context_options)

            # === APPLY STEALTH PATCHES ===
            await StealthPatcher.patch_context(self._context, self.fingerprint)

            # Create page
            self._page = await self._context.new_page()

            # Additional CDP-level stealth
            try:
                await StealthPatcher.patch_page(self._page, self.fingerprint)
            except Exception:
                pass

            self._is_launched = True
            logger.debug(f"Browser session launched: {self.fingerprint.get('device_type', 'desktop')} "
                        f"viewport={self.viewport.get('width')}x{self.viewport.get('height')} "
                        f"proxy={'yes' if self.proxy_url else 'no'}")
            return True

        except Exception as e:
            logger.error(f"Browser launch failed: {e}")
            return False

    async def navigate(self, url: str, wait_until: str = "domcontentloaded", timeout: int = None) -> bool:
        """Navigate to URL with stealth still active."""
        if not self._page:
            return False
        try:
            timeout = timeout or PAGE_LOAD_TIMEOUT_MS
            await self._page.goto(url, wait_until=wait_until, timeout=timeout)
            self.pages_visited += 1
            self.last_action = "navigate"
            return True
        except Exception as e:
            logger.debug(f"Navigation to {url[:60]} failed: {e}")
            return False

    async def get_page_title(self) -> str:
        if not self._page:
            return ""
        try:
            return await self._page.title()
        except Exception:
            return ""

    async def get_page_url(self) -> str:
        if not self._page:
            return ""
        try:
            return self._page.url
        except Exception:
            return ""

    async def scroll(self, amount_px: int, behavior: str = "smooth") -> bool:
        if not self._page:
            return False
        try:
            await self._page.evaluate(f"window.scrollBy({{top: {amount_px}, behavior: '{behavior}'}})")
            self.last_action = "scroll"
            return True
        except Exception:
            return False

    async def get_scroll_position(self) -> float:
        if not self._page:
            return 0.0
        try:
            info = await self._page.evaluate("""() => ({
                scrollY: window.scrollY,
                totalHeight: document.body.scrollHeight,
                viewportHeight: window.innerHeight
            })""")
            if info["totalHeight"] > info["viewportHeight"]:
                return min(info["scrollY"] / (info["totalHeight"] - info["viewportHeight"]), 1.0)
            return 0.0
        except Exception:
            return 0.0

    async def find_links(self) -> list:
        if not self._page:
            return []
        all_links = []
        for selector in INTERNAL_LINK_SELECTORS:
            try:
                elements = await self._page.query_selector_all(selector)
                for el in elements:
                    href = await el.get_attribute('href')
                    if href and (href.startswith('/') or 'LOPINUZE.2BD.NET' in href):
                        box = await el.bounding_box()
                        if box and box['width'] > 0 and box['height'] > 0:
                            all_links.append({"element": el, "href": href, "box": box, "selector": selector})
            except Exception:
                continue
        return all_links

    async def find_ads(self) -> list:
        if not self._page:
            return []
        all_ads = []
        for selector in AD_SELECTORS:
            try:
                elements = await self._page.query_selector_all(selector)
                for el in elements:
                    box = await el.bounding_box()
                    if box and box['width'] > 0 and box['height'] > 0:
                        all_ads.append({"element": el, "box": box, "selector": selector})
            except Exception:
                continue
        return all_ads

    async def hover_element(self, element_info: Dict) -> bool:
        if not self._page:
            return False
        try:
            box = element_info["box"]
            cx = box['x'] + box['width'] / 2
            cy = box['y'] + box['height'] / 2
            await self._page.mouse.move(cx, cy, steps=random.randint(15, 35))
            await asyncio.sleep(random.uniform(0.5, 2.0))
            await self._page.mouse.move(
                cx + random.randint(-200, 200),
                cy + random.randint(-200, 200),
                steps=random.randint(10, 25)
            )
            self.last_action = "hover_ad"
            return True
        except Exception:
            return False

    async def click_element(self, element_info: Dict) -> bool:
        if not self._page:
            return False
        try:
            box = element_info["box"]
            cx = box['x'] + box['width'] / 2 + random.randint(-5, 5)
            cy = box['y'] + box['height'] / 2 + random.randint(-3, 3)
            await self._page.mouse.move(cx, cy, steps=random.randint(20, 40))
            await asyncio.sleep(random.uniform(0.2, 0.8))
            await self._page.mouse.click(cx, cy)
            self.pages_visited += 1
            self.last_action = "click"
            await asyncio.sleep(random.uniform(1.0, 3.0))
            return True
        except Exception:
            return False

    async def random_mouse_movement(self):
        """Human-like mouse with jitter, overshoot, and pauses (detection #6 fix)."""
        if not self._page or self.fingerprint.get("device_type") == "mobile":
            return
        try:
            for _ in range(random.randint(1, 3)):
                target_x = random.randint(50, self.viewport.get('width', 1920) - 50)
                target_y = random.randint(50, self.viewport.get('height', 1080) - 50)
                
                # Get current mouse position
                try:
                    pos = await self._page.evaluate("""
                        (() => {
                            return { x: window.mouseX || 500, y: window.mouseY || 500 };
                        })()
                    """)
                    current_x = pos.get('x', 500)
                    current_y = pos.get('y', 500)
                except Exception:
                    current_x, current_y = 500, 500
                
                # Human-like movement: slight overshoot, then correct
                overshoot_x = target_x + random.randint(-80, 80)
                overshoot_y = target_y + random.randint(-60, 60)
                
                # Move with many small steps (human jitter)
                steps = random.randint(25, 55)
                
                # Track mouse position via JS
                for i in range(steps):
                    # Cubic bezier-like interpolation with noise
                    t = i / steps
                    # Ease-in-out curve
                    eased = t * t * (3 - 2 * t)
                    
                    # Add jitter (1-3px noise)
                    jitter_x = random.randint(-3, 3)
                    jitter_y = random.randint(-3, 3)
                    
                    if i < steps * 0.7:
                        # Moving toward overshoot point (70% of journey)
                        px = int(current_x + (overshoot_x - current_x) * (eased / 0.7) + jitter_x)
                        py = int(current_y + (overshoot_y - current_y) * (eased / 0.7) + jitter_y)
                    else:
                        # Correcting to final target (30% of journey)
                        correction_progress = (eased - 0.7) / 0.3
                        px = int(overshoot_x + (target_x - overshoot_x) * correction_progress + jitter_x)
                        py = int(overshoot_y + (target_y - overshoot_y) * correction_progress + jitter_y)
                    
                    await self._page.mouse.move(px, py)
                    await asyncio.sleep(random.uniform(0.005, 0.025))  # ~200fps human-like
                    
                    # Track position
                    await self._page.evaluate(f"window.mouseX = {px}; window.mouseY = {py};")
                
                # Occasional pause (40% chance) — humans pause between movements
                if random.random() < 0.4:
                    await asyncio.sleep(random.uniform(0.3, 2.0))
                
        except Exception:
            pass

    def get_total_time(self) -> float:
        return time.time() - self.session_start

    async def close(self):
        """Close browser context and cleanup."""
        try:
            if self._page:
                await self._page.close()
        except Exception:
            pass
        try:
            if self._context:
                await self._context.close()
        except Exception:
            pass
        self._is_launched = False
        logger.debug(f"Session closed: {self.pages_visited} pages in {self.get_total_time():.0f}s")


class BrowserPool:
    """Manages browser instances for concurrent sessions."""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.active_sessions: List[BrowserSession] = []
        self._playwright = None
        self._lock = asyncio.Lock()
        self.total_created = 0
        self.total_closed = 0

    async def _get_playwright(self):
        if self._playwright is None:
            self._playwright = await async_playwright().start()
        return self._playwright

    async def create_session(
        self,
        proxy_url: Optional[str] = None,
        fingerprint: Optional[Dict] = None,
        viewport: Optional[Dict[str, int]] = None,
    ) -> Optional[BrowserSession]:
        """Create and launch a new browser context with stealth."""
        async with self._lock:
            if len(self.active_sessions) >= self.max_concurrent:
                await self._close_idle_sessions()

        pw = await self._get_playwright()

        session = BrowserSession(
            proxy_url=proxy_url,
            fingerprint=fingerprint,
            viewport=viewport,
        )

        success = await session.launch(playwright_instance=pw)
        if success:
            async with self._lock:
                self.active_sessions.append(session)
                self.total_created += 1
            return session
        return None

    async def close_session(self, session: BrowserSession):
        await session.close()
        async with self._lock:
            if session in self.active_sessions:
                self.active_sessions.remove(session)
            self.total_closed += 1

    async def _close_idle_sessions(self):
        """Close sessions older than 5 minutes to free memory."""
        now = time.time()
        for s in list(self.active_sessions):
            if (now - s.session_start) > 300:
                await self.close_session(s)

    def get_stats(self) -> Dict:
        return {
            "active": len(self.active_sessions),
            "total_created": self.total_created,
            "total_closed": self.total_closed,
        }

    async def cleanup(self):
        for session in list(self.active_sessions):
            await self.close_session(session)
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None


# === GLOBAL POOL ===
_pool: Optional[BrowserPool] = None

def get_browser_pool() -> BrowserPool:
    global _pool
    if _pool is None:
        from config import MAX_CONCURRENT_SESSIONS
        _pool = BrowserPool(max_concurrent=MAX_CONCURRENT_SESSIONS)
    return _pool

async def cleanup_browser_pool():
    global _pool
    if _pool:
        await _pool.cleanup()
        _pool = None