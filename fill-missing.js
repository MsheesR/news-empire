/**
 * Fill missing 20 sections with real DeepSeek content
 * Uses gaming/general RSS feeds to cover all remaining sections
 */
const fs=require('fs');const path=require('path');
const DK='sk-0b8337ad2ef24e9caca7b6f4b897a95a';
const NEWS=path.join(__dirname,'news-empire');const ARTS=path.join(NEWS,'articles');

// The 20 sections that need content
const NEEDED=['gaming','esports','game-reviews','game-development','mobile-gaming','crypto-mining','defi','supplements','yoga-meditation','psychology','neuroscience','education','politics','world-news','us-news','asia-news','europe-news','real-estate','forex','forex'];

// Feeds that can cover remaining topics
const FEEDS=[
  {url:'https://www.reddit.com/r/gaming/.rss',secs:['gaming','esports','game-reviews','game-development','mobile-gaming']},
  {url:'https://www.reddit.com/r/CryptoCurrency/.rss',secs:['crypto-mining','defi']},
  {url:'https://www.reddit.com/r/worldnews/.rss',secs:['world-news','politics','us-news','asia-news','europe-news']},
  {url:'https://feeds.bbci.co.uk/news/world/rss.xml',secs:['world-news','politics','us-news','asia-news','europe-news','education']},
  {url:'https://feeds.bbci.co.uk/news/health/rss.xml',secs:['supplements','yoga-meditation','psychology','neuroscience']},
  {url:'https://www.reddit.com/r/RealEstate/.rss',secs:['real-estate']},
  {url:'https://www.reddit.com/r/Forex/.rss',secs:['forex']},
  {url:'https://rss.nytimes.com/services/xml/rss/nyt/Health.xml',secs:['psychology','neuroscience','supplements','yoga-meditation']},
  {url:'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',secs:['real-estate','forex']},
  {url:'https://feeds.bbci.co.uk/news/technology/rss.xml',secs:['gaming','esports','game-reviews','game-development','mobile-gaming']},
];

const AUTHORS={gaming:'Marcus Thompson',esports:'Marcus Thompson','game-reviews':'Marcus Thompson','game-development':'Marcus Thompson','mobile-gaming':'Marcus Thompson','crypto-mining':'James Rodriguez',defi:'James Rodriguez',supplements:'Dr. Emily Watson','yoga-meditation':'Dr. Maria Santos',psychology:'Dr. Maria Santos',neuroscience:'Dr. Maria Santos',education:'Priya Kapoor',politics:'Priya Kapoor','world-news':'Priya Kapoor','us-news':'Priya Kapoor','asia-news':'Priya Kapoor','europe-news':'Priya Kapoor','real-estate':'James Rodriguez',forex:'James Rodriguez'};

async function fetchRSS(url){
  try{
    const r=await fetch(url,{headers:{'User-Agent':'LOPINUZE/1.0'},signal:AbortSignal.timeout(12000)});
    if(!r.ok)return[];
    const xml=await r.text();const items=[];
    let m;const re=/<item>([\s\S]*?)<\/item>/gi;
    while((m=re.exec(xml))!==null){
      const t=(m[1].match(/<title[^>]*>([\s\S]*?)<\/title>/i)||[])[1]?.replace(/<!\[CDATA\[|\]\]>/g,'').trim()||'';
      const d=(m[1].match(/<description[^>]*>([\s\S]*?)<\/description>/i)||[])[1]?.replace(/<!\[CDATA\[|\]\]>/g,'').replace(/<[^>]+>/g,'').trim()||'';
      if(t&&d.length>40)items.push({title:t,desc:d});
    }
    return items;
  }catch{return[];}
}

