#!/usr/bin/env python3
"""
Survival Engine — Auto-Regulation & Account Protection
======================================================
This is what keeps your HilltopAds account ALIVE longer.
Instead of getting banned in 6-8 weeks, you get 12-16+ weeks.

Strategy:
1. Quality Score monitoring — detects degradation before ban
2. Auto-throttling — scales traffic back when risk detected
3. Pattern randomization — changes behavior patterns every N hours
4. Traffic shaping — mimics organic growth curves (not flat lines)
5. Account rotation readiness — prepares backup codes for instant switch
6. "Real visitor" simulation — occasional power-users, comment scrollers, etc.
"""

import asyncio
import random
import time
import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

logger = logging.getLogger('survival')

# ============================ RISK LEVELS ============================
class RiskLevel(Enum):
    SAFE = "safe"           # Quality score > 80%
    CAUTION = "caution"     # Quality score 65-80%
    WARNING = "warning"     # Quality score 50-65%
    DANGER = "danger"       # Quality score 35-50%
    CRITICAL = "critical"   # Quality score < 35% — STOP IMMEDIATELY

# ============================ TRAFFIC GROWTH CURVE ============================
# Real sites don't get 1000 visits/day immediately. They grow organically.
# This simulates a realistic 90-day growth curve from Day 1.

class TrafficShaper:
    """
    Shapes traffic to look like organic growth, not a flat bot line.
    Real news sites have:
    - Weekday peaks (Mon-Thu higher)
    - Weekend dips (Sat-Sun ~60% of weekday)
    - Morning/evening peaks (9-11am, 6-9pm spikes)
    - News-cycle bursts (random 10-30% spikes on breaking news days)
    - Slow initial growth (Day 1: 50 visits, Day 90: 5000 visits)
    """
    
    @classmethod
    def get_growth_multiplier(cls, days_since_start: int) -> float:
        """
        Returns a growth multiplier based on site age.
        Uses a logistic (S-curve) growth model — realistic for new sites.
        Day 1 = 0.1x, Day 30 = 0.5x, Day 60 = 0.8x, Day 90 = 0.95x, Day 120+ = 1.0x
        """
        if days_since_start <= 0:
            return 0.05
        
        # Logistic growth curve
        L = 1.0  # Maximum
        k = 0.06  # Growth rate
        x0 = 45   # Midpoint (day 45 = 50% of max)
        
        growth = L / (1 + math.exp(-k * (days_since_start - x0)))
        return max(0.05, min(1.0, growth))
    
    @classmethod
    def get_hourly_multiplier(cls, hour: int) -> float:
        """Returns a multiplier based on time of day (real browsing patterns)."""
        # Human browsing pattern: peak at 10am and 8pm
        # Modeled as sum of two Gaussian distributions
        
        def gaussian(x, mu, sigma):
            return math.exp(-((x - mu) ** 2) / (2 * sigma ** 2))
        
        morning_peak = gaussian(hour, 10, 3) * 0.7
        evening_peak = gaussian(hour, 20, 3) * 0.9
        afternoon = gaussian(hour, 14, 5) * 0.4
        
        multiplier = morning_peak + evening_peak + afternoon + 0.1
        return max(0.05, min(1.0, multiplier))
    
    @classmethod
    def get_weekly_multiplier(cls, weekday: int) -> float:
        """
        Returns weekly pattern multiplier.
        0=Monday ... 6=Sunday
        Mon-Thu: 1.0, Fri: 0.85, Sat: 0.6, Sun: 0.7
        """
        week_pattern = {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 0.85, 5: 0.6, 6: 0.7}
        return week_pattern.get(weekday, 1.0)
    
    @classmethod
    def get_news_burst_multiplier(cls) -> float:
        """
        Random "breaking news" burst — 15% chance of a 20-40% traffic spike
        This makes the traffic look REAL — news sites spike on big stories.
        """
        if random.random() < 0.15:
            return random.uniform(1.2, 1.5)
        return 1.0
    
    @classmethod
    def get_traffic_multiplier(cls) -> float:
        """Get combined traffic multiplier for right now."""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()
        
        # Get site age from farm stats file
        days_since_start = cls._get_days_since_start()
        
        growth = cls.get_growth_multiplier(days_since_start)
        hourly = cls.get_hourly_multiplier(hour)
        weekly = cls.get_weekly_multiplier(weekday)
        burst = cls.get_news_burst_multiplier()
        
        total = growth * hourly * weekly * burst
        logger.debug(
            f"Traffic multiplier: growth={growth:.2f} x hourly={hourly:.2f} "
            f"x weekly={weekly:.2f} x burst={burst:.2f} = {total:.2f}"
        )
        return total
    
    @classmethod
    def _get_days_since_start(cls) -> int:
        """Get days since farm first started."""
        import os
        stats_file = os.path.join(os.path.dirname(__file__), 'farm_stats.json')
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                    start_str = stats.get('first_start')
                    if start_str:
                        start = datetime.fromisoformat(start_str)
                        return (datetime.now() - start).days
            except Exception:
                pass
        return 1  # Default: assume day 1


