const fs = require('fs');
const path = require('path');

// 50 sections with names, slugs, and descriptions
const sections = [
  { name: "Tech", slug: "tech", desc: "Latest technology news and reviews." },
  { name: "Artificial Intelligence", slug: "ai", desc: "AI breakthroughs and research." },
  { name: "Machine Learning", slug: "machine-learning", desc: "ML algorithms and applications." },
  { name: "Deep Learning", slug: "deep-learning", desc: "Deep neural networks and frameworks." },
  { name: "Robotics", slug: "robotics", desc: "Robots, automation, and drones." },
  { name: "Gaming", slug: "gaming", desc: "Video games, consoles, and industry news." },
  { name: "Esports", slug: "esports", desc: "Competitive gaming tournaments and teams." },
  { name: "Game Reviews", slug: "game-reviews", desc: "In-depth game reviews and ratings." },
  { name: "Game Development", slug: "game-development", desc: "Indie to AAA game creation." },
  { name: "Mobile Gaming", slug: "mobile-gaming", desc: "iOS and Android game news." },
  { name: "VR/AR", slug: "vr-ar", desc: "Virtual and augmented reality innovations." },
  { name: "Cybersecurity", slug: "cybersecurity", desc: "Hacks, data breaches, and defense." },
  { name: "Cloud Computing", slug: "cloud-computing", desc: "AWS, Azure, GCP, and SaaS." },
  { name: "Blockchain", slug: "blockchain", desc: "Distributed ledger technology." },
  { name: "FinTech", slug: "fintech", desc: "Financial technology startups." },
  { name: "Investing", slug: "investing", desc: "Stock market and investment strategies." },
  { name: "Trading", slug: "trading", desc: "Day trading, forex, and options." },
  { name: "Cryptocurrency", slug: "cryptocurrency", desc: "Bitcoin, Ethereum, and altcoins." },
  { name: "Personal Finance", slug: "personal-finance", desc: "Budgeting, saving, and credit." },
  { name: "Real Estate", slug: "real-estate", desc: "Housing market and property tips." },
  { name: "Stock Market", slug: "stock-market", desc: "Market indices and analysis." },
  { name: "ETFs", slug: "etfs", desc: "Exchange traded funds and investing." },
  { name: "Forex", slug: "forex", desc: "Foreign exchange and currency trading." },
  { name: "Crypto Mining", slug: "crypto-mining", desc: "Mining hardware and profitability." },
  { name: "DeFi", slug: "defi", desc: "Decentralized finance protocols." },
  { name: "Nutrition", slug: "nutrition", desc: "Diet, supplements, and healthy eating." },
  { name: "Fitness", slug: "fitness", desc: "Workouts, gear, and training." },
  { name: "Mental Health", slug: "mental-health", desc: "Wellness and psychological insights." },
  { name: "Supplements", slug: "supplements", desc: "Vitamins, nootropics, and herbs." },
  { name: "Weight Loss", slug: "weight-loss", desc: "Diet plans and weight management." },
  { name: "Yoga/Meditation", slug: "yoga-meditation", desc: "Mindfulness and flexibility." },
  { name: "Science", slug: "science", desc: "General scientific discoveries." },
  { name: "Astronomy", slug: "astronomy", desc: "Space, stars, and planets." },
  { name: "Geology", slug: "geology", desc: "Earth sciences and earthquakes." },
  { name: "Environment", slug: "environment", desc: "Climate, conservation, and ecology." },
  { name: "Space", slug: "space", desc: "Space exploration and NASA." },
  { name: "Physics", slug: "physics", desc: "Quantum mechanics and relativity." },
  { name: "Biology", slug: "biology", desc: "Genetics, evolution, and ecosystems." },
  { name: "Chemistry", slug: "chemistry", desc: "Materials, reactions, and research." },
  { name: "Medicine", slug: "medicine", desc: "Medical breakthroughs and healthcare." },
  { name: "Psychology", slug: "psychology", desc: "Behavior, cognition, and mental processes." },
  { name: "Neuroscience", slug: "neuroscience", desc: "Brain research and neural networks." },
  { name: "Climate", slug: "climate", desc: "Climate change and global warming." },
  { name: "Energy", slug: "energy", desc: "Renewable and fossil fuels." },
  { name: "Education", slug: "education", desc: "Edtech and learning resources." },
  { name: "Politics", slug: "politics", desc: "Global political news and analysis." },
  { name: "World News", slug: "world-news", desc: "International headlines." },
  { name: "US News", slug: "us-news", desc: "United States news and policy." },
  { name: "Asia News", slug: "asia-news", desc: "Asia-Pacific region coverage." },
  { name: "Europe News", slug: "europe-news", desc: "European Union and countries news." }
];

