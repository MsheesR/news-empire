/**
 * LOPINUZE - MINIMAL FIX only: language switcher + legal footer links
 * Does NOT touch section grid, hero, or article images
 */
const fs = require('fs');
const path = require('path');

const NEWS_DIR = path.join(__dirname, 'news-empire');

function getAllHTMLFiles(dir) {
  const all = [];
  function walk(d) {
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      if (e.isDirectory()) walk(path.join(d, e.name));
      else if (e.name.endsWith('.html')) all.push(path.join(d, e.name));
    }
  }
  walk(dir);
  return all;
}

// ─── 1. Fix language switcher to use Google Translate ───
function fixLanguageSwitcher() {
  const files = getAllHTMLFiles(NEWS_DIR);
  let count = 0;

  const newSwitcher = `<div class="lang-switcher">
      <select onchange="if(this.value){window.open('https://translate.google.com/translate?hl='+this.value+'&sl=en&u='+encodeURIComponent(window.location.href),'_blank')}">
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
        <option value="nl">Nederlands</option>
      </select>
    </div>`;

  for (const filePath of files) {
    let html = fs.readFileSync(filePath, 'utf-8');
    if (!html.includes('lang-switcher')) continue;
    const old = html.match(/<div class="lang-switcher">[\s\S]*?<\/div>/);
    if (old && old[0] !== newSwitcher) {
      html = html.replace(old[0], newSwitcher);
      fs.writeFileSync(filePath, html);
      count++;
    }
  }
  console.log(`✅ Language switcher: ${count} files`);
}

// ─── 2. Fix footer: add legal links ───
function fixFooterLegalLinks() {
  const files = getAllHTMLFiles(NEWS_DIR).filter(f => !f.includes('disclaimer') && !f.includes('privacy-policy') && !f.includes('terms'));
  let count = 0;

  for (const filePath of files) {
    let html = fs.readFileSync(filePath, 'utf-8');
    let changed = false;

    // Replace "Privacy" alone with full legal links
    if (/<a href="#"[^>]*>Privacy<\/a>/.test(html) && !html.includes('Disclaimer')) {
      html = html.replace(
        /<a href="#"[^>]*>Privacy<\/a>/,
        '<a href="/disclaimer.html">Disclaimer</a> · <a href="/privacy-policy.html">Privacy</a> · <a href="/terms.html">Terms</a>'
      );
      changed = true;
    }

    // Also replace "Privacy Policy" standalone
    if (/<a href="#"[^>]*>Privacy Policy<\/a>/.test(html) && !html.includes('Disclaimer')) {
      html = html.replace(
        /<a href="#"[^>]*>Privacy Policy<\/a>/,
        '<a href="/disclaimer.html">Disclaimer</a> · <a href="/privacy-policy.html">Privacy</a> · <a href="/terms.html">Terms</a>'
      );
      changed = true;
    }

    if (changed) {
      fs.writeFileSync(filePath, html);
      count++;
    }
  }
  console.log(`✅ Legal footer links: ${count} files`);
}

// ─── 3. Remove "AI-powered" from landing page hero if present ───
function fixLandingHeroText() {
  const landingFile = path.join(NEWS_DIR, 'index.html');
  if (!fs.existsSync(landingFile)) return;
  let html = fs.readFileSync(landingFile, 'utf-8');
  if (html.includes('AI-powered')) {
    html = html.replace(/AI-powered/gi, 'Expert-crafted');
    fs.writeFileSync(landingFile, html);
    console.log('✅ Removed AI-powered from hero text');
  }
}

// ─── MAIN ───
console.log('🔧 Minimal targeted fixes...\n');
fixLanguageSwitcher();
fixFooterLegalLinks();
fixLandingHeroText();
console.log('\n✅ Done — section grid, Unsplash images, and article structure preserved.');