 * Zero images | Pure typography | SEO/GEO/AEO ready
 */
const fs=require('fs');const path=require('path');
const S='LOPINUZE';const D='LOPINUZE.2BD.NET';const O=path.join(__dirname,'news-empire');
const APP=12;const TAS=24;

const SECTIONS=[
  {s:'tech',n:'Technology',g:'Technology'},{s:'ai',n:'Artificial Intelligence',g:'Technology'},
  {s:'machine-learning',n:'Machine Learning',g:'Technology'},{s:'deep-learning',n:'Deep Learning',g:'Technology'},
  {s:'robotics',n:'Robotics',g:'Technology'},{s:'gaming',n:'Gaming',g:'Gaming'},
  {s:'esports',n:'Esports',g:'Gaming'},{s:'game-reviews',n:'Game Reviews',g:'Gaming'},
  {s:'game-development',n:'Game Development',g:'Gaming'},{s:'mobile-gaming',n:'Mobile Gaming',g:'Gaming'},
  {s:'vr-ar',n:'VR/AR',g:'Technology'},{s:'cybersecurity',n:'Cybersecurity',g:'Technology'},
  {s:'cloud-computing',n:'Cloud Computing',g:'Technology'},{s:'blockchain',n:'Blockchain',g:'Technology'},
  {s:'fintech',n:'FinTech',g:'Finance'},{s:'investing',n:'Investing',g:'Finance'},
  {s:'trading',n:'Trading',g:'Finance'},{s:'cryptocurrency',n:'Cryptocurrency',g:'Finance'},
  {s:'personal-finance',n:'Personal Finance',g:'Finance'},{s:'real-estate',n:'Real Estate',g:'Finance'},
  {s:'stock-market',n:'Stock Market',g:'Finance'},{s:'etfs',n:'ETFs',g:'Finance'},
  {s:'forex',n:'Forex',g:'Finance'},{s:'crypto-mining',n:'Crypto Mining',g:'Finance'},
  {s:'defi',n:'DeFi',g:'Finance'},{s:'nutrition',n:'Nutrition',g:'Health'},
  {s:'fitness',n:'Fitness',g:'Health'},{s:'mental-health',n:'Mental Health',g:'Health'},
  {s:'supplements',n:'Supplements',g:'Health'},{s:'weight-loss',n:'Weight Loss',g:'Health'},
  {s:'yoga-meditation',n:'Yoga/Meditation',g:'Health'},{s:'science',n:'Science',g:'Science'},
  {s:'astronomy',n:'Astronomy',g:'Science'},{s:'geology',n:'Geology',g:'Science'},
  {s:'environment',n:'Environment',g:'Science'},{s:'space',n:'Space',g:'Science'},
  {s:'physics',n:'Physics',g:'Science'},{s:'biology',n:'Biology',g:'Science'},
  {s:'chemistry',n:'Chemistry',g:'Science'},{s:'medicine',n:'Medicine',g:'Health'},
  {s:'psychology',n:'Psychology',g:'Health'},{s:'neuroscience',n:'Neuroscience',g:'Science'},
  {s:'climate',n:'Climate',g:'Science'},{s:'energy',n:'Energy',g:'Science'},
  {s:'education',n:'Education',g:'World'},{s:'politics',n:'Politics',g:'World'},
  {s:'world-news',n:'World News',g:'World'},{s:'us-news',n:'US News',g:'World'},
  {s:'asia-news',n:'Asia News',g:'World'},{s:'europe-news',n:'Europe News',g:'World'},
];
const GROUPS={Technology:['tech','ai','machine-learning','deep-learning','robotics','cybersecurity','cloud-computing','blockchain','vr-ar'],Gaming:['gaming','esports','game-reviews','game-development','mobile-gaming'],Finance:['fintech','investing','trading','cryptocurrency','personal-finance','real-estate','stock-market','etfs','forex','crypto-mining','defi'],Health:['nutrition','fitness','mental-health','supplements','weight-loss','yoga-meditation','medicine','psychology'],Science:['science','astronomy','geology','environment','space','physics','biology','chemistry','neuroscience','climate','energy'],World:['education','politics','world-news','us-news','asia-news','europe-news'],};
const AUTHORS=[
  {name:'Dr. Sarah Chen',title:'Technology Editor',av:'SC',s:['tech','ai','machine-learning','deep-learning','robotics']},
  {name:'James Rodriguez',title:'Finance Correspondent',av:'JR',s:['fintech','investing','trading','cryptocurrency','stock-market','etfs','forex','defi','crypto-mining','personal-finance','real-estate']},
  {name:'Dr. Emily Watson',title:'Health & Science Editor',av:'EW',s:['nutrition','fitness','mental-health','supplements','weight-loss','yoga-meditation','medicine','psychology','neuroscience','biology','chemistry']},
  {name:'Marcus Thompson',title:'Gaming & Esports Lead',av:'MT',s:['gaming','esports','game-reviews','game-development','mobile-gaming']},
  {name:'Priya Kapoor',title:'World Affairs Correspondent',av:'PK',s:['politics','world-news','us-news','asia-news','europe-news','climate','energy','education','environment']},
  {name:'Prof. David Kim',title:'Science & Space Editor',av:'DK',s:['science','astronomy','geology','space','physics']},
  {name:'Alex Rivera',title:'Cybersecurity Analyst',av:'AR',s:['cybersecurity','cloud-computing','blockchain','vr-ar']},
];
function getA(s){for(const a of AUTHORS)if(a.s.includes(s))return a;return{name:'LOPINUZE News Desk',title:'Staff Reporter',av:'LN'}}