// Shared minimal CSS
const styleCSS = `
:root {
  --bg: #ffffff;
  --surface: #f8f9fa;
  --text: #212529;
  --text-light: #6c757d;
  --primary: #0d6efd;
  --border: #dee2e6;
  --radius: 8px;
  --max-width: 1200px;
  --font-sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: var(--font-sans);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}
.container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 1.5rem;
}
.site-header {
  background: #111;
  color: white;
  padding: 0.5rem 0;
  position: sticky;
  top: 0;
  z-index: 10;
}
.site-header .container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  font-size: 1.5rem;
  font-weight: 700;
  text-decoration: none;
  color: white;
}
.nav-links {
  display: flex;
  gap: 1.5rem;
  list-style: none;
}
.nav-links a {
  color: rgba(255,255,255,0.85);
  text-decoration: none;
  font-size: 0.9rem;
}
.nav-links a:hover { color: white; }
.lang-switcher select {
  padding: 0.3rem 0.5rem;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: #222;
  color: white;
  font-size: 0.85rem;
}
.breaking-news {
  background: #e63946;
  color: white;
  padding: 0.35rem 0;
  font-size: 0.85rem;
  overflow: hidden;
}
.breaking-news .container { white-space: nowrap; }
.hero {
  padding: 4rem 0 3rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}
.hero h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
.hero p { color: var(--text-light); font-size: 1.1rem; max-width: 700px; }
.section-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 3rem 0;
}
.section-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  transition: box-shadow 0.2s;
  text-decoration: none;
  color: inherit;
}
.section-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.section-card h3 { margin-bottom: 0.5rem; color: var(--primary); }
.section-card p { color: var(--text-light); font-size: 0.9rem; }
.category-header {
  padding: 2rem 0 1rem;
  border-bottom: 1px solid var(--border);
}
.category-header h1 { font-size: 2rem; }
.category-header p { color: var(--text-light); max-width: 600px; }
.article-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
  padding: 2rem 0;
}
.article-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.article-card img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  background: var(--surface);
}
.article-card .card-body { padding: 1.25rem; flex: 1; }
.article-card h3 { font-size: 1.15rem; margin-bottom: 0.35rem; }
.article-card h3 a { color: var(--text); text-decoration: none; }
.article-card h3 a:hover { color: var(--primary); }
.article-card .meta {
  font-size: 0.8rem;
  color: var(--text-light);
  margin-bottom: 0.75rem;
}
.article-card p { color: var(--text-light); font-size: 0.9rem; line-height: 1.5; }
.site-footer {
  background: #111;
  color: rgba(255,255,255,0.7);
  padding: 2rem 0;
  margin-top: 4rem;
  font-size: 0.9rem;
}
.site-footer .container { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 2rem; }
.site-footer a { color: white; text-decoration: none; }
`;

// Shared JS
const scriptJS = `
document.querySelector('.lang-switcher select')?.addEventListener('change', (e) => {
  alert('Language change to: ' + e.target.value + ' (demo only)');
});
const ticker = document.querySelector('.breaking-news .container');
if (ticker) {
  const headlines = [
    "BREAKING_SECTION breaking: Latest developments happening now"
  ];
  let i = 0;
  setInterval(() => {
    ticker.textContent = headlines[i % headlines.length];
    i++;
  }, 5000);
}
`;

