#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LOPINUZE AD FARM V3 — MAXIMUM SECURITY                   ║
║             80-Worker Concurrent Traffic Engine With Self-Healing           ║
║                                                                            ║
║  V3 Stack:                                                                 ║
║  - Playwright Chromium (GPU-accelerated, RTX 3050)                         ║
║  - CDP-Level Stealth (15 detection vectors neutralized)                    ║
║  - Per-Session Fingerprint (coherent CPU/GPU/RAM/OS spoofing)              ║
║  - 30+ Source Proxy Aggregation (4-stage verification)                     ║
║  - Tier-Aware Proxy Rotation (S/A/B/C tiers with cooldowns)                ║
║  - WireGuard VPN Tunnel (double-hop protection)                            ║
║  - DeepSeek AI Behavior (real-time human mimicry)                          ║
║  - Multi-Ad-Network (HilltopAds + PopAds + Adsterra + AdMaven)            ║
║  - Survival Auto-Regulation (quality monitoring + auto-throttle + switch)  ║
║  - Real-Time Web Dashboard (Flask, localhost:5000)                         ║
║                                                                            ║
║  V3 Architecture:                                                          ║
║  farm.py → session_engine.py → {browser_manager, fingerprint, stealth}    ║
║         → survival_integration.py → survival_engine.py                     ║
║         → revenue_optimizer.py → multi-network routing                     ║
║         → proxy_manager.py → {proxy_filter, smart_rotator}                 ║
║         → vpn_tunnel.py → WireGuard                                        ║
║         → dashboard.py → Web UI                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import random
import time
import signal
import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    SITE_URL, SITE_NAME,
    MIN_VISIT_DELAY, MAX_VISIT_DELAY,
    HUMAN_HOURS_START, HUMAN_HOURS_END,
    WEEKEND_TRAFFIC_MULTIPLIER,
    MAX_CONCURRENT_SESSIONS,
    REFERRAL_SOURCES,
    AD_CLICK_PROBABILITY,
    DASHBOARD_HOST, DASHBOARD_PORT, DASHBOARD_ENABLED,
    LOG_LEVEL, LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT,
    validate_config,
)
from sections import get_random_section, get_section_count, get_section_url

# ============================ LOGGING SETUP ============================
def setup_logging():
    log_dir = Path(__file__).parent
    log_path = log_dir / LOG_FILE
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    for lib in ['aiohttp', 'urllib3', 'asyncio', 'playwright']:
        logging.getLogger(lib).setLevel(logging.WARNING)

logger = logging.getLogger('farm')


