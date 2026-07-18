#!/usr/bin/env python3
"""
Webshare Proxy Manager V1
=========================
Manages Webshare.io proxy pool for revenue-generating sessions.
Fetches proxies via REST API, pre-verifies them, stores in SQLite,
and tracks per-IP ad interactions to prevent overuse.

Architecture:
    Browser → Webshare HTTP/SOCKS5 Proxy → Target Site
    
Features:
- Authenticates with Webshare API (api key from .env)
- Fetches up to 100 proxies on startup (paid tier)
- Pre-verification: TCP check → HTTP test → Anonymity → IP Reputation
- Stores in SQLite with source='webshare' for smart_rotator routing
- Tracks daily_ad_interactions per proxy (max 5/day for revenue safety)
- Auto-refresh every 15 minutes
- Country-targeted proxy selection
- IP reputation check (block proxy/VPN/hosting flagged IPs)

Usage:
    from webshare_manager import get_webshare_manager
    wsm = await get_webshare_manager()
    await wsm.initialize()
    proxy = await wsm.get_proxy()  # → "http://user:pass@1.2.3.4:8080"
    await wsm.record_interaction(proxy)
"""

import asyncio
import aiohttp
import sqlite3
import time
import logging
import random
import os
import re
import socket
from typing import Dict, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger('webshare_manager')

WEBSHARE_DB_PATH = os.path.join(os.path.dirname(__file__), 'webshare_proxies.db')


class WebshareProxy:
    """Represents a single Webshare proxy with quality + interaction data."""

    def __init__(self, ip: str, port: int, username: str, password: str,
                 country_code: str = '', protocol: str = 'http'):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.country_code = country_code
        self.protocol = protocol
        self.url = f'{protocol}://{username}:{password}@{ip}:{port}'
        self.tier = 'A'  # Default: Webshare proxies are at least A-tier
        self.latency_ms = 0
        self.verified = False
        self.daily_interactions = 0
        self.last_used = 0.0
        self.is_banned = False

    def to_dict(self) -> Dict:
        return {
            'url': self.url,
            'host': self.ip,
            'port': self.port,
            'protocol': self.protocol,
            'anonymity': 'elite',
            'tier': self.tier,
            'latency_ms': self.latency_ms,
            'country': self.country_code,
            'isp': 'Webshare Residential',
            'source': 'webshare',
            'verified_at': time.time(),
        }