const BROADSHEET_CSS=`@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap');
:root{--paper:#f4f1ea;--surface:#f9f6f0;--ink:#2b2b2b;--faded:#4a4a4a;--accent:#8b2e16;--bdr:#3a3a3a;--mw:1200px;--font:'Libre Baskerville',serif;--heading:'Playfair Display',serif;--body:'Libre Baskerville',serif}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html{font-size:16px;scroll-behavior:smooth}
body{font-family:var(--body);color:var(--ink);line-height:1.6;-webkit-font-smoothing:antialiased;display:flex;justify-content:center;min-height:100vh;position:relative;background-color:#f7f3eb;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E")}
body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse at 50% 30%,transparent 55%,rgba(180,160,130,0.04) 100%);pointer-events:none;z-index:9997}
.broadsheet{max-width:var(--mw);width:100%;padding:2rem;background:transparent}
.container{max-width:var(--mw);margin:0 auto;padding:0 2rem}
/* Header */
.site-header{background:var(--ink);color:var(--paper);padding:0.55rem 0;position:sticky;top:0;z-index:100;border-bottom:4px double var(--accent)}
.site-header .container{display:flex;align-items:center;justify-content:space-between;gap:1rem}
.logo{font:900 1.2rem var(--heading);color:var(--paper);text-decoration:none;letter-spacing:1px;text-transform:uppercase}
.nav-links{display:flex;gap:0;list-style:none;align-items:center}
.nav-links a{color:rgba(244,241,234,0.7);text-decoration:none;font:700 0.7rem var(--heading);padding:0.25rem 0.45rem;text-transform:uppercase;letter-spacing:1px}
.nav-links a:hover{color:var(--paper);text-decoration:underline}
.nav-links a.nav-active{color:var(--paper)}
.lang-switcher select{padding:0.2rem 0.3rem;border:1px solid rgba(244,241,234,0.2);background:var(--ink);color:var(--paper);font-size:0.65rem;cursor:pointer;font-family:var(--heading)}
/* Breaking bar */
.breaking-news-bar{background:var(--accent);color:var(--paper);padding:0.3rem 0;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;overflow:hidden;border-bottom:2px solid var(--ink)}
.breaking-news-bar .container{display:flex;gap:0.5rem;align-items:center}.breaking-label{background:rgba(244,241,234,0.15);padding:0.04rem 0.5rem;font-weight:900;font-size:0.62rem;letter-spacing:2px}
/* Masthead */
.masthead{text-align:center;border-bottom:4px double var(--ink);padding:2rem 2rem 1.2rem;margin-bottom:1.5rem}
.masthead h1{font:900 clamp(2.5rem,6vw,5rem) var(--heading);margin:0;letter-spacing:-2px;text-transform:uppercase;text-shadow:0.5px 0.5px 1px rgba(0,0,0,0.1)}
.masthead .subhead{display:flex;justify-content:space-between;border-top:1px solid var(--ink);border-bottom:1px solid var(--ink);padding:0.4rem 0;margin-top:0.8rem;font:700 0.72rem var(--heading);text-transform:uppercase;letter-spacing:1px;color:var(--faded)}
.trust-bar{display:flex;justify-content:space-around;padding:0.5rem 0;margin:1rem 2rem;border-top:1px solid var(--bdr);border-bottom:1px solid var(--bdr);font:700 0.65rem var(--heading);text-transform:uppercase;letter-spacing:1px;color:var(--faded)}
.trust-bar div{text-align:center}
.trust-bar .num{font:900 1.1rem var(--heading);color:var(--ink)}
/* Category groups */
.cat-group{margin:3rem 2rem 1.5rem;border-bottom:1px solid var(--bdr);padding-bottom:0.8rem}
.cat-group h2{font:900 1.1rem var(--heading);color:var(--ink);text-transform:uppercase;letter-spacing:2px;margin-bottom:0.3rem;border-bottom:3px double var(--bdr);display:inline-block;padding-bottom:0.3rem}
.section-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:0.35rem;padding:0.3rem 0}
.section-card{background:var(--surface);border:1px solid var(--bdr);padding:0.45rem 0.6rem;text-decoration:none;color:inherit;display:flex;align-items:center;gap:0.4rem;border-left:3px solid var(--accent);transition:all 0.15s}
.section-card:hover{background:#faf7f0;border-left-width:5px}
.section-card h3{font:700 0.8rem var(--heading);color:var(--ink);margin:0}
.section-card:hover h3{color:var(--accent)}
/* Section page */
.sec-header{padding:2.5rem 2rem 1rem;border-bottom:4px double var(--ink)}
.sec-header h1{font:900 2.8rem var(--heading);text-transform:uppercase;letter-spacing:-1px;margin-bottom:0.3rem}
.sec-header p{font:400 0.82rem var(--body);color:var(--faded);font-style:italic}
/* Article list */
.article-list{padding:1.5rem 2rem;display:flex;flex-direction:column;gap:0.5rem}
.article-card-newspaper{border-bottom:1px solid var(--bdr);padding:0.8rem 0;cursor:pointer;display:flex;gap:1rem;transition:all 0.15s}
.article-card-newspaper:hover{background:rgba(0,0,0,0.01)}
.article-card-newspaper .num-col{font:900 1.6rem var(--heading);color:var(--accent);min-width:36px;text-align:right;opacity:0.5}
.article-card-newspaper .content-col{flex:1}
.article-card-newspaper h3{font:700 1.05rem/1.2 var(--heading);margin-bottom:0.2rem}
.article-card-newspaper h3 a{color:var(--ink);text-decoration:none}.article-card-newspaper h3 a:hover{color:var(--accent)}
.article-card-newspaper .meta{font:400 0.65rem var(--heading);color:var(--faded)}
.article-card-newspaper p{font:400 0.78rem/1.5 var(--body);color:var(--faded);margin-top:0.3rem}
.pagination{display:flex;justify-content:center;gap:0.5rem;padding:1.5rem 2rem;border-top:1px solid var(--bdr)}
.pagination a,.pagination span{padding:0.3rem 1rem;border:1px solid var(--bdr);text-decoration:none;font:700 0.72rem var(--heading);color:var(--ink)}.pagination a:hover{background:var(--ink);color:var(--paper)}.pagination span{background:var(--ink);color:var(--paper)}
/* Article detail */
.article-detail{max-width:750px;margin:0 auto;padding:3rem 1.5rem}
.article-detail h1{font:900 2.8rem/1.1 var(--heading);letter-spacing:-1px;margin-bottom:1rem}
.article-detail .byline{font:700 0.72rem var(--heading);color:var(--faded);padding-bottom:0.8rem;border-bottom:3px double var(--bdr);margin-bottom:1.5rem;display:flex;gap:1rem;flex-wrap:wrap}
.article-detail .content{column-count:2;column-gap:2rem;column-rule:1px solid var(--faded);text-align:justify;line-height:1.7}
.article-detail .content p{margin-bottom:1rem}
.article-detail .content p:first-child::first-letter{font:900 3.5rem var(--heading);float:left;line-height:0.8;padding-right:0.4rem;padding-top:0.1rem}
.article-detail .content h2{font:900 1.3rem var(--heading);column-span:all;margin:2rem 0 0.5rem;text-transform:uppercase;letter-spacing:1px;border-top:2px solid var(--bdr);padding-top:0.8rem}
.article-detail .content h3{font:700 1rem var(--heading);margin:1.5rem 0 0.3rem}
.article-detail blockquote{border-left:2px solid var(--accent);padding:0.3rem 0.8rem;margin:1rem 0;font:italic 0.9rem var(--heading);color:var(--faded)}
.editor-note{background:rgba(139,46,22,0.04);border:1px solid rgba(139,46,22,0.15);padding:0.6rem 0.8rem;margin:1.5rem 0;font:italic 0.72rem var(--heading);color:var(--accent);display:flex;gap:0.5rem}
.key-takeaways{background:rgba(0,0,0,0.02);border:1px solid var(--bdr);padding:0.8rem 1rem;margin:1.5rem 0}
.key-takeaways h4{font:900 0.68rem var(--heading);text-transform:uppercase;letter-spacing:2px;color:var(--accent);margin-bottom:0.5rem}
.key-takeaways li{font-size:0.82rem;color:var(--faded);padding:0.1rem 0;list-style-type:'— ';list-style-position:inside}
.source-tag{font:italic 0.68rem var(--heading);color:var(--faded);margin-top:2rem;padding:0.6rem;border:1px solid var(--bdr)}.source-tag a{color:var(--accent)}
/* Footer */
.site-footer{background:var(--ink);color:rgba(244,241,234,0.5);padding:2rem;margin-top:4rem;font:700 0.68rem var(--heading);text-align:center;border-top:4px double var(--accent);letter-spacing:0.5px}.site-footer a{color:rgba(244,241,234,0.7);text-decoration:none;margin:0 0.6rem}.site-footer a:hover{color:var(--paper)}
@media(max-width:768px){.broadsheet{padding:1rem}.article-detail .content{column-count:1}.masthead h1{font-size:2rem}.section-grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}.article-card-newspaper{flex-direction:column;gap:0.3rem}}
@media(max-width:480px){.masthead .subhead{flex-direction:column;text-align:center;gap:0.3rem}.section-grid{grid-template-columns:1fr 1fr}.container{padding:0 0.8rem}}
`;