# ============================ REFERRAL ENGINE ============================
class ReferralEngine:
    """Generates realistic referrer URLs per session.
    V4.2: Procedural query generation (detection #5 fix) — 1,000+ unique queries
    with typos, long-tail phrases, misspellings, and real-world search patterns.
    """
    
    # Base keywords per section (used to generate procedural queries)
    SECTION_KEYWORDS = {
        "tech": ["technology", "tech", "gadgets", "software", "hardware", "innovation", "startup", "silicon valley", "apple", "microsoft", "google", "android", "iphone"],
        "ai": ["artificial intelligence", "machine learning", "deep learning", "neural network", "chatgpt", "gpt", "openai", "ai tools", "ai news"],
        "gaming": ["video games", "playstation", "xbox", "nintendo", "pc gaming", "esports", "fortnite", "minecraft", "gta", "call of duty"],
        "finance": ["stock market", "investing", "cryptocurrency", "bitcoin", "ethereum", "trading", "wall street", "nasdaq", "dow jones", "interest rates", "inflation"],
        "crypto": ["crypto", "bitcoin price", "ethereum news", "defi", "nft", "blockchain", "web3", "metamask", "binance", "coinbase", "solana", "cardano"],
        "world-news": ["world news", "breaking news", "international", "politics", "election", "president", "war", "peace", "treaty", "united nations"],
        "health": ["health", "wellness", "diet", "exercise", "covid", "vaccine", "mental health", "nutrition", "sleep", "meditation", "yoga", "fitness"],
        "science": ["science", "research", "discovery", "nasa", "space", "physics", "chemistry", "biology", "climate change", "environment", "ocean", "quantum"],
        "climate": ["climate change", "global warming", "carbon emissions", "renewable energy", "solar power", "electric vehicles", "tesla", "environment", "sustainability"],
        "space": ["space", "nasa", "spacex", "mars", "moon", "astronaut", "telescope", "jwst", "galaxy", "black hole", "satellite", "rocket launch"],
    }
    
    # Query modifiers that create long-tail, realistic searches
    QUERY_MODIFIERS = [
        "today", "this week", "2024", "2025", "2026", "latest", "breaking",
        "news", "update", "analysis", "explained", "guide", "tutorial",
        "reddit", "forum", "review", "vs", "comparison", "price prediction",
        "forecast", "statistics", "trends", "graph", "chart", "data",
        "how to", "what is", "why is", "when will", "will",
    ]
    
    # Typos and variations (15% of queries have small typos — realistic)
    TYPOS = {
        "technology": "technlogy", "artificial": "artifical", "intelligence": "inteligence",
        "cryptocurrency": "cryptocurrncy", "blockchain": "blockchian",
        "breaking": "braking", "analysis": "analisys", "forecast": "forcast",
        "environment": "enviroment", "sustainability": "sustanability",
    }
    
    SOCIAL_REFERRERS = [
        "https://www.facebook.com/", "https://m.facebook.com/",
        "https://twitter.com/", "https://x.com/",
        "https://www.reddit.com/", "https://old.reddit.com/",
        "https://www.linkedin.com/", "https://news.ycombinator.com/",
        "https://www.instagram.com/", "https://www.tiktok.com/",
        "https://t.co/", "https://www.quora.com/",
        "https://www.pinterest.com/", "https://discord.com/",
    ]
    
    NEWS_AGGREGATORS = [
        "https://flipboard.com/", "https://feedly.com/",
        "https://news.google.com/", "https://apple.news/", "https://pocket.co/",
        "https://www.inoreader.com/", "https://newsblur.com/",
    ]
    
    REFERRAL_SITES = [
        "https://drudgereport.com/", "https://realclearpolitics.com/",
        "https://slashdot.org/", "https://techmeme.com/",
        "https://medium.com/", "https://www.blogger.com/",
        "https://digg.com/", "https://marginalrevolution.com/",
    ]
    
    @classmethod
    def _generate_search_query(cls, section_slug: str) -> str:
        """Generate a unique, realistic Google search query procedurally."""
        keywords = cls.SECTION_KEYWORDS.get(section_slug, cls.SECTION_KEYWORDS["world-news"])
        
        # Pick 2-4 random keywords
        num_kw = random.randint(2, min(4, len(keywords)))
        query_words = random.sample(keywords, num_kw)
        
        # Add modifier (70% chance)
        if random.random() < 0.7:
            modifier = random.choice(cls.QUERY_MODIFIERS)
            query_words.append(modifier)
        
        # Shuffle word order (real searches aren't always logical)
        random.shuffle(query_words)
        
        # Add typo (15% chance)
        for i, word in enumerate(query_words):
            if word.lower() in cls.TYPOS and random.random() < 0.15:
                query_words[i] = cls.TYPOS[word.lower()]
        
        # Randomly add site: filter (5% chance — power users)
        if random.random() < 0.05:
            domain = random.choice(["reddit.com", "wikipedia.org", "medium.com", "youtube.com"])
            query_words.append(f"site:{domain}")
        
        # Randomly add quotes around a phrase (10% chance)
        if random.random() < 0.1 and len(query_words) >= 2:
            mid = len(query_words) // 2
            query_words.insert(mid, '"')
            query_words.insert(mid + 2, '"')
        
        return " ".join(query_words)
    
    @classmethod
    def get_referrer(cls, section_slug: str) -> Tuple[str, Optional[str]]:
        r = random.random()
        cumulative = 0.0
        source = "direct"
        for src, weight in REFERRAL_SOURCES.items():
            cumulative += weight
            if r <= cumulative:
                source = src
                break
        
        if source == "google_search":
            query = cls._generate_search_query(section_slug)
            # Handle quotes properly
            encoded = query.replace(' ', '+').replace('"', '%22')
            return f"https://www.google.com/search?q={encoded}", "google_search"
        elif source == "social_media":
            return random.choice(cls.SOCIAL_REFERRERS), "social_media"
        elif source == "news_aggregator":
            return random.choice(cls.NEWS_AGGREGATORS), "news_aggregator"
        elif source == "referral_link":
            return random.choice(cls.REFERRAL_SITES), "referral_link"
        else:
            return None, "direct"


