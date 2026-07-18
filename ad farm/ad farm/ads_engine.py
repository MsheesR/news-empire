#!/usr/bin/env python3
"""
Ads Engine - HilltopAds Integration
Manages ad zone interaction, pop-under triggering, and ad density per section.
Works with the existing LOPINUZE.2BD.NET site structure.
"""

import random
import asyncio
import logging
from typing import Dict, Any, List, Optional

from config import (
    SITE_URL, HILLTOPADS_PUBLISHER_ID,
    AD_SELECTORS
)
from sections import get_ad_density

logger = logging.getLogger('ads_engine')

# ============================ HILLTOPADS AD CODES ============================
# These are the standard HilltopAds ad formats
# Replace with your actual HilltopAds publisher codes

HILLTOPADS_CONFIG = {
    "publisher_id": HILLTOPADS_PUBLISHER_ID,
    "popunder": {
        "enabled": True,
        "code": f"""
        <script>
            (function() {{
                var s = document.createElement('script');
                s.type = 'text/javascript';
                s.async = true;
                s.src = 'https://api.hilltopads.com/popunder/publisher/{HILLTOPADS_PUBLISHER_ID}.js';
                var x = document.getElementsByTagName('script')[0];
                x.parentNode.insertBefore(s, x);
            }})();
        </script>
        """
    },
    "banner_728x90": {
        "enabled": True,
        "code": f"""
        <div class="ad-container banner-728x90" style="text-align:center;margin:20px 0;">
            <script>
                (function() {{
                    var s = document.createElement('script');
                    s.type = 'text/javascript';
                    s.async = true;
                    s.src = 'https://api.hilltopads.com/banner/publisher/{HILLTOPADS_PUBLISHER_ID}/728x90.js';
                    var x = document.getElementsByTagName('script')[0];
                    x.parentNode.insertBefore(s, x);
                }})();
            </script>
        </div>
        """
    },
    "banner_300x250": {
        "enabled": True,
        "code": f"""
        <div class="ad-container banner-300x250" style="text-align:center;margin:20px 0;">
            <script>
                (function() {{
                    var s = document.createElement('script');
                    s.type = 'text/javascript';
                    s.async = true;
                    s.src = 'https://api.hilltopads.com/banner/publisher/{HILLTOPADS_PUBLISHER_ID}/300x250.js';
                    var x = document.getElementsByTagName('script')[0];
                    x.parentNode.insertBefore(s, x);
                }})();
            </script>
        </div>
        """
    },
    "native": {
        "enabled": True,
        "code": f"""
        <div class="ad-container native-ad" style="margin:20px 0;">
            <script>
                (function() {{
                    var s = document.createElement('script');
                    s.type = 'text/javascript';
                    s.async = true;
                    s.src = 'https://api.hilltopads.com/native/publisher/{HILLTOPADS_PUBLISHER_ID}.js';
                    var x = document.getElementsByTagName('script')[0];
                    x.parentNode.insertBefore(s, x);
                }})();
            </script>
        </div>
        """
    }
}

# ============================ AD PLACEMENT INSTRUCTIONS ============================
# This tells you WHERE to put the ad codes in your HTML files

AD_PLACEMENT_GUIDE = """
================================================================================
HILLTOPADS AD PLACEMENT GUIDE FOR LOPINUZE.2BD.NET
================================================================================

1. POP-UNDER (Every Page)
   Add this right before </body> in EVERY .html file:
   
   <!-- HilltopAds Pop-under -->
   <script>
       (function() {
           var s = document.createElement('script');
           s.type = 'text/javascript';
           s.async = true;
           s.src = 'https://api.hilltopads.com/popunder/publisher/YOUR_PUBLISHER_ID.js';
           var x = document.getElementsByTagName('script')[0];
           x.parentNode.insertBefore(s, x);
       })();
   </script>

2. BANNER 728x90 (Section Index Pages & Homepage)
   Add this after the breaking-news-bar, inside .broadsheet:
   
   <div class="ad-banner-728"></div>

3. BANNER 300x250 (Article Pages Sidebar)
   Add this inside .article-detail, after .key-takeaways:
   
   <div class="ad-sidebar-300"></div>

4. NATIVE ADS (Article Pages - In Content)
   Add this after the first <p> in .content:
   
   <div class="ad-native-content"></div>

================================================================================
"""

