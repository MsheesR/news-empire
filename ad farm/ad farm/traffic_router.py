#!/usr/bin/env python3
"""
Traffic Router V2 — MangoProxy ISP + Mullvad VPN + Scraped Routing
=====================================================================
Replaces Webshare with MangoProxy ISP proxies (cheaper, faster).
Routes sessions to appropriate proxy sources based on purpose.

Routing Logic:
    IMPRESSION sessions (ghost, bouncer, scanner, social_click):
      → Scraped free proxies only (5,000+ public pool)
      → No ad interactions, so IP reputation doesn't matter
      → 75% of total traffic

    REVENUE sessions (reader, deep_diver, searcher, direct_type_in):
      → MangoProxy ISP paid proxies (70% of revenue traffic)
      → Mullvad VPN tunnel (30% of revenue traffic)
      → Scraped proxies (fallback only)
      → 25% of total traffic
      → Max 25 ad interactions per MangoProxy ISP IP/day
      → Max 50 ad interactions per Mullvad IP/rotation

Per-IP Interaction Tracking:
    Prevents any single IP from generating too many ad interactions,
    which is the #1 way ad networks detect farms.

Usage:
    from traffic_router import get_router
    router = await get_router()
    proxy = await router.get_proxy_for_session(session_purpose='revenue')
    await router.record_interaction(proxy, session_purpose)
"""

import asyncio
import time
import logging
import random
from typing import Dict, Optional
from collections import defaultdict

logger = logging.getLogger('traffic_router')


