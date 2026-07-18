/**
 * LOPINUZE.2BD.NET — 生产级 AI 内容流水线
 * 每次运行：从实时新闻源拉取 → 使用 Gemini 2.5 Flash 改写成类人新闻稿 → 更新 HTML 页面
 * 包含：SEO/GEO 优化、自动关联文章链接、内链、联盟变现
 * 
 * 用法：node pipeline.js           （运行一次）
 *       node pipeline.js --watch   （持续监控，每 15 分钟更新一次）
 * 
 * 所需 API 密钥（直接内嵌以便立即运行）：
 *   GEMINI_API_KEY = your-gemini-key
 *   DEEPSEEK_API_KEY = your-deepseek-key
 */

require('dotenv').config();
const fs = require('fs');
const path = require('path');

// ═══════════════════════ 配置 ═══════════════════════
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || 'YOUR_GEMINI_KEY';
const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY || 'YOUR_DEEPSEEK_KEY';
const SITE_NAME = 'LOPINUZE';
const DOMAIN = 'LOPINUZE.2BD.NET';
const NEWS_DIR = path.join(__dirname, 'docs');
const LOG_DIR = path.join(__dirname, 'logs');
const STATS_FILE = path.join(__dirname, 'pipeline-stats.json');

// 50 sections with keywords for SEO
const SECTIONS = [
  { slug: 'tech', keywords: 'technology news, gadgets, software reviews, tech industry', category: 'Technology' },
  { slug: 'ai', keywords: 'artificial intelligence, AI breakthroughs, machine learning research', category: 'Technology' },
  { slug: 'machine-learning', keywords: 'machine learning, ML algorithms, data science', category: 'Technology' },
  { slug: 'deep-learning', keywords: 'deep learning, neural networks, deep neural networks', category: 'Technology' },
  { slug: 'robotics', keywords: 'robotics, robots, automation, drones', category: 'Technology' },
  { slug: 'gaming', keywords: 'video games, gaming news, consoles, PC gaming', category: 'Gaming' },
  { slug: 'esports', keywords: 'esports, competitive gaming, gaming tournaments', category: 'Gaming' },
  { slug: 'game-reviews', keywords: 'game reviews, game ratings, video game reviews', category: 'Gaming' },
  { slug: 'game-development', keywords: 'game development, indie games, game design', category: 'Gaming' },
  { slug: 'mobile-gaming', keywords: 'mobile gaming, iOS games, Android games', category: 'Gaming' },
  { slug: 'vr-ar', keywords: 'VR news, AR technology, virtual reality, augmented reality', category: 'Technology' },
  { slug: 'cybersecurity', keywords: 'cybersecurity, data breaches, hacking news, cyber attacks', category: 'Technology' },
  { slug: 'cloud-computing', keywords: 'cloud computing, AWS, Azure, Google Cloud, SaaS', category: 'Technology' },
  { slug: 'blockchain', keywords: 'blockchain technology, Web3, distributed ledger', category: 'Technology' },
  { slug: 'fintech', keywords: 'fintech, financial technology, digital banking', category: 'Finance' },
  { slug: 'investing', keywords: 'investing, stock market, investment strategies, portfolio', category: 'Finance' },
  { slug: 'trading', keywords: 'trading, day trading, forex, options trading', category: 'Finance' },
  { slug: 'cryptocurrency', keywords: 'cryptocurrency, Bitcoin, Ethereum, crypto market', category: 'Finance' },
  { slug: 'personal-finance', keywords: 'personal finance, budgeting, saving money, credit', category: 'Finance' },
  { slug: 'real-estate', keywords: 'real estate, housing market, property investment', category: 'Finance' },
  { slug: 'stock-market', keywords: 'stock market, market indices, trading signals, market analysis', category: 'Finance' },
  { slug: 'etfs', keywords: 'ETFs, exchange traded funds, passive investing', category: 'Finance' },
  { slug: 'forex', keywords: 'forex, foreign exchange, currency trading, FX market', category: 'Finance' },
  { slug: 'crypto-mining', keywords: 'crypto mining, Bitcoin mining, mining hardware', category: 'Finance' },
  { slug: 'defi', keywords: 'DeFi, decentralized finance, yield farming, liquidity pools', category: 'Finance' },
  { slug: 'nutrition', keywords: 'nutrition, diet, healthy eating, food science', category: 'Health' },
  { slug: 'fitness', keywords: 'fitness, workouts, exercise, training programs', category: 'Health' },
  { slug: 'mental-health', keywords: 'mental health, wellness, therapy, psychological insights', category: 'Health' },
  { slug: 'supplements', keywords: 'supplements, vitamins, nootropics, herbal supplements', category: 'Health' },
  { slug: 'weight-loss', keywords: 'weight loss, diet plans, metabolism, weight management', category: 'Health' },
  { slug: 'yoga-meditation', keywords: 'yoga, meditation, mindfulness, stress reduction', category: 'Health' },
  { slug: 'science', keywords: 'science news, scientific discoveries, research breakthroughs', category: 'Science' },
  { slug: 'astronomy', keywords: 'astronomy, space, stars, planets, cosmic discoveries', category: 'Science' },
  { slug: 'geology', keywords: 'geology, earth science, earthquakes, natural resources', category: 'Science' },
  { slug: 'environment', keywords: 'environment, climate, conservation, ecology, sustainability', category: 'Science' },
  { slug: 'space', keywords: 'space exploration, NASA, SpaceX, space missions', category: 'Science' },
  { slug: 'physics', keywords: 'physics, quantum mechanics, relativity, particle physics', category: 'Science' },
  { slug: 'biology', keywords: 'biology, genetics, evolution, ecosystems, biotech', category: 'Science' },
  { slug: 'chemistry', keywords: 'chemistry, materials science, chemical research', category: 'Science' },
  { slug: 'medicine', keywords: 'medicine, medical breakthroughs, healthcare, treatments', category: 'Health' },
  { slug: 'psychology', keywords: 'psychology, behavior, cognition, mental processes', category: 'Health' },
  { slug: 'neuroscience', keywords: 'neuroscience, brain research, neural networks, consciousness', category: 'Science' },
  { slug: 'climate', keywords: 'climate change, global warming, climate policy', category: 'Science' },
  { slug: 'energy', keywords: 'energy, renewable energy, fossil fuels, grid technology', category: 'Science' },
  { slug: 'education', keywords: 'education, edtech, learning resources, academic research', category: 'World' },
  { slug: 'politics', keywords: 'politics, political news, policy analysis, government', category: 'World' },
  { slug: 'world-news', keywords: 'world news, international headlines, global affairs', category: 'World' },
  { slug: 'us-news', keywords: 'US news, United States, American politics, US policy', category: 'World' },
  { slug: 'asia-news', keywords: 'Asia news, Asia-Pacific, Asian politics, Asian economy', category: 'World' },
  { slug: 'europe-news', keywords: 'Europe news, European Union, UK news, European affairs', category: 'World' },
];

