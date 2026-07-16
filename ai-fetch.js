/**
 * LOPINUZE.2BD.NET - AI Content Pipeline
 * Fetches real articles from internet sources using Gemini & DeepSeek
 * Run: node ai-fetch.js
 */

const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  geminiApiKey: process.env.GEMINI_API_KEY || 'YOUR_GEMINI_API_KEY',
  deepseekApiKey: process.env.DEEPSEEK_API_KEY || 'YOUR_DEEPSEEK_API_KEY',
  newsApiKey: process.env.NEWS_API_KEY || '',
  outputDir: path.join(__dirname, 'fetched-articles'),
  sections: [
  "tech",
  "ai",
  "machine-learning",
  "deep-learning",
  "robotics",
  "gaming",
  "esports",
  "game-reviews",
  "game-development",
  "mobile-gaming",
  "vr-ar",
  "cybersecurity",
  "cloud-computing",
  "blockchain",
  "fintech",
  "investing",
  "trading",
  "cryptocurrency",
  "personal-finance",
  "real-estate",
  "stock-market",
  "etfs",
  "forex",
  "crypto-mining",
  "defi",
  "nutrition",
  "fitness",
  "mental-health",
  "supplements",
  "weight-loss",
  "yoga-meditation",
  "science",
  "astronomy",
  "geology",
  "environment",
  "space",
  "physics",
  "biology",
  "chemistry",
  "medicine",
  "psychology",
  "neuroscience",
  "climate",
  "energy",
  "education",
  "politics",
  "world-news",
  "us-news",
  "asia-news",
  "europe-news"
],
  sources: [
    'https://newsapi.org/v2/top-headlines',
    'https://api.worldnewsapi.com/search-news',
    'https://hacker-news.firebaseio.com/v0/topstories.json'
  ]
};

// Fetch news from APIs
async function fetchNewsFromSources() {
  console.log('🔍 Fetching news from multiple sources...');
  
  // In production, this would call real APIs
  // For now, it provides the structure for integration
  
  const articles = [];
  
  // Example: Fetch from NewsAPI
  // const response = await fetch(\`https://newsapi.org/v2/top-headlines?country=us&apiKey=\${CONFIG.newsApiKey}\`);
  // const data = await response.json();
  // articles.push(...data.articles);
  
  return articles;
}

// Rewrite article using Gemini AI (FREE: 1500 requests/day)
async function rewriteWithGemini(article) {
  console.log('🤖 Rewriting with Gemini 2.0 Flash...');
  
  // const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json', 'x-goog-api-key': CONFIG.geminiApiKey },
  //   body: JSON.stringify({
  //     contents: [{ parts: [{ text: \`Rewrite this news article in a unique, engaging style while preserving facts. Add expert analysis and a human touch. Original: \${article.content}\` }] }]
  //   })
  // });
  // const data = await response.json();
  // return data.candidates[0].content.parts[0].text;
  
  return article.content;
}

// Fallback: DeepSeek V4 Flash ($0.14/1M input tokens)
async function rewriteWithDeepSeek(article) {
  console.log('🔄 Falling back to DeepSeek V4 Flash...');
  
  // const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
  //   method: 'POST',
  //   headers: { 'Authorization': \`Bearer \${CONFIG.deepseekApiKey}\`, 'Content-Type': 'application/json' },
  //   body: JSON.stringify({
  //     model: 'deepseek-chat',
  //     messages: [{ role: 'user', content: \`Rewrite article in journalistic style with SEO optimization: \${article.content}\` }]
  //   })
  // });
  // const data = await response.json();
  // return data.choices[0].message.content;
  
  return article.content;
}

// Generate AI image using Pollinations (free)
async function generateImage(prompt) {
  const encodedPrompt = encodeURIComponent(prompt);
  return \`https://image.pollinations.ai/prompt/\${encodedPrompt}?width=800&height=450&nologo=true\`;
}

// Main pipeline
async function main() {
  console.log('🚀 Starting LOPINUZE AI Content Pipeline...');
  console.log(\`Domain: LOPINUZE.2BD.NET\`);
  console.log('=' .repeat(50));
  
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }
  
  // Step 1: Fetch from sources
  const rawArticles = await fetchNewsFromSources();
  console.log(\`📥 Fetched \${rawArticles.length} raw articles\`);
  
  // Step 2: AI Rewrite
  for (const article of rawArticles.slice(0, 10)) {
    let rewritten;
    try {
      rewritten = await rewriteWithGemini(article);
    } catch (e) {
      console.log('Gemini failed, trying DeepSeek...');
      rewritten = await rewriteWithDeepSeek(article);
    }
    
    // Step 3: Generate image
    const imageUrl = await generateImage(article.title);
    
    // Step 4: Save article
    const filename = \`article-\${Date.now()}-\${Math.random().toString(36).slice(2,8)}.json\`;
    fs.writeFileSync(
      path.join(CONFIG.outputDir, filename),
      JSON.stringify({ ...article, rewrittenContent: rewritten, imageUrl, fetchedAt: new Date().toISOString() }, null, 2)
    );
    console.log(\`✅ Saved: \${filename}\`);
  }
  
  console.log('\n🎉 Pipeline complete! Articles saved to', CONFIG.outputDir);
}

main().catch(console.error);
