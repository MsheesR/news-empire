/**
 * LOPINUZE — Continuous AI Content Pipeline v4.0 (GEO/AEO Optimized)
 * Fetches RSS news -> Rewrites via DeepSeek with section-specific SEO/GEO/AEO
 * Generates unique content for ALL 50 sections every run
 */

require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { getExpertQuote, GEO_HTML, generateEnhancedSchema } = require('./seo-engine.js');

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';
const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY || '';
const SITE_NAME = 'LOPINUZE';
const DOMAIN = 'lopinuze.online';
const LOG_DIR = path.join(__dirname, 'logs');
const STATS_FILE = path.join(__dirname, 'pipeline-stats.json');

const SECTIONS = [
  { slug: 'tech', name: 'Technology', keywords: 'technology news, gadgets, software reviews, tech industry', category: 'Technology' },
  { slug: 'ai', name: 'AI', keywords: 'artificial intelligence, AI breakthroughs, machine learning research, LLM', category: 'Technology' },
  { slug: 'machine-learning', name: 'Machine Learning', keywords: 'machine learning, ML algorithms, data science, neural networks', category: 'Technology' },
  { slug: 'deep-learning', name: 'Deep Learning', keywords: 'deep learning, neural networks, transformers, GPU computing', category: 'Technology' },
  { slug: 'robotics', name: 'Robotics', keywords: 'robotics, robots, automation, drones, humanoid robots', category: 'Technology' },
  { slug: 'gaming', name: 'Gaming', keywords: 'video games, gaming news, consoles, PC gaming, PlayStation Xbox', category: 'Gaming' },
  { slug: 'esports', name: 'Esports', keywords: 'esports, competitive gaming, gaming tournaments, pro gamers', category: 'Gaming' },
  { slug: 'game-reviews', name: 'Game Reviews', keywords: 'game reviews, game ratings, video game reviews, new releases', category: 'Gaming' },
  { slug: 'game-development', name: 'Game Development', keywords: 'game development, indie games, game design, Unity Unreal', category: 'Gaming' },
  { slug: 'mobile-gaming', name: 'Mobile Gaming', keywords: 'mobile gaming, iOS games, Android games, mobile esports', category: 'Gaming' },
  { slug: 'vr-ar', name: 'VR/AR', keywords: 'VR news, AR technology, virtual reality, augmented reality, Meta Quest', category: 'Technology' },
  { slug: 'cybersecurity', name: 'Cybersecurity', keywords: 'cybersecurity, data breaches, hacking news, cyber attacks, ransomware', category: 'Technology' },
  { slug: 'cloud-computing', name: 'Cloud Computing', keywords: 'cloud computing, AWS, Azure, Google Cloud, SaaS, serverless', category: 'Technology' },
  { slug: 'blockchain', name: 'Blockchain', keywords: 'blockchain technology, Web3, distributed ledger, smart contracts', category: 'Technology' },
  { slug: 'fintech', name: 'FinTech', keywords: 'fintech, financial technology, digital banking, payments', category: 'Finance' },
  { slug: 'investing', name: 'Investing', keywords: 'investing, stock market, investment strategies, portfolio management', category: 'Finance' },
  { slug: 'trading', name: 'Trading', keywords: 'trading, day trading, forex, options trading, technical analysis', category: 'Finance' },
  { slug: 'cryptocurrency', name: 'Cryptocurrency', keywords: 'cryptocurrency, Bitcoin, Ethereum, crypto market, altcoins', category: 'Finance' },
  { slug: 'personal-finance', name: 'Personal Finance', keywords: 'personal finance, budgeting, saving money, credit cards, loans', category: 'Finance' },
  { slug: 'real-estate', name: 'Real Estate', keywords: 'real estate, housing market, property investment, mortgage rates', category: 'Finance' },
  { slug: 'stock-market', name: 'Stock Market', keywords: 'stock market, S&P 500, NASDAQ, Dow Jones, market analysis', category: 'Finance' },
  { slug: 'etfs', name: 'ETFs', keywords: 'ETFs, exchange traded funds, passive investing, index funds', category: 'Finance' },
  { slug: 'forex', name: 'Forex', keywords: 'forex, foreign exchange, currency trading, FX market, dollar euro', category: 'Finance' },
  { slug: 'crypto-mining', name: 'Crypto Mining', keywords: 'crypto mining, Bitcoin mining, mining hardware, ASIC miners', category: 'Finance' },
  { slug: 'defi', name: 'DeFi', keywords: 'DeFi, decentralized finance, yield farming, liquidity pools, DEX', category: 'Finance' },
  { slug: 'nutrition', name: 'Nutrition', keywords: 'nutrition, diet, healthy eating, food science, superfoods', category: 'Health' },
  { slug: 'fitness', name: 'Fitness', keywords: 'fitness, workouts, exercise, training programs, gym, cardio', category: 'Health' },
  { slug: 'mental-health', name: 'Mental Health', keywords: 'mental health, wellness, therapy, anxiety, depression, mindfulness', category: 'Health' },
  { slug: 'supplements', name: 'Supplements', keywords: 'supplements, vitamins, nootropics, herbal supplements, protein', category: 'Health' },
  { slug: 'weight-loss', name: 'Weight Loss', keywords: 'weight loss, diet plans, metabolism, calorie deficit, intermittent fasting', category: 'Health' },
  { slug: 'yoga-meditation', name: 'Yoga/Meditation', keywords: 'yoga, meditation, mindfulness, stress reduction, breathing', category: 'Health' },
  { slug: 'science', name: 'Science', keywords: 'science news, scientific discoveries, research breakthroughs, studies', category: 'Science' },
  { slug: 'astronomy', name: 'Astronomy', keywords: 'astronomy, space, stars, planets, cosmic discoveries, telescopes', category: 'Science' },
  { slug: 'geology', name: 'Geology', keywords: 'geology, earth science, earthquakes, volcanoes, minerals', category: 'Science' },
  { slug: 'environment', name: 'Environment', keywords: 'environment, climate, conservation, ecology, sustainability, biodiversity', category: 'Science' },
  { slug: 'space', name: 'Space', keywords: 'space exploration, NASA, SpaceX, Mars, moon missions, ISS', category: 'Science' },
  { slug: 'physics', name: 'Physics', keywords: 'physics, quantum mechanics, relativity, particle physics, CERN', category: 'Science' },
  { slug: 'biology', name: 'Biology', keywords: 'biology, genetics, evolution, CRISPR, ecosystems, biodiversity', category: 'Science' },
  { slug: 'chemistry', name: 'Chemistry', keywords: 'chemistry, materials science, chemical research, periodic table', category: 'Science' },
  { slug: 'medicine', name: 'Medicine', keywords: 'medicine, medical breakthroughs, healthcare, treatments, vaccines', category: 'Health' },
  { slug: 'psychology', name: 'Psychology', keywords: 'psychology, behavior, cognition, mental processes, therapy', category: 'Health' },
  { slug: 'neuroscience', name: 'Neuroscience', keywords: 'neuroscience, brain research, neural networks, consciousness, cognition', category: 'Science' },
  { slug: 'climate', name: 'Climate', keywords: 'climate change, global warming, carbon emissions, climate policy, IPCC', category: 'Science' },
  { slug: 'energy', name: 'Energy', keywords: 'energy, renewable energy, solar power, wind energy, nuclear, fossil fuels', category: 'Science' },
  { slug: 'education', name: 'Education', keywords: 'education, edtech, online learning, universities, schools, MOOCs', category: 'World' },
  { slug: 'politics', name: 'Politics', keywords: 'politics, political news, elections, policy analysis, government', category: 'World' },
  { slug: 'world-news', name: 'World News', keywords: 'world news, international headlines, global affairs, breaking news', category: 'World' },
  { slug: 'us-news', name: 'US News', keywords: 'US news, United States, American politics, Congress, White House', category: 'World' },
  { slug: 'asia-news', name: 'Asia News', keywords: 'Asia news, China, India, Japan, South Korea, Asia-Pacific economy', category: 'World' },
  { slug: 'europe-news', name: 'Europe News', keywords: 'Europe news, European Union, UK, Germany, France, EU policy', category: 'World' },
];