// Generate landing page
function generateLandingPage() {
  const sectionLinks = sections.map(s => `
    <a href="${s.slug}.html" class="section-card">
      <h3>${s.name}</h3>
      <p>${s.desc}</p>
    </a>
  `).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Global News Empire – 50 Sections</title>
  <meta name="description" content="50 sections · 100+ countries · 14 languages. The complete, non-generic global news experience.">
  <style>${styleCSS}</style>
</head>
<body>
  <header class="site-header">
    <div class="container">
      <a href="index.html" class="logo">🌐 NewsEmpire</a>
      <nav>
        <ul class="nav-links">
          <li><a href="index.html">Home</a></li>
          <li><a href="tech.html">Tech</a></li>
          <li><a href="world-news.html">World</a></li>
          <li><a href="science.html">Science</a></li>
          <li><a href="finance.html">Finance</a></li>
        </ul>
      </nav>
      <div class="lang-switcher">
        <select>
          <option value="en">English</option>
          <option value="es">Español</option>
          <option value="fr">Français</option>
          <option value="de">Deutsch</option>
          <option value="zh">中文</option>
        </select>
      </div>
    </div>
  </header>
  <div class="breaking-news">
    <div class="container">Breaking: Global markets surge amid tech rally</div>
  </div>
  <section class="hero">
    <div class="container">
      <h1>Global News Empire</h1>
      <p>50 sections · 100+ countries · 14 languages. The complete, non‑generic news experience.</p>
    </div>
  </section>
  <main class="container">
    <div class="section-grid">
      ${sectionLinks}
    </div>
  </main>
  <footer class="site-footer">
    <div class="container">
      <div>&copy; 2026 NewsEmpire. All rights reserved.</div>
      <div><a href="#">About</a> · <a href="#">Contact</a> · <a href="#">Privacy</a></div>
    </div>
  </footer>
  <script>
    document.querySelector('.lang-switcher select')?.addEventListener('change', (e) => {
      alert('Language change to: ' + e.target.value + ' (demo only)');
    });
    const ticker = document.querySelector('.breaking-news .container');
    if (ticker) {
      const headlines = [
        "Breaking: Global markets surge amid tech rally",
        "AI breakthrough reduces energy consumption by 40%",
        "NASA announces new Mars mission timeline",
      ];
      let i = 0;
      setInterval(() => {
        ticker.textContent = headlines[i % headlines.length];
        i++;
      }, 5000);
    }
  </script>
</body>
</html>`;
}

// Generate category page
function generateCategoryPage(section) {
  const sampleArticles = [
    { title: `${section.name} trends to watch in 2026`, img: "https://placehold.co/600x400/eee/999?text=Article+1", date: "2026-07-11", author: "Alex Rivera" },
    { title: `How ${section.name.toLowerCase()} is reshaping industries`, img: "https://placehold.co/600x400/eee/999?text=Article+2", date: "2026-07-10", author: "Jordan Lee" },
    { title: `5 breakthroughs in ${section.name.toLowerCase()} this month`, img: "https://placehold.co/600x400/eee/999?text=Article+3", date: "2026-07-09", author: "Morgan Chen" },
    { title: `Expert interview: The future of ${section.name.toLowerCase()}`, img: "https://placehold.co/600x400/eee/999?text=Article+4", date: "2026-07-08", author: "Taylor Singh" },
    { title: `${section.name} startups raised $2B in Q2`, img: "https://placehold.co/600x400/eee/999?text=Article+5", date: "2026-07-07", author: "Casey Patel" },
    { title: `Why ${section.name.toLowerCase()} matters more than ever`, img: "https://placehold.co/600x400/eee/999?text=Article+6", date: "2026-07-06", author: "Riley Kim" },
  ];

  const articleCards = sampleArticles.map(a => `
    <article class="article-card">
      <img src="${a.img}" alt="${a.title}" loading="lazy">
      <div class="card-body">
        <h3><a href="#">${a.title}</a></h3>
        <div class="meta">By ${a.author} · ${a.date}</div>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
      </div>
    </article>
  `).join('');

  const pageScript = scriptJS.replace('BREAKING_SECTION', section.name);

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${section.name} – NewsEmpire</title>
  <meta name="description" content="${section.desc}">
  <style>${styleCSS}</style>
</head>
<body>
  <header class="site-header">
    <div class="container">
      <a href="index.html" class="logo">🌐 NewsEmpire</a>
      <nav>
        <ul class="nav-links">
          <li><a href="index.html">Home</a></li>
          <li><a href="tech.html">Tech</a></li>
          <li><a href="world-news.html">World</a></li>
          <li><a href="science.html">Science</a></li>
          <li><a href="finance.html">Finance</a></li>
        </ul>
      </nav>
      <div class="lang-switcher">
        <select>
          <option value="en">English</option>
          <option value="es">Español</option>
          <option value="fr">Français</option>
          <option value="de">Deutsch</option>
          <option value="zh">中文</option>
        </select>
      </div>
    </div>
  </header>
  <div class="breaking-news">
    <div class="container">${section.name} breaking: Latest developments happening now</div>
  </div>
  <div class="category-header container">
    <h1>${section.name}</h1>
    <p>${section.desc} — in‑depth coverage, expert analysis, and the latest stories.</p>
  </div>
  <main class="container">
    <div class="article-list">
      ${articleCards}
    </div>
  </main>
  <footer class="site-footer">
    <div class="container">
      <div>&copy; 2026 NewsEmpire. All rights reserved.</div>
      <div><a href="#">About</a> · <a href="#">Contact</a> · <a href="#">Privacy</a></div>
    </div>
  </footer>
  <script>${pageScript}</script>
</body>
</html>`;
}

// Create output directory
const outputDir = path.join(__dirname, 'news-empire');
if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

// Write landing page
fs.writeFileSync(path.join(outputDir, 'index.html'), generateLandingPage());
console.log('✅ Created index.html (Landing Page)');

// Write 50 category pages
sections.forEach(section => {
  fs.writeFileSync(path.join(outputDir, `${section.slug}.html`), generateCategoryPage(section));
  console.log(`✅ Created ${section.slug}.html`);
});

console.log(`\n🎉 Complete! ${sections.length + 1} pages generated inside 'news-empire/'`);
console.log('   Open news-empire/index.html in your browser.');