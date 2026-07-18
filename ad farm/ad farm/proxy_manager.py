#!/usr/bin/env python3
"""
Proxy Manager V3 — Simplified Interface
=========================================
Unified proxy interface for the entire farm. Delegates to:
- proxy_filter.py for source aggregation & verification
- smart_rotator.py for tier-aware rotation
- geo_utils.py for geo-location

V3: Removed direct MangoProxy dependency — now uses multi-source
    open-source proxy aggregation with SQLite storage.

Usage:
    from proxy_manager import get_proxy_pool
    pool = await get_proxy_pool()
    proxy = await pool.get_proxy(session_value='browse')
    pool.mark_success(proxy)
    pool.mark_failed(proxy)
"""

import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger('proxy_manager')


class ProxyPool:
    """
    Unified proxy pool interface. Delegates everything to
    proxy_filter + smart_rotator subsystems.
    """

    def __init__(self):
        self._rotator = None
        self._filter = None
        self._stats = {"assigned": 0, "success": 0, "failed": 0}

    async def _init(self):
        if self._rotator is None:
            from smart_rotator import get_rotator
            self._rotator = await get_rotator()
        if self._filter is None:
            from proxy_filter import get_proxy_filter
            self._filter = await get_proxy_filter()

    async def init_webshare_mullvad(self):
        """Initialize MangoProxy ISP and Mullvad VPN subsystems for revenue sessions."""
        try:
            from mangoproxy_manager import get_mangoproxy_manager
            mgr = await get_mangoproxy_manager()
            await mgr.initialize()
        except Exception:
            pass
        try:
            from mullvad_manager import get_mullvad_manager
            mvm = await get_mullvad_manager()
            await mvm.connect()
        except Exception:
            pass

    async def get_proxy(self, session_value: str = 'browse',
                        session_purpose: str = 'impression') -> Optional[str]:
        """Get a proxy for a session. Purpose-aware routing.
        
        Args:
            session_value: 'background', 'browse', 'high_value', 'ad_click'
            session_purpose: 'impression' (scraped) or 'revenue' (webshare/mullvad)
        """
        from traffic_router import get_router
        router = await get_router()
        proxy = await router.get_proxy_for_session(
            session_purpose=session_purpose,
            session_value=session_value
        )
        if proxy:
            self._stats["assigned"] += 1
        return proxy

    async def mark_success(self, proxy_url: str):
        """Mark proxy session as successful."""
        await self._init()
        await self._rotator.release_proxy(proxy_url, success=True)
        self._stats["success"] += 1

    async def mark_failed(self, proxy_url: str):
        """Mark proxy session as failed (triggers auto-ban after 2)."""
        await self._init()
        await self._rotator.release_proxy(proxy_url, success=False)
        self._stats["failed"] += 1

    async def refresh_pool(self, force: bool = False) -> int:
        """Refresh proxy pool from all sources."""
        await self._init()
        return await self._filter.full_pipeline()

    def get_stats(self) -> Dict:
        """Get pool statistics."""
        return {
            "assigned": self._stats["assigned"],
            "success": self._stats["success"],
            "failed": self._stats["failed"],
        }

    async def cleanup(self):
        if self._filter:
            await self._filter.close()


# === GLOBAL INSTANCE ===
_pool: Optional[ProxyPool] = None

async def get_proxy_pool() -> ProxyPool:
    global _pool
    if _pool is None:
        _pool = ProxyPool()
    return _pool

async def cleanup_proxy_pool():
    global _pool
    if _pool:
        await _pool.cleanup()
        _pool = None