#!/usr/bin/env python3
"""
VPN Tunnel — Mullvad WireGuard Integration V5 (HONEST STATUS)
===============================================================
Returns TRUE connection status — does NOT lie about VPN being connected.

Architecture:
    Browser → Mullvad WireGuard (SOCKS5 tunnel) → Target Site
"""

import asyncio
import time
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger('vpn_tunnel')


class VPNTunnel:
    """VPN tunnel using Mullvad WireGuard. Returns HONEST connection status."""

    def __init__(self):
        self._mullvad = None
        self._connected = False
        self._vpn_active = False  # Verified — actual tunnel is up
        self.session: Optional[asyncio.AbstractEventLoop] = None

    async def _init_mullvad(self):
        if self._mullvad is None:
            from mullvad_manager import get_mullvad_manager
            self._mullvad = await get_mullvad_manager()

    def config_exists(self) -> bool:
        from config import MULLVAD_ACCOUNT, MULLVAD_WG_DIR
        if not MULLVAD_ACCOUNT or 'your_' in MULLVAD_ACCOUNT:
            return False
        wg_dir = MULLVAD_WG_DIR
        if os.path.isdir(wg_dir):
            confs = [f for f in os.listdir(wg_dir) if f.endswith('.conf')]
            return len(confs) > 0
        return False

    async def connect(self) -> bool:
        """Connect to Mullvad VPN. Returns ACTUAL connection status (no lies)."""
        await self._init_mullvad()

        if self._mullvad:
            status = self._mullvad.get_status()
            if status.get('connected'):
                self._connected = True
                self._vpn_active = True
                return True

            connected = await self._mullvad.connect()
            if connected:
                self._connected = True
                self._vpn_active = True
                logger.info("✅ Mullvad VPN connected — WireGuard tunnel active")
                return True

        # VPN FAILED — report honestly
        logger.warning("⚠️  Mullvad VPN FAILED — proxy-only mode (no double-hop)")
        self._connected = False
        self._vpn_active = False
        return False

    async def disconnect(self):
        self._connected = False
        self._vpn_active = False
        if self._mullvad:
            await self._mullvad.disconnect()

    async def is_healthy(self) -> bool:
        """Check if VPN tunnel is actually verified as healthy."""
        if not self._connected or not self._vpn_active:
            return False
        if self._mullvad:
            status = self._mullvad.get_status()
            return status.get('connected', False)
        return False

    def get_status(self) -> Dict:
        """Get HONEST VPN status."""
        if self._mullvad:
            status = self._mullvad.get_status()
            return {
                'connected': self._connected,
                'vpn_active': self._vpn_active,  # NEW: actual verification
                'type': 'Mullvad WireGuard',
                'active_country': status.get('active_country'),
                'exit_ip': status.get('exit_ip'),
                'configs': status.get('configs_downloaded', 0),
            }
        return {
            'connected': False,
            'vpn_active': False,
            'type': 'Mullvad WireGuard (not configured)',
        }

    @staticmethod
    def generate_client_config(*args, **kwargs) -> str:
        return ""
    @staticmethod
    def save_config(*args, **kwargs) -> str:
        return ""


_tunnel: Optional[VPNTunnel] = None


async def get_vpn_tunnel() -> VPNTunnel:
    global _tunnel
    if _tunnel is None:
        _tunnel = VPNTunnel()
    return _tunnel


async def ensure_vpn_connected() -> bool:
    t = await get_vpn_tunnel()
    if not t._connected:
        return await t.connect()
    return True