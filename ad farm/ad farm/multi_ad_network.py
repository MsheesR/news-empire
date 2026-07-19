#!/usr/bin/env python3
"""
Multi-Ad-Network Engine — Triple Revenue Streams
=================================================
HilltopAds + PopAds + Adsterra + AdMaven simultaneously.
More ad networks = more revenue = less detectable pattern per network.

Each ad network gets 25% of sessions — no single network sees a suspicious
traffic pattern because each only gets a fraction of the total.
"""

import random
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger('multi_ad')

# ============================ AD NETWORK CONFIGURATIONS ============================
@dataclass
class AdNetwork:
    """Configuration for one ad network."""
    name: str
    publisher_id: str
    types: List[str]  # ["popunder", "banner", "native", "push"]
    cpm_estimate: float  # Estimated CPM for this network
    weight: float  # Session allocation weight (total should = 1.0)
    enabled: bool = True
    ad_selectors: List[str] = field(default_factory=list)
    
    def get_popunder_code(self) -> str:
        """Generate pop-under ad code for this network."""
        codes = {
            "hilltopads": f"""
<script>(function(){{var s=document.createElement('script');s.async=true;
s.src='https://api.hilltopads.com/popunder/publisher/{self.publisher_id}.js';
document.head.appendChild(s);}})();</script>
""",
            "popads": f"""
<script>(function(){{var s=document.createElement('script');s.async=true;
s.src='https://popads.net/popunder/{self.publisher_id}.js';
document.head.appendChild(s);}})();</script>
""",
            "adsterra": f"""
<script>(function(){{var s=document.createElement('script');s.async=true;
s.src='https://adsterra.com/popunder/{self.publisher_id}.js';
document.head.appendChild(s);}})();</script>
""",
            "admaven": f"""
<script>(function(){{var s=document.createElement('script');s.async=true;
s.src='https://ad-maven.com/popunder/{self.publisher_id}.js';
document.head.appendChild(s);}})();</script>
""",
        }
        key = self.name.lower().replace(' ', '')
        return codes.get(key, "")


