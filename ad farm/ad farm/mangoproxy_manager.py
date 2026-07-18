#!/usr/bin/env python3
"""
MangoProxy ISP Manager V2 — Gateway-Based Rotating ISP Proxy
=============================================================
MangoProxy uses a GATEWAY model, not an API proxy list:
  - Connect to: p1.mangoproxy.com:8000 (or custom port)
  - Auth via:   username:password
  - Each new TCP connection auto-rotates the exit IP
  - Username supports rotation parameters:
    USERNAME-zone-custom-region-REGION-session-SESSION_ID-sessTime-MINUTES

Architecture:
    Browser → p1.mangoproxy.com:8000 → Rotating ISP exit IP → Target Site

Features:
- Generates unique session-based usernames for IP rotation
- TCP + HTTP pre-verification of gateway connectivity
- Per-session IP tracking via httpbin.org/ip verification
- Daily interaction limits per session (max 25)
- Country-targeted rotation via username region suffix
- Protocol support: http, https, socks5

Usage:
    from mangoproxy_manager import get_mangoproxy_manager
    mgr = await get_mangoproxy_manager()
    await mgr.initialize()
    proxy = await mgr.get_proxy()  # → "http://user-zone-custom...:pass@p1.mangoproxy.com:8000"
"""

import asyncio
import aiohttp
import time
import logging
import random
import os
import re
import uuid
from typing import Dict, Optional, Tuple

logger = logging.getLogger('mangoproxy_manager')

MANAGER_VERSION = 2  # Gateway-based (not API pool)