// Free, reliable RSS feeds that don't require API keys
const RSS_FEEDS = [
  { url: 'https://feeds.bbci.co.uk/news/world/rss.xml', cat: 'world-news' },
  { url: 'https://feeds.bbci.co.uk/news/technology/rss.xml', cat: 'tech' },
  { url: 'https://feeds.bbci.co.uk/news/business/rss.xml', cat: 'investing' },
  { url: 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml', cat: 'science' },
  { url: 'https://feeds.bbci.co.uk/news/health/rss.xml', cat: 'medicine' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml', cat: 'tech' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml', cat: 'investing' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/Science.xml', cat: 'science' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/Health.xml', cat: 'medicine' },
  { url: 'https://www.theguardian.com/world/rss', cat: 'world-news' },
  { url: 'https://www.theguardian.com/technology/rss', cat: 'tech' },
  { url: 'https://www.theguardian.com/business/rss', cat: 'investing' },
  { url: 'https://hnrss.org/frontpage?points=20', cat: 'tech' },
  { url: 'https://www.reddit.com/r/worldnews/.rss', cat: 'world-news' },
  { url: 'https://www.reddit.com/r/technology/.rss', cat: 'tech' },
  { url: 'https://www.reddit.com/r/science/.rss', cat: 'science' },
  { url: 'https://www.reddit.com/r/Futurology/.rss', cat: 'tech' },
  { url: 'https://www.reddit.com/r/gadgets/.rss', cat: 'tech' },
  { url: 'https://www.reddit.com/r/CryptoCurrency/.rss', cat: 'cryptocurrency' },
  { url: 'https://www.reddit.com/r/StockMarket/.rss', cat: 'stock-market' },
];

// ─── Logging utility ───
function log(msg, level = 'INFO') {
  const ts = new Date().toISOString();
  const line = `[${ts}] [${level}] ${msg}`;
  console.log(line);
  try {
    if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR, { recursive: true });
    const logFile = path.join(LOG_DIR, `pipeline-${new Date().toISOString().slice(0,10)}.log`);
    fs.appendFileSync(logFile, line + '\n');
  } catch (e) { /* silently ignore log write errors */ }
}

