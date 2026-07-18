#!/usr/bin/env python3
"""
Ad Code Auto-Injector — Inserts HilltopAds codes into all HTML files.
This is CRITICAL — the farm can't interact with ads that don't exist!
Run this ONCE before starting the farm.

Usage: python ad_injector.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict

# ============================ AD CODES TO INJECT ============================
# Replace YOUR_PUBLISHER_ID with your actual HilltopAds publisher ID
# Get it from: https://user.hilltopads.com/ publisher dashboard
PUBLISHER_ID = "YOUR_PUBLISHER_ID"

POPUNDER_CODE = f"""<!-- HilltopAds Pop-under -->
<script>
(function() {{
    var s = document.createElement('script');
    s.type = 'text/javascript';
    s.async = true;
    s.src = 'https://api.hilltopads.com/popunder/publisher/{PUBLISHER_ID}.js';
    var x = document.getElementsByTagName('script')[0];
    x.parentNode.insertBefore(s, x);
}})();
</script>"""

BANNER_728_CODE = f"""<!-- HilltopAds Banner 728x90 -->
<div id="ad-banner-728" class="ad-container hilltop-banner" style="text-align:center;margin:15px auto;max-width:728px;overflow:hidden;">
<script>
(function() {{
    var s = document.createElement('script');
    s.type = 'text/javascript';
    s.async = true;
    s.src = 'https://api.hilltopads.com/banner/publisher/{PUBLISHER_ID}/728x90.js';
    var x = document.getElementsByTagName('script')[0];
    x.parentNode.insertBefore(s, x);
}})();
</script>
</div>"""

BANNER_300_CODE = f"""<!-- HilltopAds Banner 300x250 -->
<div id="ad-sidebar-300" class="ad-container hilltop-sidebar" style="text-align:center;margin:15px auto;max-width:300px;overflow:hidden;">
<script>
(function() {{
    var s = document.createElement('script');
    s.type = 'text/javascript';
    s.async = true;
    s.src = 'https://api.hilltopads.com/banner/publisher/{PUBLISHER_ID}/300x250.js';
    var x = document.getElementsByTagName('script')[0];
    x.parentNode.insertBefore(s, x);
}})();
</script>
</div>"""

NATIVE_AD_CODE = f"""<!-- HilltopAds Native Ad -->
<div id="ad-native-content" class="ad-container hilltop-native" style="text-align:center;margin:15px auto;max-width:100%;overflow:hidden;">
<script>
(function() {{
    var s = document.createElement('script');
    s.type = 'text/javascript';
    s.async = true;
    s.src = 'https://api.hilltopads.com/native/publisher/{PUBLISHER_ID}.js';
    var x = document.getElementsByTagName('script')[0];
    x.parentNode.insertBefore(s, x);
}})();
</script>
</div>"""

DIRECT_LINK_CODE = f"""<!-- HilltopAds Direct Link -->
<div id="ad-direct-link" class="ad-container hilltop-direct" style="text-align:center;margin:10px auto;overflow:hidden;">
<script>
(function() {{
    var s = document.createElement('script');
    s.type = 'text/javascript';
    s.async = true;
    s.src = 'https://api.hilltopads.com/direct/publisher/{PUBLISHER_ID}.js';
    var x = document.getElementsByTagName('script')[0];
    x.parentNode.insertBefore(s, x);
}})();
</script>
</div>"""


class AdInjector:
    """Injects HilltopAds codes into static HTML files."""
    
    def __init__(self, news_dir: str, publisher_id: str):
        self.news_dir = Path(news_dir)
        self.publisher_id = publisher_id
        self.stats = {"popunder": 0, "banner_728": 0, "banner_300": 0, "native": 0, "direct_link": 0}
    
    def inject_all(self):
        """Process all HTML files in the news directory."""
        html_files = list(self.news_dir.glob("*.html"))
        
        if not html_files:
            print(f"❌ No HTML files found in {self.news_dir}")
            return
        
        print(f"Found {len(html_files)} HTML files")
        print(f"Publisher ID: {self.publisher_id}")
        print()
        
        for i, filepath in enumerate(html_files, 1):
            self._inject_file(filepath)
            if i % 50 == 0:
                print(f"  Processed {i}/{len(html_files)}...")
        
        print(f"\n✅ Injection complete!")
        print(f"   Pop-under:  {self.stats['popunder']} files")
        print(f"   Banner 728: {self.stats['banner_728']} files")
        print(f"   Banner 300: {self.stats['banner_300']} files")
        print(f"   Native:     {self.stats['native']} files")
        print(f"   Direct Link: {self.stats['direct_link']} files")
    
    def _inject_file(self, filepath: Path):
        """Inject ads into a single HTML file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already injected
        if 'hilltopads.com' in content:
            return
        
        modified = content
        
        # Determine page type
        is_homepage = 'index.html' in str(filepath).lower()
        is_section = 'section-' in str(filepath).lower() or 'finance.html' in str(filepath).lower()
        is_article = 'article-' in str(filepath).lower()
        
        # 1. Inject pop-under before </body> (EVERY page)
        if '</body>' in modified:
            modified = modified.replace('</body>', f'{POPUNDER_CODE}\n</body>')
            self.stats['popunder'] += 1
        
        # 2. Inject banner 728x90 on homepage and section pages
        if is_homepage or is_section:
            # After breaking-news-bar or after masthead
            if '.breaking-news-bar' in modified:
                modified = re.sub(
                    r'(<div class="breaking-news-bar".*?</div>)',
                    r'\1\n' + BANNER_728_CODE,
                    modified, count=1, flags=re.DOTALL
                )
            elif '.masthead' in modified:
                modified = re.sub(
                    r'(</div>\s*</div>\s*</div>\s*<div class="trust-bar")',
                    BANNER_728_CODE + r'\n\1',
                    modified, count=1, flags=re.DOTALL
                )
            else:
                # Insert after first <div class="container">
                modified = modified.replace(
                    '<div class="container">',
                    f'<div class="container">\n{BANNER_728_CODE}',
                    1
                )
            self.stats['banner_728'] += 1
        
        # 3. Inject banner 300x250 on article pages
        if is_article:
            if '.key-takeaways' in modified:
                modified = re.sub(
                    r'(<div class="key-takeaways".*?</div>)',
                    r'\1\n' + BANNER_300_CODE,
                    modified, count=1, flags=re.DOTALL
                )
            elif '.editor-note' in modified:
                modified = re.sub(
                    r'(<div class="editor-note".*?</div>)',
                    r'\1\n' + BANNER_300_CODE,
                    modified, count=1, flags=re.DOTALL
                )
            self.stats['banner_300'] += 1
        
        # 4. Inject native ads in article content
        if is_article and '.content' in modified:
            # After first <p> in content
            content_match = re.search(r'(<div class="content">.*?)(<p>)', modified, re.DOTALL)
            if content_match:
                insert_pos = content_match.end(1)
                modified = modified[:insert_pos] + NATIVE_AD_CODE + modified[insert_pos:]
                self.stats['native'] += 1
        
        # 5. Inject direct link ad on section pages (extra revenue)
        if is_section and '.section-grid' in modified:
            modified = re.sub(
                r'(<div class="section-grid".*?</div>)',
                r'\1\n' + DIRECT_LINK_CODE,
                modified, count=1, flags=re.DOTALL
            )
            self.stats['direct_link'] += 1
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(modified)