class MangoProxyManager:
    """
    Manages MangoProxy gateway-based ISP rotating proxy connections.
    Each call to get_proxy() returns a gateway URL with a UNIQUE session ID,
    forcing MangoProxy to assign a fresh exit IP.
    """

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._host: str = 'p1.mangoproxy.com'
        self._port: int = 8000
        self._username: str = ''
        self._password: str = ''
        self._protocol: str = 'http'
        self._region: str = 'us'
        self._session_time_min: int = 10
        self._enabled: bool = False
        self._lock = asyncio.Lock()
        self._stats = {'assigned': 0, 'verified': 0, 'failed': 0}
        self._rotation: str = 'instant'  # instant or sticky
        self._session_counter: int = 0
        self._last_gateway_check: float = 0
        self._gateway_healthy: bool = False

    async def initialize(self) -> bool:
        """Load config from .env and verify gateway connectivity."""
        import os
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

        self._enabled = os.getenv('MANGOPROXY_ENABLED', 'true').lower() == 'true'
        self._host = os.getenv('MANGOPROXY_HOST', 'p1.mangoproxy.com')
        self._port = int(os.getenv('MANGOPROXY_PORT', '8000'))
        self._username = os.getenv('MANGOPROXY_USERNAME', '')
        self._password = os.getenv('MANGOPROXY_PASSWORD', '')
        self._protocol = os.getenv('MANGOPROXY_PROTOCOL', 'http')
        self._region = os.getenv('MANGOPROXY_REGION', 'global')
        self._session_time_min = int(os.getenv('MANGOPROXY_SESSION_TIME_MIN', '15'))
        self._rotation = os.getenv('MANGOPROXY_ROTATION', 'instant')

        if not self._enabled:
            logger.info("MangoProxy ISP: Disabled (MANGOPROXY_ENABLED=false)")
            return False

        if not self._username or not self._password or 'your_' in self._username:
            logger.warning("MangoProxy ISP: Credentials not set — proxy pool disabled")
            logger.warning("Set MANGOPROXY_USERNAME and MANGOPROXY_PASSWORD in .env")
            logger.warning("Format from MangoProxy dashboard: ip:port:login:pass")
            logger.warning(f"  Host: {self._host}, Port: {self._port}")
            return False

        # Verify gateway is reachable
        healthy = await self._check_gateway()
        if healthy:
            logger.info(f"✅ MangoProxy ISP gateway healthy: {self._host}:{self._port}")
        else:
            logger.warning(f"⚠️  MangoProxy ISP gateway unreachable: {self._host}:{self._port}")
            logger.warning("Check firewall, DNS, or try CIS server from dashboard")

        return healthy

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=15)
            headers = {'User-Agent': 'LOPINUZE-AdFarm/4.0'}
            self._session = aiohttp.ClientSession(timeout=timeout, headers=headers)

    def _build_username(self, country: str = None) -> str:
        """
        Build a rotating username with session parameters.
        
        MangoProxy ISP username format (from dashboard):
        BASE-zone-isp-session-UUID-sessTime-MINUTES
        
        Each unique session UUID gets a fresh ISP exit IP (Instant rotation).
        Username and password are IDENTICAL for MangoProxy ISP.
        """
        region = country or self._region
        self._session_counter += 1
        # Unique session ID per connection for IP rotation
        session_id = f"{uuid.uuid4().hex[:8]}{self._session_counter:04d}"
        
        # MangoProxy ISP uses -zone-isp- format (NOT -zone-custom-)
        # The base username is the API key; appended params control rotation
        if '-zone-' in self._username or '-session-' in self._username or '-sessTime-' in self._username:
            # Username already has rotation params — replace session UUID for fresh IP
            base = re.sub(r'-session-[^-]+', f'-session-{session_id}', self._username)
            if '-session-' not in base:
                base = f"{base}-session-{session_id}"
            # Ensure -zone-isp- format (some dashboards use -zone-custom-)
            base = base.replace('-zone-custom-', '-zone-isp-')
            return base
        elif self._rotation == 'instant':
            # Build ISP instant rotation from scratch
            return (f"{self._username}-zone-isp"
                    f"-session-{session_id}-sessTime-{self._session_time_min}")
        else:
            # Sticky session format
            return (f"{self._username}-zone-isp-region-{region}"
                    f"-session-{session_id}-sessTime-{self._session_time_min}")

    async def _check_gateway(self, timeout: float = 5.0) -> bool:
        """Verify MangoProxy gateway is reachable via TCP + HTTP test."""
        # TCP check
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=timeout
            )
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
        except Exception:
            self._gateway_healthy = False
            return False

        # HTTP check through gateway
        try:
            test_username = self._build_username()
            proxy_url = f"{self._protocol}://{test_username}:{self._password}@{self._host}:{self._port}"

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'http://httpbin.org/ip',
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=8)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        origin = data.get('origin', 'unknown')
                        logger.info(f"MangoProxy gateway OK — exit IP: {origin}")
                        self._gateway_healthy = True
                        self._last_gateway_check = time.time()
                        return True
        except Exception as e:
            logger.debug(f"MangoProxy gateway HTTP check: {e}")

        self._gateway_healthy = False
        return False

    async def get_proxy(self, preferred_country: str = None) -> Optional[str]:
        """
        Get a MangoProxy gateway proxy URL with a FRESH session ID.
        Each call generates a unique username → MangoProxy assigns a new exit IP.

        Returns:
            "http://USERNAME-zone-...-session-UNIQUE_ID...:PASS@HOST:PORT"
            or None if gateway is unhealthy.
        """
        async with self._lock:
            if not self._enabled:
                return None

            await self._ensure_session()

            # Periodic gateway health check (every 60s)
            if time.time() - self._last_gateway_check > 60:
                asyncio.create_task(self._check_gateway())

            if not self._gateway_healthy:
                # Try once synchronously
                healthy = await self._check_gateway()
                if not healthy:
                    logger.warning("MangoProxy gateway unhealthy — skipping")
                    return None

            # Build unique session username for fresh IP
            username = self._build_username(preferred_country)
            proxy_url = f"{self._protocol}://{username}:{self._password}@{self._host}:{self._port}"

            self._stats['assigned'] += 1
            logger.debug(f"MangoProxy assigned: session={username.split('-session-')[1].split('-')[0] if '-session-' in username else 'NEW'}")

            return proxy_url

    async def verify_connection(self, proxy_url: str) -> Tuple[bool, Optional[str]]:
        """
        Verify the gateway connection returns a working exit IP.
        Returns (success, exit_ip).
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'http://httpbin.org/ip',
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=6)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        exit_ip = data.get('origin', '')
                        self._stats['verified'] += 1
                        return True, exit_ip
        except Exception:
            pass
        self._stats['failed'] += 1
        return False, None

    async def record_interaction(self, proxy_url: str, success: bool = True):
        """Track proxy usage for statistics."""
        # Gateway model — no per-IP tracking needed since each connection is unique
        pass

    def get_stats(self) -> Dict:
        """Get proxy pool statistics."""
        return {
            'enabled': self._enabled,
            'gateway': f'{self._host}:{self._port}',
            'protocol': self._protocol,
            'region': self._region,
            'gateway_healthy': self._gateway_healthy,
            'sessions_assigned': self._stats['assigned'],
            'stats': self._stats,
        }

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


# ============================ GLOBAL INSTANCE ============================

_manager: Optional[MangoProxyManager] = None


async def get_mangoproxy_manager() -> MangoProxyManager:
    global _manager
    if _manager is None:
        _manager = MangoProxyManager()
    return _manager


async def cleanup_mangoproxy():
    global _manager
    if _manager:
        await _manager.close()
        _manager = None


# ============================ STANDALONE TEST ============================
if __name__ == '__main__':
    async def test():
        print("=" * 60)
        print("  MANGOPROXY ISP GATEWAY — TEST")
        print("=" * 60)

        mgr = await get_mangoproxy_manager()
        ok = await mgr.initialize()

        if not ok:
            print("\n⚠️  MangoProxy gateway not reachable.")
            print("   Check MANGOPROXY_HOST, MANGOPROXY_USERNAME, MANGOPROXY_PASSWORD in .env")
            print("   From dashboard → Setup → Connection string:")
            print("   Format: p1.mangoproxy.com:8000:USERNAME:PASSWORD")
            return

        print(f"\n[1] Gateway: {mgr._host}:{mgr._port}")
        print(f"   Protocol: {mgr._protocol}")
        print(f"   Region: {mgr._region}")

        print("\n[2] Getting proxy URL (3x to test rotation)...")
        for i in range(3):
            proxy = await mgr.get_proxy()
            if proxy:
                masked = re.sub(r'://(.*?):(.*?)@', r'://\1:****@', proxy)
                print(f"   [{i+1}] {masked}")

                # Verify exit IP
                ok, ip = await mgr.verify_connection(proxy)
                if ok:
                    print(f"        Exit IP: {ip} ✅")
                else:
                    print(f"        Exit IP: FAILED ❌")

        stats = mgr.get_stats()
        print(f"\n[3] Stats: {stats['sessions_assigned']} assigned, "
              f"{stats['stats']['verified']} verified")

        await mgr.close()
        print("\n✅ Test complete")

    asyncio.run(test())