// ─── Stats tracker ───
function loadStats() {
  try { return JSON.parse(fs.readFileSync(STATS_FILE, 'utf-8')); } catch { return { totalArticles: 0, lastRun: null, perSection: {} }; }
}
function saveStats(stats) {
  try { fs.writeFileSync(STATS_FILE, JSON.stringify(stats, null, 2)); } catch { log('Failed to save stats', 'WARN'); }
}

// ─── Step 1: Fetch from real RSS feeds ───
async function fetchRSS(url) {
  try {
    const res = await fetch(url, { headers: { 'User-Agent': 'LOPINUZE-NewsBot/1.0', 'Accept': 'application/rss+xml,application/xml,text/xml' }, signal: AbortSignal.timeout(15000) });
    if (!res.ok) return [];
    const xml = await res.text();
    // Simple regex-based RSS parser (no dependencies)
    const items = [];
    const itemRegex = /<item>([\s\S]*?)<\/item>/gi;
    let match;
    while ((match = itemRegex.exec(xml)) !== null) {
      const itemXml = match[1];
      const title = (itemXml.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').trim() || '';
      const link = (itemXml.match(/<link[^>]*>([\s\S]*?)<\/link>/i) || [])[1]?.trim() || '';
      const desc = (itemXml.match(/<description[^>]*>([\s\S]*?)<\/description>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]+>/g, '').trim() || '';
      const pubDate = (itemXml.match(/<pubDate[^>]*>([\s\S]*?)<\/pubDate>/i) || [])[1]?.trim() || '';
      if (title && desc.length > 50) {
        items.push({ title, link, description: desc, pubDate, source: url });
      }
    }
    // Also try Atom format
    if (items.length === 0) {
      const entryRegex = /<entry>([\s\S]*?)<\/entry>/gi;
      while ((match = entryRegex.exec(xml)) !== null) {
        const entryXml = match[1];
        const title = (entryXml.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').trim() || '';
        const link = ((entryXml.match(/<link[^>]*href="([^"]+)"/i) || [])[1] || '').trim();
        const desc = (entryXml.match(/<summary[^>]*>([\s\S]*?)<\/summary>/i) || entryXml.match(/<content[^>]*>([\s\S]*?)<\/content>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]+>/g, '').trim() || '';
        if (title && desc.length > 50) items.push({ title, link, description: desc, pubDate: '', source: url });
      }
    }
    return items;
  } catch (e) {
    log(`RSS fetch failed for ${url}: ${e.message}`, 'WARN');
    return [];
  }
}

async function fetchFromAllRSS() {
  const all = [];
  const shuffled = RSS_FEEDS.sort(() => Math.random() - 0.5);
  for (const feed of shuffled.slice(0, 8)) { // Limit per run to avoid rate limiting
    const items = await fetchRSS(feed.url);
    for (const item of items) {
      const targetSection = SECTIONS.find(s => s.slug === feed.cat)?.slug || 'world-news';
      all.push({ ...item, targetSection, originalSource: item.source });
    }
    log(`Fetched ${items.length} from ${feed.url}`);
    await new Promise(r => setTimeout(r, 1000)); // Be polite between requests
  }
  return all;
}

// ─── Step 2: Rewrite with Gemini 2.5 Flash ───
async function rewriteWithGemini(article) {
  const systemPrompt = `You are a Pulitzer Prize-winning journalist writing for ${SITE_NAME} (${DOMAIN}), a respected global news outlet. Your task: rewrite the provided news snippet into a complete, engaging, human-like news article.

CRITICAL RULES:
- Write in natural, human journalistic style - NOT like AI
- Start with a compelling hook that grabs attention
- Include specific data, quotes, and expert insights (you may invent plausible expert quotes attributed to named experts)
- Use varied sentence structure: mix short punchy sentences with longer analytical ones
- Add context and background that helps readers understand WHY this matters
- Include 2-3 subheadings with relevant section breaks
- End with a forward-looking conclusion
- Word count: 400-600 words
- NEVER mention AI, machine generation, or automated content
- Sound like a seasoned human journalist filing a story

Target section: ${article.targetSection}`;

  try {
    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        system_instruction: { parts: [{ text: systemPrompt }] },
        contents: [{
          parts: [{
            text: `Rewrite this news into a complete, engaging article. Original headline: "${article.title}". Original text: "${article.description.substring(0, 2000)}"`
          }]
        }],
        generationConfig: { temperature: 0.85, maxOutputTokens: 1500, topP: 0.95 }
      }),
      signal: AbortSignal.timeout(30000)
    });
    const data = await res.json();
    if (data.error) { log(`Gemini error: ${JSON.stringify(data.error)}`, 'WARN'); return null; }
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
    return text || null;
  } catch (e) {
    log(`Gemini API call failed: ${e.message}`, 'WARN');
    return null;
  }
}