const RSS_FEEDS = [
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
  { url: 'https://hnrss.org/frontpage?points=20', cat: 'tech' },
  { url: 'https://www.reddit.com/r/technology/.rss', cat: 'tech' },
  { url: 'https://www.reddit.com/r/artificial/.rss', cat: 'ai' },
  { url: 'https://www.reddit.com/r/MachineLearning/.rss', cat: 'machine-learning' },
  { url: 'https://www.reddit.com/r/robotics/.rss', cat: 'robotics' },
  { url: 'https://www.reddit.com/r/cybersecurity/.rss', cat: 'cybersecurity' },
  { url: 'https://www.reddit.com/r/gaming/.rss', cat: 'gaming' },
  { url: 'https://www.reddit.com/r/esports/.rss', cat: 'esports' },
  { url: 'https://www.reddit.com/r/Games/.rss', cat: 'game-reviews' },
  { url: 'https://www.reddit.com/r/gamedev/.rss', cat: 'game-development' },
  { url: 'https://www.reddit.com/r/CryptoCurrency/.rss', cat: 'cryptocurrency' },
  { url: 'https://www.reddit.com/r/StockMarket/.rss', cat: 'stock-market' },
  { url: 'https://www.reddit.com/r/investing/.rss', cat: 'investing' },
  { url: 'https://www.reddit.com/r/RealEstate/.rss', cat: 'real-estate' },
  { url: 'https://www.reddit.com/r/Forex/.rss', cat: 'forex' },
  { url: 'https://www.reddit.com/r/defi/.rss', cat: 'defi' },
  { url: 'https://www.reddit.com/r/fintech/.rss', cat: 'fintech' },
  { url: 'https://www.reddit.com/r/blockchain/.rss', cat: 'blockchain' },
  { url: 'https://www.reddit.com/r/nutrition/.rss', cat: 'nutrition' },
  { url: 'https://www.reddit.com/r/mentalhealth/.rss', cat: 'mental-health' },
  { url: 'https://www.reddit.com/r/Supplements/.rss', cat: 'supplements' },
  { url: 'https://www.reddit.com/r/loseit/.rss', cat: 'weight-loss' },
  { url: 'https://www.reddit.com/r/yoga/.rss', cat: 'yoga-meditation' },
  { url: 'https://www.reddit.com/r/psychology/.rss', cat: 'psychology' },
  { url: 'https://www.reddit.com/r/neuroscience/.rss', cat: 'neuroscience' },
  { url: 'https://www.reddit.com/r/science/.rss', cat: 'science' },
  { url: 'https://www.reddit.com/r/space/.rss', cat: 'space' },
  { url: 'https://www.reddit.com/r/Astronomy/.rss', cat: 'astronomy' },
  { url: 'https://www.reddit.com/r/Physics/.rss', cat: 'physics' },
  { url: 'https://www.reddit.com/r/biology/.rss', cat: 'biology' },
  { url: 'https://www.reddit.com/r/chemistry/.rss', cat: 'chemistry' },
  { url: 'https://www.reddit.com/r/energy/.rss', cat: 'energy' },
  { url: 'https://www.reddit.com/r/climate/.rss', cat: 'climate' },
  { url: 'https://www.reddit.com/r/worldnews/.rss', cat: 'world-news' },
  { url: 'https://www.reddit.com/r/politics/.rss', cat: 'politics' },
  { url: 'https://www.reddit.com/r/news/.rss', cat: 'us-news' },
  { url: 'https://www.reddit.com/r/europe/.rss', cat: 'europe-news' },
  { url: 'https://www.reddit.com/r/asia/.rss', cat: 'asia-news' },
];

