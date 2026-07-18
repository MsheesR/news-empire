/**
 * LOPINUZE — Continuous AI Content Pipeline v3.0 (Masterpiece Edition)
 * Fetches real-time RSS news -> Rewrites via DeepSeek/Gemini with Generative Engine Optimization (GEO)
 * Injects internal backlinks, structured data, Monetag ads, and rebuilds static site automatically.
 */

require('dotenv').config();
const fs = require('fs');
const path = require('path');

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';
const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY || '';
const SITE_NAME = 'LOPINUZE';
const DOMAIN = 'lopinuze.online';
const LOG_DIR = path.join(__dirname, 'logs');
const STATS_FILE = path.join(__dirname, 'pipeline-stats.json');

// 50 sections with keywords for SEO & GEO
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

const RSS_FEEDS = [
  // ── Major News Wires (multi-section) ──
  { url: 'https://feeds.bbci.co.uk/news/world/rss.xml', cat: 'world-news' },
  { url: 'https://feeds.bbci.co.uk/news/technology/rss.xml', cat: 'tech' },
  { url: 'https://feeds.bbci.co.uk/news/business/rss.xml', cat: 'investing' },
  { url: 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml', cat: 'science' },
  { url: 'https://feeds.bbci.co.uk/news/health/rss.xml', cat: 'medicine' },
  { url: 'https://feeds.bbci.co.uk/news/education/rss.xml', cat: 'education' },
  { url: 'https://feeds.bbci.co.uk/news/politics/rss.xml', cat: 'politics' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml', cat: 'tech' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml', cat: 'investing' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/Science.xml', cat: 'science' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/Health.xml', cat: 'medicine' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/US.xml', cat: 'us-news' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml', cat: 'world-news' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/Climate.xml', cat: 'climate' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/YourMoney.xml', cat: 'personal-finance' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/RealEstate.xml', cat: 'real-estate' },
  { url: 'https://rss.nytimes.com/services/xml/rss/nyt/Education.xml', cat: 'education' },
  { url: 'https://www.theguardian.com/world/rss', cat: 'world-news' },
  { url: 'https://www.theguardian.com/technology/rss', cat: 'tech' },
  { url: 'https://www.theguardian.com/business/rss', cat: 'investing' },
  { url: 'https://www.theguardian.com/environment/rss', cat: 'environment' },
  { url: 'https://www.theguardian.com/science/rss', cat: 'science' },
  { url: 'https://www.theguardian.com/world/europe-news/rss', cat: 'europe-news' },
  { url: 'https://www.theguardian.com/world/asia-pacific/rss', cat: 'asia-news' },
  // ── Tech & AI ──
  { url: 'https://hnrss.org/frontpage?points=20', cat: 'tech' },
  { url: 'https://www.reddit.com/r/technology/.rss', cat: 'tech' },
  { url: 'https://www.reddit.com/r/artificial/.rss', cat: 'ai' },
  { url: 'https://www.reddit.com/r/MachineLearning/.rss', cat: 'machine-learning' },
  { url: 'https://www.reddit.com/r/deeplearning/.rss', cat: 'deep-learning' },
  { url: 'https://www.reddit.com/r/robotics/.rss', cat: 'robotics' },
  { url: 'https://www.reddit.com/r/cybersecurity/.rss', cat: 'cybersecurity' },
  { url: 'https://www.reddit.com/r/cloudcomputing/.rss', cat: 'cloud-computing' },
  { url: 'https://www.reddit.com/r/Futurology/.rss', cat: 'ai' },
  { url: 'https://www.reddit.com/r/gadgets/.rss', cat: 'tech' },
  { url: 'https://www.reddit.com/r/virtualreality/.rss', cat: 'vr-ar' },
  // ── Gaming ──
  { url: 'https://www.reddit.com/r/gaming/.rss', cat: 'gaming' },
  { url: 'https://www.reddit.com/r/esports/.rss', cat: 'esports' },
  { url: 'https://www.reddit.com/r/Games/.rss', cat: 'game-reviews' },
  { url: 'https://www.reddit.com/r/gamedev/.rss', cat: 'game-development' },
  { url: 'https://www.reddit.com/r/MobileGaming/.rss', cat: 'mobile-gaming' },
  // ── Finance & Crypto ──
  { url: 'https://www.reddit.com/r/CryptoCurrency/.rss', cat: 'cryptocurrency' },
  { url: 'https://www.reddit.com/r/StockMarket/.rss', cat: 'stock-market' },
  { url: 'https://www.reddit.com/r/finance/.rss', cat: 'personal-finance' },
  { url: 'https://www.reddit.com/r/investing/.rss', cat: 'investing' },
  { url: 'https://www.reddit.com/r/options/.rss', cat: 'trading' },
  { url: 'https://www.reddit.com/r/RealEstate/.rss', cat: 'real-estate' },
  { url: 'https://www.reddit.com/r/Forex/.rss', cat: 'forex' },
  { url: 'https://www.reddit.com/r/ETFs/.rss', cat: 'etfs' },
  { url: 'https://www.reddit.com/r/defi/.rss', cat: 'defi' },
  { url: 'https://www.reddit.com/r/BitcoinMining/.rss', cat: 'crypto-mining' },
  { url: 'https://www.reddit.com/r/fintech/.rss', cat: 'fintech' },
  { url: 'https://www.reddit.com/r/blockchain/.rss', cat: 'blockchain' },
  // ── Health & Wellness ──
  { url: 'https://www.reddit.com/r/health/.rss', cat: 'fitness' },
  { url: 'https://www.reddit.com/r/nutrition/.rss', cat: 'nutrition' },
  { url: 'https://www.reddit.com/r/mentalhealth/.rss', cat: 'mental-health' },
  { url: 'https://www.reddit.com/r/Supplements/.rss', cat: 'supplements' },
  { url: 'https://www.reddit.com/r/loseit/.rss', cat: 'weight-loss' },
  { url: 'https://www.reddit.com/r/yoga/.rss', cat: 'yoga-meditation' },
  { url: 'https://www.reddit.com/r/Meditation/.rss', cat: 'yoga-meditation' },
  { url: 'https://www.reddit.com/r/psychology/.rss', cat: 'psychology' },
  { url: 'https://www.reddit.com/r/neuroscience/.rss', cat: 'neuroscience' },
  // ── Science & Space ──
  { url: 'https://www.reddit.com/r/science/.rss', cat: 'science' },
  { url: 'https://www.reddit.com/r/space/.rss', cat: 'space' },
  { url: 'https://www.reddit.com/r/Astronomy/.rss', cat: 'astronomy' },
  { url: 'https://www.reddit.com/r/geology/.rss', cat: 'geology' },
  { url: 'https://www.reddit.com/r/Physics/.rss', cat: 'physics' },
  { url: 'https://www.reddit.com/r/biology/.rss', cat: 'biology' },
  { url: 'https://www.reddit.com/r/chemistry/.rss', cat: 'chemistry' },
  { url: 'https://www.reddit.com/r/energy/.rss', cat: 'energy' },
  { url: 'https://www.reddit.com/r/climate/.rss', cat: 'climate' },
  // ── World & Politics ──
  { url: 'https://www.reddit.com/r/worldnews/.rss', cat: 'world-news' },
  { url: 'https://www.reddit.com/r/politics/.rss', cat: 'politics' },
  { url: 'https://www.reddit.com/r/news/.rss', cat: 'us-news' },
  { url: 'https://www.reddit.com/r/europe/.rss', cat: 'europe-news' },
  { url: 'https://www.reddit.com/r/asia/.rss', cat: 'asia-news' },
  { url: 'https://www.reddit.com/r/education/.rss', cat: 'education' },
];

function log(msg, level = 'INFO') {
  const ts = new Date().toISOString();
  const line = `[${ts}] [${level}] ${msg}`;
  console.log(line);
  try {
    if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR, { recursive: true });
    const logFile = path.join(LOG_DIR, `pipeline-${new Date().toISOString().slice(0,10)}.log`);
    fs.appendFileSync(logFile, line + '\n');
  } catch (e) {}
}

function loadStats() {
  try { return JSON.parse(fs.readFileSync(STATS_FILE, 'utf-8')); } catch { return { totalArticles: 0, lastRun: null, perSection: {} }; }
}
function saveStats(stats) {
  try { fs.writeFileSync(STATS_FILE, JSON.stringify(stats, null, 2)); } catch { log('Failed to save stats', 'WARN'); }
}

async function fetchRSS(url) {
  try {
    const res = await fetch(url, { headers: { 'User-Agent': 'LOPINUZE-NewsBot/1.0', 'Accept': 'application/rss+xml,application/xml,text/xml' }, signal: AbortSignal.timeout(15000) });
    if (!res.ok) return [];
    const xml = await res.text();
    const items = [];
    const itemRegex = /<item>([\s\S]*?)<\/item>/gi;
    let match;
    while ((match = itemRegex.exec(xml)) !== null) {
      const itemXml = match[1];
      const title = (itemXml.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]+>/g, '').trim() || '';
      const link = (itemXml.match(/<link[^>]*>([\s\S]*?)<\/link>/i) || [])[1]?.trim() || '';
      const desc = (itemXml.match(/<description[^>]*>([\s\S]*?)<\/description>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]+>/g, '').trim() || '';
      const pubDate = (itemXml.match(/<pubDate[^>]*>([\s\S]*?)<\/pubDate>/i) || [])[1]?.trim() || '';
      if (title && desc.length > 30) items.push({ title, link, description: desc, pubDate, source: url });
    }
    if (items.length === 0) {
      const entryRegex = /<entry>([\s\S]*?)<\/entry>/gi;
      while ((match = entryRegex.exec(xml)) !== null) {
        const entryXml = match[1];
        const title = (entryXml.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]+>/g, '').trim() || '';
        const link = ((entryXml.match(/<link[^>]*href="([^"]+)"/i) || [])[1] || '').trim();
        const desc = (entryXml.match(/<summary[^>]*>([\s\S]*?)<\/summary>/i) || entryXml.match(/<content[^>]*>([\s\S]*?)<\/content>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]+>/g, '').trim() || '';
        if (title && desc.length > 30) items.push({ title, link, description: desc, pubDate: '', source: url });
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
  const coveredSections = new Set();
  const shuffled = RSS_FEEDS.sort(() => Math.random() - 0.5);
  
  // Fetch ALL feeds to maximize section coverage
  for (const feed of shuffled) {
    const items = await fetchRSS(feed.url);
    for (const item of items) {
      const targetSection = SECTIONS.find(s => s.slug === feed.cat)?.slug || 'world-news';
      all.push({ ...item, targetSection, originalSource: item.source });
      coveredSections.add(targetSection);
    }
    if (items.length > 0) log(`Fetched ${items.length} from ${feed.url}`);
    await new Promise(r => setTimeout(r, 200));
  }
  
  // Log coverage
  const uncovered = SECTIONS.filter(s => !coveredSections.has(s.slug)).map(s => s.slug);
  log(`RSS covered ${coveredSections.size}/50 sections. Uncovered: ${uncovered.length > 0 ? uncovered.join(', ') : 'none'}`);
  
  return all;
}

// ─── Generative Engine Optimization (GEO) AI Prompts ───
const GEO_SYSTEM_PROMPT = `You are a Pulitzer Prize-winning senior editor for ${SITE_NAME} (${DOMAIN}).
Write a high-authority, human-like news report optimized for Generative Engine Optimization (GEO) and search engines.

GEO RULES FOR HIGH CITATION:
1. Start with an authoritative lead paragraph detailing the core story.
2. Include specific statistics, percentages, and market data points.
3. Include at least 2 direct quotes from named industry experts or officials.
4. Structure with clear <h2> and <h3> subheadings.
5. Naturally insert internal cross-references to key sections (e.g., <a href="/section-tech.html">Technology</a>, <a href="/finance.html">Finance Desk</a>, <a href="/section-world-news.html">World News</a>).
6. Provide an objective, forward-looking analysis paragraph.
7. Length: 450 - 650 words.
8. NEVER mention AI, automation, or LLMs. Write as a veteran journalist filing from the newsroom.`;

async function rewriteWithDeepSeek(article) {
  if (!DEEPSEEK_API_KEY) return null;
  try {
    const res = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${DEEPSEEK_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: GEO_SYSTEM_PROMPT },
          { role: 'user', content: `Write a GEO-optimized report for section '${article.targetSection}'. Headline: "${article.title}". Summary: "${article.description.substring(0, 2000)}"` }
        ],
        temperature: 0.8,
        max_tokens: 1800
      }),
      signal: AbortSignal.timeout(35000)
    });
    const data = await res.json();
    if (data.error) { log(`DeepSeek error: ${JSON.stringify(data.error)}`, 'WARN'); return null; }
    return data.choices?.[0]?.message?.content || null;
  } catch (e) {
    log(`DeepSeek API call failed: ${e.message}`, 'WARN');
    return null;
  }
}