# ============================ REVENUE TRACKER ============================
class RevenueTracker:
    POPUNDER_CPM = 3.50
    BANNER_IMPRESSION_CPM = 0.80
    BANNER_CLICK_CPC = 0.05
    NATIVE_CLICK_CPC = 0.08
    
    def __init__(self):
        self.total_popunders = 0
        self.total_banner_impressions = 0
        self.total_banner_clicks = 0
        self.total_native_clicks = 0
        self.total_sessions = 0
        self.lock = asyncio.Lock()
    
    async def record_session(self, popunders=1, banner_impressions=0, banner_clicks=0, native_clicks=0):
        async with self.lock:
            self.total_sessions += 1
            self.total_popunders += popunders
            self.total_banner_impressions += banner_impressions
            self.total_banner_clicks += banner_clicks
            self.total_native_clicks += native_clicks
    
    def get_earnings(self) -> Dict:
        popunder_rev = (self.total_popunders / 1000.0) * self.POPUNDER_CPM
        banner_imp_rev = (self.total_banner_impressions / 1000.0) * self.BANNER_IMPRESSION_CPM
        banner_click_rev = self.total_banner_clicks * self.BANNER_CLICK_CPC
        native_click_rev = self.total_native_clicks * self.NATIVE_CLICK_CPC
        total = popunder_rev + banner_imp_rev + banner_click_rev + native_click_rev
        return {
            "popunder": popunder_rev, "banner_impressions": banner_imp_rev,
            "banner_clicks": banner_click_rev, "native_clicks": native_click_rev,
            "total": total, "sessions": self.total_sessions,
            "revenue_per_session": total / max(self.total_sessions, 1),
        }


# ============================ FARM STATISTICS ============================
class FarmStats:
    def __init__(self):
        self.start_time = time.time()
        self.total_sessions = 0
        self.successful_sessions = 0
        self.failed_sessions = 0
        self.total_pages_visited = 0
        self.total_ad_hovers = 0
        self.total_ad_clicks = 0
        self.total_time_spent = 0.0
        self.sessions_by_section = {}
        self.sessions_by_device = {"desktop": 0, "tablet": 0, "mobile": 0}
        self.sessions_by_source = {}
        self.recent_sessions: List[Dict] = []
        self.errors: List[str] = []
        self.lock = asyncio.Lock()
    
    async def record_session(self, success: bool, section: str, device: str,
                             pages: int, hovers: int, clicks: int,
                             time_spent: float, source: str):
        async with self.lock:
            self.total_sessions += 1
            if success:
                self.successful_sessions += 1
            else:
                self.failed_sessions += 1
            self.total_pages_visited += pages
            self.total_ad_hovers += hovers
            self.total_ad_clicks += clicks
            self.total_time_spent += time_spent
            self.sessions_by_section[section] = self.sessions_by_section.get(section, 0) + 1
            self.sessions_by_device[device] = self.sessions_by_device.get(device, 0) + 1
            self.sessions_by_source[source] = self.sessions_by_source.get(source, 0) + 1
            
            self.recent_sessions.append({
                'id': f"S{self.total_sessions}", 'section': section[:20],
                'pages': pages, 'hovers': hovers, 'clicks': clicks,
                'time': int(time_spent), 'ok': success
            })
            if len(self.recent_sessions) > 50:
                self.recent_sessions = self.recent_sessions[-50:]
    
    def record_error(self, error: str):
        self.errors.append(f"{datetime.now().strftime('%H:%M:%S')} {error}")
        if len(self.errors) > 20:
            self.errors = self.errors[-20:]
    
    def get_summary(self, revenue_tracker=None) -> Dict:
        elapsed = time.time() - self.start_time
        success_rate = (self.successful_sessions / max(self.total_sessions, 1)) * 100
        avg_time = self.total_time_spent / max(self.successful_sessions, 1)
        sph = self.total_sessions / max(elapsed / 3600, 1)
        
        result = {
            "uptime_formatted": f"{int(elapsed//3600)}h {int((elapsed%3600)//60)}m {int(elapsed%60)}s",
            "total_sessions": self.total_sessions,
            "successful": self.successful_sessions,
            "failed": self.failed_sessions,
            "success_rate": f"{success_rate:.1f}%",
            "total_pages": self.total_pages_visited,
            "total_ad_hovers": self.total_ad_hovers,
            "total_ad_clicks": self.total_ad_clicks,
            "avg_session_time": f"{avg_time:.1f}s",
            "sessions_per_hour": f"{sph:.1f}",
            "by_device": self.sessions_by_device,
            "by_source": self.sessions_by_source,
            "concurrent": MAX_CONCURRENT_SESSIONS,
            "recent": self.recent_sessions,
            "errors": self.errors,
        }
        if revenue_tracker:
            earnings = revenue_tracker.get_earnings()
            result["estimated_revenue"] = f"${earnings['total']:.4f}"
            result["revenue_per_session"] = f"${earnings['revenue_per_session']:.6f}"
            result["projected_daily"] = f"${earnings['total'] / max(elapsed / 86400, 0.001):.2f}"
        return result
    
    def print_status(self, revenue_tracker=None):
        s = self.get_summary(revenue_tracker)
        print("\n" + "=" * 65)
        print(f"  🚜 LOPINUZE AD FARM V3 STATUS")
        print("=" * 65)
        print(f"  ⏱️  Uptime:     {s['uptime_formatted']}")
        print(f"  🔀 Workers:     {s['concurrent']}")
        print(f"  📊 Sessions:    {s['total_sessions']} ({s['sessions_per_hour']}/hr)")
        print(f"  ✅ Success:     {s['successful']} ({s['success_rate']})")
        print(f"  ❌ Failed:      {s['failed']}")
        print(f"  📄 Pages:       {s['total_pages']}")
        print(f"  🖱️  Ad hovers:   {s['total_ad_hovers']}")
        print(f"  👆 Ad clicks:   {s['total_ad_clicks']}")
        print(f"  ⏳ Avg session: {s['avg_session_time']}")
        if 'estimated_revenue' in s:
            print(f"  💰 Est Revenue: {s['estimated_revenue']}")
            print(f"  💵 Projected:   {s['projected_daily']}/day")
        print("=" * 65)


