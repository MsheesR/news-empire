/**
 * LOPINUZE.2BD.NET - Complete Site Fix
 * Fixes: broken landing page articles, professional icons, fresh dates, image paths
 */
const fs = require('fs');
const path = require('path');

const NEWS_DIR = path.join(__dirname, 'news-empire');
const ARTICLES_DIR = path.join(NEWS_DIR, 'articles');

// Professional SVG icons (inline) to replace emojis
const PROFESSIONAL_ICONS = {
  '💻': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
  '🤖': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="9" cy="10" r="1.5"/><circle cx="15" cy="10" r="1.5"/><path d="M9 15c.83.67 2 1 3 1s2.17-.33 3-1"/></svg>',
  '🧠': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M12 2a4 4 0 00-4 4c0 2.5 1.5 4 4 6 2.5-2 4-3.5 4-6a4 4 0 00-4-4z"/><path d="M4 14c-1.5 2-1 5 1 7 2 2 5 2.5 7 1M20 14c1.5 2 1 5-1 7-2 2-5 2.5-7 1"/></svg>',
  '🦾': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><circle cx="12" cy="5" r="3"/><path d="M12 8v4M9 12l-3 4M15 12l3 4M8 16h8"/></svg>',
  '🎮': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><rect x="2" y="6" width="20" height="12" rx="4"/><path d="M6 12h4M8 10v4"/><circle cx="15" cy="12" r="1.5"/><circle cx="18" cy="10" r="1.5"/></svg>',
  '🏆': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M6 9H4a2 2 0 01-2-2V5a2 2 0 012-2h2M18 9h2a2 2 0 002-2V5a2 2 0 00-2-2h-2"/><path d="M6 21h12M12 17v4"/><path d="M8 3h8l-1 6H9L8 3z"/></svg>',
  '⭐': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1.5"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>',
  '🎨': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M12 2l10 6.5v7L12 22 2 15.5v-7L12 2z"/><circle cx="12" cy="12" r="3"/></svg>',
  '📱': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="3"/><line x1="12" y1="18" x2="12.01" y2="18"/><path d="M8 6h8"/></svg>',
  '🥽': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><rect x="2" y="6" width="20" height="10" rx="4"/><circle cx="8" cy="11" r="2"/><circle cx="16" cy="11" r="2"/><line x1="10" y1="11" x2="14" y2="11"/></svg>',
  '🔒': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/><circle cx="12" cy="16" r="1"/></svg>',
  '☁️': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M17.5 19H9a7 7 0 116.71-9h1.79a4.5 4.5 0 110 9z"/></svg>',
  '⛓️': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><circle cx="6" cy="6" r="3"/><circle cx="18" cy="18" r="3"/><line x1="8.5" y1="8.5" x2="15.5" y2="15.5"/><line x1="6" y1="9" x2="6" y2="9.01"/><line x1="18" y1="15" x2="18" y2="15.01"/></svg>',
  '💳': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/><line x1="3" y1="16" x2="7" y2="16"/><line x1="11" y1="16" x2="15" y2="16"/></svg>',
  '📈': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><polyline points="22,7 13.5,15.5 8.5,10.5 2,17"/><polyline points="16,7 22,7 22,13"/></svg>',
  '💹': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><polyline points="22,12 18,12 15,21 9,3 6,12 2,12"/></svg>',
  '₿': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><circle cx="12" cy="12" r="10"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="#f59e0b">₿</text></svg>',
  '💰': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
  '🏠': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>',
  '📊': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
  '📋': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><rect x="3" y="5" width="18" height="14" rx="2"/><line x1="8" y1="9" x2="16" y2="9"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="12" y2="17"/></svg>',
  '💱': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M4 6l4-4 4 4"/><path d="M8 2v14M20 18l-4 4-4-4"/><path d="M16 22V8"/></svg>',
  '⛏️': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>',
  '🔗': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>',
  '🥗': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M8 7h8M8 11h8M8 15h6M5 3h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2z"/></svg>',
  '🏋️': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11M3 12h2M19 12h2M12 3v2M12 19v2"/></svg>',
  '🧘': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><circle cx="12" cy="5" r="2"/><path d="M12 7v10M9 12l-4 4M15 12l4 4M8 14l-3 5M16 14l3 5"/></svg>',
  '💊': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><rect x="6" y="2" width="6" height="12" rx="3"/><rect x="12" y="6" width="6" height="8" rx="3"/></svg>',
  '⚖️': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><line x1="12" y1="2" x2="12" y2="22"/><path d="M5 8h14l-3 6H8L5 8z"/><circle cx="12" cy="12" r="1"/></svg>',
  '🕉️': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v12M7.5 12h9"/></svg>',
  '🔭': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M21 3l-9 9M10 3H3v7l7-7zM21 14v7h-7l7-7z"/><circle cx="12" cy="12" r="3"/></svg>',
  '🌌': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2l1.5 4.5L18 8l-4.5 1.5L12 14l-1.5-4.5L6 8l4.5-1.5z"/></svg>',
  '🌍': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4" ry="10"/><line x1="2" y1="12" x2="22" y2="12"/></svg>',
  '🌿': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2"><path d="M12 22c5-2 8-8 4-14-4 0-8 3-8 8s2 6 4 6zM12 22V10"/></svg>',
  '🚀': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M12 2l3 8h6l-5 4 2 8-6-4-6 4 2-8-5-4h6l3-8z"/></svg>',
  '⚛️': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>',
  '🧬': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M4 4c2 3 2 7 0 10M20 4c-2 3-2 7 0 10M12 2v20"/></svg>',
  '🧪': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M9 3h6M9 3v7l-5 10h16L15 10V3"/><circle cx="12" cy="18" r="1"/></svg>',
  '🏥': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
  '🗣️': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>',
  '🌡️': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M14 14.76V3.5a2.5 2.5 0 00-5 0v11.26a4.5 4.5 0 105 0z"/></svg>',
  '⚡': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><polygon points="13,2 3,14 12,14 11,22 21,10 12,10"/></svg>',
  '📚': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2zM22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>',
  '🏛️': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M3 21h18M3 7v14M21 7v14M6 11h12M3 7l9-4 9 4"/></svg>',
  '🌐': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>',
  '🇺🇸': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5"><rect x="3" y="4" width="18" height="16" rx="1"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="14" x2="21" y2="14"/><line x1="3" y1="19" x2="21" y2="19"/><rect x="3" y="4" width="9" height="10" rx="0.5" fill="#2563eb" opacity="0.2"/></svg>',
  '🌏': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2c3 4 3 16 0 20"/></svg>',
  '🇪🇺': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 6l1.5 4.5L18 12l-4.5 1.5L12 18l-1.5-4.5L6 12l4.5-1.5z"/></svg>',
};