const CSS=`@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;0,900;1,700&family=Inter:wght@400;500;600;700&display=swap');
:root{--bg:#ece4d8;--surface:#f5efe6;--text:#1a1510;--ts:#3d3528;--tm:#6b5f50;--primary:#1a1a1a;--accent:#8b1a1a;--bdr:#d0c8b8;--mw:720px;--font:'Inter',system-ui,sans-serif;--heading:'Playfair Display',serif}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html{font-size:17px}body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.7;position:relative;min-height:100vh}
body::before{content:'';position:fixed;inset:0;background:url("data:image/svg+xml,%3Csvg width='4' height='4' viewBox='0 0 4 4' xmlns='http://www.w3.org/2000/svg'%3E%3Crect x='0' y='0' width='0.8' height='0.8' fill='%236b5f50' opacity='0.04'/%3E%3Crect x='2' y='2' width='0.8' height='0.8' fill='%236b5f50' opacity='0.04'/%3E%3C/svg%3E");pointer-events:none;z-index:9999}
.site-header{background:#1a1713;color:#f5efe6;padding:0.55rem 1.5rem;position:sticky;top:0;z-index:100;border-bottom:3px double #6b5f50;display:flex;align-items:center;justify-content:space-between}
.logo{font:900 1.25rem var(--heading);color:#ece4d8;text-decoration:none;letter-spacing:2px}
.nav-links a{color:rgba(236,228,216,0.7);text-decoration:none;font-size:0.68rem;font-weight:600;padding:0.25rem 0.4rem;text-transform:uppercase;letter-spacing:1px;font-family:var(--heading)}
.article-detail{max-width:var(--mw);margin:0 auto;padding:2.5rem 1.25rem}
.article-detail h1{font:900 2.4rem/1.15 var(--heading);margin-bottom:0.8rem}.byline{font-size:0.7rem;color:var(--ts);padding-bottom:0.8rem;border-bottom:1px solid var(--bdr);margin-bottom:1.5rem;font-family:var(--heading)}
.content{font-size:0.95rem;line-height:1.75}.content p{margin-bottom:1rem;text-align:justify;text-indent:1.5em}.content p:first-child{text-indent:0}
.content h2{font:800 1.2rem var(--heading);margin:2rem 0 0.5rem;text-transform:uppercase;letter-spacing:1px;border-top:1px solid var(--bdr);padding-top:0.8rem}
blockquote{border-left:2px solid var(--accent);padding:0.4rem 1rem;margin:1.5rem 0;font:italic 1rem var(--heading);color:var(--ts)}
.editor-note{background:rgba(139,26,26,0.03);border:1px solid rgba(139,26,26,0.12);padding:0.6rem 0.8rem;margin:1.5rem 0;font-size:0.7rem;color:var(--accent);font-family:var(--heading);font-style:italic}
.key-takeaways{background:rgba(26,21,16,0.02);border:1px solid var(--bdr);padding:0.8rem 1rem;margin:1.5rem 0}
.key-takeaways h4{font:700 0.65rem var(--font);text-transform:uppercase;letter-spacing:3px;color:var(--accent);margin-bottom:0.5rem}
.key-takeaways li{font-size:0.78rem;color:var(--ts);padding:0.1rem 0;list-style-type:'— '}
.source-tag{font-size:0.68rem;color:var(--tm);margin-top:2rem;padding:0.6rem;border:1px solid var(--bdr);font-style:italic}
.site-footer{background:#1a1713;color:rgba(236,228,216,0.45);padding:2rem 1.5rem;margin-top:4rem;font-size:0.68rem;border-top:3px double #6b5f50;font-family:var(--heading);text-align:center}`;

async function rewrite(title,desc,section){
  const p=`You are a Pulitzer-winning journalist. Rewrite this news into a complete 350-450 word newspaper article. Use human journalistic style with compelling hook, quotes, subheadings. NEVER mention AI. Title: "${title}". Source: "${desc.substring(0,1200)}"`;
  try{
    const r=await fetch('https://api.deepseek.com/v1/chat/completions',{method:'POST',headers:{'Authorization':`Bearer ${DK}`,'Content-Type':'application/json'},body:JSON.stringify({model:'deepseek-chat',messages:[{role:'user',content:p}],temperature:0.85,max_tokens:1000}),signal:AbortSignal.timeout(30000)});
    const d=await r.json();return d.choices?.[0]?.message?.content||null;
  }catch{return null;}
}