function log(msg, level = 'INFO') {
  const ts = new Date().toISOString();
  const line = `[${ts}] [${level}] ${msg}`;
  console.log(line);
  try {
    if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR, { recursive: true });
    fs.appendFileSync(path.join(LOG_DIR, `pipeline-${new Date().toISOString().slice(0,10)}.log`), line + '\n');
  } catch (e) {}
}

function loadStats() {
  try { return JSON.parse(fs.readFileSync(STATS_FILE, 'utf-8')); } catch { return { totalArticles: 0, lastRun: null, perSection: {} }; }
}
function saveStats(stats) {
  try { fs.writeFileSync(STATS_FILE, JSON.stringify(stats, null, 2)); } catch {}
}

async function fetchRSS(url) {
  try {
    const res = await fetch(url, { headers: { 'User-Agent': 'LOPINUZE-NewsBot/1.0', 'Accept': 'application/rss+xml,application/xml,text/xml' }, signal: AbortSignal.timeout(15000) });
    if (!res.ok) return [];
    const xml = await res.text();
    const items = [];
    let match;
    const itemRegex = /<item>([\s\S]*?)<\/item>/gi;
    while ((match = itemRegex.exec(xml)) !== null) {
      const itemXml = match[1];
      const title = (itemXml.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]+>/g, '').trim() || '';
      const link = (itemXml.match(/<link[^>]*>([\s\S]*?)<\/link>/i) || [])[1]?.trim() || '';
      const desc = (itemXml.match(/<description[^>]*>([\s\S]*?)<\/description>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]+>/g, '').trim() || '';
      if (title && desc.length > 30) items.push({ title, link, description: desc, source: url });
    }
    if (items.length === 0) {
      const entryRegex = /<entry>([\s\S]*?)<\/entry>/gi;
      while ((match = entryRegex.exec(xml)) !== null) {
        const entryXml = match[1];
        const title = (entryXml.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]+>/g, '').trim() || '';
        const link = ((entryXml.match(/<link[^>]*href="([^"]+)"/i) || [])[1] || '').trim();
        const desc = (entryXml.match(/<summary[^>]*>([\s\S]*?)<\/summary>/i) || entryXml.match(/<content[^>]*>([\s\S]*?)<\/content>/i) || [])[1]?.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]+>/g, '').trim() || '';
        if (title && desc.length > 30) items.push({ title, link, description: desc, source: url });
      }
    }
    return items;
  } catch (e) { return []; }
}