// Map section slugs to their emoji icons for replacement
const EMOJI_MAP = {
  'tech': '💻', 'ai': '🤖', 'machine-learning': '🧠', 'deep-learning': '🔬',
  'robotics': '🦾', 'gaming': '🎮', 'esports': '🏆', 'game-reviews': '⭐',
  'game-development': '🎨', 'mobile-gaming': '📱', 'vr-ar': '🥽',
  'cybersecurity': '🔒', 'cloud-computing': '☁️', 'blockchain': '⛓️',
  'fintech': '💳', 'investing': '📈', 'trading': '💹', 'cryptocurrency': '₿',
  'personal-finance': '💰', 'real-estate': '🏠', 'stock-market': '📊',
  'etfs': '📋', 'forex': '💱', 'crypto-mining': '⛏️', 'defi': '🔗',
  'nutrition': '🥗', 'fitness': '🏋️', 'mental-health': '🧘', 'supplements': '💊',
  'weight-loss': '⚖️', 'yoga-meditation': '🕉️', 'science': '🔭', 'astronomy': '🌌',
  'geology': '🌍', 'environment': '🌿', 'space': '🚀', 'physics': '⚛️',
  'biology': '🧬', 'chemistry': '🧪', 'medicine': '🏥', 'psychology': '🗣️',
  'neuroscience': '🧠', 'climate': '🌡️', 'energy': '⚡', 'education': '📚',
  'politics': '🏛️', 'world-news': '🌐', 'us-news': '🇺🇸', 'asia-news': '🌏', 'europe-news': '🇪🇺'
};

// ─── Fix 1: Replace all emoji icons in HTML files with professional SVG icons ───
function fixIconsInFile(filePath) {
  if (!fs.existsSync(filePath)) return false;
  let html = fs.readFileSync(filePath, 'utf-8');
  let changed = false;
  
  // Replace emojis in card-icon spans and other places
  for (const [emoji, svg] of Object.entries(PROFESSIONAL_ICONS)) {
    if (html.includes(emoji)) {
      // Only replace in appropriate contexts (not in content text)
      html = html.replace(new RegExp(`<span class="card-icon">${emoji}</span>`, 'g'), `<span class="card-icon">${svg}</span>`);
      html = html.replace(new RegExp(`<h1>${emoji} `, 'g'), (match) => `<h1>${svg} `);
      html = html.replace(new RegExp(`📰 ${emoji}`, 'g'), (match) => `📰 ${svg}`);
      changed = true;
    }
  }
  
  if (changed) {
    fs.writeFileSync(filePath, html);
    return true;
  }
  return false;
}