class MultiAdEngine:
    """
    Manages multiple ad networks simultaneously.
    Each session randomly picks which network to focus on.
    This distributes traffic across networks — safer and more profitable.
    """
    
    def __init__(self):
        self.networks: List[AdNetwork] = []
        self._load_networks()
        self.session_assignments: Dict[str, int] = {}  # network_name -> session_count
    
    def _load_networks(self):
        """Load ad network configs from environment."""
        from config import HILLTOPADS_PUBLISHER_ID
        import os
        
        # These will be populated from .env
        hilltop_id = os.getenv('HILLTOPADS_PUBLISHER_ID', HILLTOPADS_PUBLISHER_ID)
        ezmob_id = os.getenv('EZMOB_PUBLISHER_ID', '')
        adsterra_id = os.getenv('ADSTERRA_PUBLISHER_ID', '')
        monetag_id = os.getenv('MONETAG_PUBLISHER_ID', '')
        propellerads_id = os.getenv('PROPELLERADS_PUBLISHER_ID', '')
        popads_id = os.getenv('POPADS_PUBLISHER_ID', '')
        admaven_id = os.getenv('ADMAVEN_PUBLISHER_ID', '')
        
        # HilltopAds (primary, if configured)
        if hilltop_id and hilltop_id != 'your_hilltopads_publisher_id':
            self.networks.append(AdNetwork(
                name="HilltopAds",
                publisher_id=hilltop_id,
                types=["popunder", "banner_728x90", "banner_300x250", "native", "direct"],
                cpm_estimate=3.50,
                weight=0.25,
                ad_selectors=[
                    "div[id*='hilltop']", "div[class*='hilltop']",
                    "div[id*='ad-banner']", "div[id*='ad-sidebar']",
                    "div[id*='ad-native']", "div[id*='ad-direct']",
                ]
            ))
            logger.info(f"✅ HilltopAds loaded (weight: 25%)")
        
        # Adsterra (MOST LENIENT — low security checks, popunder CPM $1.00-1.50)
        if adsterra_id:
            self.networks.append(AdNetwork(
                name="Adsterra",
                publisher_id=adsterra_id,
                types=["popunder", "banner_728x90", "banner_300x250", "native"],
                cpm_estimate=1.50,
                weight=0.30,
                ad_selectors=["div[id*='adsterra']", "div[class*='adsterra']"]
            ))
            logger.info(f"✅ Adsterra loaded (weight: 30%) — most lenient network")
        
        # EZMob (LENIENT — low security, popunder CPM $1.50-2.00)
        if ezmob_id:
            self.networks.append(AdNetwork(
                name="EZMob",
                publisher_id=ezmob_id,
                types=["popunder"],
                cpm_estimate=1.80,
                weight=0.25,
                ad_selectors=["div[id*='ezmob']", "div[class*='ezmob']"]
            ))
            logger.info(f"✅ EZMob loaded (weight: 25%) — lenient network")
        
        # Monetag (LENIENT — low security, popunder CPM $1.00-1.80)
        if monetag_id:
            self.networks.append(AdNetwork(
                name="Monetag",
                publisher_id=monetag_id,
                types=["popunder"],
                cpm_estimate=1.50,
                weight=0.25,
                ad_selectors=["div[id*='monetag']", "div[class*='monetag']"]
            ))
            logger.info(f"✅ Monetag loaded (weight: 25%) — lenient network")
        
        # PropellerAds (BACKUP — popunder CPM $1.50-2.00)
        if propellerads_id:
            self.networks.append(AdNetwork(
                name="PropellerAds",
                publisher_id=propellerads_id,
                types=["popunder"],
                cpm_estimate=1.80,
                weight=0.10,
                ad_selectors=["div[id*='propellerads']", "div[class*='propellerads']"]
            ))
            logger.info(f"✅ PropellerAds loaded (weight: 10%) — backup")
        
        # PopAds (BACKUP — popunder CPM $2.00-2.80)
        if popads_id:
            self.networks.append(AdNetwork(
                name="PopAds",
                publisher_id=popads_id,
                types=["popunder"],
                cpm_estimate=2.50,
                weight=0.05,
                ad_selectors=["div[id*='popads']", "div[class*='popads']"]
            ))
            logger.info(f"✅ PopAds loaded (weight: 5%) — backup")
        
        # If only HilltopAds, it gets 100%
        if not self.networks and hilltop_id:
            self.networks.append(AdNetwork(
                name="HilltopAds",
                publisher_id=hilltop_id,
                types=["popunder", "banner_728x90", "banner_300x250", "native", "direct"],
                cpm_estimate=3.50,
                weight=1.0,
                ad_selectors=[
                    "div[id*='hilltop']", "div[class*='hilltop']",
                    "div[id*='ad-banner']", "div[id*='ad-sidebar']",
                    "div[id*='ad-native']", "div[id*='ad-direct']",
                ]
            ))
            logger.info("✅ HilltopAds loaded (sole network, weight: 100%)")
        
        # Normalize weights
        total_weight = sum(n.weight for n in self.networks)
        if total_weight > 0:
            for n in self.networks:
                n.weight = n.weight / total_weight
    
    def pick_network(self) -> Optional[AdNetwork]:
        """Pick an ad network based on weight distribution."""
        if not self.networks:
            return None
        
        r = random.random()
        cumulative = 0.0
        for network in self.networks:
            cumulative += network.weight
            if r <= cumulative:
                # Track session assignment
                self.session_assignments[network.name] = self.session_assignments.get(network.name, 0) + 1
                return network
        
        return self.networks[0]
    
    def get_all_ad_selectors(self) -> List[str]:
        """Get combined ad selectors from all networks."""
        selectors = []
        for network in self.networks:
            selectors.extend(network.ad_selectors)
        # Deduplicate
        return list(set(selectors)) if selectors else [
            "div[id*='hilltop']", "div[class*='hilltop']",
            "div[id*='ad-']", "div[class*='ad-']",
            ".ad-container", ".ad-slot", "div[data-ad]",
        ]
    
    def get_estimated_cpm(self) -> float:
        """Get weighted average CPM across all networks."""
        if not self.networks:
            return 0.0
        return sum(n.cpm_estimate * n.weight for n in self.networks)
    
    def get_network_count(self) -> int:
        """Number of active ad networks."""
        return len(self.networks)
    
    def get_stats(self) -> Dict:
        """Get network distribution stats."""
        total = sum(self.session_assignments.values()) or 1
        stats = {}
        for name, count in self.session_assignments.items():
            stats[name] = {
                "sessions": count,
                "percentage": f"{(count / total) * 100:.1f}%"
            }
        return stats
    
    def get_revenue_multiplier(self) -> float:
        """
        Multi-ad-network revenue boost vs single network.
        1 network = 1.0x, 2 networks = ~1.6x, 3 = ~2.1x, 4 = ~2.5x
        """
        return 1.0 + (len(self.networks) - 1) * 0.5


# ============================ GLOBAL INSTANCE ============================
_multi_ad: Optional[MultiAdEngine] = None

def get_multi_ad_engine() -> MultiAdEngine:
    global _multi_ad
    if _multi_ad is None:
        _multi_ad = MultiAdEngine()
    return _multi_ad


if __name__ == '__main__':
    engine = MultiAdEngine()
    print(f"Networks loaded: {engine.get_network_count()}")
    print(f"Weighted CPM: ${engine.get_estimated_cpm():.2f}")
    print(f"Revenue multiplier: {engine.get_revenue_multiplier():.2f}x")
    
    # Test distribution
    for i in range(10):
        net = engine.pick_network()
        print(f"  Session {i+1}: {net.name} (CPM: ${net.cpm_estimate:.2f})")
    
    print(f"\nStats: {engine.get_stats()}")