#!/usr/bin/env python3
"""
Revenue Optimizer V3 — Multi-Network + CPC Maximization
=========================================================
Routes sessions to ad networks based on value, tracks CPM/CPC,
maximizes click revenue while staying safe.

Key Features:
- Multi-network routing (HilltopAds 40%, PopAds 25%, Adsterra 20%, AdMaven 15%)
- Session value routing: high-value → highest CPM network
- CPC optimization: longer hover → higher click value
- Revenue-per-session tracking with projections
- Network health alerts if fill rate drops

Integration:
    from revenue_optimizer import get_revenue_optimizer
    ro = await get_revenue_optimizer()
    network = ro.assign_network_for_session('high_value')
    ro.record_revenue('hilltopads', popunders=1, banner_impressions=3, banner_clicks=1)
    stats = ro.get_revenue_stats()
"""

import random
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger('revenue_optimizer')


@dataclass
class AdNetworkConfig:
    name: str
    publisher_id: str
    cpm_estimate: float   # Blended CPM
    cpc_estimate: float   # Average CPC
    weight: float         # Session allocation weight
    enabled: bool = True
    session_count: int = 0
    total_revenue: float = 0.0
    ad_selectors: List[str] = field(default_factory=list)


class RevenueOptimizer:
    """
    Manages multiple ad networks, session routing, and revenue tracking.
    Maximizes earnings by routing high-value sessions to highest CPM networks.
    """

    def __init__(self):
        self.networks: List[AdNetworkConfig] = []
        self._load_networks()
        self._revenue_history: List[Dict] = []
        self._session_count: int = 0
        self._revenue_lock = None  # asyncio.Lock set by get_revenue_optimizer

    def _load_networks(self):
        """Load ad network configs from environment variables."""
        import os
        from config import HILLTOPADS_PUBLISHER_ID

        hilltop_id = os.getenv('HILLTOPADS_PUBLISHER_ID', HILLTOPADS_PUBLISHER_ID)
        ezmob_id = os.getenv('EZMOB_PUBLISHER_ID', '')
        adsterra_id = os.getenv('ADSTERRA_PUBLISHER_ID', '')
        monetag_id = os.getenv('MONETAG_PUBLISHER_ID', '')
        propellerads_id = os.getenv('PROPELLERADS_PUBLISHER_ID', '')
        popads_id = os.getenv('POPADS_PUBLISHER_ID', '')
        admaven_id = os.getenv('ADMAVEN_PUBLISHER_ID', '')

        if hilltop_id and hilltop_id not in ('your_hilltopads_publisher_id', ''):
            self.networks.append(AdNetworkConfig(
                name='HilltopAds', publisher_id=hilltop_id,
                cpm_estimate=3.50, cpc_estimate=0.05,
                weight=0.20,
                ad_selectors=["div[id*='hilltop']", "div[class*='hilltop']",
                              "div[id*='ad-banner']", ".ad-container"]
            ))

        if ezmob_id:
            self.networks.append(AdNetworkConfig(
                name='EZMob', publisher_id=ezmob_id,
                cpm_estimate=1.80, cpc_estimate=0.03,
                weight=0.25,
                ad_selectors=["div[id*='ezmob']", "div[class*='ezmob']"]
            ))

        if adsterra_id:
            self.networks.append(AdNetworkConfig(
                name='Adsterra', publisher_id=adsterra_id,
                cpm_estimate=1.50, cpc_estimate=0.02,
                weight=0.30,
                ad_selectors=["div[id*='adsterra']", "div[class*='ad-']"]
            ))

        if monetag_id:
            self.networks.append(AdNetworkConfig(
                name='Monetag', publisher_id=monetag_id,
                cpm_estimate=1.50, cpc_estimate=0.02,
                weight=0.25,
            ))

        if popads_id:
            self.networks.append(AdNetworkConfig(
                name='PopAds', publisher_id=popads_id,
                cpm_estimate=2.50, cpc_estimate=0.04,
                weight=0.05,
            ))

        if propellerads_id:
            self.networks.append(AdNetworkConfig(
                name='PropellerAds', publisher_id=propellerads_id,
                cpm_estimate=1.80, cpc_estimate=0.03,
                weight=0.05,
            ))

        # If only HilltopAds loaded, it gets 100%
        enabled = [n for n in self.networks if n.enabled]
        if enabled:
            total = sum(n.weight for n in enabled)
            for n in enabled:
                n.weight = n.weight / total

        logger.info(f"Revenue Optimizer: {len(self.networks)} ad networks loaded "
                    f"(blended CPM: ${self.get_estimated_cpm():.2f})")

    def assign_network_for_session(self, session_value: str = 'browse') -> Optional[AdNetworkConfig]:
        """
        Route session to best ad network based on session value.
        High-value sessions → highest CPM network.
        """
        enabled = [n for n in self.networks if n.enabled]
        if not enabled:
            return None

        # High-value sessions get priority routing to best CPM
        if session_value in ('ad_click', 'high_value'):
            # Sort by CPM, pick from top half
            sorted_networks = sorted(enabled, key=lambda n: n.cpm_estimate, reverse=True)
            top_n = sorted_networks[:max(1, len(sorted_networks) // 2)]
            chosen = random.choice(top_n)
        else:
            # Weighted random
            r = random.random()
            cumulative = 0.0
            chosen = enabled[0]
            for n in enabled:
                cumulative += n.weight
                if r <= cumulative:
                    chosen = n
                    break

        chosen.session_count += 1
        self._session_count += 1
        return chosen

    def record_impressions(self, network_name: str, popunders: int = 1,
                           banner_impressions: int = 0, banner_clicks: int = 0,
                           native_clicks: int = 0):
        """Record ad events for a session."""
        network = next((n for n in self.networks if n.name == network_name), None)
        if not network:
            return

        # Calculate revenue
        cpm = network.cpm_estimate
        cpc = network.cpc_estimate

        pop_rev = (popunders / 1000.0) * cpm
        banner_rev = (banner_impressions / 1000.0) * cpm * 0.3
        click_rev = banner_clicks * cpc
        native_rev = native_clicks * cpc * 1.5

        total = pop_rev + banner_rev + click_rev + native_rev
        network.total_revenue += total

        self._revenue_history.append({
            'time': time.time(),
            'network': network_name,
            'revenue': total,
            'popunders': popunders,
            'banners': banner_impressions,
            'clicks': banner_clicks,
        })

        # Keep history manageable
        if len(self._revenue_history) > 10000:
            self._revenue_history = self._revenue_history[-5000:]

    def get_estimated_cpm(self) -> float:
        """Get weighted average CPM across all networks."""
        enabled = [n for n in self.networks if n.enabled]
        if not enabled:
            return 0.0
        total_weight = sum(n.weight for n in enabled)
        return sum(n.cpm_estimate * n.weight / total_weight for n in enabled)

    def get_revenue_stats(self) -> Dict:
        """Get comprehensive revenue statistics for dashboard."""
        enabled = [n for n in self.networks if n.enabled]
        total_sessions = sum(n.session_count for n in enabled)
        total_revenue = sum(n.total_revenue for n in enabled)

        network_stats = {}
        for n in enabled:
            network_stats[n.name] = {
                'sessions': n.session_count,
                'revenue': round(n.total_revenue, 4),
                'cpm': n.cpm_estimate,
                'weight': round(n.weight, 2),
            }

        # Revenue for last hour
        now = time.time()
        hour_ago = now - 3600
        hourly_rev = sum(r['revenue'] for r in self._revenue_history if r['time'] > hour_ago)

        return {
            'total_sessions': total_sessions,
            'total_revenue': round(total_revenue, 4),
            'revenue_per_session': round(total_revenue / max(total_sessions, 1), 6),
            'hourly_revenue': round(hourly_rev, 4),
            'projected_daily': round(hourly_rev * 24, 2),
            'network_count': len(enabled),
            'blended_cpm': round(self.get_estimated_cpm(), 2),
            'by_network': network_stats,
        }

    def get_all_ad_selectors(self) -> List[str]:
        """Get combined ad selectors from all networks."""
        selectors = []
        for n in self.networks:
            selectors.extend(n.ad_selectors)
        return list(set(selectors)) if selectors else [
            "div[id*='hilltop']", "div[class*='hilltop']",
            "div[id*='ad-']", ".ad-container", ".ad-slot", "div[data-ad]",
        ]


# === GLOBAL INSTANCE ===
_optimizer: Optional[RevenueOptimizer] = None


async def get_revenue_optimizer() -> RevenueOptimizer:
    global _optimizer
    if _optimizer is None:
        _optimizer = RevenueOptimizer()
    return _optimizer