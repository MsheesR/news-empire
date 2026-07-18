#!/usr/bin/env python3
"""
Session Engine V3.1 — Human Behavior Mimicry
=============================================
Orchestrates 8 distinct human session types with realistic
power-law duration, content-aware scrolling, dynamic CTR,
failed request simulation, mobile touch events, and
ad blocker simulation.

Session Types (weighted by SESSION_TYPES in config):
  1. bouncer (25%) — 3-8s visit, no interaction
  2. scanner (20%) — browses headlines, 10-25s
  3. searcher (15%) — Google→article→leave, 20-60s
  4. reader (15%) — reads article fully, 45-120s
  5. deep_diver (8%) — multiple articles, 2-10min
  6. social_click (7%) — Facebook/Twitter→article, 10-45s
  7. direct_type_in (5%) — types URL, 15-50s
  8. ghost (5%) — 0.5-3s instant bounce

Key V3.1 improvements:
- Each session type has different scroll/click/hover/ad rates
- CTR varies by section, time-of-day, and device
- Power-law session duration (not uniform random)
- 3% of navigations simulate failures (timeout/refused/DNS)
- 35% of sessions simulate ad blocker
- 15% visit external sites for browsing trails
- Mobile sessions use touch events instead of mouse
"""

import asyncio
import random
import time
import logging
from typing import Dict, Any, Optional, Tuple

from config import (
    SITE_URL, SESSION_TYPES, SECTION_AD_RATES, FALLBACK_AD_RATES,
    HOURLY_CTR_MODIFIER, DEVICE_CTR_MODIFIER, SCROLL_PROFILES, FALLBACK_SCROLL,
    POWER_LAW_DURATION_BUCKETS, FAILED_REQUEST_CHANCE, AD_BLOCKER_PROBABILITY,
    EXTERNAL_SITES, EXTERNAL_VISIT_CHANCE, OFF_HOURS_GHOST_MULTIPLIER, OFF_HOURS,
    REFERRAL_SOURCES, RETURNING_VISITOR_PROBABILITY,
)

logger = logging.getLogger('session_engine')


class SessionEngine:
    """Orchestrates full session lifecycle with human behavior patterns."""

    def __init__(self):
        self._geo = None
        self._fingerprint_factory = None
        self._rotator = None
        self._vpn = None
        self._survival = None
        self._revenue_opt = None
        self._behavior = None
        self._browser_pool = None
        self._ads = None

    async def _init_subsystems(self):
        if self._geo is None:
            from geo_utils import get_geo_client; self._geo = get_geo_client()
        if self._fingerprint_factory is None:
            from fingerprint_manager import get_fingerprint_factory; self._fingerprint_factory = get_fingerprint_factory()
        if self._rotator is None:
            from smart_rotator import get_rotator; self._rotator = await get_rotator()
        if self._vpn is None:
            from vpn_tunnel import get_vpn_tunnel; self._vpn = await get_vpn_tunnel()
        if self._survival is None:
            from survival_integration import get_survival_integrator; self._survival = await get_survival_integrator()
        if self._revenue_opt is None:
            from revenue_optimizer import get_revenue_optimizer; self._revenue_opt = await get_revenue_optimizer()
        if self._behavior is None:
            from ai_behavior import get_behavior_engine; self._behavior = get_behavior_engine()
        if self._browser_pool is None:
            from browser_manager import get_browser_pool; self._browser_pool = get_browser_pool()
        if self._ads is None:
            from ads_engine import get_ads_engine; self._ads = get_ads_engine()

    def _pick_session_type(self) -> Dict:
        """Pick a random session type using weighted distribution."""
        types = list(SESSION_TYPES.values())
        weights = [t["weight"] for t in types]
        total = sum(weights)
        r = random.random() * total
        cumulative = 0
        for t in types:
            cumulative += t["weight"]
            if r <= cumulative:
                return t.copy()
        return types[0].copy()

    def _get_power_law_duration(self, session_type: Dict) -> float:
        """Get session duration using LOG-NORMAL distribution (detection #10 fix).
        
        Uses Box-Muller transform for true log-normal sampling without numpy.
        Produces SMOOTH unbucketed values — no histogram edges for bot detectors.
        
        Median mapped to session type's stay_ms_range for realistic durations:
        - Ghost: median 1.2s → most sessions 0.5-3s
        - Bouncer: median 5s → most sessions 2-8s
        - Scanner: median 17s → most sessions 10-25s
        - Reader: median 80s → most sessions 45-120s
        - Deep diver: median 360s → most sessions 120-600s
        """
        import math
        # Get median from session type configuration (in seconds)
        stay_range = session_type.get("stay_ms_range", (10000, 25000))
        median_seconds = ((stay_range[0] + stay_range[1]) / 2) / 1000
        
        # Box-Muller transform: two uniforms → standard normal
        u1 = random.random()
        u2 = random.random()
        # Guard against log(0)
        z = math.sqrt(-2.0 * math.log(max(u1, 0.0001))) * math.cos(2.0 * math.pi * u2)
        
        # Log-normal: median * exp(sigma * z)
        # sigma=0.6 gives natural spread (95% within 0.3x-3x of median)
        sigma = 0.55 + random.uniform(-0.05, 0.05)  # Slight variation per session
        
        duration_seconds = median_seconds * math.exp(sigma * z)
        
        # Clamp to realistic bounds (0.5s minimum, 15min maximum)
        duration_ms = int(max(500, min(900000, duration_seconds * 1000)))
        
        return duration_ms

    def _get_dynamic_ctr(self, section_slug: str, device_type: str, hour: int) -> Dict:
        """Get dynamic click/hover rates for a section/time/device combination."""
        base = SECTION_AD_RATES.get(section_slug, FALLBACK_AD_RATES)
        hourly_mod = HOURLY_CTR_MODIFIER.get(hour, 0.8)
        device_mod = DEVICE_CTR_MODIFIER.get(device_type, 0.75)
        return {
            "hover": min(base["hover"] * hourly_mod * device_mod, 0.8),
            "click": min(base["click"] * hourly_mod * device_mod, 0.06),
        }

    def _get_scroll_profile(self, page_type: str) -> Dict:
        """Get scroll parameters for a given page type."""
        return SCROLL_PROFILES.get(page_type, FALLBACK_SCROLL)

    async def _simulate_failed_request(self, page) -> bool:
        """Simulate failed request with realistic recovery behavior."""
        if random.random() > FAILED_REQUEST_CHANCE:
            return True  # Success

        fail_type = random.random()
        await asyncio.sleep(random.uniform(0.5, 2.0))

        if fail_type < 0.5:  # Timeout
            await asyncio.sleep(random.uniform(1.0, 3.0))
            return True  # Retry succeeds
        elif fail_type < 0.85:  # Connection refused
            return False  # Page "fails to load"
        else:  # DNS failure
            return False

    async def _simulate_ad_blocker(self, page):
        """Inject ad blocker detection evasion if session has ad blocker."""
        if random.random() < AD_BLOCKER_PROBABILITY:
            try:
                # Remove some ad elements to simulate uBlock Origin
                await page.evaluate("""
                    (function() {
                        var ads = document.querySelectorAll('[id*="ad-"], [class*="ad-"], .ad-container, .ad-slot');
                        ads.forEach(function(el) {
                            el.style.display = 'none';
                            el.style.height = '0px';
                        });
                    })();
                """)
                return True
            except Exception:
                pass
        return False

    async def _mobile_touch_events(self, page, x: int, y: int):
        """Generate touch events instead of mouse events for mobile."""
        await page.evaluate(f"""
            (function() {{
                var target = document.elementFromPoint({x}, {y});
                if (!target) return;
                target.dispatchEvent(new TouchEvent('touchstart', {{
                    touches: [{{ clientX: {x}, clientY: {y} }}],
                    bubbles: true
                }}));
                target.dispatchEvent(new TouchEvent('touchend', {{
                    touches: [],
                    bubbles: true
                }}));
                target.click();
            }})();
        """)

    async def run_session(self, session_id: str) -> Dict[str, Any]:
        """Execute one human-mimicking browsing session."""
        await self._init_subsystems()

        result = {'session_id': session_id, 'success': False, 'pages_visited': 0,
                  'ad_hovers': 0, 'ad_clicks': 0, 'banner_impressions': 0,
                  'banner_clicks': 0, 'native_clicks': 0, 'time_spent': 0.0,
                  'proxy_tier': 'unknown', 'network_used': 'hilltopads',
                  'section_visited': 'unknown', 'device_type': 'desktop',
                  'source_type': 'direct', 'session_type': 'bouncer', 'error': None}

        session_start = time.time()
        proxy_url = None
        session = None

        try:
            # === STEP 1: Survival check ===
            if self._survival:
                allowed, throttle = await self._survival.pre_session_check()
                if not allowed:
                    result['error'] = 'survival_rejected'
                    return result

            # === STEP 2: Pick session type ===
            session_type = self._pick_session_type()
            result['session_type'] = list(SESSION_TYPES.keys())[list(SESSION_TYPES.values()).index(session_type)] if session_type in SESSION_TYPES.values() else 'bouncer'

            # Ghost sessions are ultra-light — no proxy needed
            if session_type.get("ad_hover_probability", 0) == 0 and session_type.get("ad_click_probability", 0) == 0:
                session_value = 'background'
            else:
                section_tier = random.choice([1, 2])
                session_value = 'high_value' if section_tier == 1 else 'browse'

            # === STEP 3: Determine session purpose ===
            # Revenue sessions = any session with ad_hover_probability >= 0.3 or ad_click_probability >= 0.01
            if session_type.get("ad_click_probability", 0) >= 0.01:
                session_purpose = 'revenue'
            elif session_type.get("ad_hover_probability", 0) >= 0.3:
                session_purpose = 'revenue'
            else:
                session_purpose = 'impression'

            result['session_purpose'] = session_purpose

            # === STEP 4: Proxy via TrafficRouter (purpose-aware) ===
            if session_type.get("stay_ms_range", (0, 0))[1] > 3000:
                from traffic_router import get_router
                router = await get_router()
                proxy_url = await router.get_proxy_for_session(
                    session_purpose=session_purpose,
                    session_value=session_value
                )
                if not proxy_url:
                    result['error'] = 'no_proxy'
                    return result
                result['proxy_source'] = 'webshare' if '@' in (proxy_url or '') else 'mullvad' if 'socks5' in (proxy_url or '') else 'scraped'
                result['proxy_url'] = proxy_url

            # === STEP 5: Geo + Fingerprint + Country Behavior ===
            geo_config = await self._geo.get_browser_geo_config(proxy_url) if proxy_url else {'timezone': 'America/New_York', 'locale': 'en-US', 'language': 'en', 'country': 'US'}
            
            # Apply country-based behavior modifiers
            from config import COUNTRY_BEHAVIOR, FALLBACK_COUNTRY_BEHAVIOR
            country_code = geo_config.get('country', 'US')
            country_behavior = COUNTRY_BEHAVIOR.get(country_code, FALLBACK_COUNTRY_BEHAVIOR)
            
            # Adjust device distribution for this country
            device_bias = country_behavior.get('device_bias', 'balanced')
            if device_bias == 'mobile_heavy':
                weighted = random.random()
                if weighted < 0.65: device_type = 'mobile'
                elif weighted < 0.85: device_type = 'desktop'
                else: device_type = 'tablet'
            elif device_bias == 'desktop_heavy':
                weighted = random.random()
                if weighted < 0.55: device_type = 'desktop'
                elif weighted < 0.90: device_type = 'mobile'
                else: device_type = 'tablet'
            else:
                weighted = random.random()
                if weighted < 0.55: device_type = 'mobile'
                elif weighted < 0.90: device_type = 'desktop'
                else: device_type = 'tablet'
            
            # Generate fingerprint with country-aware device type
            fingerprint = self._fingerprint_factory.generate(geo_config=geo_config)
            fp_dict = fingerprint.to_dict()
            fp_dict['device_type'] = device_type
            fp_dict['timezone'] = geo_config.get('timezone', 'America/New_York')
            fp_dict['locale'] = geo_config.get('locale', 'en-US')
            result['device_type'] = device_type

            # === STEP 6: Network ===
            network = self._revenue_opt.assign_network_for_session(session_value) if session_value != 'background' else None
            result['network_used'] = network.name if network else 'none'

            # === STEP 7: Browser ===
            viewport = {'width': fp_dict.get('screen_width', 1920), 'height': fp_dict.get('screen_height', 1080)}
            session = await self._browser_pool.create_session(proxy_url=proxy_url, fingerprint=fp_dict, viewport=viewport)
            if not session:
                if proxy_url: await self._rotator.release_proxy(proxy_url, success=False)
                result['error'] = 'browser_failed'
                return result

            # === STEP 8: Ad blocker simulation ===
            has_ad_blocker = await self._simulate_ad_blocker(session.page)

            # === STEP 9: Section & Referrer ===
            from sections import get_random_section, get_section_url, get_latest_article_url
            section = get_random_section()
            result['section_visited'] = section["slug"]

            from farm import ReferralEngine
            ref_bias = session_type.get("referrer_bias", {"direct": 1.0})
            ref_url, source_type = ReferralEngine.get_referrer(section["slug"])
            result['source_type'] = source_type

            if ref_url and session.page:
                try: await session.page.set_extra_http_headers({"Referer": ref_url})
                except: pass

            # === STEP 10: Navigate (with possible failures) ===
            path = session_type.get("path", ["article_direct"])
            scroll_profile = ("article" if "article" in str(path) else "homepage" if "homepage" in str(path) else "section_index")
            sp = self._get_scroll_profile(scroll_profile)
            steps = random.randint(sp["steps"][0], sp["steps"][1])

            # Navigate to first page — with freshness bias for article paths
            article_url = get_latest_article_url(section)  # 75% bias toward newer articles
            section_url = f"{SITE_URL}{get_section_url(section)}"
            
            if "homepage" in str(path):
                first_url = SITE_URL
            elif "article" in str(path):
                first_url = f"{SITE_URL}{article_url}"  # Visit actual article, not section index
            else:
                first_url = section_url

            nav_ok = await self._simulate_failed_request(session.page)
            if nav_ok:
                ok = await session.navigate(first_url)
                if not ok:
                    result['pages_visited'] = 0
                    result['time_spent'] = time.time() - session_start
                    result['error'] = 'nav_failed'
                    await session.close()
                    if proxy_url: await self._rotator.release_proxy(proxy_url, success=False)
                    return result
                result['pages_visited'] += 1
            else:
                result['pages_visited'] = 0
                result['time_spent'] = random.uniform(1.0, 5.0)
                await session.close()
                if proxy_url: await self._rotator.release_proxy(proxy_url, success=True)
                return result  # "Failed request" session — realistic

            # === STEP 11: Scroll with touch/mouse ===
            for step in range(steps):
                px = random.randint(sp["px_per_step"][0], sp["px_per_step"][1])

                if device_type == "mobile":
                    # Touch scroll + tap
                    vw = viewport.get('width', 375)
                    vh = viewport.get('height', 812)
                    tx = random.randint(50, vw - 50)
                    ty = random.randint(vh // 2, vh - 100)
                    await self._mobile_touch_events(session.page, tx, ty)
                    await session.scroll(px, "smooth" if random.random() < 0.7 else "auto")
                    await asyncio.sleep(random.uniform(0.2, 1.0))
                else:
                    await session.scroll(px, "smooth" if random.random() < 0.7 else "auto")
                    await asyncio.sleep(random.uniform(0.2, 1.5))
                    if step % 3 == 0:
                        await session.random_mouse_movement()

            # === STEP 12: Ad interaction (dynamic CTR) ===
            if not has_ad_blocker and session_type.get("ad_hover_probability", 0) > 0:
                now = time.localtime()
                ctr = self._get_dynamic_ctr(section["slug"], device_type, now.tm_hour)
                ads_found = await session.find_ads()

                if ads_found:
                    max_h = 2 if device_type == "mobile" else 4
                    for ad in ads_found[:max_h]:
                        if random.random() < ctr["hover"]:
                            await session.hover_element(ad)
                            await asyncio.sleep(random.uniform(0.3, 2.0))
                            result['ad_hovers'] += 1
                            result['banner_impressions'] += 1

                    # Ad click (dynamic rate)
                    if random.random() < ctr["click"] and ads_found:
                        await asyncio.sleep(random.uniform(2.0, 8.0))
                        target = random.choice(ads_found)
                        try:
                            box = target["box"]
                            cx = box['x'] + box['width'] / 2 + random.randint(-5, 5)
                            cy = box['y'] + box['height'] / 2 + random.randint(-3, 3)
                            if device_type == "mobile":
                                await self._mobile_touch_events(session.page, int(cx), int(cy))
                            else:
                                await session.page.mouse.move(cx, cy, steps=random.randint(20, 40))
                                await asyncio.sleep(random.uniform(0.2, 0.8))
                                await session.page.mouse.click(cx, cy)
                            result['ad_clicks'] += 1
                            result['banner_clicks'] += 1
                            logger.info(f"[{session_id}] 💰 AD CLICKED (ctr={ctr['click']:.3f})")
                            await asyncio.sleep(random.uniform(2.0, 5.0))
                        except Exception:
                            pass

            # === STEP 13: External browsing trail ===
            if random.random() < EXTERNAL_VISIT_CHANCE:
                ext_url = random.choice(EXTERNAL_SITES)
                try:
                    await session.navigate(ext_url)
                    await asyncio.sleep(random.uniform(1.0, 5.0))
                    await session.navigate(f"{SITE_URL}{get_section_url(section)}")
                    result['pages_visited'] += 1
                except Exception:
                    pass

            # === STEP 14: Second page (readers/deep divers) ===
            if result['pages_visited'] >= 1 and random.random() < 0.25:
                new_section = get_random_section()
                await session.navigate(f"{SITE_URL}{get_section_url(new_section)}")
                result['pages_visited'] += 1
                for _ in range(random.randint(2, 5)):
                    await session.scroll(random.randint(200, 600))
                    await asyncio.sleep(random.uniform(0.3, 1.0))

            # === STEP 15: Popunder handling (detection #2-3 fix) ===
            # Only fire popunders for session types with scroll (not ghost/bouncer who don't engage)
            if steps >= 2:  # Session scrolled at least 2 steps
                try:
                    from popunder_handler import handle_popunder_window
                    await handle_popunder_window(session.page, result['session_type'])
                except Exception:
                    pass

            # === STEP 16: Post-popunder browse (detection #11 fix) ===
            if random.random() < 0.15:
                try:
                    from popunder_handler import simulate_post_popunder_activity
                    await simulate_post_popunder_activity(session.page)
                except Exception:
                    pass

            # === STEP 17: Dwell time (continuous distribution — detection #10 fix) ===
            dwell_ms = self._get_power_law_duration(session_type)
            elapsed = (time.time() - session_start) * 1000
            remaining = max(0, dwell_ms - elapsed)
            await asyncio.sleep(remaining / 1000)

            result['success'] = True
            result['time_spent'] = time.time() - session_start

        except Exception as e:
            logger.error(f"[{session_id}] Error: {e}")
            result['error'] = str(e)[:100]
            result['time_spent'] = time.time() - session_start
        finally:
            if session:
                try: await self._browser_pool.close_session(session)
                except: pass
            if proxy_url:
                await self._rotator.release_proxy(proxy_url, success=result['success'])
            if self._survival and result['success']:
                await self._survival.post_session_feedback(result)
        return result


_engine: Optional[SessionEngine] = None

def get_session_engine() -> SessionEngine:
    global _engine
    if _engine is None:
        _engine = SessionEngine()
    return _engine