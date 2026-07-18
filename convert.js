const fs = require('fs');
let code = fs.readFileSync('build-newspaper.js', 'utf8');

// 1. Change output dir to docs
code = code.replace(/const O=path\.join\(__dirname,'news-empire'\);/g, "const O=path.join(__dirname,'docs');");

// 2. Add Monetag script and Adsterra/Monetag/EZMob verification meta tags
const monetag = '<!-- EZMob Site Validation Code: EZMFXSJHYTGLUZ7YKTW --><meta name="monetag" content="439975c2b466e46aa6206140297bfdcc"><meta name="adsterra" content="439975c2b466e46aa6206140297bfdcc"><meta name="a.validate.02" content="439975c2b466e46aa6206140297bfdcc"><script>(function(d,z,s){s.src="https://"+d+"/401/"+z;try{(document.body||document.documentElement).appendChild(s)}catch(e){}})("5gvci.com",11342729,document.createElement("script"))</script>';
code = code.replace(/<head>/g, '<head>' + monetag);

// 3. Make it a module
code = code.split('if(fs.existsSync(O))fs.rmSync(O,{recursive:true,force:true});').join('function buildSite() {\nloadAiArticles();\nif(fs.existsSync(O))fs.rmSync(O,{recursive:true,force:true});');
code = code.split("fs.writeFileSync(path.join(O,'disclaimer.html'),disc);").join("fs.writeFileSync(path.join(O,'disclaimer.html'),disc);\nif(fs.existsSync('CNAME')) fs.copyFileSync('CNAME', path.join(O, 'CNAME'));\nif(fs.existsSync('sw.js')) fs.copyFileSync('sw.js', path.join(O, 'sw.js'));\nif(fs.existsSync('9a0153ac34adb4656ff5.txt')) fs.copyFileSync('9a0153ac34adb4656ff5.txt', path.join(O, '9a0153ac34adb4656ff5.txt'));");
code += '\n}\nmodule.exports = { buildSite };\n';

// Define loadAiArticles and allAiArticles at the top level
const aiReadLogic = `
let allAiArticles = [];
function loadAiArticles() {
  allAiArticles = [];
  const aiDir = path.join(__dirname, 'raw_articles');
  if (fs.existsSync(aiDir)) {
    try {
      const files = fs.readdirSync(aiDir).filter(f => f.endsWith('.json'));
      files.sort().reverse();
      for (const file of files) {
        let obj = JSON.parse(fs.readFileSync(path.join(aiDir, file), 'utf8'));
        obj.actualFile = file.replace('.json', '.html');
        allAiArticles.push(obj);
      }
    } catch(e) {}
  }
}
`;
code = code.replace(/const fs=require\('fs'\);/, "const fs=require('fs');\n" + aiReadLogic);