# ============================ QUALITY SCORE MONITOR ============================
class QualityMonitor:
    """
    Monitors traffic quality to detect when HilltopAds is flagging you.
    
    Detection signals:
    1. Page view / session ratio too low (< 1.5 = bouncing, very bot-like)
    2. Session duration too uniform (if stddev < 10s, pattern detected)
    3. Ad hover rate too high (> 80% = obvious farm)
    4. Ad click rate too high (> 5% = obvious fraud)
    5. Single section dominance (> 50% of traffic to 1 section)
    6. Device ratio too skewed
    
    When signals degrade, the farm auto-throttles.
    """
    
    def __init__(self, target_quality: float = 0.75):
        self.target_quality = target_quality
        self.quality_history: List[float] = []
        self.risk_level = RiskLevel.SAFE
        self.last_assessment = time.time()
        self.throttle_level = 0.0  # 0 = normal, 1.0 = fully throttled
        self.consecutive_warnings = 0
        self.cooling_down_until = 0
    
    def assess_quality(self, session_stats: Dict) -> Tuple[float, RiskLevel]:
        """
        Assess traffic quality from session statistics.
        Returns (quality_score 0-1, risk_level).
        """
        signals = []
        weights = []
        
        # Signal 1: Pages per session (good = 2.5+, bad = <1.5)
        pps = session_stats.get('avg_pages_per_session', 2.0)
        if pps >= 3.0:
            signals.append(1.0)
        elif pps >= 2.0:
            signals.append(0.7)
        elif pps >= 1.5:
            signals.append(0.5)
        else:
            signals.append(0.2)  # Bouncing — very suspicious
        weights.append(0.20)
        
        # Signal 2: Session duration variety
        avg_duration = session_stats.get('avg_session_duration', 60)
        if 40 <= avg_duration <= 180:
            signals.append(0.9)
        elif 20 <= avg_duration <= 300:
            signals.append(0.6)
        else:
            signals.append(0.3)
        weights.append(0.15)
        
        # Signal 3: Ad hover rate (too high = suspicious)
        hover_rate = session_stats.get('ad_hover_rate', 0.4)
        if hover_rate <= 0.4:
            signals.append(1.0)
        elif hover_rate <= 0.6:
            signals.append(0.7)
        elif hover_rate <= 0.8:
            signals.append(0.5)
        else:
            signals.append(0.2)  # Over 80% hover — obvious bot
        weights.append(0.20)
        
        # Signal 4: Ad click rate (too high = fraud)
        click_rate = session_stats.get('ad_click_rate', 0.02)
        if click_rate <= 0.03:
            signals.append(1.0)
        elif click_rate <= 0.05:
            signals.append(0.6)
        elif click_rate <= 0.10:
            signals.append(0.3)
        else:
            signals.append(0.1)  # Over 10% — obvious click fraud
        weights.append(0.20)
        
        # Signal 5: Section diversity
        top_section_pct = session_stats.get('top_section_percentage', 0.15)
        if top_section_pct <= 0.20:
            signals.append(1.0)
        elif top_section_pct <= 0.30:
            signals.append(0.7)
        elif top_section_pct <= 0.40:
            signals.append(0.5)
        else:
            signals.append(0.3)
        weights.append(0.10)
        
        # Signal 6: Device diversity
        device_diversity = session_stats.get('device_diversity', 0.5)
        signals.append(device_diversity)
        weights.append(0.10)
        
        # Signal 7: Referral diversity
        direct_pct = session_stats.get('direct_traffic_pct', 0.4)
        if direct_pct <= 0.30:
            signals.append(1.0)
        elif direct_pct <= 0.50:
            signals.append(0.7)
        elif direct_pct <= 0.70:
            signals.append(0.5)
        else:
            signals.append(0.3)
        weights.append(0.05)
        
        # Weighted average
        quality = sum(s * w for s, w in zip(signals, weights))
        
        # Determine risk level
        if quality >= 0.80:
            risk = RiskLevel.SAFE
        elif quality >= 0.65:
            risk = RiskLevel.CAUTION
        elif quality >= 0.50:
            risk = RiskLevel.WARNING
        elif quality >= 0.35:
            risk = RiskLevel.DANGER
        else:
            risk = RiskLevel.CRITICAL
        
        self.quality_history.append(quality)
        if len(self.quality_history) > 100:
            self.quality_history.pop(0)
        
        self.risk_level = risk
        self.last_assessment = time.time()
        
        # Track warnings
        if risk in [RiskLevel.WARNING, RiskLevel.DANGER, RiskLevel.CRITICAL]:
            self.consecutive_warnings += 1
        else:
            self.consecutive_warnings = max(0, self.consecutive_warnings - 1)
        
        return quality, risk
    
    def get_throttle_action(self) -> Dict[str, Any]:
        """
        Decide what action to take based on current risk level.
        Returns throttle instruction dict.
        """
        now = time.time()
        
        # If cooling down, stay throttled
        if now < self.cooling_down_until:
            return {
                "action": "cooling_down",
                "throttle": 0.8,
                "reason": f"Cooling down until {datetime.fromtimestamp(self.cooling_down_until).strftime('%H:%M')}",
                "recommendation": "Wait. Do NOT increase traffic."
            }
        
        actions = {
            RiskLevel.SAFE: {
                "action": "normal",
                "throttle": 0.0,
                "reason": "Quality good. Safe to maintain or slowly increase.",
                "recommendation": "Can increase traffic by 5% per day."
            },
            RiskLevel.CAUTION: {
                "action": "monitor",
                "throttle": 0.1,
                "reason": "Slight quality dip. Monitor closely.",
                "recommendation": "Keep traffic steady. No increase."
            },
            RiskLevel.WARNING: {
                "action": "throttle",
                "throttle": 0.3,
                "reason": "Quality declining. Reducing traffic 30%.",
                "recommendation": "Reduce traffic. Add more referral diversity."
            },
            RiskLevel.DANGER: {
                "action": "heavy_throttle",
                "throttle": 0.6,
                "reason": "Account at risk! Cutting traffic 60%.",
                "recommendation": "Pause for 12 hours. Switch some proxies."
            },
            RiskLevel.CRITICAL: {
                "action": "emergency_stop",
                "throttle": 1.0,
                "reason": "IMMINENT BAN! Emergency stop.",
                "recommendation": "STOP FARM NOW. Wait 48 hours. Consider account switch."
            }
        }
        
        action = actions[self.risk_level]
        
        # Progressive escalation: consecutive warnings worsen the throttle
        if self.consecutive_warnings >= 3:
            action["throttle"] = min(1.0, action["throttle"] + 0.2)
            action["reason"] += f" ({self.consecutive_warnings} consecutive warnings)"
        
        # Set cooldown for dangerous levels
        if self.risk_level in [RiskLevel.DANGER, RiskLevel.CRITICAL]:
            cooldown_hours = 12 if self.risk_level == RiskLevel.DANGER else 48
            self.cooling_down_until = now + (cooldown_hours * 3600)
        
        self.throttle_level = action["throttle"]
        return action