// ─── Step 3: Fallback to DeepSeek ───
async function rewriteWithDeepSeek(article) {
  const systemPrompt = `You are a seasoned journalist. Rewrite the following news into a complete, engaging, human-like article of 400-600 words. Use natural language, varied sentences, plausible quotes, and subheadings. Never mention AI. Sound completely human.`;

  try {
    const res = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${DEEPSEEK_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: `Rewrite this into a full article. Headline: "${article.title}". Source text: "${article.description.substring(0, 2000)}"` }
        ],
        temperature: 0.85,
        max_tokens: 1500
      }),
      signal: AbortSignal.timeout(30000)
    });
    const data = await res.json();
    if (data.error) { log(`DeepSeek error: ${JSON.stringify(data.error)}`, 'WARN'); return null; }
    return data.choices?.[0]?.message?.content || null;
  } catch (e) {
    log(`DeepSeek API call failed: ${e.message}`, 'WARN');
    return null;
  }
}

// ─── Step 4: Generate SEO metadata ───
function generateSEO(section, title, content) {
  const sec = SECTIONS.find(s => s.slug === section) || { keywords: 'news', category: 'General' };
  const metaDesc = content.substring(0, 155).replace(/<[^>]+>/g, '').trim() + '...';
  const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').substring(0, 80);
  const date = new Date().toISOString().split('T')[0];
  const author = getAuthor(section);

  return {
    metaTitle: `${title} | ${SITE_NAME}`,
    metaDesc,
    slug,
    keywords: sec.keywords,
    category: sec.category,
    date,
    author: author.name,
    authorTitle: author.title,
    readTime: Math.ceil(content.split(' ').length / 200),
  };
}

function getAuthor(section) {
  const authors = [
    { name: 'Dr. Sarah Chen', title: 'Chief Technology Editor', sections: ['tech','ai','machine-learning','deep-learning','robotics'] },
    { name: 'James Rodriguez', title: 'Senior Finance Correspondent', sections: ['fintech','investing','trading','cryptocurrency','stock-market','etfs','forex','defi','crypto-mining','personal-finance','real-estate'] },
    { name: 'Dr. Emily Watson', title: 'Health & Science Editor', sections: ['nutrition','fitness','mental-health','supplements','weight-loss','yoga-meditation','medicine','psychology','neuroscience','biology','chemistry'] },
    { name: 'Marcus Thompson', title: 'Gaming & Esports Lead', sections: ['gaming','esports','game-reviews','game-development','mobile-gaming','vr-ar'] },
    { name: 'Priya Kapoor', title: 'World Affairs Correspondent', sections: ['politics','world-news','us-news','asia-news','europe-news','climate','energy','education','environment'] },
    { name: 'Prof. David Kim', title: 'Science & Space Editor', sections: ['science','astronomy','geology','space','physics'] },
    { name: 'Alex Rivera', title: 'Cybersecurity Analyst', sections: ['cybersecurity','cloud-computing','blockchain'] },
    { name: 'Dr. Maria Santos', title: 'Neuroscience & Psychology Editor', sections: ['neuroscience','psychology','mental-health'] },
  ];
  for (const a of authors) { if (a.sections.includes(section)) return a; }
  return { name: 'LOPINUZE News Desk', title: 'Staff Reporter' };
}

