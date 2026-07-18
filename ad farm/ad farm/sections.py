#!/usr/bin/env python3
"""
50-Section Definition with Weighted Traffic Distribution
Matches LOPINUZE.2BD.NET section structure exactly.
"""

import random
from typing import List, Tuple, Dict, Any

# ============================ 50 SECTIONS ============================
# Each section maps to existing site pages at /section-{slug}.html
# Articles exist at /article-{slug}-{n}.html

SECTIONS_ALL = [
    # ---- TIER 1: High Demand (15% each totaling ~52.5%) ----
    {"slug": "tech", "name": "Technology", "tier": 1, "weight": 15.0,
     "section_url": "/section-tech.html", "article_pattern": "/article-tech-{n}.html",
     "article_count": 24, "category": "technology"},
    {"slug": "ai", "name": "Artificial Intelligence", "tier": 1, "weight": 15.0,
     "section_url": "/section-ai.html", "article_pattern": "/article-ai-{n}.html",
     "article_count": 24, "category": "technology"},
    {"slug": "gaming", "name": "Gaming", "tier": 1, "weight": 15.0,
     "section_url": "/section-gaming.html", "article_pattern": "/article-gaming-{n}.html",
     "article_count": 24, "category": "gaming"},
    {"slug": "finance", "name": "Finance", "tier": 1, "weight": 12.0,
     "section_url": "/finance.html", "article_pattern": "/article-finance-{n}.html",
     "article_count": 24, "category": "finance"},
    {"slug": "crypto", "name": "Cryptocurrency", "tier": 1, "weight": 12.0,
     "section_url": "/section-cryptocurrency.html", "article_pattern": "/article-cryptocurrency-{n}.html",
     "article_count": 24, "category": "finance"},
    {"slug": "investing", "name": "Investing", "tier": 1, "weight": 8.0,
     "section_url": "/section-investing.html", "article_pattern": "/article-investing-{n}.html",
     "article_count": 24, "category": "finance"},
    {"slug": "world-news", "name": "World News", "tier": 1, "weight": 8.0,
     "section_url": "/section-world-news.html", "article_pattern": "/article-world-news-{n}.html",
     "article_count": 24, "category": "world"},

    # ---- TIER 2: Medium Demand (5% each totaling ~35%) ----
    {"slug": "health", "name": "Health", "tier": 2, "weight": 5.0,
     "section_url": "/section-health.html", "article_pattern": "/article-health-{n}.html",
     "article_count": 24, "category": "health"},
    {"slug": "fitness", "name": "Fitness", "tier": 2, "weight": 5.0,
     "section_url": "/section-fitness.html", "article_pattern": "/article-fitness-{n}.html",
     "article_count": 24, "category": "health"},
    {"slug": "science", "name": "Science", "tier": 2, "weight": 5.0,
     "section_url": "/section-science.html", "article_pattern": "/article-science-{n}.html",
     "article_count": 24, "category": "science"},
    {"slug": "nutrition", "name": "Nutrition", "tier": 2, "weight": 5.0,
     "section_url": "/section-nutrition.html", "article_pattern": "/article-nutrition-{n}.html",
     "article_count": 24, "category": "health"},
    {"slug": "cybersecurity", "name": "Cybersecurity", "tier": 2, "weight": 5.0,
     "section_url": "/section-cybersecurity.html", "article_pattern": "/article-cybersecurity-{n}.html",
     "article_count": 24, "category": "technology"},
    {"slug": "cloud-computing", "name": "Cloud Computing", "tier": 2, "weight": 5.0,
     "section_url": "/section-cloud-computing.html", "article_pattern": "/article-cloud-computing-{n}.html",
     "article_count": 24, "category": "technology"},
    {"slug": "blockchain", "name": "Blockchain", "tier": 2, "weight": 5.0,
     "section_url": "/section-blockchain.html", "article_pattern": "/article-blockchain-{n}.html",
     "article_count": 24, "category": "technology"},

    # ---- TIER 3: Developing/Regional (1-2% each totaling ~30%) ----
    {"slug": "machine-learning", "name": "Machine Learning", "tier": 3, "weight": 2.0,
     "section_url": "/section-machine-learning.html", "article_pattern": "/article-machine-learning-{n}.html",
     "article_count": 24, "category": "technology"},
    {"slug": "deep-learning", "name": "Deep Learning", "tier": 3, "weight": 2.0,
     "section_url": "/section-deep-learning.html", "article_pattern": "/article-deep-learning-{n}.html",
     "article_count": 24, "category": "technology"},
    {"slug": "robotics", "name": "Robotics", "tier": 3, "weight": 2.0,
     "section_url": "/section-robotics.html", "article_pattern": "/article-robotics-{n}.html",
     "article_count": 24, "category": "technology"},
    {"slug": "vr-ar", "name": "VR/AR", "tier": 3, "weight": 2.0,
     "section_url": "/section-vr-ar.html", "article_pattern": "/article-vr-ar-{n}.html",
     "article_count": 24, "category": "technology"},
    {"slug": "esports", "name": "Esports", "tier": 3, "weight": 2.0,
     "section_url": "/section-esports.html", "article_pattern": "/article-esports-{n}.html",
     "article_count": 24, "category": "gaming"},
    {"slug": "game-reviews", "name": "Game Reviews", "tier": 3, "weight": 2.0,
     "section_url": "/section-game-reviews.html", "article_pattern": "/article-game-reviews-{n}.html",
     "article_count": 24, "category": "gaming"},
    {"slug": "game-development", "name": "Game Development", "tier": 3, "weight": 2.0,
     "section_url": "/section-game-development.html", "article_pattern": "/article-game-development-{n}.html",
     "article_count": 24, "category": "gaming"},
    {"slug": "mobile-gaming", "name": "Mobile Gaming", "tier": 3, "weight": 2.0,
     "section_url": "/section-mobile-gaming.html", "article_pattern": "/article-mobile-gaming-{n}.html",
     "article_count": 24, "category": "gaming"},
    {"slug": "fintech", "name": "FinTech", "tier": 3, "weight": 2.0,
     "section_url": "/section-fintech.html", "article_pattern": "/article-fintech-{n}.html",
     "article_count": 24, "category": "finance"},
    {"slug": "trading", "name": "Trading", "tier": 3, "weight": 2.0,
     "section_url": "/section-trading.html", "article_pattern": "/article-trading-{n}.html",
     "article_count": 24, "category": "finance"},
    {"slug": "personal-finance", "name": "Personal Finance", "tier": 3, "weight": 2.0,
     "section_url": "/section-personal-finance.html", "article_pattern": "/article-personal-finance-{n}.html",
     "article_count": 24, "category": "finance"},
    {"slug": "real-estate", "name": "Real Estate", "tier": 3, "weight": 2.0,
     "section_url": "/section-real-estate.html", "article_pattern": "/article-real-estate-{n}.html",
     "article_count": 24, "category": "finance"},
    {"slug": "stock-market", "name": "Stock Market", "tier": 3, "weight": 2.0,
     "section_url": "/section-stock-market.html", "article_pattern": "/article-stock-market-{n}.html",
     "article_count": 24, "category": "finance"},
    {"slug": "etfs", "name": "ETFs", "tier": 3, "weight": 1.5,
     "section_url": "/section-etfs.html", "article_pattern": "/article-etfs-{n}.html",
     "article_count": 24, "category": "finance"},
    {"slug": "forex", "name": "Forex", "tier": 3, "weight": 1.5,
     "section_url": "/section-forex.html", "article_pattern": "/article-forex-{n}.html",
     "article_count": 24, "category": "finance"},
    {"slug": "crypto-mining", "name": "Crypto Mining", "tier": 3, "weight": 1.5,
     "section_url": "/section-crypto-mining.html", "article_pattern": "/article-crypto-mining-{n}.html",
     "article_count": 24, "category": "finance"},
    {"slug": "defi", "name": "DeFi", "tier": 3, "weight": 1.5,
     "section_url": "/section-defi.html", "article_pattern": "/article-defi-{n}.html",
     "article_count": 24, "category": "finance"},
    # Health sub-sections
    {"slug": "mental-health", "name": "Mental Health", "tier": 3, "weight": 2.0,
     "section_url": "/section-mental-health.html", "article_pattern": "/article-mental-health-{n}.html",
     "article_count": 24, "category": "health"},
    {"slug": "supplements", "name": "Supplements", "tier": 3, "weight": 1.5,
     "section_url": "/section-supplements.html", "article_pattern": "/article-supplements-{n}.html",
     "article_count": 24, "category": "health"},
    {"slug": "weight-loss", "name": "Weight Loss", "tier": 3, "weight": 1.5,
     "section_url": "/section-weight-loss.html", "article_pattern": "/article-weight-loss-{n}.html",
     "article_count": 24, "category": "health"},
    {"slug": "yoga-meditation", "name": "Yoga/Meditation", "tier": 3, "weight": 1.0,
     "section_url": "/section-yoga-meditation.html", "article_pattern": "/article-yoga-meditation-{n}.html",
     "article_count": 24, "category": "health"},
    {"slug": "medicine", "name": "Medicine", "tier": 3, "weight": 1.5,
     "section_url": "/section-medicine.html", "article_pattern": "/article-medicine-{n}.html",
     "article_count": 24, "category": "health"},
    {"slug": "psychology", "name": "Psychology", "tier": 3, "weight": 1.5,
     "section_url": "/section-psychology.html", "article_pattern": "/article-psychology-{n}.html",
     "article_count": 24, "category": "health"},
    # Science sub-sections
    {"slug": "astronomy", "name": "Astronomy", "tier": 3, "weight": 1.5,
     "section_url": "/section-astronomy.html", "article_pattern": "/article-astronomy-{n}.html",
     "article_count": 24, "category": "science"},
    {"slug": "geology", "name": "Geology", "tier": 3, "weight": 1.0,
     "section_url": "/section-geology.html", "article_pattern": "/article-geology-{n}.html",
     "article_count": 24, "category": "science"},
    {"slug": "environment", "name": "Environment", "tier": 3, "weight": 1.5,
     "section_url": "/section-environment.html", "article_pattern": "/article-environment-{n}.html",
     "article_count": 24, "category": "science"},
    {"slug": "space", "name": "Space", "tier": 3, "weight": 1.5,
     "section_url": "/section-space.html", "article_pattern": "/article-space-{n}.html",
     "article_count": 24, "category": "science"},
    {"slug": "physics", "name": "Physics", "tier": 3, "weight": 1.5,
     "section_url": "/section-physics.html", "article_pattern": "/article-physics-{n}.html",
     "article_count": 24, "category": "science"},
    {"slug": "biology", "name": "Biology", "tier": 3, "weight": 1.5,
     "section_url": "/section-biology.html", "article_pattern": "/article-biology-{n}.html",
     "article_count": 24, "category": "science"},
    {"slug": "chemistry", "name": "Chemistry", "tier": 3, "weight": 1.5,
     "section_url": "/section-chemistry.html", "article_pattern": "/article-chemistry-{n}.html",
     "article_count": 24, "category": "science"},
    {"slug": "neuroscience", "name": "Neuroscience", "tier": 3, "weight": 1.5,
     "section_url": "/section-neuroscience.html", "article_pattern": "/article-neuroscience-{n}.html",
     "article_count": 24, "category": "science"},
    {"slug": "climate", "name": "Climate", "tier": 3, "weight": 1.5,
     "section_url": "/section-climate.html", "article_pattern": "/article-climate-{n}.html",
     "article_count": 24, "category": "science"},
    {"slug": "energy", "name": "Energy", "tier": 3, "weight": 1.5,
     "section_url": "/section-energy.html", "article_pattern": "/article-energy-{n}.html",
     "article_count": 24, "category": "science"},
    # World/News sub-sections
    {"slug": "us-news", "name": "US News", "tier": 3, "weight": 2.0,
     "section_url": "/section-us-news.html", "article_pattern": "/article-us-news-{n}.html",
     "article_count": 24, "category": "world"},
    {"slug": "asia-news", "name": "Asia News", "tier": 3, "weight": 2.0,
     "section_url": "/section-asia-news.html", "article_pattern": "/article-asia-news-{n}.html",
     "article_count": 24, "category": "world"},
    {"slug": "europe-news", "name": "Europe News", "tier": 3, "weight": 2.0,
     "section_url": "/section-europe-news.html", "article_pattern": "/article-europe-news-{n}.html",
     "article_count": 24, "category": "world"},
    {"slug": "education", "name": "Education", "tier": 3, "weight": 2.0,
     "section_url": "/section-education.html", "article_pattern": "/article-education-{n}.html",
     "article_count": 24, "category": "world"},
    {"slug": "politics", "name": "Politics", "tier": 3, "weight": 2.0,
     "section_url": "/section-politics.html", "article_pattern": "/article-politics-{n}.html",
     "article_count": 24, "category": "world"},
]

# ============================ SECTION LOOKUP ============================
SECTION_BY_SLUG: Dict[str, Dict[str, Any]] = {s["slug"]: s for s in SECTIONS_ALL}
SECTION_NAMES: List[str] = [s["name"] for s in SECTIONS_ALL]
SECTION_SLUGS: List[str] = [s["slug"] for s in SECTIONS_ALL]

# ============================ WEIGHTED SELECTION ============================
def _build_weighted_list() -> List[Tuple[str, float]]:
    """Build list of (slug, cumulative_weight) for weighted random selection."""
    weighted = []
    cumulative = 0.0
    for s in SECTIONS_ALL:
        cumulative += s["weight"]
        weighted.append((s["slug"], cumulative))
    return weighted

WEIGHTED_SECTIONS = _build_weighted_list()
TOTAL_WEIGHT = WEIGHTED_SECTIONS[-1][1]


def get_random_section() -> Dict[str, Any]:
    """Return a random section based on weighted distribution."""
    r = random.random() * TOTAL_WEIGHT
    for slug, cum_weight in WEIGHTED_SECTIONS:
        if r <= cum_weight:
            return SECTION_BY_SLUG[slug]
    return SECTIONS_ALL[0]


def get_random_article_url(section: Dict[str, Any]) -> str:
    """Get a random article URL for a given section."""
    n = random.randint(1, section["article_count"])
    return section["article_pattern"].format(n=n)


def get_latest_article_url(section: Dict[str, Any]) -> str:
    """
    Get an article URL with freshness bias — higher numbers = newer.
    Uses configurable ARTICLE_FRESHNESS_BIAS from config.py.
    
    75% chance (default): pick from the newest 50% of articles
    25% chance: pick any article (uniform)
    
    This makes Google see that new content gets immediate engagement
    while old content still gets occasional traffic (archive browsing).
    """
    from config import ARTICLE_FRESHNESS_BIAS, RECENT_ARTICLE_THRESHOLD
    
    total = section["article_count"]
    recent_start = int(total * (1 - RECENT_ARTICLE_THRESHOLD)) + 1  # e.g., 13 for 24 articles
    
    if random.random() < ARTICLE_FRESHNESS_BIAS:
        # Pick from recent half (higher article numbers)
        n = random.randint(recent_start, total)
    else:
        # Pick from any article (including older ones — realistic archive browsing)
        n = random.randint(1, total)
    
    return section["article_pattern"].format(n=n)


def get_article_url_between(section: Dict[str, Any], min_age_hours: int = 2, max_age_hours: int = 168) -> str:
    """
    Get an article URL with age-gating — avoids brand-new articles (<2h old)
    that Google hasn't indexed yet, and very old articles (>1 week).
    
    Maps article numbers to ages: article-1 = oldest (~1 week), article-24 = newest (now).
    Skips the very newest articles to let Google index them first.
    """
    total = section["article_count"]
    
    # Assume linear mapping: article-1 = max_age_hours old, article-24 = 0 hours old
    # We want articles between min_age_hours and max_age_hours old
    oldest_n = 1
    newest_allowed_n = int(total * (1 - min_age_hours / max_age_hours))
    newest_allowed_n = max(1, min(newest_allowed_n, total - 1))
    
    # Pick from the safe range (indexed articles, not too fresh)
    n = random.randint(oldest_n, newest_allowed_n)
    
    return section["article_pattern"].format(n=n)