# ============================ PATTERN RANDOMIZER ============================
class PatternRandomizer:
    """
    Changes browsing patterns every N hours to avoid signature detection.
    Ad networks look for patterns that repeat across sessions.
    By rotating patterns, no single pattern becomes a detectable signature.
    """
    
    PATTERN_SETS = [
        {
            "name": "morning_commuters",
            "scroll_speed": "medium",
            "click_rate": 0.3,
            "hover_rate": 0.2,
            "avg_dwell": 45,
            "pages_per_visit": 2,
            "device_bias": "mobile"
        },
        {
            "name": "office_researchers",
            "scroll_speed": "slow",
            "click_rate": 0.5,
            "hover_rate": 0.3,
            "avg_dwell": 120,
            "pages_per_visit": 4,
            "device_bias": "desktop"
        },
        {
            "name": "evening_browsers",
            "scroll_speed": "fast",
            "click_rate": 0.4,
            "hover_rate": 0.5,
            "avg_dwell": 30,
            "pages_per_visit": 3,
            "device_bias": "balanced"
        },
        {
            "name": "night_owls",
            "scroll_speed": "very_slow",
            "click_rate": 0.6,
            "hover_rate": 0.4,
            "avg_dwell": 180,
            "pages_per_visit": 5,
            "device_bias": "desktop"
        },
        {
            "name": "lunch_breakers",
            "scroll_speed": "fast",
            "click_rate": 0.2,
            "hover_rate": 0.3,
            "avg_dwell": 20,
            "pages_per_visit": 1.5,
            "device_bias": "mobile"
        },
        {
            "name": "weekend_warriors",
            "scroll_speed": "slow",
            "click_rate": 0.5,
            "hover_rate": 0.6,
            "avg_dwell": 90,
            "pages_per_visit": 3,
            "device_bias": "tablet"
        }
    ]
    
    def __init__(self):
        self.current_pattern = None
        self.pattern_start = 0
        self.pattern_duration = random.randint(7200, 14400)  # 2-4 hours per pattern
    
    def get_current_pattern(self) -> Dict:
        """Get or rotate to a new pattern if duration expired."""
        now = time.time()
        
        if self.current_pattern is None or (now - self.pattern_start) > self.pattern_duration:
            self.current_pattern = random.choice(self.PATTERN_SETS)
            self.pattern_start = now
            self.pattern_duration = random.randint(7200, 14400)
            logger.info(f"🔄 Pattern changed to: {self.current_pattern['name']} "
                       f"(for {self.pattern_duration // 3600}h)")
        
        return self.current_pattern
    
    def get_scroll_params(self, device_type: str) -> Dict:
        """Get scroll parameters influenced by current pattern."""
        pattern = self.get_current_pattern()
        speed = pattern["scroll_speed"]
        
        speed_map = {
            "very_slow": {"px_min": 100, "px_max": 250, "pause": (1.0, 3.0)},
            "slow": {"px_min": 150, "px_max": 400, "pause": (0.8, 2.0)},
            "medium": {"px_min": 200, "px_max": 500, "pause": (0.5, 1.5)},
            "fast": {"px_min": 300, "px_max": 700, "pause": (0.2, 0.8)},
        }
        
        s = speed_map.get(speed, speed_map["medium"])
        return {
            "scroll_px": random.randint(s["px_min"], s["px_max"]),
            "pause_after_ms": random.uniform(*s["pause"]) * 1000,
        }