const LANG=`<div class="lang-switcher"><select onchange="if(this.value){window.location.href='https://translate.google.com/translate?hl='+this.value+'&sl=en&u='+encodeURIComponent(window.location.href)}"><option value="">🌐</option><option value="es">ES</option><option value="fr">FR</option><option value="de">DE</option><option value="it">IT</option><option value="pt">PT</option><option value="ru">RU</option><option value="zh">中文</option><option value="ja">日本語</option><option value="ko">한국어</option><option value="ar">العربية</option><option value="hi">हिन्दी</option></select></div>`;
const FOOTER=`<footer class="site-footer">${S} &copy; 2026 · ${D}<br><a href="/disclaimer.html">Disclaimer</a> · <a href="/privacy-policy.html">Privacy</a> · <a href="/terms.html">Terms</a> · <a href="/sitemap.xml">Sitemap</a></footer>`;
function today(){return new Date().toLocaleDateString('en-US',{weekday:'long',year:'numeric',month:'long',day:'numeric'});}

const ICONS={Technology:'●',Gaming:'◆',Finance:'■',Health:'▲',Science:'★',World:'○'};
function secIcon(g){return ICONS[g]||'●';}

function landing(){
let gs='';
for(const[gn,slugs]of Object.entries(GROUPS)){
const cards=slugs.map(s=>{const sec=SECTIONS.find(x=>x.s===s);if(!sec)return'';return'<a href="/section-'+s+'.html" class="section-card"><h3>'+secIcon(gn)+' '+sec.n+'</h3></a>'}).join('');
gs+='<div class="cat-group"><h2>'+gn+'</h2><div class="section-grid">'+cards+'</div></div>';
}
return'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+S+' – Global Newspaper | 50 Sections</title><meta name="description" content="'+S+' ('+D+') — Expert journalism across Technology, Gaming, Finance, Health, Science & World. Vintage newspaper aesthetic, modern reporting."><meta property="og:title" content="'+S+' – Global Newspaper"><meta property="og:description" content="50 sections. 100+ countries. Independent journalism."><meta property="og:type" content="website"><link rel="canonical" href="https://'+D+'/"><script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"'+S+'","url":"https://'+D+'/","potentialAction":{"@type":"SearchAction","target":"https://'+D+'/search?q={search_term_string}","query-input":"required name=search_term_string"}}</script><style>'+BROADSHEET_CSS+'</style></head><body><div class="broadsheet"><header class="site-header"><div class="container"><a href="/index.html" class="logo">'+S+'</a><nav><ul class="nav-links"><li><a href="/index.html" class="nav-active">Home</a></li><li><a href="/section-tech.html">Tech</a></li><li><a href="/section-ai.html">AI</a></li><li><a href="/section-gaming.html">Gaming</a></li><li><a href="/finance.html">Finance</a></li><li><a href="/section-world-news.html">World</a></li><li><a href="/section-science.html">Science</a></li></ul></nav>'+LANG+'</div></header><div class="breaking-news-bar"><div class="container"><span class="breaking-label">LATEST</span> '+today()+' — Markets surge · Global climate summit · NASA Mars habitat update</div></div><div class="masthead"><h1>LOPINUZE</h1><div class="subhead"><span>Vol. I — No. 1</span><span>'+today()+'</span><span>All the News That\'s Fit to Print</span></div></div><div class="trust-bar"><div><span class="num">50</span> Sections</div><div><span class="num">100+</span> Countries</div><div><span class="num">24/7</span> Live Wire</div><div><span class="num">Editorial</span> Review</div></div>'+gs+FOOTER+'</div></body></html>';
}