// In sectionPage, before generating dummy articles, use aiArticles for this section
const aiInjection = `
let aiArticles = allAiArticles.filter(a => a.targetSection === sec.s);

const tp=Math.ceil(TAS/APP);
const start=(page-1)*APP+1;
const end=Math.min(start+APP-1,TAS);
let arts='';

let currentIdx = start;
if (page === 1) {
  for (const a of aiArticles) {
    if (currentIdx > end) break;
    const link = '/articles/' + a.actualFile;
    arts += '<article class="article-card-newspaper" onclick="location.href=\\'' + link + '\\'"><div class="num-col">NEW</div><div class="content-col"><div class="section-label">' + sec.n + '</div><h3><a href="' + link + '">' + a.title + '</a></h3><div class="meta">By ' + (a.seo?.author || 'Staff') + ' · ' + (a.seo?.date || '') + ' · ' + (a.seo?.readTime || 3) + ' min read</div><p>' + (a.content.substring(0, 150).replace(/<[^>]+>/g,'')) + '...</p></div></article>';
    currentIdx++;
  }
}
`;
code = code.replace(/const tp=Math\.ceil\(TAS\/APP\);\s*const start=\(page-1\)\*APP\+1;\s*const end=Math\.min\(start\+APP-1,TAS\);\s*let arts='';/g, aiInjection);
code = code.replace(/for\(let i=start;i<=end;i\+\+\)\{/g, 'for(let i=currentIdx;i<=end;i++){');

// Inject latest breaking news into landing()
const landingAI = `
let latestAI = allAiArticles.slice(0, 6);
let latestHTML = '';
if (latestAI.length > 0) {
  const cards = latestAI.map(a => '<article class="article-card-newspaper" style="border:1px solid var(--bdr);padding:1rem;margin-bottom:0.5rem;" onclick="location.href=\\'/articles/' + a.actualFile + '\\'"><div class="section-label">LATEST</div><h3 style="margin:0.2rem 0;"><a href="/articles/' + a.actualFile + '">' + a.title + '</a></h3><div class="meta" style="margin-bottom:0.4rem;">' + (a.seo?.date||'') + '</div><p style="margin:0;font-size:0.8rem;">' + a.content.substring(0,120).replace(/<[^>]+>/g,'') + '...</p></article>').join('');
  latestHTML = '<div class="cat-group"><h2>🔥 Breaking News</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;padding-bottom:2rem;">' + cards + '</div></div>';
}
`;
code = code.replace(/function landing\(\)\{/, 'function landing(){\n' + landingAI);
code = code.replace(/<main class="container">'\+gs\+'<\/main>/, "<main class=\"container\">' + latestHTML + gs + '</main>");

// Generate individual AI HTML articles inside buildSite() with GEO & internal interlinking
const generateAiArticles = `
// GENERATE AI ARTICLE PAGES WITH GEO & INTERNAL BACKLINKS
const monetag = '<script>(function(d,z,s){s.src="https://"+d+"/401/"+z;try{(document.body||document.documentElement).appendChild(s)}catch(e){}})("5gvci.com",11342729,document.createElement("script"))</script>';
if (!fs.existsSync(path.join(O, 'articles'))) fs.mkdirSync(path.join(O, 'articles'), {recursive:true});
for (const a of allAiArticles) {
  const sec = SECTIONS.find(s => s.s === a.targetSection) || SECTIONS[0];
  const t = a.title;
  const author = { name: a.seo?.author || 'Staff', title: a.seo?.authorTitle || 'Reporter', av: (a.seo?.author || 'S')[0] };
  const d = a.seo?.date || today();
  const rt = a.seo?.readTime || 4;
  let formattedContent = a.content;
  if(!formattedContent.includes('<p>')) {
    formattedContent = a.content.split(/\\n{2,}/).map(p => {
       p = p.trim();
       if (p.startsWith('## ') || p.startsWith('### ')) {
         const level = p.startsWith('## ') ? 'h2' : 'h3';
         return '<' + level + '>' + p.replace(/^##\\s*|^###\\s*/, '') + '</' + level + '>';
       }
       return '<p>' + p + '</p>';
    }).join('\\n');
  }

  const jsonLd = JSON.stringify({
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": t,
    "description": (a.seo?.metaDesc || t),
    "datePublished": d,
    "author": { "@type": "Person", "name": author.name },
    "publisher": { "@type": "Organization", "name": S, "url": "https://lopinuze.online" }
  });

  const relPosts = SECTIONS.slice(0, 4).map(s => '<a href="/section-' + s.s + '.html"><h5>' + s.n + ' Updates</h5><div class="meta">Global Desk</div></a>').join('');

  const html = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + monetag + '<title>' + t + ' – ' + S + '</title><meta name="description" content="' + (a.seo?.metaDesc || t) + '"><meta name="keywords" content="' + sec.n + ', technology news, market report, global updates"><meta name="author" content="' + author.name + '"><meta name="robots" content="index,follow"><meta name="geo.region" content="US-NY, GB-LND, EU, GLOBAL"><meta name="geo.placename" content="Global Desk"><meta property="og:title" content="' + t + '"><meta property="og:type" content="article"><meta property="og:url" content="https://lopinuze.online/articles/' + a.actualFile + '"><link rel="canonical" href="https://lopinuze.online/articles/' + a.actualFile + '"><script type="application/ld+json">' + jsonLd + '</script><style>' + CSS + '</style></head><body><header class="site-header"><div class="container"><a href="/index.html" class="logo">' + S + '</a><nav><ul class="nav-links"><li><a href="/index.html">Home</a></li><li><a href="/section-' + sec.s + '.html">' + sec.n + '</a></li><li><a href="/finance.html">Finance</a></li><li><a href="/section-world-news.html">World</a></li><li><a href="/section-tech.html">Tech</a></li></ul></nav>' + LANG + '</div></header><main><article class="article-detail"><div class="breadcrumb"><a href="/index.html">Home</a> &rsaquo; <a href="/section-' + sec.s + '.html">' + sec.n + '</a> &rsaquo; Article</div><div class="sec-tag">' + sec.n + ' · ANALYSIS</div><h1>' + t + '</h1><div class="byline"><strong>' + author.name + '</strong> · ' + d + ' · ' + rt + ' min read</div><div class="key-takeaways"><h4>Key Takeaways</h4><ul><li>Market data & verified insights on ' + sec.n + '</li><li>Expert analysis by ' + author.name + '</li><li>Internal coverage across 50 global news desks</li></ul></div><div class="content">' + formattedContent + '</div><div class="editor-note"><strong>Editor\\'s Note</strong> — Reviewed by ' + author.name + '. Based on reporting from trusted global wire services.</div><div class="author-bio"><div class="author-avatar" style="width:44px;height:44px;font-size:0.85rem">' + author.av + '</div><div><h4>' + author.name + '</h4><p style="font-size:0.68rem;color:var(--tm);margin-bottom:0.15rem">' + author.title + '</p><p style="font-size:0.75rem">Senior correspondent covering ' + sec.n.toLowerCase() + ' for ' + S + '.</p></div></div><div class="cat-group"><h2>Related Coverage & Internal Links</h2><div class="rel-posts">' + relPosts + '</div></div></article></main>' + FOOTER + '</body></html>';
  fs.writeFileSync(path.join(O, 'articles', a.actualFile), html);
}

// ALSO SYNC TO ROOT DIRECTORY FOR GITHUB PAGES ROOT COMPATIBILITY
try {
  const docsFiles = fs.readdirSync(O);
  for (const f of docsFiles) {
    if (f === 'articles') {
      if (!fs.existsSync(path.join(__dirname, 'articles'))) fs.mkdirSync(path.join(__dirname, 'articles'), {recursive:true});
      const artFiles = fs.readdirSync(path.join(O, 'articles'));
      for (const af of artFiles) {
        fs.copyFileSync(path.join(O, 'articles', af), path.join(__dirname, 'articles', af));
      }
    } else {
      fs.copyFileSync(path.join(O, f), path.join(__dirname, f));
    }
  }
  console.log('✅ Synced vintage newspaper to root directory for GitHub Pages root compatibility');
} catch(e) { console.error('Root sync warning:', e.message); }
`;
code = code.replace(/console\.log\('\\n🎉 Complete! '\+String\(3\+1\+1\+sc\+ac\)\+' vintage newspaper pages\.'\);/, generateAiArticles + "\nconsole.log('\\n🎉 Complete!');");

fs.writeFileSync('build-newspaper-module.js', code);
console.log('✅ Generated build-newspaper-module.js');