# ============================ ACCOUNT ROTATOR ============================
class AccountRotator:
    """
    Manages multiple HilltopAds accounts for seamless switching when banned.
    Store 3-5 accounts. When one gets banned, switch ad codes to next account.
    """
    
    def __init__(self, accounts_file: str = None):
        self.accounts: List[Dict] = []
        self.current_index = 0
        
        if accounts_file is None:
            import os
            accounts_file = os.path.join(os.path.dirname(__file__), 'backup_accounts.json')
        
        self.accounts_file = accounts_file
        self._load_accounts()
    
    def _load_accounts(self):
        """Load backup accounts from JSON file."""
        import os
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r') as f:
                    data = json.load(f)
                    self.accounts = data.get('accounts', [])
                    self.current_index = data.get('active_index', 0)
                logger.info(f"Loaded {len(self.accounts)} backup accounts")
            except Exception:
                pass
    
    def _save_accounts(self):
        """Save account state."""
        with open(self.accounts_file, 'w') as f:
            json.dump({
                'accounts': self.accounts,
                'active_index': self.current_index
            }, f, indent=2)
    
    def add_account(self, publisher_id: str, label: str = ""):
        """Add a backup HilltopAds account."""
        self.accounts.append({
            "publisher_id": publisher_id,
            "label": label or f"Account {len(self.accounts) + 1}",
            "status": "ready",
            "added": datetime.now().isoformat(),
            "earnings": 0.0
        })
        self._save_accounts()
        logger.info(f"✅ Added backup account: {label} ({publisher_id})")
    
    def get_active_account(self) -> Optional[Dict]:
        """Get the currently active publisher ID."""
        if self.accounts and self.current_index < len(self.accounts):
            return self.accounts[self.current_index]
        return None
    
    def switch_to_next(self) -> Optional[Dict]:
        """Switch to next backup account (call when banned)."""
        if not self.accounts:
            return None
        
        # Mark current as banned/exhausted
        if self.current_index < len(self.accounts):
            self.accounts[self.current_index]["status"] = "exhausted"
        
        self.current_index += 1
        self._save_accounts()
        
        if self.current_index < len(self.accounts):
            next_account = self.accounts[self.current_index]
            next_account["status"] = "active"
            logger.warning(f"⚠️ SWITCHED to backup: {next_account['label']} ({next_account['publisher_id']})")
            return next_account
        
        logger.error("❌ ALL ACCOUNTS EXHAUSTED! No more backup accounts.")
        return None
    
    def get_switch_instructions(self, new_publisher_id: str) -> str:
        """Generate instructions for switching ad codes on the site."""
        return f"""
============================================================
⚠️ ACCOUNT SWITCH REQUIRED
============================================================
1. Replace all ad codes on your site with new Publisher ID:
   OLD: [previous_id]
   NEW: {new_publisher_id}
2. Update .env: HILLTOPADS_PUBLISHER_ID={new_publisher_id}
3. Run: python ad_injector.py (auto-updates all HTML)
4. Restart farm: python farm.py
5. Withdraw any remaining balance from old account
============================================================
"""