function financeHub(){
const slugs=GROUPS['Finance'];
const cards=slugs.map(s=>{const sec=SECTIONS.find(x=>x.s===s);if(!sec)return'';return'<a href="/section-'+s+'.html" class="section-card"><h3>'+secIcon('Finance')+' '+sec.n+'</h3></a>'}).join('');
return'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Finance – '+S+'</title><meta name="description" content="Markets, Crypto, Trading, Investing."><style>'+BROADSHEET_CSS+'</style></head><body><div class="broadsheet"><header class="site-header"><div class="container"><a href="/index.html" class="logo">'+S+'</a><nav><ul class="nav-links"><li><a href="/index.html">Home</a></li><li><a href="/section-tech.html">Tech</a></li><li><a href="/section-ai.html">AI</a></li><li><a href="/section-gaming.html">Gaming</a></li><li><a href="/finance.html" class="nav-active">Finance</a></li><li><a href="/section-world-news.html">World</a></li></ul></nav>'+LANG+'</div></header><div class="sec-header"><h1>Finance</h1><p>Markets, investing, cryptocurrency, and personal finance — expert coverage from our financial desk.</p></div><div class="section-grid" style="padding:1.5rem 2rem">'+cards+'</div>'+FOOTER+'</div></body></html>';
}

function sectionPage(sec,page=1){
const author=getA(sec.s);const tp=Math.ceil(TAS/APP);const start=(page-1)*APP+1;const end=Math.min(start+APP-1,TAS);
let arts='';
for(let i=start;i<=end;i++){
const titles=['Industry transformation accelerates','Global investment reaches record levels in Q2','Regulatory shifts create new growth opportunities','Market leaders announce breakthrough innovations','Research reveals surprising sector trends','Consumer behavior drives industry evolution','Policies reshape competitive landscape','International collaboration yields results','Startup ecosystem thrives amid conditions','Sustainability becomes corporate strategy','Expert panel discusses future at summit','New data challenges conventional wisdom'];
const t=titles[(i-1)%12];
arts+='<article class="article-card-newspaper" onclick="location.href=\'/article-'+sec.s+'-'+i+'.html\'"><div class="num-col">'+String(i).padStart(2,'0')+'</div><div class="content-col"><h3><a href="/article-'+sec.s+'-'+i+'.html">'+t+'</a></h3><div class="meta">By '+author.name+' · 2026-07-'+String(15-(i%14)).padStart(2,'0')+'</div><p>Comprehensive coverage from our editorial team on '+sec.n.toLowerCase()+'.</p></div></article>';
}
let pag='';if(tp>1){pag='<div class="pagination">';for(let p=1;p<=tp;p++)pag+=p===page?'<span>Page '+p+'</span>':'<a href="/section-'+sec.s+'-page-'+p+'.html">Page '+p+'</a>';pag+='</div>';}
return'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+sec.n+' – '+S+'</title><meta name="description" content="Latest '+sec.n.toLowerCase()+' news."><style>'+BROADSHEET_CSS+'</style></head><body><div class="broadsheet"><header class="site-header"><div class="container"><a href="/index.html" class="logo">'+S+'</a><nav><ul class="nav-links"><li><a href="/index.html">Home</a></li><li><a href="/section-tech.html">Tech</a></li><li><a href="/section-ai.html">AI</a></li><li><a href="/finance.html">Finance</a></li><li><a href="/section-world-news.html">World</a></li><li><a href="/section-science.html">Science</a></li></ul></nav>'+LANG+'</div></header><div class="sec-header"><h1>'+sec.n+'</h1><p>Expert analysis and latest coverage — '+TAS+' articles total'+(page>1?' · Page '+page+' of '+tp:'')+'.</p></div><div class="article-list">'+arts+'</div>'+pag+FOOTER+'</div></body></html>';
}

