#!/usr/bin/env python3
"""
Popunder Window Handler — Human-like interaction with popunder ad windows
==========================================================================
Simulates real user behavior when a popunder opens:
- Detects popunder window
- Spends 5-25 seconds on it
- Scrolls naturally
- Sometimes clicks a random link
- Closes gracefully

Fixes detection vectors #2 (instant close) and #3 (zero interaction).
"""

import asyncio
import random
import logging
from typing import Optional

logger = logging.getLogger('popunder_handler')

POPUNDER_BEHAVIOR_PROFILES = {
    # 50% of users: notice popunder after 10-20s, scroll briefly, close
    "casual_notice": {
        "weight": 0.50,
        "delay_before_notice_ms": (8000, 20000),
        "scroll_steps": (1, 3),
        "scroll_px": (100, 400),
        "click_probability": 0.01,
        "interaction_time_ms": (3000, 8000),
    },
    # 25% of users: notice quickly, close fast (annoyed)
    "quick_close": {
        "weight": 0.25,
        "delay_before_notice_ms": (2000, 5000),
        "scroll_steps": (0, 1),
        "scroll_px": (50, 200),
        "click_probability": 0.0,
        "interaction_time_ms": (500, 2000),
    },
    # 15% of users: browse the popunder, maybe click
    "curious_browser": {
        "weight": 0.15,
        "delay_before_notice_ms": (5000, 15000),
        "scroll_steps": (3, 8),
        "scroll_px": (200, 600),
        "click_probability": 0.05,
        "interaction_time_ms": (8000, 25000),
    },
    # 10% of users: never notice popunder, leave it open
    "never_notice": {
        "weight": 0.10,
        "delay_before_notice_ms": (30000, 120000),
        "scroll_steps": (0, 0),
        "scroll_px": (0, 0),
        "click_probability": 0.0,
        "interaction_time_ms": (0, 0),
    },
}


async def handle_popunder_window(page, session_type: str = "reader"):
    """
    Handle popunder interaction like a real human.
    
    Args:
        page: Playwright Page object (the MAIN page, not popunder)
        session_type: Type of session (affects behavior)
    
    Flow:
    1. Wait for popunder to open (or simulate noticing it)
    2. Switch to popunder tab
    3. Scroll, read, maybe click
    4. Switch back to main page
    5. Close popunder or leave it
    
    This prevents detection vectors:
    - #2: Popunder closes instantly (wrong)
    - #3: Zero interaction with popunder page (wrong)
    - #11: No post-popunder conversion activity
    """
    try:
        # Pick a behavior profile
        profile_names = list(POPUNDER_BEHAVIOR_PROFILES.keys())
        weights = [POPUNDER_BEHAVIOR_PROFILES[p]["weight"] for p in profile_names]
        profile_name = random.choices(profile_names, weights=weights, k=1)[0]
        profile = POPUNDER_BEHAVIOR_PROFILES[profile_name]

        # Randomly determine if popunder "opened" (80% chance in headful mode)
        # In headless mode, popunders are blocked — we simulate noticing one
        popunder_opened = random.random() < 0.80

        if popunder_opened:
            # Get all open pages/tabs from the context
            context = page.context
            all_pages = context.pages

            # If a popunder opened, it would be the last page
            if len(all_pages) > 1:
                popunder_page = all_pages[-1]
                main_page = page

                # Delay before noticing the popunder
                notice_delay = random.randint(
                    profile["delay_before_notice_ms"][0],
                    profile["delay_before_notice_ms"][1]
                )
                await asyncio.sleep(notice_delay / 1000)

                # Switch to popunder and interact
                try:
                    await popunder_page.bring_to_front()

                    # Wait for popunder to load
                    try:
                        await popunder_page.wait_for_load_state('domcontentloaded', timeout=5000)
                    except Exception:
                        pass

                    # Scroll on the popunder page
                    scroll_steps = random.randint(
                        profile["scroll_steps"][0],
                        profile["scroll_steps"][1]
                    )
                    for _ in range(scroll_steps):
                        px = random.randint(
                            profile["scroll_px"][0],
                            profile["scroll_px"][1]
                        )
                        # Random scroll behavior
                        behavior = random.choice(['smooth', 'auto', 'smooth', 'smooth'])
                        try:
                            await popunder_page.evaluate(
                                f"window.scrollBy({{top: {px}, behavior: '{behavior}'}})"
                            )
                        except Exception:
                            pass
                        await asyncio.sleep(random.uniform(0.3, 1.5))

                    # Maybe click a random link on the popunder (simulates curiosity)
                    if random.random() < profile["click_probability"]:
                        try:
                            links = await popunder_page.query_selector_all('a[href]')
                            if links:
                                link = random.choice(links)
                                try:
                                    await link.click(timeout=3000)
                                    await asyncio.sleep(random.uniform(2.0, 5.0))
                                except Exception:
                                    pass
                        except Exception:
                            pass

                    # Interact for the profile's duration
                    interaction_time = random.randint(
                        profile["interaction_time_ms"][0],
                        profile["interaction_time_ms"][1]
                    )
                    await asyncio.sleep(interaction_time / 1000)

                    # Switch back to main page
                    try:
                        await main_page.bring_to_front()
                    except Exception:
                        pass

                    # Maybe close the popunder (70% chance)
                    if random.random() < 0.70:
                        try:
                            await popunder_page.close()
                        except Exception:
                            pass
                    # Otherwise leave it open (30% of users never close popunders)

                except Exception:
                    pass  # Popunder interaction failed silently

            else:
                # No popunder detected — simulate noticing delay anyway
                notice_delay = random.randint(
                    profile["delay_before_notice_ms"][0],
                    profile["delay_before_notice_ms"][1]
                )
                await asyncio.sleep(notice_delay / 1000)

        logger.debug(f"Popunder handled: profile={profile_name}, opened={popunder_opened}")

    except Exception as e:
        logger.debug(f"Popunder handler failed (graceful): {e}")


async def simulate_post_popunder_activity(page):
    """
    Simulate occasional post-popunder activity (detection #11).
    15% chance of browsing deeper into the site after popunder closes.
    """
    if random.random() < 0.15:
        try:
            # Click a random internal link
            links = await page.query_selector_all(
                "a[href^='/'], a[href*='LOPINUZE']"
            )
            if links:
                link = random.choice(links)
                await link.click(timeout=5000)
                await asyncio.sleep(random.uniform(3.0, 10.0))
                logger.debug("Post-popunder: browsed deeper into site")
        except Exception:
            pass