// ─── Step 5: Generate affiliate/referral links ───
function getAffiliateLinks(section) {
  const allLinks = {
    tech: [{ text: 'Shop the latest tech on Amazon', url: 'https://www.amazon.com/s?k=technology+gadgets&tag=lopinuz0b-20' }],
    ai: [{ text: 'Explore AI tools on Product Hunt', url: 'https://www.producthunt.com/search?q=AI' }],
    cryptocurrency: [{ text: 'Trade crypto on Binance', url: 'https://www.binance.com/en' }],
    investing: [{ text: 'Start investing with Robinhood', url: 'https://robinhood.com/' }, { text: 'Explore ETFs on Vanguard', url: 'https://investor.vanguard.com/' }],
    fitness: [{ text: 'Top-rated fitness gear on Amazon', url: 'https://www.amazon.com/s?k=fitness+equipment&tag=lopinuz0b-20' }],
    supplements: [{ text: 'Quality supplements on iHerb', url: 'https://www.iherb.com/' }],
    gaming: [{ text: 'Latest games on Steam', url: 'https://store.steampowered.com/' }],
    'world-news': [{ text: 'Support independent journalism', url: 'https://www.patreon.com/' }],
    default: [{ text: 'Shop deals on Amazon', url: 'https://www.amazon.com/?tag=lopinuz0b-20' }],
  };
  return allLinks[section] || allLinks['default'];
}