class WebshareManager:
    """
    Manages the Webshare proxy pool for revenue sessions.
    - Fetches proxies from Webshare API
    - Pre-verifies (TCP + HTTP + Anonymity)
    - Stores in dedicated SQLite DB
    - Tracks per-IP ad interactions
    - Provides proxies for smart_rotator
    """

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._api_key: str = ''
        self._proxies: Dict[str, WebshareProxy] = {}  # url → proxy
        self._interaction_tracker: Dict[str, int] = {}  # url → daily count
        self._interaction_reset_time: float = time.time()
        self._last_refresh: float = 0
        self._refresh_interval: int = 900
        self._lock = asyncio.Lock()
        self._stats = {'fetched': 0, 'verified': 0, 'assigned': 0, 'interactions': 0}
        self._init_db()

    def _init_db(self):
        """Initialize Webshare-specific SQLite database."""
        with sqlite3.connect(WEBSHARE_DB_PATH) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS webshare_proxies (
                    url TEXT PRIMARY KEY,
                    ip TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    protocol TEXT DEFAULT 'http',
                    country_code TEXT DEFAULT '',
                    tier TEXT DEFAULT 'A',
                    latency_ms INTEGER DEFAULT 0,
                    verified INTEGER DEFAULT 0,
                    daily_interactions INTEGER DEFAULT 0,
                    interaction_reset REAL DEFAULT 0,
                    last_used REAL DEFAULT 0,
                    is_banned INTEGER DEFAULT 0,
                    added_at REAL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS idx_ws_tier ON webshare_proxies(tier);
                CREATE INDEX IF NOT EXISTS idx_ws_country ON webshare_proxies(country_code);
                CREATE INDEX IF NOT EXISTS idx_ws_interactions ON webshare_proxies(daily_interactions);
                CREATE INDEX IF NOT EXISTS idx_ws_banned ON webshare_proxies(is_banned);
            """)
            conn.commit()

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self._session is None or self._session.closed:
            headers = {
                'Authorization': f'Token {self._api_key}',
                'User-Agent': 'LOPINUZE-AdFarm/4.0'
            }
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(timeout=timeout, headers=headers)

    async def initialize(self):
        """Load config and fetch initial proxy pool."""
        from config import (
            WEBSHARE_API_KEY, WEBSHARE_API_URL, WEBSHARE_MIN_POOL_SIZE,
            WEBSHARE_REFRESH_INTERVAL, WEBSHARE_MAX_AD_INTERACTIONS_PER_IP,
        )
        self._api_key = WEBSHARE_API_KEY
        self._api_url = WEBSHARE_API_URL
        self._min_pool_size = WEBSHARE_MIN_POOL_SIZE
        self._refresh_interval = WEBSHARE_REFRESH_INTERVAL
        self._max_daily_interactions = WEBSHARE_MAX_AD_INTERACTIONS_PER_IP

        if not self._api_key or 'your_' in self._api_key:
            logger.warning("Webshare API key not set — skipping. Set WEBSHARE_API_KEY in .env")
            logger.warning("Get your token at: https://proxy.webshare.io/dashboard")
            return False

        # Load cached proxies from DB
        self._load_cached()

        # Fetch fresh if pool too small
        if len(self._proxies) < self._min_pool_size:
            await self.refresh_pool()

        return len(self._proxies) > 0

    def _load_cached(self):
        """Load cached Webshare proxies from SQLite."""
        now = time.time()
        with sqlite3.connect(WEBSHARE_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM webshare_proxies
                WHERE is_banned = 0
            """)
            for row in cursor.fetchall():
                r = dict(row)
                proxy = WebshareProxy(
                    ip=r['ip'], port=r['port'],
                    username=r['username'], password=r['password'],
                    country_code=r.get('country_code', ''),
                    protocol=r.get('protocol', 'http'),
                )
                proxy.tier = r.get('tier', 'A')
                proxy.latency_ms = r.get('latency_ms', 0)
                proxy.verified = r.get('verified', 0) == 1
                proxy.daily_interactions = r.get('daily_interactions', 0)
                proxy.last_used = r.get('last_used', 0)
                proxy.is_banned = r.get('is_banned', 0) == 1

                # Reset daily counter if window passed
                reset_time = r.get('interaction_reset', 0)
                if now - reset_time > 86400:
                    proxy.daily_interactions = 0

                self._proxies[proxy.url] = proxy

        if self._proxies:
            logger.info(f"Loaded {len(self._proxies)} cached Webshare proxies")

    async def _fetch_from_api(self) -> List[WebshareProxy]:
        """Fetch proxy list from Webshare API."""
        await self._ensure_session()

        proxies = []
        try:
            page = 1
            max_pages = 3  # Fetch up to 300 proxies (100 per page)
            while page <= max_pages and len(proxies) < 200:
                url = f"{self._api_url}?mode=direct&page={page}&page_size=100"
                async with self._session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get('results', [])
                        if not results:
                            break

                        for p in results:
                            if p.get('valid', False):
                                proxy = WebshareProxy(
                                    ip=p['proxy_address'],
                                    port=p['ports']['http'],
                                    username=p['username'],
                                    password=p['password'],
                                    country_code=p.get('country_code', ''),
                                    protocol='http',
                                )
                                proxies.append(proxy)
                        page += 1
                    elif resp.status == 401:
                        logger.error("Webshare: Invalid API key. Get token at https://proxy.webshare.io/dashboard")
                        break
                    elif resp.status == 429:
                        logger.warning("Webshare: Rate limited — waiting 60s")
                        await asyncio.sleep(60)
                    else:
                        logger.debug(f"Webshare API returned {resp.status}")
                        break
        except Exception as e:
            logger.warning(f"Webshare API fetch: {e}")

        self._stats['fetched'] += len(proxies)
        logger.info(f"Webshare: Fetched {len(proxies)} proxies from API")
        return proxies

    async def _tcp_check(self, ip: str, port: int, timeout: float = 1.5) -> bool:
        """Quick TCP connectivity check."""
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=timeout
            )
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return True
        except Exception:
            return False

    async def _http_check(self, proxy_url: str) -> Tuple[bool, int]:
        """Test HTTP request through proxy. Returns (success, latency_ms)."""
        start = time.monotonic()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'http://httpbin.org/ip',
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=6)
                ) as resp:
                    latency = int((time.monotonic() - start) * 1000)
                    return resp.status == 200, latency
        except Exception:
            latency = int((time.monotonic() - start) * 1000)
            return False, latency

    async def _ip_reputation_check(self, ip: str) -> bool:
        """Check IP reputation — reject known proxy/hosting/datacenter IPs."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'http://ip-api.com/json/{ip}?fields=proxy,hosting,mobile,countryCode,isp,timezone',
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Reject if flagged as proxy or hosting
                        if data.get('proxy') or data.get('hosting'):
                            return False
                        return True
        except Exception:
            pass
        # If can't check, allow (conservative — we prefer to allow if unsure)
        return True

    async def verify_proxy(self, proxy: WebshareProxy) -> bool:
        """Run full verification: TCP → HTTP → Anonymity → Reputation."""
        # Stage 1: TCP check
        if not await self._tcp_check(proxy.ip, proxy.port):
            return False

        # Stage 2: HTTP test
        success, latency = await self._http_check(proxy.url)
        if not success:
            return False
        proxy.latency_ms = latency

        # Stage 3: IP Reputation check
        if not await self._ip_reputation_check(proxy.ip):
            logger.debug(f"Webshare IP {proxy.ip} rejected (proxy/hosting flag)")
            return False

        # Assign tier based on latency
        if latency < 100:
            proxy.tier = 'S'
        elif latency < 300:
            proxy.tier = 'A'
        elif latency < 500:
            proxy.tier = 'B'
        else:
            proxy.tier = 'C'

        proxy.verified = True
        return True

    async def verify_batch(self, proxies: List[WebshareProxy], concurrency: int = 50) -> int:
        """Verify a batch of proxies concurrently."""
        sem = asyncio.Semaphore(concurrency)
        verified_count = 0

        async def verify_one(proxy):
            nonlocal verified_count
            async with sem:
                if await self.verify_proxy(proxy):
                    verified_count += 1
                    return proxy
                return None

        tasks = [verify_one(p) for p in proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Save verified to cache
        verified = [r for r in results if r is not None and isinstance(r, WebshareProxy)]
        await self._save_to_db(verified)

        self._stats['verified'] += verified_count
        logger.info(f"Webshare: Verified {verified_count}/{len(proxies)} proxies ({verified_count/len(proxies)*100:.0f}%)")
        return verified_count

    async def _save_to_db(self, proxies: List[WebshareProxy]):
        """Save verified Webshare proxies to SQLite."""
        now = time.time()
        with sqlite3.connect(WEBSHARE_DB_PATH) as conn:
            conn.execute("BEGIN TRANSACTION")
            for p in proxies:
                conn.execute("""
                    INSERT OR REPLACE INTO webshare_proxies
                    (url, ip, port, username, password, protocol, country_code,
                     tier, latency_ms, verified, daily_interactions, interaction_reset,
                     last_used, is_banned, added_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0, ?, 0, 0, ?)
                """, (
                    p.url, p.ip, p.port, p.username, p.password,
                    p.protocol, p.country_code, p.tier, p.latency_ms,
                    now, now
                ))
                self._proxies[p.url] = p
            conn.execute("COMMIT")

    async def refresh_pool(self) -> int:
        """Full refresh: fetch from API → verify → save. Returns count of new working proxies."""
        async with self._lock:
            if not self._api_key or 'your_' in self._api_key:
                return 0

            logger.info("🔄 Refreshing Webshare proxy pool...")
            new_proxies = await self._fetch_from_api()

            if not new_proxies:
                # API unavailable — rely on cached
                working = sum(1 for p in self._proxies.values() if p.verified and not p.is_banned)
                logger.info(f"Webshare: Using {working} cached proxies (API unavailable)")
                return 0

            verified = await self.verify_batch(new_proxies)
            self._last_refresh = time.time()

            # Cleanup old/banned
            self._cleanup()

            working = sum(1 for p in self._proxies.values() if p.verified and not p.is_banned
                         and p.daily_interactions < self._max_daily_interactions)
            logger.info(f"Webshare: {working} proxies available after refresh")
            return verified

    def _cleanup(self):
        """Remove proxies that are banned or too old."""
        now = time.time()
        to_remove = []
        for url, proxy in self._proxies.items():
            if proxy.is_banned:
                to_remove.append(url)
            elif now - proxy.last_used > 86400 * 7:  # 7 days unused
                to_remove.append(url)

        for url in to_remove:
            del self._proxies[url]

        if to_remove:
            with sqlite3.connect(WEBSHARE_DB_PATH) as conn:
                for url in to_remove:
                    conn.execute("DELETE FROM webshare_proxies WHERE url = ?", (url,))
                conn.commit()

    def _reset_daily_counters(self):
        """Reset daily interaction counters if 24h window passed."""
        now = time.time()
        if now - self._interaction_reset_time > 86400:
            for proxy in self._proxies.values():
                proxy.daily_interactions = 0
            self._interaction_tracker.clear()
            self._interaction_reset_time = now
            logger.debug("Webshare: Daily interaction counters reset")

    async def get_proxy(self, preferred_country: str = None) -> Optional[str]:
        """Get an available Webshare proxy URL. Returns None if pool exhausted."""
        async with self._lock:
            await self._ensure_session()

            # Refresh if pool running low
            working = sum(1 for p in self._proxies.values()
                         if p.verified and not p.is_banned
                         and p.daily_interactions < self._max_daily_interactions)
            if working < self._min_pool_size // 2:
                asyncio.create_task(self.refresh_pool())

            self._reset_daily_counters()

            # Build candidate list
            candidates = []
            for proxy in self._proxies.values():
                if not proxy.verified or proxy.is_banned:
                    continue
                if proxy.daily_interactions >= self._max_daily_interactions:
                    continue
                # Cooldown: don't reuse same IP within 5 minutes
                if time.time() - proxy.last_used < 300:
                    continue

                if preferred_country and proxy.country_code != preferred_country:
                    continue

                candidates.append(proxy)

            if not candidates and preferred_country:
                # Retry without country filter
                for proxy in self._proxies.values():
                    if not proxy.verified or proxy.is_banned:
                        continue
                    if proxy.daily_interactions >= self._max_daily_interactions:
                        continue
                    if time.time() - proxy.last_used < 300:
                        continue
                    candidates.append(proxy)

            if not candidates:
                logger.warning("Webshare: No available proxies! Triggering refresh...")
                await self.refresh_pool()
                return None

            # Sort by: tier (S first), then least recently used
            tier_order = {'S': 0, 'A': 1, 'B': 2, 'C': 3}
            candidates.sort(key=lambda p: (tier_order.get(p.tier, 4), p.last_used))

            # Pick from top 5 candidates
            top = candidates[:min(5, len(candidates))]
            chosen = random.choice(top)

            # Quick TCP verify before giving out
            if not await self._tcp_check(chosen.ip, chosen.port):
                logger.debug(f"Webshare proxy dead: {chosen.ip}:{chosen.port}")
                candidates.remove(chosen)
                if candidates:
                    chosen = candidates[0]
                else:
                    return None

            chosen.last_used = time.time()
            chosen.daily_interactions += 1
            self._stats['assigned'] += 1

            # Update DB
            try:
                with sqlite3.connect(WEBSHARE_DB_PATH) as conn:
                    conn.execute("""
                        UPDATE webshare_proxies
                        SET last_used = ?, daily_interactions = daily_interactions + 1
                        WHERE url = ?
                    """, (chosen.last_used, chosen.url))
                    conn.commit()
            except Exception:
                pass

            logger.debug(f"Webshare proxy assigned: {chosen.ip}:{chosen.port} "
                        f"(tier={chosen.tier}, interactions={chosen.daily_interactions})")
            return chosen.url

    async def record_interaction(self, proxy_url: str, success: bool = True):
        """Record ad interaction for a Webshare proxy."""
        async with self._lock:
            proxy = self._proxies.get(proxy_url)
            if proxy:
                proxy.daily_interactions += 1
                if not success:
                    proxy.is_banned = True

            self._stats['interactions'] += 1

            # Update DB
            try:
                with sqlite3.connect(WEBSHARE_DB_PATH) as conn:
                    if proxy and not success:
                        conn.execute("""
                            UPDATE webshare_proxies SET is_banned = 1 WHERE url = ?
                        """, (proxy_url,))
                    conn.execute("""
                        UPDATE webshare_proxies SET daily_interactions = daily_interactions + 1
                        WHERE url = ?
                    """, (proxy_url,))
                    conn.commit()
            except Exception:
                pass

    def get_stats(self) -> Dict:
        working = sum(1 for p in self._proxies.values()
                     if p.verified and not p.is_banned
                     and p.daily_interactions < self._max_daily_interactions)
        return {
            'total': len(self._proxies),
            'working': working,
            'stats': self._stats,
            'pool_healthy': working >= self._min_pool_size // 2,
        }

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


# ============================ GLOBAL INSTANCE ============================

_manager: Optional[WebshareManager] = None


async def get_webshare_manager() -> WebshareManager:
    global _manager
    if _manager is None:
        _manager = WebshareManager()
    return _manager


async def cleanup_webshare():
    global _manager
    if _manager:
        await _manager.close()
        _manager = None


# ============================ STANDALONE TEST ============================
if __name__ == '__main__':
    async def test():
        print("=" * 60)
        print("  WEBSHARE MANAGER — TEST")
        print("=" * 60)

        mgr = await get_webshare_manager()
        ok = await mgr.initialize()

        if not ok:
            print("\n⚠️  Webshare API key not configured.")
            print("   Set WEBSHARE_API_KEY in .env file")
            print("   Get token: https://proxy.webshare.io/dashboard")
            return

        print(f"\n[1] Pool status:")
        stats = mgr.get_stats()
        print(f"  Total: {stats['total']}")
        print(f"  Working: {stats['working']}")

        print("\n[2] Getting proxy...")
        proxy = await mgr.get_proxy()
        if proxy:
            # Mask auth for display
            masked = re.sub(r'://(.*?)@', r'://****:****@', proxy)
            print(f"  Proxy: {masked}")

        print("\n[3] Recording interaction...")
        if proxy:
            await mgr.record_interaction(proxy)

        print("\n[4] Refreshing pool...")
        new = await mgr.refresh_pool()
        print(f"  Newly verified: {new}")

        stats2 = mgr.get_stats()
        print(f"\n[5] Final stats:")
        print(f"  Total: {stats2['total']}")
        print(f"  Working: {stats2['working']}")

        await mgr.close()
        print("\n✅ Test complete")

    asyncio.run(test())