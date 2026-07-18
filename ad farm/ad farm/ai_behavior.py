#!/usr/bin/env python3
"""
AI-Driven Behavior Engine - DeepSeek Powered Human Mimicry
Uses real-time AI decisions to generate natural browsing behavior.
No pattern, no repetition — each session is unique.
"""

import random
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
import aiohttp

from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL,
    BEHAVIOR_PROFILES, DEVICE_DISTRIBUTION
)

logger = logging.getLogger('ai_behavior')

# ============================ DEEPSEEK AI CLIENT ============================
class DeepSeekClient:
    """Async client for DeepSeek AI API for real-time behavior decisions."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = DEEPSEEK_API_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self.enabled = bool(api_key and api_key != 'your_deepseek_api_key_here')
        
        if not self.enabled:
            logger.warning("DeepSeek API key not configured. Using randomized behavior (no AI).")
    
    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
    
    async def ask_behavior(
        self,
        current_url: str,
        page_title: str,
        section: str,
        scroll_percentage: float,
        time_on_page: int,
        device_type: str,
        links_visible: int,
        ads_visible: int,
        is_article: bool = False
    ) -> Dict[str, Any]:
        """
        Ask DeepSeek AI to decide the next human-like action.
        Returns a decision dict with action, probability, and reasoning.
        
        If AI is unavailable, uses smart randomized fallback.
        """
        if not self.enabled:
            return self._fallback_decision(current_url, section, scroll_percentage, 
                                           time_on_page, device_type, links_visible, 
                                           ads_visible, is_article)
        
        await self._ensure_session()
        
        context = f"""You are simulating a real human casually browsing the news website LOPINUZE.2BD.NET.
Current state:
- URL: {current_url}
- Page title: {page_title}
- Section: {section}
- Device: {device_type}
- Scroll depth: {scroll_percentage:.0%} of the page
- Time on this page: {time_on_page} seconds
- Visible article links: {links_visible}
- Ad zones visible: {ads_visible}
- Is this an article page: {is_article}

Choose what a {device_type} user would do next. Consider:
- A real person doesn't click every link — they're selective
- Scrolling patterns vary: sometimes they read, sometimes they skim
- On mobile, people scroll more and click less
- After 60+ seconds, people usually either click something or leave
- Ad hover only happens naturally — maybe 30-50% chance if ads are visible
- People rarely stay on a single article for more than 3 minutes
- Most browsing sessions include 1-3 page views before exiting

Respond with a JSON object:
{{
    "action": "scroll|click_link|hover_ad|read_more|go_back|switch_section|exit",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of this human-like choice",
    "scroll_amount": number of scroll steps (1-5 if scrolling),
    "wait_ms": milliseconds to wait before executing this action (500-5000)
}}

