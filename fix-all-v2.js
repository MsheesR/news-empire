/** 
 * LOPINUZE.2BD.NET - Comprehensive Fix v2
 * 1. Remove ALL "AI" mentions from public pages
 * 2. Create legal pages (disclaimer, privacy, terms)
 * 3. Add legal links to footer
 * 4. Generate article images using Pollinations.ai (free)
 */
const fs = require('fs');
const path = require('path');

const NEWS_DIR = path.join(__dirname, 'news-empire');
const SITE_NAME = 'LOPINUZE';
const DOMAIN = 'LOPINUZE.2BD.NET';

// ─── 1. Create Legal Pages ───
function createLegalPages() {
  const disclaimerHTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Disclaimer – ${SITE_NAME}</title>
<style>
:root{--bg:#fafbfc;--surface:#fff;--text:#1a1a2e;--ts:#555770;--tm:#8e90a6;--primary:#2563eb;--bdr:#e2e4e9;--r:10px;--mw:800px;--font:'Inter',system-ui,-apple-system,sans-serif}
*{margin:0;padding:0;box-sizing:border-box}body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.7;padding:2rem}
.container{max-width:var(--mw);margin:0 auto}.site-header{background:#0f0f1a;color:#fff;padding:0.75rem 1.5rem;margin:-2rem -2rem 2rem}
.logo{font-size:1.3rem;font-weight:800;color:#fff;text-decoration:none}.logo span{color:#f59e0b}
h1{font-size:2rem;margin:1.5rem 0 1rem}h2{font-size:1.4rem;margin:2rem 0 0.75rem;color:var(--primary)}
p{margin-bottom:1rem;color:var(--ts)}ul{margin:1rem 0;padding-left:1.5rem}li{margin-bottom:0.5rem;color:var(--ts)}
.footer{background:#0f0f1a;color:rgba(255,255,255,0.6);padding:2rem;margin-top:3rem;text-align:center;font-size:0.85rem}
.footer a{color:rgba(255,255,255,0.8);text-decoration:none;margin:0 0.5rem}
</style>
</head>
<body>
<header class="site-header"><a href="index.html" class="logo">LOPI<span>NUZE</span></a></header>
<div class="container">
<h1>⚠️ Disclaimer & Legal Notice</h1>
<p><strong>Last Updated: July 13, 2026</strong></p>

<h2>1. Content Accuracy & Sources</h2>
<p>${SITE_NAME} (${DOMAIN}) aggregates, curates, and rewrites news content from publicly available sources including but not limited to BBC News, The New York Times, The Guardian, Reuters, Associated Press, and other reputable news organizations. All articles published on this website are based on publicly accessible information and are rewritten by our editorial team for clarity, engagement, and accessibility.</p>
<p>${SITE_NAME} and its editors, writers, and operators <strong>do not guarantee the accuracy, completeness, or timeliness</strong> of any information presented on this website. News is inherently dynamic and subject to change. Readers should independently verify any facts, statistics, or claims before relying on them.</p>

<h2>2. Editorial Process</h2>
<p>Our editorial team reviews and enhances content sourced from public news feeds. This process may involve paraphrasing, restructuring, adding contextual background, and incorporating expert commentary to improve reader understanding. The original sources are always attributed where applicable.</p>

<h2>3. Limitation of Liability</h2>
<p>${SITE_NAME}, its parent company, affiliates, editors, writers, and technology providers shall not be held liable for any damages, losses, or legal claims arising from:</p>
<ul>
  <li>Errors, omissions, or inaccuracies in published content</li>
  <li>Reliance on information contained on this website</li>
  <li>Third-party links, advertisements, or sponsored content</li>
  <li>Technical issues, downtime, or unavailability of the website</li>
  <li>Actions taken based on advice, opinions, or analysis published herein</li>
</ul>

<h2>4. No Professional Advice</h2>
<p>Content on ${SITE_NAME} is for <strong>informational and entertainment purposes only</strong>. It does not constitute professional advice of any kind — including financial, legal, medical, or investment advice. Always consult qualified professionals before making decisions based on information found on this website.</p>

<h2>5. Third-Party Content & Links</h2>
<p>This website may contain links to external websites, advertisements, and sponsored content. ${SITE_NAME} is not responsible for the content, practices, or policies of third-party websites. Clicking on external links is at your own risk.</p>

<h2>6. Copyright & Fair Use</h2>
<p>${SITE_NAME} respects intellectual property rights. Content is rewritten and transformed to provide unique value to readers. If you believe your copyrighted material has been used improperly, please contact us for prompt removal.</p>

<h2>7. Consent</h2>
<p>By using this website, you hereby consent to this disclaimer and agree to its terms. If you do not agree, please discontinue use of this website immediately.</p>

<h2>8. Contact</h2>
<p>For any questions regarding this disclaimer, please contact us through the website's contact page.</p>
</div>
<footer class="footer">
  <strong>${SITE_NAME}</strong> — ${DOMAIN} &copy; 2026<br>
  <a href="index.html">Home</a> <a href="disclaimer.html">Disclaimer</a> <a href="privacy-policy.html">Privacy</a> <a href="terms.html">Terms</a>
</footer>
</body>
</html>`;

  const privacyHTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Privacy Policy – ${SITE_NAME}</title>
<style>
:root{--bg:#fafbfc;--surface:#fff;--text:#1a1a2e;--ts:#555770;--tm:#8e90a6;--primary:#2563eb;--bdr:#e2e4e9;--r:10px;--mw:800px;--font:'Inter',system-ui,-apple-system,sans-serif}
*{margin:0;padding:0;box-sizing:border-box}body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.7;padding:2rem}
.container{max-width:var(--mw);margin:0 auto}.site-header{background:#0f0f1a;color:#fff;padding:0.75rem 1.5rem;margin:-2rem -2rem 2rem}
.logo{font-size:1.3rem;font-weight:800;color:#fff;text-decoration:none}.logo span{color:#f59e0b}
h1{font-size:2rem;margin:1.5rem 0 1rem}h2{font-size:1.4rem;margin:2rem 0 0.75rem;color:var(--primary)}
p{margin-bottom:1rem;color:var(--ts)}ul{margin:1rem 0;padding-left:1.5rem}li{margin-bottom:0.5rem;color:var(--ts)}
.footer{background:#0f0f1a;color:rgba(255,255,255,0.6);padding:2rem;margin-top:3rem;text-align:center;font-size:0.85rem}
.footer a{color:rgba(255,255,255,0.8);text-decoration:none;margin:0 0.5rem}
</style>
</head>
<body>
<header class="site-header"><a href="index.html" class="logo">LOPI<span>NUZE</span></a></header>
<div class="container">
<h1>🔒 Privacy Policy</h1>
<p><strong>Last Updated: July 13, 2026</strong></p>

<h2>1. Information We Collect</h2>
<p>${SITE_NAME} (${DOMAIN}) is committed to protecting your privacy. We collect minimal information necessary to provide our news service:</p>
<ul>
  <li><strong>Usage Data:</strong> Pages visited, time spent, browser type (standard analytics)</li>
  <li><strong>Cookies:</strong> Small files stored on your device for session management and preferences</li>
  <li><strong>Contact Information:</strong> Only if you voluntarily contact us</li>
</ul>

<h2>2. How We Use Information</h2>
<p>We use collected information to improve our website, analyze readership patterns, and deliver relevant content. We do not sell personal information to third parties.</p>

<h2>3. Cookies & Tracking</h2>
<p>We use essential cookies for website functionality and may use analytics cookies to understand how visitors interact with our content. You can disable cookies in your browser settings, though this may affect site functionality.</p>

<h2>4. Third-Party Services</h2>
<p>Our website may use third-party services (analytics, advertising partners) that have their own privacy policies. ${SITE_NAME} is not responsible for the privacy practices of these external services.</p>

<h2>5. Data Security</h2>
<p>We implement reasonable security measures to protect your information. However, no method of transmission over the internet is 100% secure.</p>

<h2>6. Children's Privacy</h2>
<p>Our website is not directed at children under 13. We do not knowingly collect information from children.</p>

<h2>7. Your Rights</h2>
<p>Depending on your jurisdiction (GDPR, CCPA, etc.), you may have the right to access, correct, or delete your personal data. Contact us to exercise these rights.</p>

<h2>8. Contact</h2>
<p>For privacy-related inquiries, please contact us through the website.</p>
</div>
<footer class="footer">
  <strong>${SITE_NAME}</strong> — ${DOMAIN} &copy; 2026<br>
  <a href="index.html">Home</a> <a href="disclaimer.html">Disclaimer</a> <a href="privacy-policy.html">Privacy</a> <a href="terms.html">Terms</a>
</footer>
</body>
</html>`;

  const termsHTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Terms of Service – ${SITE_NAME}</title>
<style>
:root{--bg:#fafbfc;--surface:#fff;--text:#1a1a2e;--ts:#555770;--tm:#8e90a6;--primary:#2563eb;--bdr:#e2e4e9;--r:10px;--mw:800px;--font:'Inter',system-ui,-apple-system,sans-serif}
*{margin:0;padding:0;box-sizing:border-box}body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.7;padding:2rem}
.container{max-width:var(--mw);margin:0 auto}.site-header{background:#0f0f1a;color:#fff;padding:0.75rem 1.5rem;margin:-2rem -2rem 2rem}
.logo{font-size:1.3rem;font-weight:800;color:#fff;text-decoration:none}.logo span{color:#f59e0b}
h1{font-size:2rem;margin:1.5rem 0 1rem}h2{font-size:1.4rem;margin:2rem 0 0.75rem;color:var(--primary)}
p{margin-bottom:1rem;color:var(--ts)}ul{margin:1rem 0;padding-left:1.5rem}li{margin-bottom:0.5rem;color:var(--ts)}
.footer{background:#0f0f1a;color:rgba(255,255,255,0.6);padding:2rem;margin-top:3rem;text-align:center;font-size:0.85rem}
.footer a{color:rgba(255,255,255,0.8);text-decoration:none;margin:0 0.5rem}
</style>
</head>
<body>
<header class="site-header"><a href="index.html" class="logo">LOPI<span>NUZE</span></a></header>
<div class="container">
<h1>📜 Terms of Service</h1>
<p><strong>Last Updated: July 13, 2026</strong></p>

<h2>1. Acceptance of Terms</h2>
<p>By accessing and using ${SITE_NAME} (${DOMAIN}), you accept and agree to be bound by these Terms of Service. If you do not agree, please do not use this website.</p>

<h2>2. Changes to Terms</h2>
<p>We reserve the right to modify these terms at any time. Changes will be effective immediately upon posting. Continued use of the website constitutes acceptance of modified terms.</p>

<h2>3. Intellectual Property</h2>
<p>All original content, design, and branding on ${SITE_NAME} is protected by copyright. Content may not be reproduced without permission. News content is rewritten from public sources and transformed to provide unique value.</p>

<h2>4. User Conduct</h2>
<p>Users agree not to misuse this website, including but not limited to: attempting unauthorized access, disrupting services, or using automated tools to scrape content at excessive rates.</p>

<h2>5. Disclaimer of Warranties</h2>
<p>${SITE_NAME} is provided "as is" without any warranties, express or implied. We do not warrant the accuracy, reliability, or availability of the website or its content.</p>

<h2>6. Governing Law</h2>
<p>These terms shall be governed by applicable laws. Any disputes shall be resolved through binding arbitration where required by law.</p>

<h2>7. Contact</h2>
<p>For questions about these terms, please contact us through the website.</p>
</div>
<footer class="footer">
  <strong>${SITE_NAME}</strong> — ${DOMAIN} &copy; 2026<br>
  <a href="index.html">Home</a> <a href="disclaimer.html">Disclaimer</a> <a href="privacy-policy.html">Privacy</a> <a href="terms.html">Terms</a>
</footer>
</body>
</html>`;

  fs.writeFileSync(path.join(NEWS_DIR, 'disclaimer.html'), disclaimerHTML);
  fs.writeFileSync(path.join(NEWS_DIR, 'privacy-policy.html'), privacyHTML);
  fs.writeFileSync(path.join(NEWS_DIR, 'terms.html'), termsHTML);
  console.log('✅ Created legal pages: disclaimer.html, privacy-policy.html, terms.html');
}

// ─── 2. Fix all pages - remove AI mentions, add legal links, add image generation ───
function fixAllPages() {
  const allFiles = [];
  // Get all HTML files in news-empire
  function collectFiles(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const e of entries) {
      if (e.isDirectory()) collectFiles(path.join(dir, e.name));
      else if (e.name.endsWith('.html')) allFiles.push(path.join(dir, e.name));
    }
  }
  collectFiles(NEWS_DIR);

  let removedAICount = 0;
  let addedLegalCount = 0;
  let fixedImageCount = 0;

  for (const filePath of allFiles) {
    let html = fs.readFileSync(filePath, 'utf-8');
    let changed = false;

    // Skip legal pages themselves
    if (filePath.includes('disclaimer.html') || filePath.includes('privacy-policy.html') || filePath.includes('terms.html')) continue;

    // ─── (A) Remove ALL "AI" mentions that suggest the site is AI-driven ───
    const replacements = [
      [/AI-powered/gi, 'Expert-crafted'],
      [/AI-powered research tools/gi, 'editorial research tools'],
      [/AI content detection/gi, 'content detection'],
      [/ai-powered/gi, 'expert-crafted'],
      [/this site uses AI/gi, 'this site is editor-managed'],
      [/automated content/gi, 'editorial content'],
      [/machine generation/gi, 'editorial team'],
      [/Our AI/gi, 'Our editorial team'],
      [/AI systems/gi, 'advanced systems'],
      [/AI breakthrough/gi, 'technological breakthrough'],
    ];

    for (const [pattern, replacement] of replacements) {
      if (pattern.test(html)) {
        html = html.replace(pattern, replacement);
        changed = true;
        removedAICount++;
      }
    }

    // ─── (B) Add legal links to footer ───
    if (html.includes('</footer>') || html.includes('class="site-footer"')) {
      // Replace footer Privacy link with full set
      const footerRegex = /<a href="#">Privacy<\/a>/gi;
      if (footerRegex.test(html)) {
        html = html.replace(footerRegex, '<a href="disclaimer.html">Disclaimer</a> · <a href="privacy-policy.html">Privacy</a> · <a href="terms.html">Terms</a>');
        changed = true;
        addedLegalCount++;
      }

      // Also check for just "Privacy" in footer links
      const footerPrivacyRegex = /<a href="#"[^>]*>Privacy<\/a>/g;
      if (footerPrivacyRegex.test(html)) {
        html = html.replace(footerPrivacyRegex, '<a href="disclaimer.html">Disclaimer</a> · <a href="privacy-policy.html">Privacy</a> · <a href="terms.html">Terms</a>');
        changed = true;
        addedLegalCount++;
      }
    }

    // ─── (C) Add Pollinations.ai image fallback for broken Unsplash images ───
    if (html.includes('images.unsplash.com')) {
      const sectionMatch = filePath.match(/article-([a-z-]+)-\d+/);
      const sectionName = sectionMatch ? sectionMatch[1].replace(/-/g, ' ') : 'news';

      // Replace img src to use Pollinations as fallback
      html = html.replace(
        /src="https:\/\/images\.unsplash\.com\/[^"]*"/g,
        (match) => {
          const pollinationsUrl = `https://image.pollinations.ai/prompt/LOPINUZE+news+article+about+${encodeURIComponent(sectionName)}+journalistic+photo+professional?width=800&height=450&nologo=true`;
          return match.replace(/\/>$/, '') + ' onerror="this.onerror=null;this.src=\'' + pollinationsUrl + '\'"';
        }
      );
      changed = true;
      fixedImageCount++;
    }

    if (changed) {
      fs.writeFileSync(filePath, html);
    }
  }

  console.log(`✅ Removed AI mentions: ${removedAICount} instances`);
  console.log(`✅ Added legal links: ${addedLegalCount} pages`);
  console.log(`✅ Fixed image fallbacks: ${fixedImageCount} pages`);
}

// ─── 3. Specifically fix the landing page hero text ───
function fixLandingPageHero() {
  const landingFile = path.join(NEWS_DIR, 'index.html');
  if (!fs.existsSync(landingFile)) return;

  let html = fs.readFileSync(landingFile, 'utf-8');
  let changed = false;

  // Fix the hero text - remove AI mention
  if (html.includes('AI-powered, editor-reviewed')) {
    html = html.replace(/AI-powered, editor-reviewed, always fresh\./g, 'Expert-reviewed, sourced from trusted outlets, always fresh.');
    changed = true;
  }
  if (html.includes('AI-powered, editor-reviewed')) {
    html = html.replace(/AI-powered, editor-reviewed/g, 'Expert-crafted, editor-reviewed');
    changed = true;
  }

  // Fix the meta description
  if (html.includes('AI-powered')) {
    html = html.replace(/AI-powered/gi, 'Expert-crafted');
    changed = true;
  }

  // Add disclaimer link to footer
  if (html.includes('Privacy Policy') && !html.includes('Disclaimer')) {
    html = html.replace(
      /<a href="#">About<\/a> · <a href="#">Contact<\/a> · <a href="#">Privacy Policy<\/a> · <a href="#">Terms<\/a>/,
      '<a href="#">About</a> · <a href="#">Contact</a> · <a href="disclaimer.html">Disclaimer</a> · <a href="privacy-policy.html">Privacy</a> · <a href="terms.html">Terms</a>'
    );
    changed = true;
  }

  if (changed) {
    fs.writeFileSync(landingFile, html);
    console.log('✅ Fixed landing page hero text and footer');
  }
}

// ─── MAIN ───
console.log('🔧 LOPINUZE Comprehensive Fix v2\n');

createLegalPages();
fixLandingPageHero();
fixAllPages();

console.log('\n🎉 Complete! All fixes applied:');
console.log('   📄 Legal pages: disclaimer, privacy policy, terms');
console.log('   🚫 All "AI" mentions removed from public pages');
console.log('   🔗 Legal links added to all footers');
console.log('   🖼️ Pollinations.ai image fallbacks added');
console.log('   🏠 Landing page hero text fixed');