function articlePage(sec,num){
const author=getA(sec.s);
const titles=['Industry transformation accelerates','Global investment reaches record levels','Regulatory shifts open new opportunities','Market leaders announce innovations','Research reveals surprising sector trends','Consumer behavior drives evolution','Policies reshape competitive landscape','International collaboration yields success','Startup ecosystem thrives in new era','Sustainability becomes central strategy','Expert panel discusses future at summit','New data challenges conventional wisdom'];
const t=titles[(num-1)%12];const d='2026-07-'+String(15-(num%14)).padStart(2,'0');
const content='<p><strong>'+sec.n.toUpperCase()+'</strong> — The landscape of <strong>'+sec.n.toLowerCase()+'</strong> continues to evolve rapidly, with significant developments reshaping the industry. Analysts and experts are closely monitoring emerging trends that promise to transform the sector in the months ahead.</p><p>According to the latest data, the '+sec.n.toLowerCase()+' sector has experienced a <strong>47% increase in investment</strong> during the most recent quarter, reflecting growing confidence among stakeholders and signaling robust growth potential, market researchers indicate.</p><h2>Key Developments</h2><p>Several notable breakthroughs have been announced in recent weeks. Leading research institutions and major corporations have unveiled initiatives that could fundamentally alter the competitive dynamics of the industry, amid broader shifts in the global economic landscape.</p><p>"We are witnessing a fundamental transformation," said '+author.name+', '+author.title+' at '+S+'. "The convergence of multiple trends is creating opportunities that were difficult to imagine just a few years ago. Organizations that position themselves correctly now will be well-placed for sustained success."</p><blockquote>"The convergence of multiple trends is creating unprecedented opportunities. We are at the beginning of a new chapter in '+sec.n.toLowerCase()+'."<br>— <strong>'+author.name+'</strong>, '+author.title+'</blockquote><h2>Industry Implications</h2><p>The implications for businesses and consumers are significant. Companies that adapt swiftly to the changing landscape stand to gain substantial competitive advantages, while those that delay may find themselves facing considerable challenges in maintaining their market position.</p><p>Market analysts project that the '+sec.n.toLowerCase()+' sector could reach a valuation of <strong>$500 billion by 2030</strong>, driven by accelerating adoption across multiple verticals globally.</p><h2>Outlook</h2><p>Looking ahead, experts anticipate several key trends that will define the next phase of evolution. These include deeper integration with advanced systems, improved accessibility for organizations of all sizes, and the development of more robust regulatory frameworks designed to protect stakeholders and ensure sustainable growth.</p><p>For continued coverage of these developments, stay tuned to <strong>'+S+'</strong>. Our team of expert editors and correspondents provides comprehensive, fact-based reporting on the stories that matter most to our readers around the globe.</p>';
return'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+t+' – '+S+'</title><meta name="description" content="'+t+'"><meta name="robots" content="index,follow"><meta property="og:title" content="'+t+'"><meta property="og:type" content="article"><link rel="canonical" href="https://'+D+'/'+sec.s+'/article-'+num+'"><script type="application/ld+json">{"@context":"https://schema.org","@type":"NewsArticle","headline":"'+t+'","author":{"@type":"Person","name":"'+author.name+'"},"datePublished":"'+d+'","publisher":{"@type":"Organization","name":"'+S+'"}}</script><style>'+BROADSHEET_CSS+'</style></head><body><div class="broadsheet"><header class="site-header"><div class="container"><a href="/index.html" class="logo">'+S+'</a><nav><ul class="nav-links"><li><a href="/index.html">Home</a></li><li><a href="/section-'+sec.s+'.html">'+sec.n+'</a></li><li><a href="/finance.html">Finance</a></li><li><a href="/section-world-news.html">World</a></li></ul></nav>'+LANG+'</div></header><main><article class="article-detail"><h1>'+t+'</h1><div class="byline"><strong>'+author.name+'</strong> · '+author.title+' · 📅 '+d+'</div><div class="content">'+content+'</div><div class="key-takeaways"><h4>Key Takeaways</h4><ul><li>'+sec.n+' market projected to reach $500B by 2030</li><li>47% increase in sector investment this quarter</li><li>Experts recommend strategic positioning for growth</li></ul></div><div class="editor-note">✎ <strong>Editor\'s Note</strong> — Reviewed by '+author.name+'. Based on publicly available reporting.</div></article></main>'+FOOTER+'</div></body></html>';
}
const disc='<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Disclaimer – '+S+'</title><style>'+BROADSHEET_CSS+'body{padding:2rem}.site-header{margin:-2rem -2rem 2rem}h2{margin-top:2rem;font:900 1.2rem var(--heading);color:var(--accent)}p{color:var(--faded);margin-bottom:1rem}</style></head><body><div class="broadsheet"><header class="site-header"><a href="/index.html" class="logo">'+S+'</a></header><h1>Disclaimer</h1><p>Content aggregated and rewritten from publicly available sources. No accuracy guarantee.</p></div>'+FOOTER+'</body></html>';
const priv='<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Privacy – '+S+'</title><style>'+BROADSHEET_CSS+'body{padding:2rem}.site-header{margin:-2rem -2rem 2rem}h2{margin-top:2rem;font:900 1.2rem var(--heading);color:var(--accent)}p{color:var(--faded);margin-bottom:1rem}</style></head><body><div class="broadsheet"><header class="site-header"><a href="/index.html" class="logo">'+S+'</a></header><h1>Privacy Policy</h1><p>Minimal data collection. No personal information sold.</p></div>'+FOOTER+'</body></html>';
const terms='<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Terms – '+S+'</title><style>'+BROADSHEET_CSS+'body{padding:2rem}.site-header{margin:-2rem -2rem 2rem}h2{margin-top:2rem;font:900 1.2rem var(--heading);color:var(--accent)}p{color:var(--faded);margin-bottom:1rem}</style></head><body><div class="broadsheet"><header class="site-header"><a href="/index.html" class="logo">'+S+'</a></header><h1>Terms of Service</h1><p>Content provided "as is". No warranties.</p></div>'+FOOTER+'</body></html>';

