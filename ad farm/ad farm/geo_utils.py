#!/usr/bin/env python3
"""
Geo Utilities - IP Geolocation, Timezone, and Locale Matching
Ensures browser fingerprints match the proxy's actual geographical location.
Prevents timezone/locale mismatch detection.
"""

import asyncio
import random
import logging
from typing import Dict, Optional, Tuple
import aiohttp

logger = logging.getLogger('geo_utils')

# ============================ GEO IP SERVICE URLS ============================
# Free APIs for IP geolocation lookup
GEO_IP_SERVICES = [
    "https://ipapi.co/{ip}/json/",
    "https://ipinfo.io/{ip}/json",
    "https://api.ipgeolocation.io/ipgeo?apiKey=free&ip={ip}",
    "http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp",
]

# ============================ TIMEZONE MAPPINGS ============================
# Timezone -> Locale mapping
TIMEZONE_LOCALE_MAP = {
    "America/New_York": "en-US",
    "America/Chicago": "en-US",
    "America/Los_Angeles": "en-US",
    "America/Toronto": "en-CA",
    "Europe/London": "en-GB",
    "Europe/Berlin": "de-DE",
    "Europe/Paris": "fr-FR",
    "Europe/Madrid": "es-ES",
    "Europe/Rome": "it-IT",
    "Europe/Amsterdam": "nl-NL",
    "Europe/Warsaw": "pl-PL",
    "Asia/Tokyo": "ja-JP",
    "Asia/Shanghai": "zh-CN",
    "Asia/Seoul": "ko-KR",
    "Asia/Dubai": "ar-AE",
    "Asia/Kolkata": "hi-IN",
    "Asia/Karachi": "ur-PK",
    "Asia/Bangkok": "th-TH",
    "Asia/Singapore": "en-SG",
    "Australia/Sydney": "en-AU",
    "Pacific/Auckland": "en-NZ",
    "America/Sao_Paulo": "pt-BR",
    "America/Mexico_City": "es-MX",
    "Africa/Johannesburg": "en-ZA",
    "Africa/Lagos": "en-NG",
}

# Country code -> Timezone mapping (best effort)
COUNTRY_TIMEZONE_MAP = {
    "US": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"],
    "GB": ["Europe/London"],
    "DE": ["Europe/Berlin"],
    "FR": ["Europe/Paris"],
    "CA": ["America/Toronto", "America/Vancouver", "America/Edmonton"],
    "AU": ["Australia/Sydney", "Australia/Melbourne", "Australia/Brisbane", "Australia/Perth"],
    "JP": ["Asia/Tokyo"],
    "IN": ["Asia/Kolkata"],
    "BR": ["America/Sao_Paulo", "America/Fortaleza"],
    "PK": ["Asia/Karachi"],
    "AE": ["Asia/Dubai"],
    "SA": ["Asia/Riyadh"],
    "NG": ["Africa/Lagos"],
    "ZA": ["Africa/Johannesburg"],
    "SG": ["Asia/Singapore"],
    "KR": ["Asia/Seoul"],
    "CN": ["Asia/Shanghai"],
    "RU": ["Europe/Moscow", "Asia/Yekaterinburg", "Asia/Novosibirsk"],
    "MX": ["America/Mexico_City"],
    "ES": ["Europe/Madrid"],
    "IT": ["Europe/Rome"],
    "NL": ["Europe/Amsterdam"],
    "PL": ["Europe/Warsaw"],
    "TH": ["Asia/Bangkok"],
    "NZ": ["Pacific/Auckland"],
}