def get_section_url(section: Dict[str, Any]) -> str:
    """Get the section index URL."""
    return section["section_url"]


def get_section_by_slug(slug: str) -> Dict[str, Any]:
    """Get section data by slug."""
    return SECTION_BY_SLUG.get(slug, SECTIONS_ALL[0])


def get_tier_sections(tier: int) -> List[Dict[str, Any]]:
    """Get all sections for a given tier."""
    return [s for s in SECTIONS_ALL if s["tier"] == tier]


def get_section_count() -> int:
    """Return total number of sections."""
    return len(SECTIONS_ALL)


# ============================ AD DENSITY PER SECTION ============================
def get_ad_density(section: Dict[str, Any]) -> str:
    """Return ad density level based on section tier and category."""
    if section["tier"] == 1:
        return "high"
    elif section["tier"] == 2:
        return "medium"
    else:
        return "low"


if __name__ == '__main__':
    print(f"Total sections: {len(SECTIONS_ALL)}")
    print(f"Total weight: {TOTAL_WEIGHT}")
    
    # Test weighted distribution
    from collections import Counter
    counts = Counter()
    for _ in range(10000):
        s = get_random_section()
        counts[s["slug"]] += 1
    
    print("\nDistribution test (10,000 random picks):")
    for slug, count in counts.most_common(15):
        pct = (count / 10000) * 100
        expected = SECTION_BY_SLUG[slug]["weight"]
        print(f"  {slug:25s}: {pct:5.1f}% (expected {expected:5.1f}%)")