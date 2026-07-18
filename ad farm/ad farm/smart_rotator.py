#!/usr/bin/env python3
"""
Smart Proxy Rotator — Tier-Aware, Self-Learning
=================================================
Provides intelligent proxy assignment per session based on proxy quality tier,
session value, and usage history. Prevents proxy reuse within cooldown period.
"""

import asyncio
import random
import time
import socket
import logging
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger('smart_rotator')

SESSION_TIER_REQUIREMENTS = {
    'ad_click':    'S',
    'high_value':  'A',
    'browse':      'B',
    'background':  'C',
}

TIER_COOLDOWNS = {
    'S': 7200, 'A': 5400, 'B': 3600, 'C': 1800,
}

# Quick TCP verification timeout (seconds)
QUICK_TCP_CHECK_TIMEOUT = 1.5


class SmartRotator:
    """Intelligent proxy rotation engine with tier-aware routing + pre-use verification."""

    def __init__(self, db_path: str = "proxies.db"):
        import os
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self._active_proxies: Dict[str, float] = {}
        self._last_refresh: float = 0
        self._refresh_interval: int = 300  # 5 minutes
        self._stats: Dict = defaultdict(int)
        self._lock = asyncio.Lock()
        self._country_usage: Dict[str, int] = defaultdict(int)

    async def _ensure_pool_fresh(self):
        now = time.time()
        if (now - self._last_refresh) > self._refresh_interval:
            await self.get_pool_stats()
            self._last_refresh = now

    async def _quick_tcp_check(self, host: str, port: int) -> bool:
        """Fast TCP connectivity check before assigning proxy. Returns True if reachable."""
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=QUICK_TCP_CHECK_TIMEOUT
            )
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return True
        except Exception:
            return False

    async def assign_proxy(self, session_value: str = 'browse',
                           preferred_country: str = None,
                           source_filter: list = None) -> Optional[str]:
        """Assign a LIVE proxy after TCP verification. Returns None if none available.
        
        Args:
            session_value: 'background', 'browse', 'high_value', 'ad_click'
            preferred_country: Optional 2-letter country code
            source_filter: Optional list of allowed sources e.g. ['scraped'], ['webshare'], ['mullvad']
        """
        async with self._lock:
            await self._ensure_pool_fresh()

            min_tier = SESSION_TIER_REQUIREMENTS.get(session_value, 'B')
            tier_order = {'S': 0, 'A': 1, 'B': 2, 'C': 3}
            min_rank = tier_order.get(min_tier, 2)
            now = time.time()

            import sqlite3
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    # Build query with optional source filtering
                    source_clause = ''
                    source_params = []
                    if source_filter:
                        placeholders = ','.join(['?' for _ in source_filter])
                        source_clause = f' AND source IN ({placeholders})'
                        source_params = list(source_filter)
                    else:
                        # Default: only scraped proxies from main pool
                        # Webshare/Mullvad are managed separately
                        source_clause = " AND (source = 'scraped' OR source IS NULL)"
                    
                    if preferred_country:
                        params = [preferred_country] + source_params
                        cursor = conn.execute(f"""
                            SELECT * FROM proxies
                            WHERE is_banned = 0 AND fail_count < 2 AND country = ?{source_clause}
                            ORDER BY CASE tier WHEN 'S' THEN 0 WHEN 'A' THEN 1
                                     WHEN 'B' THEN 2 WHEN 'C' THEN 3 ELSE 4 END, last_used ASC
                            LIMIT 50
                        """, params)
                    else:
                        cursor = conn.execute(f"""
                            SELECT * FROM proxies
                            WHERE is_banned = 0 AND fail_count < 2{source_clause}
                            ORDER BY CASE tier WHEN 'S' THEN 0 WHEN 'A' THEN 1
                                     WHEN 'B' THEN 2 WHEN 'C' THEN 3 ELSE 4 END, last_used ASC
                            LIMIT 100
                        """, source_params)
                    rows = cursor.fetchall()
            except sqlite3.OperationalError:
                logger.warning("No proxies table yet (run proxy_filter first)")
                return None

            if not rows:
                logger.warning(f"No proxies available")
                return None

            candidates = []
            for row in rows:
                proxy = dict(row)
                proxy_tier_rank = tier_order.get(proxy['tier'], 4)
                if proxy_tier_rank > min_rank:
                    continue
                cooldown = TIER_COOLDOWNS.get(proxy['tier'], 3600)
                if now - proxy['last_used'] < cooldown:
                    continue
                if proxy['url'] in self._active_proxies:
                    continue
                # Country diversity: avoid >20% from same country
                country = proxy.get('country', '??')
                total_used = sum(self._country_usage.values()) or 1
                if self._country_usage.get(country, 0) / total_used > 0.20 and preferred_country != country:
                    continue
                
                # Datacenter proxies REJECTED for ALL sessions (residential/mobile only)
                isp = proxy.get('isp', '')
                DATACENTER_KEYWORDS = ['hosting', 'cloud', 'vps', 'server', 'digitalocean', 'aws', 'azure', 'google cloud', 'linode', 'vultr', 'hetzner', 'ovh', 'datacenter', 'colo']
                is_datacenter = any(w in (isp or '').lower() for w in DATACENTER_KEYWORDS)
                if is_datacenter:
                    continue  # Skip all datacenter — residential/mobile only
                
                candidates.append(proxy)

            if not candidates:
                for row in rows:
                    proxy = dict(row)
                    if proxy['url'] not in self._active_proxies:
                        if now - proxy['last_used'] < 900:
                            continue
                        candidates.append(proxy)

            if not candidates:
                logger.error("No available proxies! Run proxy_filter to refresh pool.")
                return None

            # Try up to 5 candidates, picking the first LIVE one
            trial_candidates = candidates[:min(5, len(candidates))]
            random.shuffle(trial_candidates)

            for candidate in trial_candidates:
                host = candidate.get('host', '')
                port = candidate.get('port', 8080)
                
                # Quick TCP connectivity check
                if not await self._quick_tcp_check(host, port):
                    logger.debug(f"Proxy DEAD: {host}:{port} — skipping")
                    # Mark as failed silently (don't auto-ban on first check)
                    continue
                
                # LIVE proxy found — use it
                chosen = candidate
                self._active_proxies[chosen['url']] = now

                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("UPDATE proxies SET last_used = ? WHERE url = ?", (now, chosen['url']))
                        conn.commit()
                except sqlite3.OperationalError:
                    pass

                country = chosen.get('country', '??')
                self._country_usage[country] += 1
                self._stats['assigned'] += 1
                self._stats['tcp_verified'] = self._stats.get('tcp_verified', 0) + 1
                
                logger.debug(f"Proxy assigned + VERIFIED: {host}:{port} (tier={chosen['tier']})")
                return chosen['url']

            # No live proxy found — trigger emergency refresh
            logger.warning("All candidate proxies failed TCP check! Triggering emergency refresh...")
            await self.emergency_refresh()
            return None

    async def release_proxy(self, proxy_url: str, success: bool = True):
        """Release a proxy after session. Auto-ban after 2 failures."""
        async with self._lock:
            if proxy_url in self._active_proxies:
                del self._active_proxies[proxy_url]

            import sqlite3
            try:
                with sqlite3.connect(self.db_path) as conn:
                    if success:
                        conn.execute("""
                            UPDATE proxies SET success_count = success_count + 1,
                            fail_count = 0, last_used = ? WHERE url = ?
                        """, (time.time(), proxy_url))
                        self._stats['success'] += 1
                    else:
                        conn.execute("""
                            UPDATE proxies SET fail_count = fail_count + 1,
                            last_used = ? WHERE url = ?
                        """, (time.time(), proxy_url))
                        self._stats['failed'] += 1
                        conn.execute("""
                            UPDATE proxies SET is_banned = 1, tier = 'F'
                            WHERE url = ? AND fail_count >= 2
                        """, (proxy_url,))
                        self._stats['banned'] += 1
                    conn.commit()
            except sqlite3.OperationalError:
                pass

    async def get_pool_stats(self) -> Dict:
        import sqlite3
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT tier, COUNT(*) as cnt,
                           SUM(CASE WHEN is_banned=0 AND fail_count<2 THEN 1 ELSE 0 END) as working
                    FROM proxies GROUP BY tier ORDER BY tier
                """)
                tiers = {}
                for row in cursor.fetchall():
                    tiers[row[0]] = {'total': row[1], 'working': row[2]}
                total = conn.execute("SELECT COUNT(*) FROM proxies").fetchone()[0]
                working = conn.execute("SELECT COUNT(*) FROM proxies WHERE is_banned=0 AND fail_count<2").fetchone()[0]
            return {
                'total': total, 'working': working, 'active': len(self._active_proxies),
                'by_tier': tiers, 'rotator_stats': dict(self._stats),
                'country_dist': dict(self._country_usage),
            }
        except sqlite3.OperationalError:
            return {"total": 0, "working": 0, "active": 0, "by_tier": {}, "rotator_stats": dict(self._stats), "country_dist": dict(self._country_usage)}

    async def emergency_refresh(self):
        from proxy_filter import get_proxy_filter
        pf = await get_proxy_filter()
        await pf.full_pipeline()
        self._last_refresh = time.time()
        logger.info("Emergency proxy pool refresh completed")


_rotator: Optional[SmartRotator] = None

async def get_rotator() -> SmartRotator:
    global _rotator
    if _rotator is None:
        _rotator = SmartRotator()
    return _rotator