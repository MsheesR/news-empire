#!/usr/bin/env python3
"""
Health Monitor — Critical Component Watchdog
=============================================
Monitors all critical systems and AUTO-STOPS the farm if any
component fails in a way that would flag detection.

Monitored Components:
1. MangoProxy gateway health
2. Mullvad VPN tunnel status
3. Proxy pool size (minimum threshold)
4. Session success rate (below threshold = stop)

Auto-Stop Triggers:
- MangoProxy gateway DOWN for > 2 minutes → STOP
- Proxy pool drops below 50 working proxies → STOP
- Session success rate below 40% for 5 minutes → STOP

Imported and used by farm.py main loop.
"""

import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger('health_monitor')


@dataclass
class ComponentHealth:
    name: str
    healthy: bool = True
    status: str = ""
    last_ok: float = field(default_factory=time.time)
    consecutive_failures: int = 0


class HealthMonitor:
    """Watches all critical farm components and triggers auto-stop."""

    def __init__(self):
        self._components: Dict[str, ComponentHealth] = {}
        self._should_stop: bool = False
        self._stop_reason: str = ""
        self._check_interval: int = 30
        self._last_check: float = 0

    async def check_all(self) -> Tuple[bool, str]:
        """Check all components. Returns (should_stop, reason)."""
        # MangoProxy health
        try:
            from mangoproxy_manager import get_mangoproxy_manager
            mgr = await get_mangoproxy_manager()
            mgr_stats = mgr.get_stats()
            mp_healthy = mgr_stats.get('gateway_healthy', False)
            self._update('mangoproxy', mp_healthy,
                        f"Gateway: {mgr_stats.get('gateway')}, Healthy: {mp_healthy}")
            if not mp_healthy and self._consecutive('mangoproxy') > 4:
                self._should_stop = True
                self._stop_reason = "🛑 MangoProxy gateway DOWN for >2 minutes — stopping to avoid detection"
        except Exception as e:
            self._update('mangoproxy', False, f"Error: {e}")

        # Mullvad VPN health
        try:
            from vpn_tunnel import get_vpn_tunnel
            vpn = await get_vpn_tunnel()
            vpn_status = vpn.get_status()
            vpn_healthy = vpn_status.get('vpn_active', False)
            if vpn.config_exists() and not vpn_healthy:
                self._update('mullvad', False, "Config exists but tunnel DOWN")
            else:
                self._update('mullvad', True if not vpn.config_exists() else vpn_healthy,
                            f"VPN: {'Active' if vpn_healthy else 'Not required'}")
        except Exception:
            self._update('mullvad', True, "OK (not configured)")

        # Proxy pool health
        try:
            from smart_rotator import get_rotator
            rotator = await get_rotator()
            pool_stats = await rotator.get_pool_stats()
            working = pool_stats.get('working', 0)
            total = pool_stats.get('total', 0)
            healthy = working >= 50
            self._update('proxy_pool', healthy, f"Working: {working}/{total}")
            if not healthy and self._consecutive('proxy_pool') > 3:
                self._should_stop = True
                self._stop_reason = f"🛑 Proxy pool critically low: {working} working proxies"
        except Exception as e:
            self._update('proxy_pool', False, f"Error: {e}")

        return self._should_stop, self._stop_reason

    def check_session_rate(self, total_sessions: int, successful: int) -> bool:
        """Check if session success rate is dangerously low."""
        if total_sessions < 20:
            return True
        rate = successful / max(total_sessions, 1)
        healthy = rate >= 0.40
        self._update('session_rate', healthy,
                    f"Success: {successful}/{total_sessions} ({rate:.0%})")
        if not healthy and self._consecutive('session_rate') > 10:
            self._should_stop = True
            self._stop_reason = f"🛑 Session success rate critically low: {rate:.0%}"
        return healthy

    def _update(self, name: str, healthy: bool, status: str):
        if name not in self._components:
            self._components[name] = ComponentHealth(name=name)
        comp = self._components[name]
        comp.status = status
        if healthy:
            comp.healthy = True
            comp.last_ok = time.time()
            comp.consecutive_failures = 0
        else:
            comp.healthy = False
            comp.consecutive_failures += 1

    def _consecutive(self, name: str) -> int:
        comp = self._components.get(name)
        return comp.consecutive_failures if comp else 0

    def get_status(self) -> Dict:
        return {
            'should_stop': self._should_stop,
            'stop_reason': self._stop_reason,
            'components': {
                name: {'healthy': c.healthy, 'status': c.status,
                       'failures': c.consecutive_failures}
                for name, c in self._components.items()
            }
        }

    def reset(self):
        self._should_stop = False
        self._stop_reason = ""


_health_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor