#!/usr/bin/env python3
"""
Survival Integration Layer — Connects Survival Engine to Main Loop
====================================================================
This is the CRITICAL missing piece from V2. The survival_engine.py
has all the quality/traffic/pattern/account logic, but nothing
called it. This file bridges that gap.

Integration Points:
1. pre_session_check() called BEFORE every session
   → Checks QualityMonitor risk level
   → CRITICAL = reject session, enter cooldown
   → DANGER = reduce concurrency via throttle
   → WARNING = apply throttle multiplier to delays

2. post_session_feedback() called AFTER every session
   → Feeds session metrics to QualityMonitor
   → Triggers reassessment every 100 sessions
   → Updates quality history

3. get_traffic_shape() called for session scheduling
   → Blends TrafficShaper + QualityMonitor throttle
   → Returns final delay multiplier (0.0-1.0)

4. check_account_health() called every 30 min
   → Triggers auto-switch if quality < 35% for 3 consecutive checks

Usage:
    from survival_integration import get_survival_integrator
    survival = await get_survival_integrator()
    allowed, throttle = await survival.pre_session_check()
    if not allowed:
        await asyncio.sleep(3600)  # Wait during cooldown
"""

import asyncio
import time
import logging
from typing import Dict, Optional, Tuple
from collections import deque

logger = logging.getLogger('survival_integration')

DEFAULT_QUALITY_CHECK_INTERVAL = 100  # Sessions between quality reassessments
DEFAULT_ACCOUNT_CHECK_INTERVAL = 1800  # 30 minutes


class SurvivalIntegrator:
    """
    Bridges survival_engine.py into the main farm loop.
    All quality/traffic/pattern/account decisions flow through here.
    """

    def __init__(self):
        import survival_engine as se
        self._quality_monitor = se.get_quality_monitor()
        self._pattern_randomizer = se.get_pattern_randomizer()
        self._account_rotator = se.get_account_rotator()
        self._traffic_shaper = se.TrafficShaper()

        # Rolling metrics collection for quality assessment
        self._recent_sessions: deque = deque(maxlen=500)
        self._session_count_since_check: int = 0
        self._last_account_check: float = 0
        self._last_quality_assessment: float = time.time()
        self._in_cooldown: bool = False
        self._cooldown_end: float = 0
        self._consecutive_critical: int = 0
        self._lock = asyncio.Lock()

    async def pre_session_check(self) -> Tuple[bool, float]:
        """
        Called BEFORE starting a new session.
        
        Returns:
            (allowed: bool, throttle_factor: float)
            allowed=False → Do NOT start session (cooldown/critical)
            throttle_factor=0.0-1.0 → Apply to session delay
        """
        async with self._lock:
            # Check if in cooldown
            if self._in_cooldown:
                if time.time() < self._cooldown_end:
                    remaining = int(self._cooldown_end - time.time())
                    logger.debug(f"Cooldown active: {remaining}s remaining")
                    return False, 1.0
                else:
                    self._in_cooldown = False
                    logger.info("Cooldown expired, resuming sessions")

            # Check risk level
            risk = self._quality_monitor.risk_level
            from survival_engine import RiskLevel

            if risk == RiskLevel.CRITICAL:
                self._consecutive_critical += 1
                if self._consecutive_critical >= 3:
                    # Auto-switch account
                    self._consecutive_critical = 0
                    new_account = self._account_rotator.switch_to_next()
                    if new_account:
                        logger.critical(f"⚠️ AUTO-SWITCHED to backup account: {new_account.get('publisher_id')}")
                    else:
                        logger.critical("❌ No more backup accounts! Farm must stop.")
                self._in_cooldown = True
                self._cooldown_end = time.time() + 172800  # 48 hours
                logger.critical("CRITICAL risk — entering 48h cooldown")
                return False, 1.0

            elif risk == RiskLevel.DANGER:
                self._in_cooldown = True
                self._cooldown_end = time.time() + 43200  # 12 hours
                logger.warning("DANGER risk — entering 12h cooldown")
                return False, 0.8

            elif risk == RiskLevel.WARNING:
                action = self._quality_monitor.get_throttle_action()
                throttle = action.get("throttle", 0.3)
                logger.warning(f"WARNING risk — throttle {throttle:.0%}")
                return True, throttle

            elif risk == RiskLevel.CAUTION:
                return True, 0.1

            # SAFE
            return True, 0.0

    async def post_session_feedback(self, session_result: Dict):
        """
        Called AFTER a session completes.
        Feeds metrics into quality monitor for assessment.
        """
        async with self._lock:
            self._recent_sessions.append({
                'pages_visited': session_result.get('pages_visited', 1),
                'ad_hovers': session_result.get('ad_hovers', 0),
                'ad_clicks': session_result.get('ad_clicks', 0),
                'time_spent': session_result.get('time_spent', 30),
                'section_visited': session_result.get('section_visited', 'unknown'),
                'device_type': session_result.get('device_type', 'desktop'),
                'source_type': session_result.get('source_type', 'direct'),
                'success': session_result.get('success', True),
            })

            self._session_count_since_check += 1

            # Reassess quality every N sessions
            if self._session_count_since_check >= DEFAULT_QUALITY_CHECK_INTERVAL:
                await self._reassess_quality()
                self._session_count_since_check = 0

    async def _reassess_quality(self):
        """Run QualityMonitor assessment on recent sessions."""
        if len(self._recent_sessions) < 10:
            return

        sessions = list(self._recent_sessions)
        successful = [s for s in sessions if s['success']]

        # Calculate quality signals
        avg_pages = sum(s['pages_visited'] for s in successful) / max(len(successful), 1)
        avg_duration = sum(s['time_spent'] for s in successful) / max(len(successful), 1)
        hover_rate = sum(s['ad_hovers'] for s in successful) / max(sum(s['pages_visited'] for s in successful), 1)
        click_rate = sum(s['ad_clicks'] for s in successful) / max(len(successful), 1)

        # Section diversity
        from collections import Counter
        section_counts = Counter(s['section_visited'] for s in successful)
        top_section_pct = section_counts.most_common(1)[0][1] / max(len(successful), 1) if section_counts else 0

        # Device diversity
        device_counts = Counter(s['device_type'] for s in successful)
        device_diversity = len(device_counts) / 3.0  # 3 device types

        # Direct traffic percentage
        direct_pct = sum(1 for s in successful if s['source_type'] == 'direct') / max(len(successful), 1)

        stats = {
            'avg_pages_per_session': avg_pages,
            'avg_session_duration': avg_duration,
            'ad_hover_rate': hover_rate,
            'ad_click_rate': click_rate,
            'top_section_percentage': top_section_pct,
            'device_diversity': min(device_diversity, 1.0),
            'direct_traffic_pct': direct_pct,
        }

        quality, risk = self._quality_monitor.assess_quality(stats)

        logger.info(
            f"Quality assessment: score={quality:.2f}, risk={risk.value}, "
            f"signals: pages={avg_pages:.1f}, hover={hover_rate:.1%}, "
            f"click={click_rate:.1%}, duration={avg_duration:.0f}s"
        )

        self._last_quality_assessment = time.time()

    async def check_account_health(self) -> Dict:
        """Called every 30 minutes to check account health."""
        now = time.time()
        if now - self._last_account_check < DEFAULT_ACCOUNT_CHECK_INTERVAL:
            return {'action': 'skip'}

        self._last_account_check = now

        # Check if quality has been consistently low
        if len(self._quality_monitor.quality_history) >= 3:
            recent = self._quality_monitor.quality_history[-3:]
            avg = sum(recent) / 3
            if avg < 0.35:
                logger.critical("Quality consistently < 35% — triggering account rotation")
                new_account = self._account_rotator.switch_to_next()
                if new_account:
                    return {
                        'action': 'switched',
                        'new_publisher_id': new_account.get('publisher_id'),
                        'instructions': self._account_rotator.get_switch_instructions(
                            new_account.get('publisher_id', '')
                        )
                    }

        return {'action': 'ok'}

    def get_traffic_shape(self) -> float:
        """Get current traffic multiplier from TrafficShaper."""
        return self._traffic_shaper.get_traffic_multiplier()

    def get_pattern(self) -> Dict:
        """Get current behavioral pattern for session variation."""
        return self._pattern_randomizer.get_current_pattern()

    def get_stats(self) -> Dict:
        """Get survival system stats for dashboard."""
        return {
            'risk_level': self._quality_monitor.risk_level.value,
            'throttle': self._quality_monitor.throttle_level,
            'in_cooldown': self._in_cooldown,
            'cooldown_remaining': max(0, int(self._cooldown_end - time.time())) if self._in_cooldown else 0,
            'quality_history': list(self._quality_monitor.quality_history[-10:]),
            'consecutive_warnings': self._quality_monitor.consecutive_warnings,
            'account_count': len(self._account_rotator.accounts),
            'sessions_collected': len(self._recent_sessions),
            'pattern': self._pattern_randomizer.current_pattern.get('name', 'none') if self._pattern_randomizer.current_pattern else 'none',
        }


# === GLOBAL INSTANCE ===
_integrator: Optional[SurvivalIntegrator] = None


async def get_survival_integrator() -> SurvivalIntegrator:
    global _integrator
    if _integrator is None:
        _integrator = SurvivalIntegrator()
    return _integrator