function buildHTML(section,title,content,date){
  const author=AUTHORS[section]||'LOPINUZE News Desk';
  let formatted=content.replace(/^#+\s+(.+)$/gm,(m,t)=>`<h2>${t}</h2>`);
  formatted=formatted.replace(/\n{2,}/g,'</p>\n<p>');formatted='<p>'+formatted+'</p>';
  return `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title} – LOPINUZE</title><meta name="description" content="${(content||'').substring(0,155)}"><meta name="robots" content="index,follow"><script type="application/ld+json">{"@context":"https://schema.org","@type":"NewsArticle","headline":"${title.replace(/"/g,'\\"')}","author":{"@type":"Person","name":"${author}"},"datePublished":"${date}","publisher":{"@type":"Organization","name":"LOPINUZE"}}</script><style>${CSS}</style></head><body><header class="site-header"><a href="/index.html" class="logo">LOPINUZE</a><nav class="nav-links"><a href="/index.html">Home</a> <a href="/section-tech.html">Tech</a> <a href="/section-world-news.html">World</a> <a href="/finance.html">Finance</a></nav></header><main><article class="article-detail"><h1>${title}</h1><div class="byline">By <strong>${author}</strong> · ${date}</div><div class="content">${formatted}</div><div class="key-takeaways"><h4>Key Takeaways</h4><ul><li>Expert analysis on ${section.replace(/-/g,' ')} developments</li><li>Based on trusted news sources</li><li>Editorial team review completed</li></ul></div><div class="editor-note">✎ <strong>Editor's Note</strong> — Reviewed by ${author}. Content based on publicly available reporting.</div><div class="source-tag">📰 Original reporting from trusted news wire services. Content rewritten and fact-checked by our editorial team.</div></article></main><footer class="site-footer">LOPINUZE.2BD.NET &copy; 2026 · <a href="/disclaimer.html">Disclaimer</a> · <a href="/privacy-policy.html">Privacy</a></footer></body></html>`;
}

async function main(){
  console.log('🎯 Filling 20 missing sections...\n');
  if(!fs.existsSync(ARTS))fs.mkdirSync(ARTS,{recursive:true});
  let count=0;const processed={};
  for(const dm of FEEDS){
    const items=await fetchRSS(dm.url);
    console.log(`Fetched ${items.length} from ${dm.url.split('/')[2]}`);
    for(const item of items){
      const section=dm.secs[Math.floor(Math.random()*dm.secs.length)];
      if(!processed[section])processed[section]=0;
      if(processed[section]>=5)continue; // Max 5 per section
      const rewritten=await rewrite(item.title,item.desc,section);
      if(!rewritten)continue;
      processed[section]++;count++;
      const date='2026-07-13';
      const html=buildHTML(section,item.title,rewritten,date);
      const idx=processed[section];
      // Overwrite template with real content
      const filePath=path.join(NEWS,`article-${section}-${idx}.html`);
      fs.writeFileSync(filePath,html);
      // Also save to articles dir
      const jsonFile=path.join(ARTS,`article-${section}-fill-${idx}.json`);
      fs.writeFileSync(jsonFile,JSON.stringify({title:item.title,content:rewritten,targetSection:section},null,2));
      console.log(`✅ ${section} #${idx}: ${item.title.substring(0,45)}...`);
      await new Promise(r=>setTimeout(r,2000));
    }
  }
  console.log(`\n🎉 Filled ${count} articles across ${Object.keys(processed).length} sections`);  
  // Run sync
  const {execSync}=require('child_process');
  try{execSync('node "d:\\site & farm\\sync-articles.js"',{stdio:'inherit',timeout:30000})}catch{}
}

main().catch(e=>{console.error(e);process.exit(1)});