ONLY respond with the JSON, no other text."""

        try:
            payload = {
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a human browser simulation engine. Output only valid JSON."},
                    {"role": "user", "content": context}
                ],
                "temperature": 0.8,
                "max_tokens": 200,
                "response_format": {"type": "json_object"}
            }
            
            async with self.session.post(self.api_url, json=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    content = result['choices'][0]['message']['content']
                    decision = json.loads(content)
                    logger.debug(f"AI Decision: {decision['action']} ({decision['reasoning'][:50]}...)")
                    return decision
                else:
                    logger.warning(f"DeepSeek API error: {resp.status}")
                    return self._fallback_decision(current_url, section, scroll_percentage, 
                                                   time_on_page, device_type, links_visible, 
                                                   ads_visible, is_article)
        except Exception as e:
            logger.debug(f"DeepSeek call failed: {e}, using fallback")
            return self._fallback_decision(current_url, section, scroll_percentage, 
                                           time_on_page, device_type, links_visible, 
                                           ads_visible, is_article)
    
    def _fallback_decision(
        self, current_url: str, section: str, scroll_percentage: float,
        time_on_page: int, device_type: str, links_visible: int,
        ads_visible: int, is_article: bool
    ) -> Dict[str, Any]:
        """Smart randomized fallback when AI is unavailable."""
        
        # Decision matrix based on real human browsing patterns
        actions_weights = {}
        
        # If just loaded, scroll first
        if time_on_page < 5:
            actions_weights = {"scroll": 0.7, "click_link": 0.2, "hover_ad": 0.1}
        # If been reading for a while
        elif time_on_page > 120:
            actions_weights = {"click_link": 0.4, "exit": 0.3, "switch_section": 0.2, "scroll": 0.1}
        # If scrolled through most content
        elif scroll_percentage > 0.7:
            actions_weights = {"click_link": 0.35, "scroll": 0.2, "hover_ad": 0.2, "exit": 0.15, "switch_section": 0.1}
        # Normal browsing
        else:
            actions_weights = {"scroll": 0.4, "click_link": 0.3, "hover_ad": 0.2, "read_more": 0.1}
        
        # Adjust for device type
        if device_type == "mobile":
            actions_weights["scroll"] = actions_weights.get("scroll", 0) + 0.1
            actions_weights["click_link"] = actions_weights.get("click_link", 0) - 0.05
        elif device_type == "desktop":
            actions_weights["hover_ad"] = actions_weights.get("hover_ad", 0) + 0.1
        
        # If no ads visible, remove hover_ad
        if ads_visible == 0:
            actions_weights.pop("hover_ad", None)
        
        # If no links, remove click_link
        if links_visible == 0 and not is_article:
            actions_weights.pop("click_link", None)
        
        # Weighted random selection
        total = sum(actions_weights.values())
        r = random.random() * total
        cumulative = 0.0
        chosen_action = "scroll"
        for action, weight in actions_weights.items():
            cumulative += weight
            if r <= cumulative:
                chosen_action = action
                break
        
        scroll_amount = random.randint(1, 5) if chosen_action == "scroll" else 0
        wait_ms = random.randint(500, 5000)
        
        return {
            "action": chosen_action,
            "confidence": 0.5,
            "reasoning": f"Fallback: {device_type} user at {scroll_percentage:.0%} scroll after {time_on_page}s",
            "scroll_amount": scroll_amount,
            "wait_ms": wait_ms
        }
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


# ============================ BEHAVIOR ENGINE ============================
class BehaviorEngine:
    """
    Orchestrates human-like behavior for each browsing session.
    Combines DeepSeek AI decisions with behavioral profiles.
    """
    
    def __init__(self, deepseek_client: Optional[DeepSeekClient] = None):
        self.ai = deepseek_client or DeepSeekClient(DEEPSEEK_API_KEY)
        self.session_history: List[Dict] = []  # Track this session's actions
    
    def get_random_profile(self) -> Dict[str, Any]:
        """Pick a random behavior profile based on weights."""
        total = sum(p["weight"] for p in BEHAVIOR_PROFILES)
        r = random.random() * total
        cumulative = 0.0
        for profile in BEHAVIOR_PROFILES:
            cumulative += profile["weight"]
            if r <= cumulative:
                return profile.copy()
        return BEHAVIOR_PROFILES[0].copy()
    
    def get_random_device(self) -> Tuple[str, str, Dict[str, int]]:
        """Pick a random device type with weighted distribution."""
        from config import DEVICE_DISTRIBUTION, VIEWPORTS, USER_AGENTS
        
        total = sum(DEVICE_DISTRIBUTION.values())
        r = random.random() * total
        cumulative = 0.0
        chosen_type = "mobile"
        for dtype, weight in DEVICE_DISTRIBUTION.items():
            cumulative += weight
            if r <= cumulative:
                chosen_type = dtype
                break
        
        viewport = random.choice(VIEWPORTS[chosen_type])
        user_agent = random.choice(USER_AGENTS[chosen_type])
        
        return chosen_type, user_agent, viewport
    
    def get_random_scroll_params(self, device_type: str) -> Dict[str, Any]:
        """Generate human-like scroll parameters."""
        if device_type == "mobile":
            scroll_px_min, scroll_px_max = 150, 400
            pause_min, pause_max = 0.3, 1.5
        elif device_type == "tablet":
            scroll_px_min, scroll_px_max = 200, 500
            pause_min, pause_max = 0.5, 2.0
        else:
            scroll_px_min, scroll_px_max = 200, 700
            pause_min, pause_max = 0.5, 2.5
        
        return {
            "scroll_px": random.randint(scroll_px_min, scroll_px_max),
            "pause_after_ms": random.uniform(pause_min, pause_max) * 1000,
            "scroll_behavior": random.choice(["smooth", "auto"]),
            "scroll_speed": random.choice(["slow", "medium", "fast"]),
        }
    
    def get_reading_pause_ms(self, text_length_estimate: int = 500) -> float:
        """Calculate human-like reading pause based on content length."""
        # Average reading speed: 200-250 words per minute
        # That's about 4 words per second
        words = text_length_estimate / 5  # rough word count
        base_time = words / 4  # seconds at average reading speed
        
        # Add variability: ±50%
        actual_time = base_time * random.uniform(0.5, 1.5)
        
        # Cap at realistic limits
        return min(max(actual_time, 2.0), 45.0) * 1000
    
    async def decide_next_action(
        self,
        current_url: str = "",
        page_title: str = "",
        section: str = "",
        scroll_percentage: float = 0.0,
        time_on_page: int = 0,
        device_type: str = "desktop",
        links_visible: int = 5,
        ads_visible: int = 2,
        is_article: bool = False,
        profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main decision function — uses AI or fallback to determine next action.
        Returns a dict with action details.
        """
        # Ask DeepSeek AI
        decision = await self.ai.ask_behavior(
            current_url=current_url,
            page_title=page_title,
            section=section,
            scroll_percentage=scroll_percentage,
            time_on_page=time_on_page,
            device_type=device_type,
            links_visible=links_visible,
            ads_visible=ads_visible,
            is_article=is_article
        )
        
        # Blend with behavior profile if available
        if profile:
            if decision["action"] == "click_link":
                max_clicks = profile.get("clicks_max", 3)
                # Limit clicks based on profile
                recent_clicks = sum(1 for h in self.session_history if h.get("action") == "click_link")
                if recent_clicks >= max_clicks:
                    decision["action"] = "exit"
                    decision["reasoning"] = f"Profile limit: max {max_clicks} clicks reached"
            
            if decision["action"] == "hover_ad":
                ad_prob = profile.get("ad_hover_probability", 0.5)
                if random.random() > ad_prob:
                    decision["action"] = "scroll"
                    decision["reasoning"] = "Profile: skipping ad hover"
        
        # Record in session history
        self.session_history.append({
            "action": decision["action"],
            "url": current_url,
            "time": time_on_page,
            "confidence": decision.get("confidence", 0.5)
        })
        
        return decision
    
    def get_session_summary(self) -> Dict:
        """Get summary of the current session."""
        actions = [h["action"] for h in self.session_history]
        return {
            "total_actions": len(actions),
            "scrolls": actions.count("scroll"),
            "clicks": actions.count("click_link"),
            "ad_hovers": actions.count("hover_ad"),
            "exits": actions.count("exit"),
            "pages_visited": len(set(h.get("url", "") for h in self.session_history)),
            "avg_confidence": sum(h.get("confidence", 0.5) for h in self.session_history) / max(len(self.session_history), 1)
        }
    
    def reset_session(self):
        """Reset session history for a new visitor."""
        self.session_history = []
    
    async def close(self):
        await self.ai.close()