# ============================ SESSION WORKER ============================
async def session_worker(worker_id: int, stats: FarmStats, revenue: RevenueTracker):
    """Runs indefinitely, executing sessions via SessionEngine."""
    from session_engine import get_session_engine
    from survival_integration import get_survival_integrator
    
    engine = get_session_engine()
    survival = await get_survival_integrator()
    session_counter = 0
    
    while True:
        try:
            # 24/7 operation with power-law volume regulation
            # Instead of blocking, just throttle volume at off-peak hours
            now = datetime.now()
            hour = now.hour
            weekday = now.weekday()
            
            # Power-law multiplier: night = 8% of peak, morning = 40%, peak = 100%
            from config import OFF_HOURS, OFF_HOURS_GHOST_MULTIPLIER
            if hour in OFF_HOURS:
                if random.random() > OFF_HOURS_GHOST_MULTIPLIER:
                    await asyncio.sleep(random.randint(60, 180))
                    continue  # Skip most sessions at night (realistic)
            weekday = now.weekday()
            if weekday >= 5 and random.random() > WEEKEND_TRAFFIC_MULTIPLIER:
                await asyncio.sleep(random.randint(30, 90))
                continue
            
            # Survival pre-check
            allowed, throttle = await survival.pre_session_check()
            if not allowed:
                logger.info(f"[W{worker_id}] Paused by survival engine (cooldown)")
                await asyncio.sleep(300)
                continue
            
            # Run session
            sid = f"W{worker_id}-{session_counter}"
            result = await engine.run_session(sid)
            
            # Record stats
            section = result.get('section_visited', 'unknown')
            device = result.get('device_type', 'desktop')
            source = result.get('source_type', 'direct')
            
            await stats.record_session(
                success=result['success'],
                section=section,
                device=device,
                pages=result['pages_visited'],
                hovers=result['ad_hovers'],
                clicks=result['ad_clicks'],
                time_spent=result['time_spent'],
                source=source,
            )
            
            if result['success']:
                await revenue.record_session(
                    popunders=1,
                    banner_impressions=result['banner_impressions'],
                    banner_clicks=result['banner_clicks'],
                    native_clicks=result.get('native_clicks', 0),
                )
            else:
                if result.get('error'):
                    stats.record_error(f"{sid}: {result['error']}")
            
            session_counter += 1
            
            # Randomized delay with throttle
            base_delay = random.randint(MIN_VISIT_DELAY, MAX_VISIT_DELAY)
            if 9 <= hour <= 12 or 18 <= hour <= 22:
                base_delay = max(20, base_delay // 2)
            if throttle > 0:
                base_delay = int(base_delay * (1 + throttle * 3))
            
            await asyncio.sleep(base_delay)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"[W{worker_id}] Worker error: {e}")
            stats.record_error(f"W{worker_id}: {str(e)[:80]}")
            await asyncio.sleep(30)