def main():
    print("=" * 60)
    print("  HILLTOPADS AD CODE INJECTOR")
    print("=" * 60)
    print()
    
    # Get publisher ID from .env if available
    publisher_id = "YOUR_PUBLISHER_ID"
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('HILLTOPADS_PUBLISHER_ID='):
                    publisher_id = line.split('=', 1)[1].strip()
                    break
    
    if publisher_id == 'YOUR_PUBLISHER_ID' or not publisher_id:
        print("⚠️  WARNING: Publisher ID not set!")
        print("   Edit .env and set HILLTOPADS_PUBLISHER_ID=your_actual_id")
        print("   Then run: python ad_injector.py")
        return
    
    # Find news-empire directory
    news_dir = Path(__file__).parent.parent / 'news-empire'
    if not news_dir.exists():
        print(f"❌ News directory not found: {news_dir}")
        print("   Make sure news-empire/ exists in parent directory")
        return
    
    injector = AdInjector(str(news_dir), publisher_id)
    injector.inject_all()
    
    print()
    print("=" * 60)
    print("  NEXT STEPS:")
    print("  1. Your HTML files now have HilltopAds codes")
    print("  2. Verify: open any article-*.html in browser")
    print("  3. Run the farm: python farm.py")
    print("=" * 60)


if __name__ == '__main__':
    main()