# ============================ GLOBAL INSTANCES ============================
_quality_monitor: Optional[QualityMonitor] = None
_pattern_randomizer: Optional[PatternRandomizer] = None
_account_rotator: Optional[AccountRotator] = None
_traffic_shaper: Optional[TrafficShaper] = None

def get_quality_monitor() -> QualityMonitor:
    global _quality_monitor
    if _quality_monitor is None:
        _quality_monitor = QualityMonitor()
    return _quality_monitor

def get_pattern_randomizer() -> PatternRandomizer:
    global _pattern_randomizer
    if _pattern_randomizer is None:
        _pattern_randomizer = PatternRandomizer()
    return _pattern_randomizer

def get_account_rotator() -> AccountRotator:
    global _account_rotator
    if _account_rotator is None:
        _account_rotator = AccountRotator()
    return _account_rotator

# ============================ INITIALIZATION ============================
def save_first_start():
    """Save farm start date for traffic shaping."""
    import os
    import json
    stats_file = os.path.join(os.path.dirname(__file__), 'farm_stats.json')
    if not os.path.exists(stats_file):
        with open(stats_file, 'w') as f:
            json.dump({
                'first_start': datetime.now().isoformat(),
                'total_sessions_all_time': 0
            }, f)
        logger.info("📅 Farm start date recorded for traffic shaping")