async function rewriteWithGemini(article) {
  if (!GEMINI_API_KEY) return null;
  try {
    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        system_instruction: { parts: [{ text: GEO_SYSTEM_PROMPT }] },
        contents: [{
          parts: [{ text: `Write a GEO-optimized report for section '${article.targetSection}'. Headline: "${article.title}". Summary: "${article.description.substring(0, 2000)}"` }]
        }],
        generationConfig: { temperature: 0.8, maxOutputTokens: 1800 }
      }),
      signal: AbortSignal.timeout(35000)
    });
    const data = await res.json();
    if (data.error) { log(`Gemini error: ${JSON.stringify(data.error)}`, 'WARN'); return null; }
    return data.candidates?.[0]?.content?.parts?.[0]?.text || null;
  } catch (e) {
    log(`Gemini API call failed: ${e.message}`, 'WARN');
    return null;
  }
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
  ];
  for (const a of authors) { if (a.sections.includes(section)) return a; }
  return { name: 'LOPINUZE News Desk', title: 'Staff Reporter' };
}

function generateSEO(section, title, content) {
  const sec = SECTIONS.find(s => s.slug === section) || { keywords: 'news', category: 'General' };
  const metaDesc = content.substring(0, 160).replace(/<[^>]+>/g, '').trim() + '...';
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
    readTime: Math.max(3, Math.ceil(content.split(' ').length / 180)),
  };
}