# ============================ GLOBAL ENGINE INSTANCE ============================
_engine: Optional[BehaviorEngine] = None

def get_behavior_engine() -> BehaviorEngine:
    """Get or create the global behavior engine instance."""
    global _engine
    if _engine is None:
        _engine = BehaviorEngine()
    return _engine

async def cleanup_behavior_engine():
    global _engine
    if _engine:
        await _engine.close()
        _engine = None


# ============================ TEST ============================
if __name__ == '__main__':
    async def test():
        engine = BehaviorEngine()
        
        # Test profile selection
        profile = engine.get_random_profile()
        print(f"Profile: {profile['name']}")
        
        # Test device selection
        device_type, ua, vp = engine.get_random_device()
        print(f"Device: {device_type}, Viewport: {vp['label']}")
        print(f"UA: {ua[:70]}...")
        
        # Test AI decision
        decision = await engine.decide_next_action(
            current_url="https://lopinuze.2bd.net/section-ai.html",
            page_title="Artificial Intelligence News",
            section="ai",
            scroll_percentage=0.5,
            time_on_page=30,
            device_type=device_type,
            links_visible=10,
            ads_visible=3,
            is_article=False,
            profile=profile
        )
        print(f"\nAI Decision: {json.dumps(decision, indent=2)}")
        
        # Test scroll params
        scroll = engine.get_random_scroll_params(device_type)
        print(f"\nScroll params: {json.dumps(scroll, indent=2)}")
        
        await engine.close()
    
    asyncio.run(test())