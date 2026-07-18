#!/usr/bin/env python3
"""
VPN Tunnel — Mullvad WireGuard Integration (V4)
=================================================
Uses Mullvad VPN (WireGuard) for clean residential exit IPs.
Mullvad exit IPs are NOT on public proxy/VPN blacklists.

Architecture:
    Browser → Mullvad WireGuard (SOCKS5 tunnel) → Target Site
    
Features:
- Auto-generates WireGuard configs from Mullvad API
- Multi-country rotation (US, UK, DE, NL, CH, CA, SE, NO, FR, JP)
- Health monitoring + auto-reconnect
- Per-IP ad interaction tracking
- Falls back to proxy-only mode if WireGuard not installed

Setup:
    1. Sign up at https://mullvad.net (€5/month)
    2. Get your 16-digit account number
    3. Set MULLVAD_ACCOUNT in .env
    4. Install WireGuard: https://www.wireguard.com/install/
    5. Run the farm — configs auto-generate

Usage:
    from vpn_tunnel import get_vpn_tunnel
    vpn = await get_vpn_tunnel()
    await vpn.connect()
"""

import asyncio
import time
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger('vpn_tunnel')


class VPNTunnel:
    """
    VPN tunnel using Mullvad WireGuard for clean residential exit IPs.
    Compatible with session_engine.py API.
    """

    def __init__(self):
        self._mullvad = None
        self._connected = False

    async def _init_mullvad(self):
        if self._mullvad is None:
            from mullvad_manager import get_mullvad_manager
            self._mullvad = await get_mullvad_manager()

    def config_exists(self) -> bool:
        """Check if Mullvad WireGuard configs exist."""
        from config import MULLVAD_ACCOUNT, MULLVAD_WG_DIR
        if not MULLVAD_ACCOUNT or 'your_' in MULLVAD_ACCOUNT:
            return False
        wg_dir = MULLVAD_WG_DIR
        if os.path.isdir(wg_dir):
            confs = [f for f in os.listdir(wg_dir) if f.endswith('.conf')]
            return len(confs) > 0
        return False

    async def connect(self) -> bool:
        """Connect to Mullvad VPN tunnel."""
        await self._init_mullvad()

        if self._mullvad:
            status = self._mullvad.get_status()
            if status.get('connected'):
                self._connected = True
                return True

            connected = await self._mullvad.connect()
            if connected:
                self._connected = True
                logger.info("✅ Mullvad VPN connected — WireGuard tunnel active")
                return True

        # Fallback: proxy-only mode (Webshare proxies handle revenue)
        logger.info("ℹ️  Mullvad not available — using proxy-only mode (Webshare + scraped)")
        self._connected = True  # Mark as "not blocking" — proxies work
        return True

    async def disconnect(self):
        """Disconnect Mullvad tunnel."""
        self._connected = False
        if self._mullvad:
            await self._mullvad.disconnect()

    async def is_healthy(self) -> bool:
        """Check if tunnel is healthy."""
        return self._connected

    def get_status(self) -> Dict:
        """Get VPN status for dashboard display."""
        if self._mullvad:
            status = self._mullvad.get_status()
            return {
                'connected': status.get('connected', False),
                'type': 'Mullvad WireGuard',
                'active_country': status.get('active_country'),
                'exit_ip': status.get('exit_ip'),
                'configs': status.get('configs_downloaded', 0),
                'rotations': status.get('stats', {}).get('total_rotations', 0),
            }
        return {
            'connected': False,
            'type': 'Mullvad WireGuard (not configured)',
        }

    @staticmethod
    def generate_client_config(*args, **kwargs) -> str:
        return ""
    @staticmethod
    def save_config(*args, **kwargs) -> str:
        return ""


# ============================ GLOBAL INSTANCE ============================

_tunnel: Optional[VPNTunnel] = None


async def get_vpn_tunnel() -> VPNTunnel:
    global _tunnel
    if _tunnel is None:
        _tunnel = VPNTunnel()
    return _tunnel


async def ensure_vpn_connected() -> bool:
    """Ensure VPN is connected. Returns True if active (or proxy-only mode)."""
    t = await get_vpn_tunnel()
    if not t._connected:
        return await t.connect()
    return True