async function runPipeline() {
  const stats = loadStats();
  const startTime = Date.now();
  log('══════ STARTING PIPELINE RUN ══════');

  const rawArticles = await fetchFromAllRSS();
  if (rawArticles.length === 0) {
    log('No RSS articles fetched.', 'WARN');
    return;
  }

  log(`Fetched ${rawArticles.length} total articles from RSS feeds`);

  const processedArticles = [];
  const articlesDir = path.join(__dirname, 'raw_articles');
  if (!fs.existsSync(articlesDir)) fs.mkdirSync(articlesDir, { recursive: true });

  // Deduplication: check existing articles to avoid re-processing same titles
  const existingTitles = new Set();
  try {
    const existingFiles = fs.readdirSync(articlesDir).filter(f => f.endsWith('.json'));
    for (const f of existingFiles) {
      try {
        const data = JSON.parse(fs.readFileSync(path.join(articlesDir, f), 'utf-8'));
        if (data.title) existingTitles.add(data.title.toLowerCase().trim());
      } catch {}
    }
  } catch {}
  log(`Dedup: ${existingTitles.size} existing articles loaded`);

  // Deduplicate and prioritize uncovered sections
  const sectionCounts = {};
  const existingBySection = {};
  try {
    const existingFiles = fs.readdirSync(articlesDir).filter(f => f.endsWith('.json'));
    for (const f of existingFiles) {
      const sec = f.replace('article-','').replace(/-\d+\.json$/, '');
      existingBySection[sec] = (existingBySection[sec] || 0) + 1;
    }
  } catch {}
  
  // Sort: sections with fewer articles first, then randomize within
  const dedupedArticles = rawArticles
    .filter(a => !existingTitles.has(a.title.toLowerCase().trim()))
    .sort((a, b) => (existingBySection[a.targetSection] || 0) - (existingBySection[b.targetSection] || 0));

  // Ensure at least 1 article per section before adding more to popular sections
  const selectedArticles = [];
  const selectedSections = new Set();
  for (const art of dedupedArticles) {
    if (!selectedSections.has(art.targetSection)) {
      selectedArticles.push(art);
      selectedSections.add(art.targetSection);
    }
  }
  // Fill remaining slots with other articles
  for (const art of dedupedArticles) {
    if (!selectedArticles.includes(art) && selectedArticles.length < 50) {
      selectedArticles.push(art);
    }
  }

  log(`Processing ${selectedArticles.length} articles across ${selectedSections.size} sections...`);

  // Process up to 50 articles per run (1 per section minimum)
  for (const raw of selectedArticles.slice(0, 50)) {
    // Try DeepSeek first as requested by user, fall back to Gemini
    let rewritten = await rewriteWithDeepSeek(raw);
    if (!rewritten) {
      log(`DeepSeek unavailable for "${raw.title.substring(0, 40)}...", trying Gemini...`);
      rewritten = await rewriteWithGemini(raw);
    }

    if (!rewritten) {
      log(`Both AI engines failed for "${raw.title.substring(0, 40)}...", skipping`, 'WARN');
      continue;
    }

    const seo = generateSEO(raw.targetSection, raw.title, rewritten);

    const articleData = {
      title: raw.title,
      targetSection: raw.targetSection,
      originalUrl: raw.link,
      originalSource: raw.originalSource,
      content: rewritten,
      seo,
      processedAt: new Date().toISOString(),
    };

    const jsonFile = path.join(articlesDir, `article-${raw.targetSection}-${Date.now()}.json`);
    fs.writeFileSync(jsonFile, JSON.stringify(articleData, null, 2));
    processedArticles.push(articleData);

    stats.totalArticles = (stats.totalArticles || 0) + 1;
    stats.perSection[raw.targetSection] = (stats.perSection[raw.targetSection] || 0) + 1;
    stats.lastRun = new Date().toISOString();
    saveStats(stats);

    log(`✅ Processed: "${raw.title.substring(0,50)}..." → ${raw.targetSection}`);
    await new Promise(r => setTimeout(r, 1000));
  }

  const { buildSite } = require('./build-newspaper-module.js');
  log('Rebuilding 1200+ vintage pages with Monetag & SEO/GEO optimization...');
  buildSite();

  const duration = ((Date.now() - startTime) / 1000).toFixed(1);
  log(`══════ PIPELINE COMPLETE: ${processedArticles.length} articles in ${duration}s ══════`);
}

(async () => {
  log(`🚀 LOPINUZE Pipeline v3.0 — ${DOMAIN}`);
  await runPipeline();
})();
