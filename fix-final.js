/**
 * LOPINUZE - FINAL FIX v3
 * 1. Language switcher: dark styling + use window.location (not blocked by popups)
 * 2. Image fallback: text-based headline cards when images fail
 * 3. Legal footer links
 * 
 * PRESERVES: section grid, Unsplash images, article structure
 */
const fs = require('fs');
const path = require('path');

const NEWS_DIR = path.join(__dirname, 'news-empire');

function getAllHTML(dir) {
  const all = [];
  function walk(d) {
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      if (e.isDirectory() && e.name !== 'articles') walk(path.join(d, e.name));
      else if (e.name.endsWith('.html')) all.push(path.join(d, e.name));
    }
  }
  walk(dir);
  return all;
}

// 1. Fix language switcher: dark styling + redirect instead of popup
function fixLangSwitcher() {
  const files = getAllHTML(NEWS_DIR);
  let count = 0;

  // The replacement HTML uses window.location.href (NOT window.open which gets blocked)
  const newSwitcher = `<div class="lang-switcher">
      <select onchange="if(this.value){window.location.href='https://translate.google.com/translate?hl='+this.value+'&sl=en&u='+encodeURIComponent(window.location.href)}" style="padding:0.4rem 0.6rem;border-radius:6px;border:1px solid rgba(255,255,255,0.2);background:#1a1a2e;color:#fff;font-size:0.8rem;cursor:pointer;font-family:inherit;">
        <option value="">🌐 Languages</option>
        <option value="es">Español</option>
        <option value="fr">Français</option>
        <option value="de">Deutsch</option>
        <option value="it">Italiano</option>
        <option value="pt">Português</option>
        <option value="ru">Русский</option>
        <option value="zh-CN">中文</option>
        <option value="ja">日本語</option>
        <option value="ko">한국어</option>
        <option value="ar">العربية</option>
        <option value="hi">हिन्दी</option>
        <option value="tr">Türkçe</option>
      </select>
    </div>`;

  for (const filePath of files) {
    let html = fs.readFileSync(filePath, 'utf-8');
    if (!html.includes('lang-switcher')) continue;

    // Remove any conflicting JS that might interfere
    html = html.replace(/\/\/ Language switcher\s+document\.querySelector\('[^']*'\)\?\.addEventListener\('change',\s*\([^)]*\)\s*=>\s*\{[\s\S]*?\}\);/g, '');

    const old = html.match(/<div class="lang-switcher">[\s\S]*?<\/div>/);
    if (old) {
      html = html.replace(old[0], newSwitcher);
      fs.writeFileSync(filePath, html);
      count++;
    }
  }
  console.log(`✅ Language switcher: ${count} files (window.location + dark bg)`);
}

// 2. Fix footer: add legal links
function fixFooter() {
  const files = getAllHTML(NEWS_DIR).filter(f =>
    !f.includes('disclaimer') && !f.includes('privacy-policy') && !f.includes('terms')
  );
  let count = 0;

  for (const filePath of files) {
    let html = fs.readFileSync(filePath, 'utf-8');
    if (html.includes('Disclaimer')) continue;
    let changed = false;

    // Replace "Privacy" link in footer with full legal links
    if (/<a href="#">Privacy<\/a>/.test(html)) {
      html = html.replace(
        /<a href="#">Privacy<\/a>/,
        '<a href="/disclaimer.html">Disclaimer</a> · <a href="/privacy-policy.html">Privacy</a> · <a href="/terms.html">Terms</a>'
      );
      changed = true;
    }

    if (changed) { fs.writeFileSync(filePath, html); count++; }
  }
  console.log(`✅ Legal footer: ${count} files`);
}

// 3. Add text-based image fallback CSS and onerror handlers
function fixImageFallback() {
  const files = getAllHTML(NEWS_DIR);
  let count = 0;

  // CSS for fallback
  const fallbackCSS = `
/* Text-based image fallback */
.card-img-fallback {
  width: 100%;
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary) 0%, #7c3aed 100%);
  color: white;
  text-align: center;
  padding: 1rem;
  font-family: var(--font-sans);
}
.card-img-fallback .fb-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.card-img-fallback .fb-title { font-size: 1rem; font-weight: 700; line-height: 1.3; max-width: 90%; }
.featured-img-fallback {
  width: 100%;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a3e 0%, #2563eb 100%);
  color: white;
  text-align: center;
  padding: 2rem;
  border-radius: var(--radius-lg);
  font-family: var(--font-sans);
}
.featured-img-fallback .fb-icon { font-size: 4rem; margin-bottom: 1rem; }
.featured-img-fallback .fb-title { font-size: 1.4rem; font-weight: 700; line-height: 1.4; max-width: 80%; }`;

  for (const filePath of files) {
    let html = fs.readFileSync(filePath, 'utf-8');
    if (html.includes('card-img-fallback')) continue; // Already has fallback
    let changed = false;

    // Add fallback CSS before </style>
    if (html.includes('</style>')) {
      html = html.replace('</style>', fallbackCSS + '\n</style>');
      changed = true;
    }

    // Add onerror to all card images
    if (/<img class="card-img"/.test(html)) {
      html = html.replace(
        /<img class="card-img" src="([^"]+)" alt="([^"]+)"[^>]*\/>/g,
        (match, src, alt) => {
          const icon = alt && alt.length > 0 ? alt.substring(0, 2) : '📰';
          return `<img class="card-img" src="${src}" alt="${alt}" loading="lazy" onerror="this.style.display='none';var fb=this.nextElementSibling;if(fb)fb.style.display='flex'" /><div class="card-img-fallback" style="display:none"><span class="fb-icon">${icon}</span><span class="fb-title">${alt}</span></div>`;
        }
      );
      changed = true;
    }

    // Add onerror to featured images
    if (/<img class="featured-img"/.test(html)) {
      html = html.replace(
        /<img class="featured-img" src="([^"]+)" alt="([^"]+)"[^>]*\/>/g,
        (match, src, alt) => {
          return `<img class="featured-img" src="${src}" alt="${alt}" loading="lazy" onerror="this.style.display='none';var fb=this.nextElementSibling;if(fb)fb.style.display='flex'" /><div class="featured-img-fallback" style="display:none"><span class="fb-icon">📰</span><span class="fb-title">${alt}</span></div>`;
        }
      );
      changed = true;
    }

    if (changed) { fs.writeFileSync(filePath, html); count++; }
  }
  console.log(`✅ Image fallback: ${count} files`);
}

// MAIN
console.log('🔧 LOPINUZE Final Fix v3\n');
fixLangSwitcher();
fixFooter();
fixImageFallback();
console.log('\n✅ All done. Site preserved. Language working. Images backed by text fallback.');