# ============================ DASHBOARD UPDATER ============================
async def dashboard_updater(stats: FarmStats, revenue: RevenueTracker):
    """Periodically pushes stats to dashboard.py via its update_state function."""
    if not DASHBOARD_ENABLED:
        return
    try:
        from dashboard import update_state
        from vpn_tunnel import get_vpn_tunnel
        from survival_integration import get_survival_integrator
        from proxy_manager import get_proxy_pool
        
        vpn = await get_vpn_tunnel()
        survival = await get_survival_integrator()
        pool = await get_proxy_pool()
        
        while True:
            try:
                summary = stats.get_summary(revenue)
                earnings = revenue.get_earnings()
                survival_stats = survival.get_stats()
                vpn_status = vpn.get_status()
                pool_stats = pool.get_stats()
                
                update_state(
                    running=True,
                    uptime=summary['uptime_formatted'],
                    total_sessions=summary['total_sessions'],
                    successful=summary['successful'],
                    failed=summary['failed'],
                    success_rate=summary['success_rate'],
                    total_pages=summary['total_pages'],
                    total_ad_hovers=summary['total_ad_hovers'],
                    total_ad_clicks=summary['total_ad_clicks'],
                    avg_session_time=summary['avg_session_time'],
                    sessions_per_hour=summary['sessions_per_hour'],
                    concurrent=MAX_CONCURRENT_SESSIONS,
                    proxy_working=pool_stats.get('success', 0),
                    proxy_total=pool_stats.get('assigned', 0),
                    estimated_revenue=f"${earnings['total']:.4f}",
                    projected_daily=summary.get('projected_daily', '$0.00'),
                    risk_level=survival_stats.get('risk_level', 'safe'),
                    throttle=survival_stats.get('throttle', 0),
                    vpn_connected=vpn_status.get('connected', False),
                    network_count=1,
                    errors=summary.get('errors', []),
                    recent_sessions=summary.get('recent', []),
                )
            except Exception:
                pass
            await asyncio.sleep(5)
    except ImportError:
        pass