class TrafficRouter:
    """
    Routes sessions to appropriate proxy sources based on purpose.
    Tracks per-IP ad interactions to prevent detection.
    """

    def __init__(self):
        self._rotator = None
        self._mangoproxy = None
        self._mullvad = None
        self._lock = asyncio.Lock()
        self._interactions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._interactions_reset: float = time.time()
        self._stats = {
            'impression_assigned': 0,
            'revenue_assigned': 0,
            'mangoproxy_assigned': 0,
            'mullvad_assigned': 0,
            'scraped_assigned': 0,
        }
        # Per-IP limits
        self.MANGOPROXY_MAX = 25   # ISP IPs last up to 24h, safer to rotate after 25 session interactions
        self.MULLVAD_MAX = 50      # VPN tunnel, rotate every 2h or 50 interactions

    async def _init_subsystems(self):
        """Lazy-init all proxy subsystems."""
        if self._rotator is None:
            from smart_rotator import get_rotator
            self._rotator = await get_rotator()
        if self._mangoproxy is None:
            from mangoproxy_manager import get_mangoproxy_manager
            self._mangoproxy = await get_mangoproxy_manager()
        if self._mullvad is None:
            from mullvad_manager import get_mullvad_manager
            self._mullvad = await get_mullvad_manager()

    def _reset_daily_counters(self):
        """Reset daily interaction counters if 24h passed."""
        now = time.time()
        if now - self._interactions_reset > 86400:
            self._interactions.clear()
            self._interactions_reset = now

    async def get_proxy_for_session(self,
                                     session_purpose: str = 'impression',
                                     session_value: str = 'browse',
                                     preferred_country: str = None) -> Optional[str]:
        """
        Get a proxy URL based on session purpose.

        Args:
            session_purpose: 'impression' or 'revenue'
            session_value: 'background', 'browse', 'high_value', 'ad_click'
            preferred_country: Optional 2-letter country code

        Returns:
            Proxy URL string or None
        """
        await self._init_subsystems()
        self._reset_daily_counters()

        if session_purpose == 'revenue':
            return await self._get_revenue_proxy(session_value, preferred_country)
        else:
            return await self._get_impression_proxy(session_value, preferred_country)

    async def _get_impression_proxy(self, session_value: str, country: str = None) -> Optional[str]:
        """Get proxy from scraped pool for impression-only sessions."""
        proxy = await self._rotator.assign_proxy(
            session_value=session_value,
            preferred_country=country,
            source_filter=['scraped']
        )
        if proxy:
            self._stats['impression_assigned'] += 1
            self._stats['scraped_assigned'] += 1
        return proxy

    async def _get_revenue_proxy(self, session_value: str, country: str = None) -> Optional[str]:
        """Get proxy from MangoProxy or Mullvad for revenue sessions."""
        # 70/30 split: MangoProxy ISP first (cheaper), Mullvad backup
        use_mangoproxy = random.random() < 0.70

        if use_mangoproxy:
            # Try MangoProxy ISP first
            if self._mangoproxy:
                proxy = await self._mangoproxy.get_proxy(preferred_country=country)
                if proxy:
                    ip = self._extract_ip(proxy)
                    if self._can_use_ip('mangoproxy', ip, self.MANGOPROXY_MAX):
                        self._stats['revenue_assigned'] += 1
                        self._stats['mangoproxy_assigned'] += 1
                        return proxy
                    else:
                        logger.debug(f"MangoProxy IP {ip} at limit, falling back to Mullvad")

            # MangoProxy failed — try Mullvad
            if self._mullvad:
                proxy = await self._mullvad.get_proxy_url()
                if proxy:
                    ip = self._extract_ip(proxy) or 'mullvad_tunnel'
                    if self._can_use_ip('mullvad', ip, self.MULLVAD_MAX):
                        self._stats['revenue_assigned'] += 1
                        self._stats['mullvad_assigned'] += 1
                        return proxy

        else:
            # Try Mullvad first (VPN)
            if self._mullvad:
                proxy = await self._mullvad.get_proxy_url()
                if proxy:
                    ip = self._extract_ip(proxy) or 'mullvad_tunnel'
                    if self._can_use_ip('mullvad', ip, self.MULLVAD_MAX):
                        self._stats['revenue_assigned'] += 1
                        self._stats['mullvad_assigned'] += 1
                        return proxy

            # Mullvad failed — try MangoProxy ISP
            if self._mangoproxy:
                proxy = await self._mangoproxy.get_proxy(preferred_country=country)
                if proxy:
                    ip = self._extract_ip(proxy)
                    if self._can_use_ip('mangoproxy', ip, self.MANGOPROXY_MAX):
                        self._stats['revenue_assigned'] += 1
                        self._stats['mangoproxy_assigned'] += 1
                        return proxy

        # Both paid sources exhausted — fallback to scraped with warning
        logger.warning("Revenue session using SCRAPED proxy (MangoProxy+Mullvad exhausted!)")
        proxy = await self._rotator.assign_proxy(
            session_value=session_value,
            preferred_country=country,
            source_filter=['scraped']
        )
        if proxy:
            self._stats['revenue_assigned'] += 1
            self._stats['scraped_assigned'] += 1
        return proxy

    def _extract_ip(self, proxy_url: str) -> Optional[str]:
        """Extract IP from proxy URL."""
        import re
        if not proxy_url:
            return None
        match = re.search(r'(?:@)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', proxy_url)
        return match.group(1) if match else None

    def _can_use_ip(self, source: str, ip: str, max_interactions: int) -> bool:
        """Check if IP has room for more interactions today."""
        if not ip:
            return True
        count = self._interactions[source][ip]
        return count < max_interactions

    async def record_interaction(self, proxy_url: str, session_purpose: str = 'impression'):
        """Record an ad interaction on this proxy for tracking."""
        ip = self._extract_ip(proxy_url)
        if not ip:
            return

        # Determine source from proxy URL pattern
        if '127.0.0.1' in proxy_url and '1081' in proxy_url:
            source = 'mullvad'
        elif '@' in proxy_url:
            source = 'mangoproxy'
        else:
            source = 'scraped'

        async with self._lock:
            self._interactions[source][ip] += 1

        # Also notify the respective manager
        if source == 'mangoproxy' and self._mangoproxy:
            await self._mangoproxy.record_interaction(proxy_url)
        elif source == 'mullvad' and self._mullvad:
            await self._mullvad.record_interaction()

    def get_stats(self) -> Dict:
        """Get routing statistics."""
        return {
            **self._stats,
            'mangoproxy_interactions': dict(self._interactions.get('mangoproxy', {})),
            'mullvad_interactions': dict(self._interactions.get('mullvad', {})),
            'total_interactions_tracked': sum(
                sum(ips.values()) for ips in self._interactions.values()
            ),
        }


# ============================ GLOBAL INSTANCE ============================

_router: Optional[TrafficRouter] = None


async def get_router() -> TrafficRouter:
    global _router
    if _router is None:
        _router = TrafficRouter()
    return _router