async function fetchFromAllRSS() {
  const all = [];
  const coveredSections = new Set();
  for (const feed of RSS_FEEDS.sort(() => Math.random() - 0.5)) {
    const items = await fetchRSS(feed.url);
    for (const item of items) {
      const ts = SECTIONS.find(s => s.slug === feed.cat)?.slug || 'world-news';
      all.push({ ...item, targetSection: ts, originalSource: item.source });
      coveredSections.add(ts);
    }
    if (items.length > 0) log(`Fetched ${items.length} from ${feed.url}`);
    await new Promise(r => setTimeout(r, 150));
  }
  const uncovered = SECTIONS.filter(s => !coveredSections.has(s.slug)).map(s => s.slug);
  log(`RSS covered ${coveredSections.size}/50. Uncovered: ${uncovered.length > 0 ? uncovered.slice(0,10).join(', ') + (uncovered.length > 10 ? '...' : '') : 'none'}`);
  return { all, coveredSections, uncovered };
}

// Section-specific GEO/AEO prompt
function makePrompt(section) {
  const sec = SECTIONS.find(s => s.slug === section) || SECTIONS[0];
  const cat = sec.category;
  
  const cats = {
    Technology: 'tech innovation, funding rounds, product launches, digital disruption',
    Gaming: 'gaming industry, esports, game releases, player communities, streaming',
    Finance: 'financial markets, investment strategies, economic indicators, wealth management',
    Health: 'medical breakthroughs, wellness research, nutrition science, healthcare policy',
    Science: 'scientific discoveries, space exploration, environmental research, academic studies',
    World: 'international relations, geopolitics, policy developments, regional affairs'
  };
  
  // Get TWO different real expert names for quotes (never repeat the same expert)
  const expert1 = getExpertQuote(section);
  let expert2 = getExpertQuote(section);
  while (expert2.name === expert1.name) expert2 = getExpertQuote(section);

  return `You are a Pulitzer Prize-winning senior correspondent for ${SITE_NAME} (${DOMAIN}), a global news network covering 50 sections across Technology, Gaming, Finance, Health, Science, and World News.

SECTION: ${sec.name} (${cat})
SEO KEYWORDS: ${sec.keywords}

Write a COMPLETE, authoritative news article optimized for:
1. SEO (Search Engine Optimization) - Natural keyword placement in headings and body
2. GEO (Generative Engine Optimization) - Answer-style structure that AI assistants cite
3. AEO (Answer Engine Optimization) - Clear facts, statistics, and expert quotes that answer engines surface

You MUST include the following in your article:
- QUOTE 1: Include a direct quote from ${expert1.name}, ${expert1.title}. Write exactly: "QUOTE FROM ${expert1.name.toUpperCase()}: [insert a realistic, professional quote here about this ${sec.name.toLowerCase()} topic]"
- QUOTE 2: Include a direct quote from ${expert2.name}, ${expert2.title}. Write exactly: "QUOTE FROM ${expert2.name.toUpperCase()}: [insert a different perspective or complementary quote]"

STRUCTURE REQUIREMENTS:
- Opening paragraph: WHO, WHAT, WHEN, WHERE, WHY in first 2 sentences
- Include at least 2 specific statistics/data points with sources
- Use the two expert quotes above (do NOT invent any other expert names)
- Use <h2> and <h3> HTML tags for subheadings
- Naturally insert 2-3 internal links to related LOPINUZE sections (e.g., <a href="/section-ai.html">AI Desk</a>)
- Add a "Key Takeaways" section with <ul><li> bullet points
- End with a forward-looking analysis paragraph
- Format as HTML-ready content using <p>, <h2>, <h3>, <blockquote>, <ul>, <li> tags
- Write 400-550 words
- NEVER mention AI, ChatGPT, LLMs, or automated content. Write as a human journalist.
- Topic focus: ${cats[cat] || cats.World}`;
}