// SEO files
const robots=`User-agent: *\nAllow: /\nSitemap: https://${D}/sitemap.xml`;
function sitemap(){
let xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
xml+='<url><loc>https://'+D+'/</loc><priority>1.0</priority><changefreq>hourly</changefreq></url>\n';
xml+='<url><loc>https://'+D+'/finance.html</loc><priority>0.9</priority></url>\n';
SECTIONS.forEach(s=>{xml+='<url><loc>https://'+D+'/section-'+s.s+'.html</loc><priority>0.8</priority><changefreq>hourly</changefreq></url>\n';});
SECTIONS.forEach(s=>{for(let i=1;i<=6;i++)xml+='<url><loc>https://'+D+'/article-'+s.s+'-'+i+'.html</loc><priority>0.6</priority></url>\n';});
xml+='</urlset>';return xml;
}

// Build
if(fs.existsSync(O))fs.rmSync(O,{recursive:true,force:true});fs.mkdirSync(O,{recursive:true});
fs.writeFileSync(path.join(O,'robots.txt'),robots);
fs.writeFileSync(path.join(O,'sitemap.xml'),sitemap());
console.log('✅ robots.txt + sitemap.xml');
fs.writeFileSync(path.join(O,'disclaimer.html'),disc);
fs.writeFileSync(path.join(O,'privacy-policy.html'),priv);
fs.writeFileSync(path.join(O,'terms.html'),terms);
fs.writeFileSync(path.join(O,'index.html'),landing());
fs.writeFileSync(path.join(O,'finance.html'),financeHub());
console.log('✅ Legal + Landing + Finance');
let sc=0;SECTIONS.forEach(sec=>{const tp=Math.ceil(TAS/APP);for(let p=1;p<=tp;p++){const fn=p===1?`section-${sec.s}.html`:`section-${sec.s}-page-${p}.html`;fs.writeFileSync(path.join(O,fn),sectionPage(sec,p));sc++;}});
console.log('✅ '+sc+' section pages');
let ac=0;SECTIONS.forEach(sec=>{for(let i=1;i<=TAS;i++){fs.writeFileSync(path.join(O,`article-${sec.s}-${i}.html`),articlePage(sec,i));ac++;}});
console.log('✅ '+ac+' article pages');
console.log('\n🎉 Vintage newspaper built! '+String(6+sc+ac)+' pages\n');