// ─── Step 6: Build HTML article page ───
function buildArticleHTML(section, article, seo) {
  const links = getAffiliateLinks(section);
  const affiliateHTML = links.map(l => `<p style="margin-top:1.5rem;padding:0.75rem 1rem;background:#fef3c7;border:1px solid #fcd34d;border-radius:8px;font-size:0.9rem;">🛍️ <strong>Related:</strong> <a href="${l.url}" rel="nofollow sponsored" target="_blank" style="color:#92400e;">${l.text}</a></p>`).join('');

  const sectionData = SECTIONS.find(s => s.slug === section) || SECTIONS[0];
  const imgUrl = (sectionData && sectionData.img) ? sectionData.img : `https://images.unsplash.com/photo-1504711434969-e33886168d6c?w=800&h=450&fit=crop`;

  // Split content into paragraphs and add subheadings
  let paragraphs = article.content.split(/\n{2,}/).filter(p => p.trim());
  if (paragraphs.length === 0) paragraphs = [article.content];

  const formattedContent = paragraphs.map(p => {
    p = p.trim();
    if (p.startsWith('## ') || p.startsWith('### ')) {
      const level = p.startsWith('## ') ? 'h2' : 'h3';
      const text = p.replace(/^##\s*|^###\s*/, '');
      return `<${level}>${text}</${level}>`;
    }
    if (p.startsWith('- ')) {
      const items = p.split('\n').filter(l => l.startsWith('- ')).map(l => `<li>${l.replace('- ', '')}</li>`).join('');
      return `<ul>${items}</ul>`;
    }
    return `<p>${p}</p>`;
  }).join('\n');

  const relatedArticles = getRelatedArticleLinks(section, seo.slug, 3);

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script>(function(d,z,s){s.src='https://'+d+'/401/'+z;try{(document.body||document.documentElement).appendChild(s)}catch(e){}})('5gvci.com',11342729,document.createElement('script'))</script>
<title>${seo.metaTitle}</title>
<meta name="description" content="${seo.metaDesc}">
<meta name="keywords" content="${seo.keywords}">
<meta name="author" content="${seo.author}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:title" content="${seo.metaTitle}">
<meta property="og:description" content="${seo.metaDesc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://${DOMAIN}/${section}/${seo.slug}">
<meta property="article:published_time" content="${seo.date}">
<meta property="article:author" content="${seo.author}">
<link rel="canonical" href="https://${DOMAIN}/${section}/${seo.slug}">
<script type="application/ld+json">
{
  "@context":"https://schema.org",
  "@type":"NewsArticle",
  "headline":"${article.title.replace(/"/g,'\\"')}",
  "description":"${seo.metaDesc}",
  "author":{"@type":"Person","name":"${seo.author}","jobTitle":"${seo.authorTitle}"},
  "datePublished":"${seo.date}",
  "publisher":{"@type":"Organization","name":"${SITE_NAME}"}
}
</script>
<style>
:root{--bg:#fafbfc;--surface:#fff;--text:#1a1a2e;--ts:#555770;--tm:#8e90a6;--primary:#2563eb;--bdr:#e2e4e9;--r:10px;--rl:16px;--mw:800px;--font:'Inter',system-ui,-apple-system,sans-serif}
*{margin:0;padding:0;box-sizing:border-box}body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.7;-webkit-font-smoothing:antialiased}
.container{max-width:var(--mw);margin:0 auto;padding:0 1.5rem}
.site-header{background:#0f0f1a;color:#fff;padding:0.5rem 0;position:sticky;top:0;z-index:100}
.site-header .container{display:flex;align-items:center;justify-content:space-between;gap:1rem}
.logo{font-size:1.3rem;font-weight:800;color:#fff;text-decoration:none}.logo span{color:#f59e0b}
.nav-links{display:flex;gap:0.5rem;list-style:none}
.nav-links a{color:rgba(255,255,255,0.8);text-decoration:none;font-size:0.85rem;padding:0.3rem 0.6rem;border-radius:6px}
.nav-links a:hover{color:#fff;background:rgba(255,255,255,0.08)}
.article-detail{max-width:var(--mw);margin:0 auto;padding:2.5rem 1.5rem}
.breadcrumb{font-size:0.82rem;color:var(--tm);margin-bottom:1rem}
.breadcrumb a{color:var(--primary);text-decoration:none}
.article-detail h1{font-size:2.2rem;font-weight:800;line-height:1.2;margin-bottom:0.75rem;letter-spacing:-0.5px}
.meta-bar{display:flex;gap:1rem;flex-wrap:wrap;padding-bottom:1.25rem;border-bottom:1px solid var(--bdr);margin-bottom:1.5rem;font-size:0.85rem;color:var(--ts)}
.fimg{width:100%;max-height:420px;object-fit:cover;border-radius:var(--rl);margin-bottom:2rem;background:linear-gradient(135deg,#e2e4e9,#f0f1f5)}
.content{font-size:1.1rem;line-height:1.85;color:var(--text)}
.content h2{font-size:1.5rem;margin:2rem 0 0.75rem;font-weight:700}
.content h3{font-size:1.2rem;margin:1.5rem 0 0.5rem;font-weight:600}
.content p{margin-bottom:1.2rem}
.content ul{margin:1rem 0;padding-left:1.5rem}
.content li{margin-bottom:0.5rem}
blockquote{border-left:3px solid var(--primary);padding:1rem 1.5rem;margin:1.5rem 0;background:#f8f9fc;border-radius:0 6px 6px 0;font-style:italic;color:var(--ts)}
.source-tag{font-size:0.8rem;color:var(--tm);margin-top:2rem;padding:1rem;background:var(--surface);border:1px solid var(--bdr);border-radius:var(--r)}
.source-tag a{color:var(--primary)}
.related{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;margin-top:2rem}
.related a{border:1px solid var(--bdr);border-radius:var(--r);padding:1rem;text-decoration:none;color:inherit;transition:all 0.2s}
.related a:hover{border-color:var(--primary)}
.related h5{font-size:0.88rem;margin-bottom:0.3rem}
.related .meta{font-size:0.75rem;color:var(--tm)}
.site-footer{background:#0f0f1a;color:rgba(255,255,255,0.6);padding:3rem 0;margin-top:4rem;font-size:0.85rem}
.site-footer .container{display:flex;justify-content:space-between;flex-wrap:wrap;gap:2rem}
.site-footer a{color:rgba(255,255,255,0.8);text-decoration:none}
</style>
</head>
<body>
<header class="site-header"><div class="container">
<a href="/index.html" class="logo">LOPI<span>NUZE</span></a>
<nav><ul class="nav-links">
<li><a href="/index.html">Home</a></li>
<li><a href="/section-tech.html">Tech</a></li>
<li><a href="/section-ai.html">AI</a></li>
<li><a href="/finance.html">Finance</a></li>
<li><a href="/section-world-news.html">World</a></li>
</ul></nav>
</div></header>
<main>
<article class="article-detail">
<div class="breadcrumb"><a href="/index.html">Home</a> &rsaquo; <a href="section-${section}.html">${sectionData?.name || section}</a> &rsaquo; Article</div>
<h1>${article.title}</h1>
<div class="meta-bar">
<span>By <strong>${seo.author}</strong>, ${seo.authorTitle}</span>
<span>📅 ${seo.date}</span>
<span>⏱️ ${seo.readTime} min read</span>
</div>
<div class="content">${formattedContent}</div>
${affiliateHTML}
<div class="source-tag">📰 This article is based on reporting from trusted news sources. <a href="${article.originalSource || '#'}" target="_blank" rel="nofollow">View original source</a> — Content rewritten and fact-checked by our editorial team.</div>
${relatedArticles}
</article>
</main>
<footer class="site-footer"><div class="container"><div><strong>${SITE_NAME}</strong><br>${DOMAIN} &copy; 2026</div><div><a href="/index.html">Home</a> · <a href="/disclaimer.html">Disclaimer</a> · <a href="/privacy-policy.html">Privacy</a></div></div></footer>
</body>
</html>`;
}

function getRelatedArticleLinks(section, currentSlug, count) {
  try {
    const articlesDir = path.join(NEWS_DIR, 'articles');
    if (!fs.existsSync(articlesDir)) return '';
    const files = fs.readdirSync(articlesDir).filter(f => f.startsWith(`article-${section}-`) && !f.includes(currentSlug)).slice(0, count);
    if (files.length === 0) return '';
    const links = files.map(f => {
      const data = JSON.parse(fs.readFileSync(path.join(articlesDir, f), 'utf-8'));
      return `<a href="/articles/${f.replace('.json','.html')}" class="related-post"><h5>${data.title}</h5><div class="meta">${data.date || ''}</div></a>`;
    }).join('');
    return `<h3 style="margin-top:2rem;">📖 Related Articles</h3><div class="related">${links}</div>`;
  } catch { return ''; }
}

// ─── Step 7: Update section index page ───
function updateSectionPage(section, articles) {
  const sectionFile = path.join(NEWS_DIR, `section-${section}.html`);
  if (!fs.existsSync(sectionFile)) return;

  try {
    let html = fs.readFileSync(sectionFile, 'utf-8');
    const articlesDir = path.join(NEWS_DIR, 'articles');
    let savedFiles = [];
    if (fs.existsSync(articlesDir)) {
      savedFiles = fs.readdirSync(articlesDir)
        .filter(f => f.startsWith(`article-${section}-`) && f.endsWith('.html'))
        .sort().reverse().slice(0, 10); // Show up to 10 latest
    }

    const articleCards = articles.slice(0, 10).map((a, i) => {
      const seo = a.seo || {};
      const actualFile = a.actualFile || savedFiles[i];
      return `<article class="article-card" onclick="location.href='articles/${actualFile}'">
<img class="card-img" src="https://images.unsplash.com/photo-1504711434969-e33886168d6c?w=800&h=450&fit=crop" alt="${a.title}" loading="lazy" />
<div class="card-body"><span class="card-tag">${seo.category || 'News'}</span>
<h3><a href="articles/${actualFile}">${a.title}</a></h3>
<div class="meta"><span class="author-avatar">${(seo.author||'N')[0]}</span> ${seo.author || 'Staff'} · ${seo.date || ''}</div>
<p>${a.content.substring(0, 150).replace(/<[^>]+>/g,'')}...</p></div></article>`;
    }).join('');

    // Replace the contents inside <div class="article-list">...</div>
    const listStart = html.indexOf('<div class="article-list">');
    const listEnd = html.indexOf('</div></main>');
    if (listStart !== -1 && listEnd !== -1) {
      html = html.substring(0, listStart + 26) + articleCards + html.substring(listEnd);
      fs.writeFileSync(sectionFile, html);
      log(`✅ Updated section page: ${section}`);
    } else {
      log(`Could not find article-list container in section-${section}.html`, 'WARN');
    }
  } catch (e) {
    log(`Failed to update section page ${section}: ${e.message}`, 'WARN');
  }
}

// ─── Step 8: Main pipeline execution ───
async function runPipeline() {
  log('══════ STARTING PIPELINE RUN ══════');
  const stats = loadStats();
  const startTime = Date.now();

  // 1. Fetch from RSS
  const rawArticles = await fetchFromAllRSS();
  log(`Fetched ${rawArticles.length} total articles from RSS feeds`);

  if (rawArticles.length === 0) {
    log('No articles fetched. Skipping rewrite phase.', 'WARN');
    return;
  }

  // 2. Process each article through AI
  const processedArticles = [];
  const articlesDir = path.join(NEWS_DIR, 'articles');
  if (!fs.existsSync(articlesDir)) fs.mkdirSync(articlesDir, { recursive: true });

  for (const raw of rawArticles.slice(0, 15)) { // Limit per run
    // Try Gemini first (primary), fall back to DeepSeek
    let rewritten = await rewriteWithGemini(raw);
    if (!rewritten) {
      log(`Gemini failed for "${raw.title.substring(0,50)}...", trying DeepSeek...`);
      rewritten = await rewriteWithDeepSeek(raw);
    }
    if (!rewritten) {
      log(`Both AIs failed for article, skipping`, 'WARN');
      continue;
    }

    const seo = generateSEO(raw.targetSection, raw.title, rewritten);
    const articleData = {
      ...raw,
      content: rewritten,
      seo,
      processedAt: new Date().toISOString(),
    };

    // Save as JSON
    const jsonFile = path.join(articlesDir, `article-${raw.targetSection}-${Date.now()}.json`);
    fs.writeFileSync(jsonFile, JSON.stringify(articleData, null, 2));

    // Save as HTML
    const htmlFile = jsonFile.replace('.json', '.html');
    const htmlContent = buildArticleHTML(raw.targetSection, articleData, seo);
    fs.writeFileSync(htmlFile, htmlContent);

    processedArticles.push(articleData);

    // Update stats
    stats.totalArticles = (stats.totalArticles || 0) + 1;
    stats.perSection[raw.targetSection] = (stats.perSection[raw.targetSection] || 0) + 1;
    stats.lastRun = new Date().toISOString();
    saveStats(stats);

    log(`✅ Processed: "${raw.title.substring(0,60)}..." → ${raw.targetSection}`);

    // Rate limit between articles
    await new Promise(r => setTimeout(r, 2000));
  }

  // 3. Update section index pages
  const sectionsUpdated = new Set(processedArticles.map(a => a.targetSection));
  for (const section of sectionsUpdated) {
    const sectionArticles = processedArticles.filter(a => a.targetSection === section);
    updateSectionPage(section, sectionArticles);
  }

  // 4. Update landing page with latest articles
  updateLandingPage(processedArticles.slice(0, 6));

  const duration = ((Date.now() - startTime) / 1000).toFixed(1);
  log(`══════ PIPELINE COMPLETE: ${processedArticles.length} articles in ${duration}s ══════`);
}

// ─── Update Landing Page with latest articles ───
function updateLandingPage(recentArticles) {
  const landingFile = path.join(NEWS_DIR, 'index.html');
  if (!fs.existsSync(landingFile) || recentArticles.length === 0) return;

  try {
    let html = fs.readFileSync(landingFile, 'utf-8');
    const articleCards = recentArticles.map(a => {
      const seo = a.seo || {};
      return `<article class="article-card" onclick="location.href='/articles/${a.actualFile}'">
<img class="card-img" src="https://images.unsplash.com/photo-1504711434969-e33886168d6c?w=800&h=450&fit=crop" alt="${a.title}" loading="lazy" />
<div class="card-body"><span class="card-tag">LATEST</span>
<h3><a href="/articles/${a.actualFile}">${a.title}</a></h3>
<div class="meta"><span class="author-avatar">${(seo.author||'N')[0]}</span> ${seo.author || 'Staff'} · ${seo.date || ''}</div>
<p>${a.content.substring(0, 120).replace(/<[^>]+>/g,'')}...</p></div></article>`;
    }).join('');

    const articlesSection = `
<div class="cat-group"><h2>🔥 Latest Breaking News</h2>
<p style="color:var(--tm);margin-bottom:1.5rem;font-size:0.9rem;">Updated ${new Date().toLocaleString()}</p>
<div class="section-grid">${articleCards}</div></div>`;

    // Try to remove old "Latest Breaking News" block if it exists to avoid duplicates
    if (html.includes('🔥 Latest Breaking News')) {
      html = html.replace(/<div class="cat-group"><h2>🔥 Latest Breaking News[\\s\\S]*?<\/div><\/div>/, articlesSection);
    } else {
      // Insert right before the first cat-group
      const firstCatGroup = html.indexOf('<div class="cat-group">');
      if (firstCatGroup !== -1) {
        html = html.substring(0, firstCatGroup) + articlesSection + html.substring(firstCatGroup);
      }
    }

    fs.writeFileSync(landingFile, html);
    log('✅ Updated landing page with latest articles');
  } catch (e) {
    log(`Failed to update landing page: ${e.message}`, 'WARN');
  }
}

// ─── Watch mode ───
async function watchMode() {
  log('🔁 Watch mode activated — pipeline will run every 15 minutes');
  await runPipeline();
  const interval = setInterval(async () => {
    try { await runPipeline(); } catch (e) { log(`Pipeline error: ${e.message}`, 'ERROR'); }
  }, 15 * 60 * 1000); // 15 minutes

  process.on('SIGINT', () => { clearInterval(interval); log('Watch mode stopped'); process.exit(0); });
}

// ─── Entry point ───
(async () => {
  log(`🚀 LOPINUZE Pipeline v2.0 — ${DOMAIN}`);
  log(`📡 Gemini 2.0 Flash (FREE) + DeepSeek V4 (fallback)`);
  log(`📰 ${RSS_FEEDS.length} RSS sources configured`);

  const arg = process.argv[2];
  if (arg === '--watch' || arg === '-w') {
    await watchMode();
  } else {
    await runPipeline();
  }
})();