async function rewriteWithDeepSeek(article) {
  if (!DEEPSEEK_API_KEY) return null;
  try {
    const prompt = makePrompt(article.targetSection);
    const hasContent = article.description && article.description.length > 50;
    const userMsg = hasContent
      ? `Source headline: "${article.title}". Source summary: "${article.description.substring(0, 2000)}". Rewrite as original GEO/AEO-optimized report.`
      : `Write an original news report on this ${SECTIONS.find(s=>s.slug===article.targetSection)?.name||'news'} topic: "${article.title}". Make it factual, data-rich, and engaging.`;
    
    const res = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${DEEPSEEK_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: prompt },
          { role: 'user', content: userMsg }
        ],
        temperature: 0.85,
        max_tokens: 2200
      }),
      signal: AbortSignal.timeout(50000)
    });
    const data = await res.json();
    if (data.error) { log(`DeepSeek error: ${JSON.stringify(data.error)}`, 'WARN'); return null; }
    return data.choices?.[0]?.message?.content || null;
  } catch (e) { log(`DeepSeek call failed: ${e.message}`, 'WARN'); return null; }
}

function getAuthor(section) {
  const authors = [
    { name: 'Dr. Sarah Chen', title: 'Chief Technology Editor', av: 'SC', sections: ['tech','ai','machine-learning','deep-learning','robotics','vr-ar','cybersecurity','cloud-computing','blockchain'] },
    { name: 'James Rodriguez', title: 'Senior Finance Correspondent', av: 'JR', sections: ['fintech','investing','trading','cryptocurrency','personal-finance','real-estate','stock-market','etfs','forex','crypto-mining','defi'] },
    { name: 'Dr. Emily Watson', title: 'Health & Science Editor', av: 'EW', sections: ['nutrition','fitness','mental-health','supplements','weight-loss','yoga-meditation','medicine','psychology','neuroscience','biology','chemistry'] },
    { name: 'Marcus Thompson', title: 'Gaming & Esports Lead', av: 'MT', sections: ['gaming','esports','game-reviews','game-development','mobile-gaming'] },
    { name: 'Priya Kapoor', title: 'World Affairs Correspondent', av: 'PK', sections: ['politics','world-news','us-news','asia-news','europe-news','climate','energy','education','environment'] },
    { name: 'Prof. David Kim', title: 'Science & Space Editor', av: 'DK', sections: ['science','astronomy','geology','space','physics'] },
  ];
  for (const a of authors) if (a.sections.includes(section)) return a;
  return { name: 'LOPINUZE News Desk', title: 'Staff Reporter', av: 'LN' };
}

function generateSEO(section, title, content) {
  const sec = SECTIONS.find(s => s.slug === section) || { keywords: 'news', category: 'General', name: 'News' };
  const plain = content.replace(/<[^>]+>/g, '').trim();
  const metaDesc = plain.substring(0, 155).trim() + '...';
  const author = getAuthor(section);
  return {
    metaTitle: `${title} | ${SITE_NAME} ${sec.name} Desk`,
    metaDesc,
    slug: title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').substring(0, 80),
    keywords: sec.keywords,
    category: sec.category,
    date: new Date().toISOString().split('T')[0],
    author: author.name,
    authorTitle: author.title,
    authorAv: author.av,
    readTime: Math.max(3, Math.ceil(plain.split(/\s+/).length / 180)),
  };
}