# ============================ GEO IP CLIENT ============================
class GeoIPClient:
    """Looks up geographical information for a given IP or proxy."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Dict] = {}  # IP -> geo data cache
    
    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def lookup_ip(self, ip: str) -> Optional[Dict]:
        """Look up geographical info for an IP address."""
        if ip in self.cache:
            return self.cache[ip]
        
        await self._ensure_session()
        
        for service_url in GEO_IP_SERVICES:
            try:
                url = service_url.format(ip=ip)
                async with self.session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data:
                            self.cache[ip] = data
                            return data
            except Exception:
                continue
        
        return None
    
    async def get_geo_from_proxy(self, proxy_url: str) -> Optional[Dict]:
        """Get geo info by making a request through the proxy."""
        await self._ensure_session()
        
        try:
            # Use httpbin to see what IP the proxy gives us
            async with self.session.get(
                "https://httpbin.org/ip",
                proxy=proxy_url,
                ssl=False
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    ip = data.get('origin', '')
                    if ip:
                        return await self.lookup_ip(ip)
        except Exception:
            pass
        
        return None
    
    def get_timezone_for_country(self, country_code: str) -> str:
        """Get a reasonable timezone for a country code."""
        timezones = COUNTRY_TIMEZONE_MAP.get(country_code, ["America/New_York"])
        return random.choice(timezones)
    
    def get_locale_for_timezone(self, timezone: str) -> str:
        """Get a locale for a timezone."""
        return TIMEZONE_LOCALE_MAP.get(timezone, "en-US")
    
    def get_language_for_locale(self, locale: str) -> str:
        """Extract language code from locale."""
        return locale.split('-')[0]
    
    async def get_browser_geo_config(self, proxy_url: Optional[str] = None) -> Dict:
        """
        Get complete geo configuration for a browser session.
        Returns timezone, locale, geolocation, and language matching the proxy.
        """
        # Default to US if no proxy
        default_config = {
            "timezone": "America/New_York",
            "locale": "en-US",
            "language": "en",
            "geolocation": {"latitude": 40.7128, "longitude": -74.0060},
            "country": "US",
            "city": "New York",
        }
        
        if not proxy_url:
            return default_config
        
        # Try to get geo from proxy
        geo_data = await self.get_geo_from_proxy(proxy_url)
        
        if not geo_data:
            # Try extracting IP from proxy URL and look it up
            try:
                # Parse IP from proxy URL
                import re
                ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', proxy_url)
                if ip_match:
                    geo_data = await self.lookup_ip(ip_match.group(1))
            except Exception:
                pass
        
        if not geo_data:
            logger.debug(f"Could not get geo for proxy, using default US config")
            return default_config
        
        # Extract geo information
        country_code = geo_data.get('countryCode', geo_data.get('country', 'US')).upper()
        timezone = geo_data.get('timezone', self.get_timezone_for_country(country_code))
        locale = self.get_locale_for_timezone(timezone)
        language = self.get_language_for_locale(locale)
        
        lat = float(geo_data.get('lat', geo_data.get('latitude', 40.7128)))
        lon = float(geo_data.get('lon', geo_data.get('longitude', -74.0060)))
        
        config = {
            "timezone": timezone,
            "locale": locale,
            "language": language,
            "geolocation": {"latitude": lat, "longitude": lon},
            "country": country_code,
            "city": geo_data.get('city', 'Unknown'),
            "region": geo_data.get('region', ''),
            "isp": geo_data.get('isp', geo_data.get('org', '')),
        }
        
        logger.debug(f"Geo config: {country_code}/{config['city']} -> tz={timezone}, locale={locale}")
        return config
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


# ============================ GLOBAL CLIENT ============================
_geo_client: Optional[GeoIPClient] = None

def get_geo_client() -> GeoIPClient:
    """Get or create the global GeoIP client."""
    global _geo_client
    if _geo_client is None:
        _geo_client = GeoIPClient()
    return _geo_client

async def cleanup_geo_client():
    global _geo_client
    if _geo_client:
        await _geo_client.close()
        _geo_client = None


# ============================ UTILITY FUNCTIONS ============================
def get_random_us_timezone() -> str:
    """Get a random US timezone."""
    return random.choice(COUNTRY_TIMEZONE_MAP["US"])

def get_random_eu_timezone() -> str:
    """Get a random European timezone."""
    eu_countries = ["GB", "DE", "FR", "NL", "ES", "IT", "PL"]
    country = random.choice(eu_countries)
    return random.choice(COUNTRY_TIMEZONE_MAP[country])

# ============================ TEST ============================
if __name__ == '__main__':
    async def test():
        client = GeoIPClient()
        
        # Test IP lookup
        print("Looking up IP 8.8.8.8...")
        geo = await client.lookup_ip("8.8.8.8")
        if geo:
            print(f"  Country: {geo.get('country')} ({geo.get('countryCode')})")
            print(f"  City: {geo.get('city')}")
            print(f"  Timezone: {geo.get('timezone')}")
        
        # Test browser config generation
        print("\nBrowser geo config for US proxy...")
        config = await client.get_browser_geo_config(None)
        print(f"  Timezone: {config['timezone']}")
        print(f"  Locale: {config['locale']}")
        print(f"  Geo: {config['geolocation']}")
        
        print("\nRandom US timezone:", get_random_us_timezone())
        print("Random EU timezone:", get_random_eu_timezone())
        
        await client.close()
    
    asyncio.run(test())