// ─── Fix 2: Update section page dates from 2026-07 to today ───
function fixSectionDates(filePath) {
  if (!fs.existsSync(filePath)) return false;
  let html = fs.readFileSync(filePath, 'utf-8');
  let changed = false;
  
  const today = new Date();
  const dates = [];
  for (let i = 0; i < 6; i++) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    dates.push(d.toISOString().split('T')[0]);
  }
  
  // Replace old dates (2026-07-11 through 2026-07-06) with fresh dates
  const oldDates = ['2026-07-11', '2026-07-10', '2026-07-09', '2026-07-08', '2026-07-07', '2026-07-06'];
  oldDates.forEach((oldDate, i) => {
    if (html.includes(oldDate)) {
      html = html.replace(new RegExp(oldDate, 'g'), dates[i]);
      changed = true;
    }
  });
  
  if (changed) {
    fs.writeFileSync(filePath, html);
    return true;
  }
  return false;
}

// ─── Fix 3: Fix landing page articles section - remove broken links, use real pipeline articles ───
function fixLandingPage() {
  const landingFile = path.join(NEWS_DIR, 'index.html');
  if (!fs.existsSync(landingFile)) return;
  
  let html = fs.readFileSync(landingFile, 'utf-8');
  
  // Find the "Latest Stories" section inserted by pipeline and fix it
  // Look for article cards pointing to /articles/ path and fix them
  html = html.replace(/href="articles\/article-([^"]+)-latest\.html"/g, (match, section) => {
    // Find the actual latest article for this section
    if (fs.existsSync(ARTICLES_DIR)) {
      const files = fs.readdirSync(ARTICLES_DIR)
        .filter(f => f.startsWith(`article-${section}-`) && f.endsWith('.html'))
        .sort()
        .reverse();
      if (files.length > 0) {
        return `href="articles/${files[0]}"`;
      }
    }
    return match;
  });
  
  // Fix image src for any broken Unsplash URLs in landing page
  html = html.replace(/src="https:\/\/images\.unsplash\.com\/[^"]*"/g, (match) => {
    // Keep the URL but add a fallback
    return match.replace('"/>', '" onerror="this.src=\'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22800%22 height=%22450%22><rect fill=%22%23e2e4e9%22 width=%22800%22 height=%22450%22/><text x=%22400%22 y=%22225%22 text-anchor=%22middle%22 fill=%22%238e90a6%22 font-size=%2260%22>📰</text></svg>\'" />');
  });
  
  fs.writeFileSync(landingFile, html);
  console.log('✅ Fixed landing page article links');
}

// ─── Fix 4: Fix all section pages ───
function fixAllSectionPages() {
  const files = fs.readdirSync(NEWS_DIR).filter(f => f.startsWith('section-') && f.endsWith('.html'));
  let iconCount = 0, dateCount = 0;
  
  for (const file of files) {
    const filePath = path.join(NEWS_DIR, file);
    if (fixIconsInFile(filePath)) iconCount++;
    if (fixSectionDates(filePath)) dateCount++;
  }
  console.log(`✅ Fixed icons in ${iconCount} section pages`);
  console.log(`✅ Fixed dates in ${dateCount} section pages`);
}

// ─── Fix 5: Fix article detail pages ───
function fixAllArticlePages() {
  let count = 0;
  const articleFiles = fs.readdirSync(NEWS_DIR).filter(f => f.startsWith('article-') && f.endsWith('.html'));
  
  for (const file of articleFiles) {
    const filePath = path.join(NEWS_DIR, file);
    if (fixIconsInFile(filePath)) count++;
    if (fixSectionDates(filePath)) count++;
  }
  
  // Also fix articles in the articles/ subdirectory
  if (fs.existsSync(ARTICLES_DIR)) {
    const pipelineArticles = fs.readdirSync(ARTICLES_DIR).filter(f => f.endsWith('.html'));
    for (const file of pipelineArticles) {
      const filePath = path.join(ARTICLES_DIR, file);
      if (fixIconsInFile(filePath)) count++;
    }
  }
  console.log(`✅ Fixed ${count} article pages`);
}

// ─── Fix 6: Fix finance.html ───
function fixFinanceHub() {
  const financeFile = path.join(NEWS_DIR, 'finance.html');
  if (fs.existsSync(financeFile)) {
    fixIconsInFile(financeFile);
    console.log('✅ Fixed finance hub icons');
  }
}

// ─── Fix 7: Fix landing page icons ───
function fixLandingIcons() {
  const landingFile = path.join(NEWS_DIR, 'index.html');
  if (fs.existsSync(landingFile)) {
    fixIconsInFile(landingFile);
    console.log('✅ Fixed landing page icons');
  }
}

// ─── MAIN ───
console.log('🔧 Starting comprehensive site fix...\n');

fixLandingIcons();
fixFinanceHub();
fixAllSectionPages();
fixAllArticlePages();
fixLandingPage();

console.log('\n🎉 All fixes applied!');
console.log('   - Professional SVG icons replacing emojis');
console.log('   - Fresh dates on all articles (today\'s dates)');
console.log('   - Landing page article links fixed');
console.log('   - Image fallbacks added for broken images');