async function runPipeline() {
  const stats = loadStats();
  const startTime = Date.now();
  log('══════ STARTING PIPELINE RUN ══════');

  const { all: rawArticles, coveredSections, uncovered } = await fetchFromAllRSS();
  log(`Fetched ${rawArticles.length} total articles`);

  const processedArticles = [];
  const articlesDir = path.join(__dirname, 'raw_articles');
  if (!fs.existsSync(articlesDir)) fs.mkdirSync(articlesDir, { recursive: true });

  const existingTitles = new Set();
  const existingBySection = {};
  try {
    for (const f of fs.readdirSync(articlesDir).filter(f => f.endsWith('.json'))) {
      try {
        const d = JSON.parse(fs.readFileSync(path.join(articlesDir, f), 'utf-8'));
        if (d.title) existingTitles.add(d.title.toLowerCase().trim());
        if (d.targetSection) existingBySection[d.targetSection] = (existingBySection[d.targetSection] || 0) + 1;
      } catch {}
    }
  } catch {}

  const deduped = rawArticles
    .filter(a => !existingTitles.has(a.title.toLowerCase().trim()))
    .sort((a, b) => (existingBySection[a.targetSection] || 0) - (existingBySection[b.targetSection] || 0));

  // Ensure at least 50 articles, prioritizing uncovered sections
  const selected = [];
  const selectedSections = new Set();
  
  // First pass: get 1 article per covered section
  for (const art of deduped) {
    if (!selectedSections.has(art.targetSection)) {
      selected.push(art);
      selectedSections.add(art.targetSection);
    }
  }
  
  // Generate articles for completely uncovered sections from scratch
  for (const slug of uncovered) {
    const sec = SECTIONS.find(s => s.slug === slug);
    if (!sec) continue;
    const topicTitles = {
      tech: 'Latest Technology Innovations Reshaping Industries in 2026',
      ai: 'Artificial Intelligence Breakthroughs: How AI Is Transforming Business',
      'machine-learning': 'Machine Learning Advances Drive New Era of Data Science',
      'deep-learning': 'Deep Learning Models Achieve Breakthrough Performance in Key Benchmarks',
      robotics: 'Robotics Industry Sees Record Investment as Automation Demand Surges',
      gaming: 'Gaming Industry Trends: New Releases and Esports Growth',
      esports: 'Esports Tournament Prize Pools Hit New Records in 2026',
      'game-reviews': 'Most Anticipated Game Releases: Reviews and First Impressions',
      'game-development': 'Indie Game Development Scene Produces Breakout Hits',
      'mobile-gaming': 'Mobile Gaming Revenue Surpasses Console Market in Latest Quarter',
      'vr-ar': 'VR and AR Technologies Gain Mainstream Adoption Across Industries',
      cybersecurity: 'Cybersecurity Threats Evolve: New Defense Strategies for 2026',
      'cloud-computing': 'Cloud Computing Market Growth Accelerates as Enterprises Migrate',
      blockchain: 'Blockchain Technology Finds New Applications Beyond Cryptocurrency',
      fintech: 'FinTech Startups Disrupt Traditional Banking with AI-Powered Solutions',
      investing: 'Investment Strategies for 2026: Expert Analysis and Market Outlook',
      trading: 'Day Trading and Options Markets See Surge in Retail Participation',
      cryptocurrency: 'Cryptocurrency Market Update: Bitcoin and Altcoin Price Analysis',
      'personal-finance': 'Personal Finance Tips: Building Wealth in Uncertain Economic Times',
      'real-estate': 'Real Estate Market Trends: Housing Prices and Mortgage Rate Forecast',
      'stock-market': 'Stock Market Analysis: Key Indices and Sector Performance Review',
      etfs: 'ETF Investment Trends: Passive Investing Strategies for 2026',
      forex: 'Forex Market Update: Major Currency Pairs Analysis and Forecast',
      'crypto-mining': 'Cryptocurrency Mining: Hardware Efficiency and Profitability Analysis',
      defi: 'DeFi Protocols Revolutionize Lending and Borrowing in Crypto Space',
      nutrition: 'Nutrition Science Breakthroughs: Diet and Health Research Updates',
      fitness: 'Fitness Trends 2026: New Workout Routines and Training Methods',
      'mental-health': 'Mental Health Awareness: New Research on Anxiety and Depression Treatments',
      supplements: 'Dietary Supplements Market: Vitamin and Nootropic Trends',
      'weight-loss': 'Weight Loss Science: Effective Strategies Backed by New Research',
      'yoga-meditation': 'Yoga and Meditation Benefits Confirmed by Neuroscience Research',
      science: 'Major Scientific Discoveries Reshaping Our Understanding of the Universe',
      astronomy: 'Astronomy Breakthroughs: New Exoplanet Discoveries and Cosmic Phenomena',
      geology: 'Geological Research Reveals New Insights into Earth\'s Structure',
      environment: 'Environmental Conservation Efforts Show Promising Results Globally',
      space: 'Space Exploration Update: NASA and SpaceX Mission Developments',
      physics: 'Physics Breakthroughs: Quantum Mechanics and Particle Research Advances',
      biology: 'Biology Research: Genetic Discoveries and Ecosystem Studies',
      chemistry: 'Chemistry Innovations: New Materials and Sustainable Chemical Processes',
      medicine: 'Medical Breakthroughs: New Treatments and Healthcare Innovations',
      psychology: 'Psychology Research Reveals New Insights into Human Behavior',
      neuroscience: 'Neuroscience Advances: Brain Research Unlocks Mysteries of Consciousness',
      climate: 'Climate Change Update: Global Policy and Emission Reduction Progress',
      energy: 'Energy Sector Transformation: Renewable Sources Surpass Fossil Fuels',
      education: 'Education Technology Trends: Online Learning and EdTech Innovations',
      politics: 'Political Analysis: Key Policy Developments and Election Updates',
      'world-news': 'Global Affairs: International Developments and Diplomatic Relations',
      'us-news': 'US News: Domestic Policy and Economic Developments Update',
      'asia-news': 'Asia-Pacific Region: Economic Growth and Geopolitical Developments',
      'europe-news': 'European Union: Policy Updates and Economic Integration Progress'
    };
    const title = topicTitles[slug] || `${sec.name} Latest Developments and Analysis for July 2026`;
    selected.push({
      title,
      description: '',
      link: '',
      targetSection: slug,
      originalSource: 'LOPINUZE Editorial Desk',
      isGenerated: true
    });
    selectedSections.add(slug);
  }
  
  // Fill remaining slots
  for (const art of deduped) {
    if (!selected.includes(art) && selected.length < 50) selected.push(art);
  }

  log(`Processing ${selected.length} articles across ${selectedSections.size} sections (${uncovered.length} generated from scratch)...`);

  for (const raw of selected.slice(0, 50)) {
    let rewritten = await rewriteWithDeepSeek(raw);
    
    if (!rewritten) {
      log(`Retrying "${raw.title.substring(0, 50)}..."`);
      await new Promise(r => setTimeout(r, 3000));
      rewritten = await rewriteWithDeepSeek(raw);
    }

    if (!rewritten) {
      log(`FAILED: "${raw.title.substring(0, 50)}..."`, 'WARN');
      continue;
    }

    const seo = generateSEO(raw.targetSection, raw.title, rewritten);
    const articleData = { title: raw.title, targetSection: raw.targetSection, originalUrl: raw.link || '', originalSource: raw.originalSource || 'LOPINUZE Editorial', content: rewritten, seo, processedAt: new Date().toISOString() };

    const fname = `article-${raw.targetSection}-${Date.now()}.json`;
    fs.writeFileSync(path.join(articlesDir, fname), JSON.stringify(articleData, null, 2));
    processedArticles.push(articleData);

    stats.totalArticles = (stats.totalArticles || 0) + 1;
    stats.perSection[raw.targetSection] = (stats.perSection[raw.targetSection] || 0) + 1;
    stats.lastRun = new Date().toISOString();
    saveStats(stats);

    log(`✅ [${raw.targetSection}] "${raw.title.substring(0, 50)}..."`);
    await new Promise(r => setTimeout(r, 1000));
  }

  // Rebuild the static site
  try {
    const { buildSite } = require('./build-newspaper-module.js');
    log('Rebuilding site with new articles...');
    buildSite();
  } catch (e) { log(`Build error: ${e.message}`, 'ERROR'); }

  log(`══════ PIPELINE DONE: ${processedArticles.length} articles in ${((Date.now()-startTime)/1000).toFixed(1)}s ══════`);
}

(async () => {
  log(`🚀 LOPINUZE Pipeline v4.0 — ${DOMAIN}`);
  log(`📡 AI: DeepSeek (primary) | Sections: ${SECTIONS.length} | RSS sources: ${RSS_FEEDS.length}`);
  await runPipeline();
})();