# ============================ AD DENSITY CONFIG ============================
# Maps section tiers to ad interaction intensity

AD_DENSITY_CONFIG = {
    "high": {
        "hover_probability": 0.6,
        "max_ad_hovers_per_page": 3,
        "popunder_trigger_delay_ms": (2000, 5000),
        "banner_hover_duration_ms": (1000, 3000),
        "scrolling_ad_zone_encounters": (2, 4),  # Times scrolled past ad zones
    },
    "medium": {
        "hover_probability": 0.4,
        "max_ad_hovers_per_page": 2,
        "popunder_trigger_delay_ms": (3000, 7000),
        "banner_hover_duration_ms": (800, 2500),
        "scrolling_ad_zone_encounters": (1, 3),
    },
    "low": {
        "hover_probability": 0.25,
        "max_ad_hovers_per_page": 1,
        "popunder_trigger_delay_ms": (5000, 10000),
        "banner_hover_duration_ms": (500, 2000),
        "scrolling_ad_zone_encounters": (0, 2),
    }
}

# ============================ ADS INTERACTION ENGINE ============================
class AdsEngine:
    """
    Handles ad-related interactions during a browsing session.
    Triggers pop-unders, hovers over banners, and scrolls past ad zones.
    """
    
    def __init__(self):
        self.total_hovers = 0
        self.total_popunders = 0
    
    def get_density_config(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Get ad density configuration for a section."""
        density = get_ad_density(section)
        return AD_DENSITY_CONFIG[density]
    
    async def wait_for_popunder_trigger(self, section: Dict[str, Any]) -> float:
        """
        Calculate natural delay before popunder triggers.
        Returns seconds to wait.
        """
        config = self.get_density_config(section)
        min_delay, max_delay = config["popunder_trigger_delay_ms"]
        delay_ms = random.randint(min_delay, max_delay)
        
        # Pop-under triggers automatically via HilltopAds script
        # We just wait the natural delay
        await asyncio.sleep(delay_ms / 1000)
        self.total_popunders += 1
        return delay_ms / 1000
    
    async def hover_ad_zones(
        self, 
        ad_elements: List[Dict], 
        section: Dict[str, Any],
        device_type: str
    ) -> int:
        """
        Hover over ad zones naturally. Returns number of ad zones hovered.
        Uses the browser session's hover_element method.
        """
        if not ad_elements:
            return 0
        
        config = self.get_density_config(section)
        hover_prob = config["hover_probability"]
        max_hovers = config["max_ad_hovers_per_page"]
        
        # Don't hover on mobile as much (touch vs mouse)
        if device_type == "mobile":
            hover_prob *= 0.5
        
        hovers_done = 0
        for ad in ad_elements[:max_hovers]:
            if random.random() < hover_prob:
                # The actual hover is done by browser_manager
                # This just tracks that we want to hover
                hovers_done += 1
                self.total_hovers += 1
                await asyncio.sleep(random.uniform(0.5, 1.5))
        
        return hovers_done
    
    def get_banner_hover_duration(self, section: Dict[str, Any]) -> float:
        """Get how long to hover over a banner ad."""
        config = self.get_density_config(section)
        min_ms, max_ms = config["banner_hover_duration_ms"]
        return random.randint(min_ms, max_ms) / 1000
    
    def should_hover_ad(self, section: Dict[str, Any], device_type: str) -> bool:
        """Decide whether to hover over an ad in this section."""
        config = self.get_density_config(section)
        prob = config["hover_probability"]
        if device_type == "mobile":
            prob *= 0.4  # Much less likely on touch device
        return random.random() < prob
    
    def get_ad_zone_encounter_count(self, section: Dict[str, Any]) -> int:
        """Number of times to scroll past ad zones."""
        config = self.get_density_config(section)
        min_count, max_count = config["scrolling_ad_zone_encounters"]
        return random.randint(min_count, max_count)
    
    def get_stats(self) -> Dict[str, int]:
        """Get ad interaction statistics."""
        return {
            "total_hovers": self.total_hovers,
            "total_popunders": self.total_popunders
        }
    
    def get_placement_html(self) -> str:
        """Generate the HTML snippets to add to your site."""
        return AD_PLACEMENT_GUIDE


# ============================ AD CODE GENERATOR ============================
def generate_ad_codes(publisher_id: str = None) -> Dict[str, str]:
    """Generate HTML ad codes for HilltopAds."""
    pid = publisher_id or HILLTOPADS_PUBLISHER_ID
    
    return {
        "popunder": f"""
<!-- HilltopAds Pop-under -->
<script>
(function() {{
    var s = document.createElement('script');
    s.type = 'text/javascript';
    s.async = true;
    s.src = 'https://api.hilltopads.com/popunder/publisher/{pid}.js';
    var x = document.getElementsByTagName('script')[0];
    x.parentNode.insertBefore(s, x);
}})();
</script>
""".strip(),
        "banner_728x90": f"""
<!-- HilltopAds Banner 728x90 -->
<div class="ad-banner-728" style="text-align:center;margin:15px 0;">
<script>
(function() {{
    var s = document.createElement('script');
    s.type = 'text/javascript';
    s.async = true;
    s.src = 'https://api.hilltopads.com/banner/publisher/{pid}/728x90.js';
    var x = document.getElementsByTagName('script')[0];
    x.parentNode.insertBefore(s, x);
}})();
</script>
</div>
""".strip(),
        "banner_300x250": f"""
<!-- HilltopAds Banner 300x250 -->
<div class="ad-sidebar-300" style="text-align:center;margin:15px 0;">
<script>
(function() {{
    var s = document.createElement('script');
    s.type = 'text/javascript';
    s.async = true;
    s.src = 'https://api.hilltopads.com/banner/publisher/{pid}/300x250.js';
    var x = document.getElementsByTagName('script')[0];
    x.parentNode.insertBefore(s, x);
}})();
</script>
</div>
""".strip(),
        "native": f"""
<!-- HilltopAds Native -->
<div class="ad-native-content" style="margin:15px 0;">
<script>
(function() {{
    var s = document.createElement('script');
    s.type = 'text/javascript';
    s.async = true;
    s.src = 'https://api.hilltopads.com/native/publisher/{pid}.js';
    var x = document.getElementsByTagName('script')[0];
    x.parentNode.insertBefore(s, x);
}})();
</script>
</div>
""".strip(),
    }


# ============================ GLOBAL ENGINE ============================
_ads_engine: Optional[AdsEngine] = None

def get_ads_engine() -> AdsEngine:
    """Get or create the global ads engine."""
    global _ads_engine
    if _ads_engine is None:
        _ads_engine = AdsEngine()
    return _ads_engine


# ============================ TEST ============================
if __name__ == '__main__':
    engine = AdsEngine()
    
    # Test density config
    test_sections = [
        {"slug": "tech", "tier": 1},
        {"slug": "health", "tier": 2},
        {"slug": "yoga", "tier": 3},
    ]
    
    for sec in test_sections:
        config = engine.get_density_config(sec)
        density = get_ad_density(sec)
        print(f"\n{sec['slug']} (tier {sec['tier']}, density={density}):")
        print(f"  Hover prob: {config['hover_probability']}")
        print(f"  Max hovers: {config['max_ad_hovers_per_page']}")
        print(f"  Pop-under delay: {config['popunder_trigger_delay_ms']}ms")
    
    # Generate ad codes
    print("\n\n=== AD CODES ===")
    codes = generate_ad_codes("YOUR_PUBLISHER_ID")
    for ad_type, code in codes.items():
        print(f"\n--- {ad_type} ---")
        print(code[:150] + "...")
    
    # Placement guide
    print(f"\n\n{engine.get_placement_html()}")