# ============================ MAIN FARM LOOP ============================
async def farm_loop():
    logger.info("=" * 65)
    logger.info(f"🚜 LOPINUZE AD FARM V3 STARTING")
    logger.info(f"   Site:       {SITE_URL}")
    logger.info(f"   Sections:   {get_section_count()}")
    logger.info(f"   Workers:    {MAX_CONCURRENT_SESSIONS}")
    logger.info(f"   GPU:        {'Enabled' if __import__('config').GPU_ENABLED else 'Disabled'}")
    logger.info(f"   Hours:      {HUMAN_HOURS_START:02d}:00 - {HUMAN_HOURS_END:02d}:00")
    logger.info(f"   Dashboard:  http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
    logger.info("=" * 65)
    
    validate_config()
    
    # Initialize subsystems
    logger.info("Initializing subsystems...")
    from proxy_manager import get_proxy_pool
    proxy_pool = await get_proxy_pool()
    await proxy_pool.refresh_pool(force=True)
    
    from smart_rotator import get_rotator
    rotator = await get_rotator()
    rotator_stats = await rotator.get_pool_stats()
    logger.info(f"✅ Proxy pool: {rotator_stats.get('working', 0)} working / {rotator_stats.get('total', 0)} total")
    
    # VPN check (non-blocking if config doesn't exist)
    try:
        from vpn_tunnel import get_vpn_tunnel
        vpn = await get_vpn_tunnel()
        if vpn.config_exists():
            await vpn.connect()
            logger.info(f"✅ VPN: {'Connected' if vpn.get_status()['connected'] else 'Config exists but not connected'}")
        else:
            logger.info("ℹ️  VPN: No WireGuard config found (Phase 11 setup needed)")
    except Exception as e:
        logger.warning(f"VPN init: {e}")
    
    stats = FarmStats()
    revenue = RevenueTracker()
    
    # Start dashboard
    if DASHBOARD_ENABLED:
        try:
            from dashboard import start_dashboard
            start_dashboard(DASHBOARD_HOST, DASHBOARD_PORT)
            logger.info(f"✅ Dashboard: http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
        except Exception as e:
            logger.warning(f"Dashboard start failed: {e}")
    
    # Start dashboard updater
    dash_task = asyncio.create_task(dashboard_updater(stats, revenue))
    
    # Launch workers
    workers = []
    for i in range(MAX_CONCURRENT_SESSIONS):
        task = asyncio.create_task(session_worker(i + 1, stats, revenue))
        workers.append(task)
    
    logger.info(f"🚀 {MAX_CONCURRENT_SESSIONS} workers running concurrently")
    
    last_status = time.time()
    last_pool_refresh = time.time()
    
    try:
        while True:
            await asyncio.sleep(30)
            
            # Status every 120s
            if time.time() - last_status > 120:
                stats.print_status(revenue)
                rotator_stats = await rotator.get_pool_stats()
                proxy_working = rotator_stats.get('working', 0)
                logger.info(f"   Proxy: {proxy_working}/{rotator_stats.get('total', 0)} | "
                           f"Workers: {MAX_CONCURRENT_SESSIONS} | "
                           f"Tiers: {rotator_stats.get('by_tier', {})}")
                last_status = time.time()
            
            # Pool refresh every 15 minutes
            if time.time() - last_pool_refresh > 900:
                logger.info("🔄 Refreshing proxy pool...")
                new_count = await proxy_pool.refresh_pool(force=True)
                logger.info(f"   {new_count} new proxies verified")
                last_pool_refresh = time.time()
            
            # Account health check every 30 min
            from survival_integration import get_survival_integrator
            survival = await get_survival_integrator()
            result = await survival.check_account_health()
            if result.get('action') == 'switched':
                logger.critical(f"⚠️ ACCOUNT SWITCHED: {result.get('new_publisher_id')}")
    
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("\n🛑 SHUTTING DOWN...")
        
        for task in workers:
            task.cancel()
        dash_task.cancel()
        await asyncio.gather(*workers, dash_task, return_exceptions=True)
        
        stats.print_status(revenue)
        earnings = revenue.get_earnings()
        logger.info(f"\n💰 FINAL REVENUE: ${earnings['total']:.4f}")
        logger.info(f"   Sessions: {earnings['sessions']} | Per session: ${earnings['revenue_per_session']:.6f}")
        
        from browser_manager import cleanup_browser_pool
        from proxy_manager import cleanup_proxy_pool
        from ai_behavior import cleanup_behavior_engine
        from geo_utils import cleanup_geo_client
        
        await cleanup_browser_pool()
        await cleanup_proxy_pool()
        await cleanup_behavior_engine()
        await cleanup_geo_client()
        
        logger.info("✅ Cleanup complete. Farm stopped.")


# ============================ ENTRY POINT ============================
if __name__ == '__main__':
    setup_logging()
    
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    
    print(r"""
╔══════════════════════════════════════════════════════════════╗
║     ██╗      ██████╗ ██████╗ ██╗███╗   ██╗██╗   ██╗███████╗
║     ██║     ██╔═══██╗██╔══██╗██║████╗  ██║██║   ██║╚══███╔╝
║     ██║     ██║   ██║██████╔╝██║██╔██╗ ██║██║   ██║  ███╔╝ 
║     ██║     ██║   ██║██╔═══╝ ██║██║╚██╗██║██║   ██║ ███╔╝  
║     ███████╗╚██████╔╝██║     ██║██║ ╚████║╚██████╔╝███████╗
║     ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝
║                                                              
║     80-WORKER AD FARM V3 — MAXIMUM SECURITY & REVENUE       
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print(f"  🌐 Target: {SITE_URL}")
    print(f"  📰 Sections: {get_section_count()}")
    print(f"  🔀 Workers: {MAX_CONCURRENT_SESSIONS}")
    print(f"  🎮 GPU: {'Enabled' if __import__('config').GPU_ENABLED else 'Disabled'}")
    print(f"  📊 Dashboard: http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
    print(f"  🕘 Hours: {HUMAN_HOURS_START:02d}:00-{HUMAN_HOURS_END:02d}:00")
    print()
    print("  Press Ctrl+C to stop.")
    print("  Starting...\n")
    
    try:
        asyncio.run(farm_loop())
    except KeyboardInterrupt:
        print("\n👋 Farm stopped by user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.exception("Fatal error")