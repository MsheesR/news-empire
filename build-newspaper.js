/**
 * LOPINUZE.2BD.NET — Vintage Newspaper Edition
 * Aged paper background, paper folds, ink bleed, custom SVG icons
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

const GROUPS={
Technology:['tech','ai','machine-learning','deep-learning','robotics','cybersecurity','cloud-computing','blockchain','vr-ar'],
Gaming:['gaming','esports','game-reviews','game-development','mobile-gaming'],
Finance:['fintech','investing','trading','cryptocurrency','personal-finance','real-estate','stock-market','etfs','forex','crypto-mining','defi'],
Health:['nutrition','fitness','mental-health','supplements','weight-loss','yoga-meditation','medicine','psychology'],
Science:['science','astronomy','geology','environment','space','physics','biology','chemistry','neuroscience','climate','energy'],
World:['education','politics','world-news','us-news','asia-news','europe-news'],
};

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

// Custom SVG icons per category group
const GI={
Technology:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="7" height="4" rx="0.5"/><rect x="14" y="4" width="7" height="4" rx="0.5"/><rect x="3" y="11" width="7" height="4" rx="0.5"/><rect x="14" y="11" width="7" height="4" rx="0.5"/><circle cx="10.5" cy="4.5" r="0.5"/><circle cx="10.5" cy="11.5" r="0.5"/><line x1="14" y1="15.5" x2="10.5" y2="20.5"/><line x1="7" y1="15.5" x2="10.5" y2="20.5"/></svg>',
Gaming:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="6" width="20" height="12" rx="3"/><line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/><circle cx="15" cy="11" r="1"/><circle cx="18" cy="11" r="1"/><circle cx="15" cy="14" r="1"/><circle cx="18" cy="14" r="1"/></svg>',
Finance:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/><polyline points="2,10 6,6 10,10"/></svg>',
Health:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 10h-6l-2 6-4-16-2 10H2"/></svg>',
Science:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="4"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4M5 5l3 3M16 16l3 3M19 5l-3 3M8 16l-3 3"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/></svg>',
World:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a14 14 0 004 10 14 14 0 01-4 10 14 14 0 01-4-10 14 14 0 014-10z"/></svg>'
};

// ══ VINTAGE NEWSPAPER CSS ══
const CSS=`@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;0,900;1,700&family=Inter:wght@400;500;600;700&display=swap');
:root{
--bg:#ece4d8;--surface:#f5efe6;--text:#1a1510;--ts:#3d3528;--tm:#6b5f50;
--primary:#1a1a1a;--accent:#8b1a1a;--bdr:#d0c8b8;--r:0;--rl:2px;
--mw:1060px;--font:'Inter',system-ui,sans-serif;--heading:'Playfair Display',serif;
--ink:rgba(26,21,16,0.12);
}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html{font-size:17px;scroll-behavior:smooth}
body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.7;-webkit-font-smoothing:antialiased;position:relative;min-height:100vh}
/* Paper texture grain */
body::before{content:'';position:fixed;inset:0;background:url("data:image/svg+xml,%3Csvg width='4' height='4' viewBox='0 0 4 4' xmlns='http://www.w3.org/2000/svg'%3E%3Crect x='0' y='0' width='0.8' height='0.8' fill='%236b5f50' opacity='0.04'/%3E%3Crect x='2' y='2' width='0.8' height='0.8' fill='%236b5f50' opacity='0.04'/%3E%3C/svg%3E");pointer-events:none;z-index:9999}
/* Darkened edge vignette */
body::after{content:'';position:fixed;inset:0;background:radial-gradient(ellipse at 50% 35%,transparent 55%,rgba(120,100,70,0.08) 100%);pointer-events:none;z-index:9998}
.container{max-width:var(--mw);margin:0 auto;padding:0 1.5rem}
/* Header */
.site-header{background:#1a1713;color:#f5efe6;padding:0.55rem 0;position:sticky;top:0;z-index:100;border-bottom:3px double #6b5f50;box-shadow:0 2px 12px rgba(0,0,0,0.3)}
.site-header .container{display:flex;align-items:center;justify-content:space-between;gap:1rem}
.logo{font:900 1.25rem var(--heading);color:#ece4d8;text-decoration:none;letter-spacing:2px;text-transform:uppercase}
.nav-links{display:flex;gap:0;list-style:none;align-items:center}
.nav-links a{color:rgba(236,228,216,0.7);text-decoration:none;font-size:0.68rem;font-weight:600;padding:0.28rem 0.45rem;text-transform:uppercase;letter-spacing:1px;font-family:var(--heading)}
.nav-links a:hover{color:#ece4d8}.nav-links a.nav-active{color:#ece4d8;border-bottom:1px solid var(--accent)}
.lang-switcher select{padding:0.22rem 0.3rem;border:1px solid rgba(236,228,216,0.2);background:#1a1713;color:#ece4d8;font-size:0.66rem;cursor:pointer;font-family:var(--font)}
.breaking-news-bar{background:var(--accent);color:#ece4d8;padding:0.25rem 0;font-size:0.68rem;font-weight:600;overflow:hidden;text-transform:uppercase;letter-spacing:1px}
.breaking-news-bar .container{display:flex;gap:0.5rem;align-items:center}.breaking-label{background:rgba(236,228,216,0.12);padding:0.04rem 0.45rem;font-weight:700;font-size:0.6rem;letter-spacing:2px}
/* Masthead */
.masthead{padding:4.5rem 0 2.5rem;text-align:center;border-bottom:3px double #1a1713;position:relative}
.masthead::after{content:'';position:absolute;bottom:-6px;left:0;width:100%;height:1px;background:#6b5f50}
.masthead h1{font:900 clamp(2.5rem,7vw,4.5rem) var(--heading);letter-spacing:5px;text-transform:uppercase;margin-bottom:0.6rem;line-height:1.1;text-shadow:0.5px 0.5px 2px var(--ink),0 0 1px rgba(0,0,0,0.05)}
.masthead .tagline{font:italic 400 0.82rem var(--font);color:var(--tm);max-width:500px;margin:0 auto 1rem;letter-spacing:0.5px}
.masthead .dateline{font:700 0.62rem var(--font);color:var(--tm);text-transform:uppercase;letter-spacing:3px;padding:0.7rem 0;border-top:1px solid var(--bdr)}
.trust-bar{background:var(--surface);border:1px solid var(--bdr);padding:0.6rem 0;margin:1.5rem 0;border-left:2px solid var(--accent);border-right:2px solid var(--accent)}
.trust-bar .container{display:flex;justify-content:space-around;flex-wrap:wrap;gap:1rem;text-align:center}
.trust-bar .num{font:700 0.95rem var(--heading);color:var(--text)}.trust-bar .lbl{font-size:0.6rem;color:var(--tm);text-transform:uppercase;letter-spacing:2px}
/* Category groups */
.cat-group{margin:3.5rem 0 1.5rem;border-bottom:1px solid var(--bdr);padding-bottom:1rem}
.cat-group h2{font:800 1rem var(--heading);color:var(--text);text-transform:uppercase;letter-spacing:2px;margin-bottom:0.3rem;display:flex;align-items:center;gap:0.4rem}
.cat-group h2 svg{color:var(--accent);flex-shrink:0}
.cat-group .cat-desc{font-size:0.68rem;color:var(--tm);margin-bottom:0.75rem;font-style:italic}
.section-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:0.35rem;padding:0.3rem 0}
.section-card{background:var(--surface);border:1px solid var(--bdr);padding:0.5rem 0.6rem;text-decoration:none;color:inherit;display:flex;align-items:center;gap:0.4rem;border-left:2px solid var(--accent);transition:all 0.15s}
.section-card:hover{background:#faf5ee;border-left-width:4px}
.section-card .si{width:16px;height:16px;display:inline-flex;align-items:center;justify-content:center;color:var(--ts);flex-shrink:0}
.section-card .si svg{width:14px;height:14px}
.section-card .sc{flex:1;min-width:0}
.section-card h3{font:600 0.76rem var(--font);color:var(--text);margin-bottom:0;line-height:1.3;letter-spacing:0.2px}
.section-card:hover h3{color:var(--accent)}
/* Section header */
.sec-header{padding:2.5rem 0 1.2rem;border-bottom:3px double #1a1713}
.sec-header .breadcrumb{font-size:0.62rem;color:var(--tm);text-transform:uppercase;letter-spacing:2px;margin-bottom:0.4rem}.sec-header a{color:var(--accent);text-decoration:none}.sec-header a:hover{text-decoration:underline}
.sec-header h1{font:900 2.4rem var(--heading);letter-spacing:1px;margin-bottom:0.3rem;text-transform:uppercase;text-shadow:0.5px 0.5px 2px var(--ink)}
.sec-header p{font-style:italic;color:var(--ts);font-size:0.82rem}
/* Article listing */
.article-list{display:grid;grid-template-columns:1fr;gap:0.4rem;padding:1.2rem 0}
.article-card-newspaper{background:var(--surface);border-bottom:1px solid var(--bdr);padding:0.8rem 0;transition:all 0.15s;cursor:pointer;display:flex;gap:1rem}
.article-card-newspaper:hover{background:rgba(0,0,0,0.006)}
.article-card-newspaper .num-col{font:700 1.6rem var(--heading);color:var(--accent);min-width:36px;text-align:right;line-height:1;opacity:0.45}
.article-card-newspaper .content-col{flex:1}
.article-card-newspaper .section-label{font-size:0.58rem;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:2px;margin-bottom:0.2rem}
.article-card-newspaper h3{font:700 0.98rem/1.25 var(--heading);margin-bottom:0.2rem;text-shadow:0.3px 0.3px 1px var(--ink)}
.article-card-newspaper h3 a{color:var(--text);text-decoration:none}.article-card-newspaper h3 a:hover{color:var(--accent)}
.article-card-newspaper .meta{font-size:0.63rem;color:var(--tm)}
.article-card-newspaper p{font:400 0.75rem/1.5 var(--font);color:var(--ts);margin-top:0.3rem}
/* Pagination */
.pagination{display:flex;justify-content:center;gap:0.35rem;margin:2rem 0;padding-top:1.5rem;border-top:1px solid var(--bdr)}
.pagination a,.pagination span{padding:0.28rem 0.75rem;border:1px solid var(--bdr);text-decoration:none;font-size:0.7rem;font-weight:600;font-family:var(--heading);color:var(--text)}.pagination a:hover{background:var(--text);color:var(--surface)}.pagination span{background:var(--text);color:var(--surface)}
/* Article detail */
.article-detail{max-width:700px;margin:0 auto;padding:3rem 1.25rem}
.article-detail .breadcrumb{font-size:0.65rem;color:var(--tm);text-transform:uppercase;letter-spacing:2px;margin-bottom:1rem}.article-detail .breadcrumb a{color:var(--accent);text-decoration:none}
.article-detail .sec-tag{font-size:0.6rem;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:3px;margin-bottom:0.6rem}
.article-detail h1{font:900 2.6rem/1.15 var(--heading);letter-spacing:-0.5px;margin-bottom:0.8rem;text-shadow:0.5px 0.5px 2px var(--ink)}
.article-detail .byline{font-size:0.7rem;color:var(--ts);padding-bottom:0.8rem;border-bottom:1px solid var(--bdr);margin-bottom:1.5rem;display:flex;gap:1rem;flex-wrap:wrap;font-family:var(--heading)}
.article-detail .content{font:400 0.92rem/1.75 var(--font);color:var(--text)}
.article-detail .content p{margin-bottom:1rem;text-align:justify;text-indent:1.5em}
.article-detail .content p:first-child{text-indent:0}
.article-detail .content h2{font:800 1.2rem var(--heading);margin:2.5rem 0 0.6rem;text-transform:uppercase;letter-spacing:1px;border-top:1px solid var(--bdr);padding-top:0.8rem;text-shadow:0.3px 0.3px 1px var(--ink)}
.article-detail .content h3{font:700 1rem var(--heading);margin:1.5rem 0 0.4rem}
.article-detail blockquote{border-left:2px solid var(--accent);padding:0.4rem 1rem;margin:1.5rem 0;font:italic 1rem var(--heading);color:var(--ts)}
.editor-note{background:rgba(139,26,26,0.03);border:1px solid rgba(139,26,26,0.12);padding:0.6rem 0.8rem;margin:1.5rem 0;font-size:0.7rem;color:var(--accent);display:flex;gap:0.5rem;font-style:italic;font-family:var(--heading)}
.key-takeaways{background:rgba(26,21,16,0.02);border:1px solid var(--bdr);padding:0.8rem 1rem;margin:1.5rem 0}.key-takeaways h4{font:700 0.65rem var(--font);text-transform:uppercase;letter-spacing:3px;color:var(--accent);margin-bottom:0.5rem}
.key-takeaways li{font-size:0.78rem;color:var(--ts);padding:0.1rem 0;list-style-position:inside;list-style-type:'— '}
.author-bio{background:var(--surface);border:1px solid var(--bdr);padding:1rem;margin:2rem 0;display:flex;gap:0.8rem;align-items:flex-start;border-left:2px solid var(--accent)}
.author-bio h4{font:700 0.8rem var(--heading);margin-bottom:0.1rem}.author-bio p{font-size:0.7rem;color:var(--ts)}
.rel-posts{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:0.5rem;margin-top:1.5rem}
.rel-posts a{border:1px solid var(--bdr);padding:0.6rem;text-decoration:none;color:inherit}.rel-posts a:hover{border-left:2px solid var(--accent)}.rel-posts h5{font:700 0.73rem var(--heading);margin-bottom:0.1rem}.rel-posts .meta{font-size:0.6rem;color:var(--tm)}
.source-tag{font-size:0.66rem;color:var(--tm);margin-top:2rem;padding:0.6rem;background:var(--surface);border:1px solid var(--bdr);font-style:italic;font-family:var(--heading)}.source-tag a{color:var(--accent)}
/* Footer */
.site-footer{background:#1a1713;color:rgba(236,228,216,0.42);padding:2rem 0;margin-top:5rem;font-size:0.68rem;border-top:3px double #6b5f50;font-family:var(--heading);letter-spacing:0.5px}.site-footer .container{display:flex;justify-content:space-between;flex-wrap:wrap;gap:1.5rem}.site-footer a{color:rgba(236,228,216,0.58);text-decoration:none}.site-footer a:hover{color:#ece4d8}
/* Responsive */
@media(max-width:768px){.masthead{padding:2.5rem 0 1.5rem}.masthead h1{font-size:1.8rem;letter-spacing:1px}.section-grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}.article-detail h1{font-size:1.8rem}.article-card-newspaper{flex-direction:column;gap:0.4rem}.article-card-newspaper .num-col{text-align:left;min-width:auto}.nav-links a{font-size:0.58rem;padding:0.2rem 0.22rem}}
@media(max-width:480px){.section-grid{grid-template-columns:1fr 1fr}.container{padding:0 0.8rem}.article-detail .content p{text-indent:0}}
`;

const LANG=`<div class="lang-switcher"><select onchange="if(this.value){window.location.href='https://translate.google.com/translate?hl='+this.value+'&sl=en&u='+encodeURIComponent(window.location.href)}"><option value="">🌐</option><option value="es">ES</option><option value="fr">FR</option><option value="de">DE</option><option value="it">IT</option><option value="pt">PT</option><option value="ru">RU</option><option value="zh-CN">中文</option><option value="ja">日本語</option><option value="ko">한국어</option><option value="ar">العربية</option><option value="hi">हिन्दी</option></select></div>`;

const FOOTER=`<footer class="site-footer"><div class="container"><div><div class="footer-brand">${S}</div><div>${D} &copy; 2026</div></div><div><a href="/index.html">Home</a> · <a href="/section-world-news.html">World</a> · <a href="/finance.html">Finance</a><br><a href="/disclaimer.html">Disclaimer</a> · <a href="/privacy-policy.html">Privacy</a> · <a href="/terms.html">Terms</a></div></div></footer>`;
function today(){const d=new Date();return d.toLocaleDateString('en-US',{weekday:'long',year:'numeric',month:'long',day:'numeric'});}
function icon(g){return GI[g]||GI.Technology;}

// Landing
function landing(){
let gs='';
for(const[gn,slugs]of Object.entries(GROUPS)){
const cards=slugs.map(s=>{const sec=SECTIONS.find(x=>x.s===s);if(!sec)return'';return'<a href="/section-'+s+'.html" class="section-card"><span class="si">'+icon(sec.g)+'</span><div class="sc"><h3>'+sec.n+'</h3></div></a>'}).join('');
gs+='<div class="cat-group"><h2>'+icon(gn)+' '+gn+'</h2><div class="cat-desc">'+slugs.length+' sections</div><div class="section-grid">'+cards+'</div></div>';
}
return'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+S+' – Global Newspaper | 50 Sections</title><meta name="description" content="'+S+' — Your global newspaper. Expert journalism across Technology, Gaming, Finance, Health, Science & World."><style>'+CSS+'</style></head><body><header class="site-header"><div class="container"><a href="/index.html" class="logo">'+S+'</a><nav><ul class="nav-links"><li><a href="/index.html" class="nav-active">Home</a></li><li><a href="/section-tech.html">Tech</a></li><li><a href="/section-ai.html">AI</a></li><li><a href="/section-gaming.html">Gaming</a></li><li><a href="/finance.html">Finance</a></li><li><a href="/section-world-news.html">World</a></li><li><a href="/section-science.html">Science</a></li></ul></nav>'+LANG+'</div></header><div class="breaking-news-bar"><div class="container"><span class="breaking-label">LATEST</span><span class="breaking-text">'+today()+' — Global markets surge — EPA clean energy targets — NASA Mars habitat unveiled</span></div></div><section class="masthead"><div class="container"><h1>LOPINUZE</h1><div class="tagline">The Global Newspaper — 50 Sections · 100+ Countries · Independent Journalism</div><div class="dateline">'+today()+' · Edition 1 · All the News That\'s Fit to Print</div></div></section><div class="trust-bar"><div class="container"><div><div class="num">50+</div><div class="lbl">Sections</div></div><div><div class="num">100+</div><div class="lbl">Countries</div></div><div><div class="num">24/7</div><div class="lbl">Live Wire</div></div><div><div class="num">Editorial</div><div class="lbl">Review</div></div></div></div><main class="container">'+gs+'</main>'+FOOTER+'</body></html>';
}

// Finance hub
function financeHub(){
const slugs=GROUPS['Finance'];
const cards=slugs.map(s=>{const sec=SECTIONS.find(x=>x.s===s);if(!sec)return'';return'<a href="/section-'+s+'.html" class="section-card"><span class="si">'+icon('Finance')+'</span><div class="sc"><h3>'+sec.n+'</h3></div></a>'}).join('');
return'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Finance – '+S+'</title><meta name="description" content="Markets, Crypto, Trading, Investing."><style>'+CSS+'</style></head><body><header class="site-header"><div class="container"><a href="/index.html" class="logo">'+S+'</a><nav><ul class="nav-links"><li><a href="/index.html">Home</a></li><li><a href="/section-tech.html">Tech</a></li><li><a href="/section-ai.html">AI</a></li><li><a href="/section-gaming.html">Gaming</a></li><li><a href="/finance.html" class="nav-active">Finance</a></li><li><a href="/section-world-news.html">World</a></li></ul></nav>'+LANG+'</div></header><div class="breaking-news-bar"><div class="container"><span class="breaking-label">MARKETS</span><span class="breaking-text">S&P 500 record — Bitcoin surges — Fed signals shift</span></div></div><div class="sec-header container"><div class="breadcrumb"><a href="/index.html">Home</a> &rsaquo; Finance</div><h1>Finance</h1><p>Markets, investing, cryptocurrency, and personal finance — expert coverage from our financial desk.</p></div><main class="container"><div class="section-grid">'+cards+'</div></main>'+FOOTER+'</body></html>';
}

// Section page
function sectionPage(sec,page=1){
const author=getA(sec.s);
const tp=Math.ceil(TAS/APP);
const start=(page-1)*APP+1;
const end=Math.min(start+APP-1,TAS);
let arts='';
for(let i=start;i<=end;i++){
const titles=['Industry transformation accelerates as new technologies emerge','Global investment reaches record levels in Q2','Regulatory shifts create new growth opportunities','Market leaders announce breakthrough innovations','Research reveals surprising sector trends','Consumer behavior drives industry evolution','Policies reshape the competitive landscape','International collaboration yields results','Startup ecosystem thrives amid conditions','Sustainability becomes corporate strategy','Expert panel discusses future outlook','New data challenges conventional wisdom'];
const t=titles[(i-1)%12];
const d='2026-07-'+String(15-(i%14)).padStart(2,'0');
arts+='<article class="article-card-newspaper" onclick="location.href=\'/article-'+sec.s+'-'+i+'.html\'"><div class="num-col">'+String(i).padStart(2,'0')+'</div><div class="content-col"><div class="section-label">'+sec.n+'</div><h3><a href="/article-'+sec.s+'-'+i+'.html">'+t+'</a></h3><div class="meta">By '+author.name+' · '+d+' · '+String(Math.floor(Math.random()*6)+3)+' min read</div><p>Comprehensive coverage from our editorial team. In-depth reporting, expert analysis, and data-driven perspectives on '+sec.n.toLowerCase()+'.</p></div></article>';
}
let pag='';
if(tp>1){pag='<div class="pagination">';for(let p=1;p<=tp;p++){if(p===page)pag+='<span>Page '+p+'</span>';else pag+='<a href="/section-'+sec.s+'-page-'+p+'.html">Page '+p+'</a>';}pag+='</div>';}
return'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+sec.n+' – '+S+(page>1?' Page '+page:'')+'</title><meta name="description" content="Latest '+sec.n.toLowerCase()+' news and coverage.'+(page>1?' Page '+page+' of '+tp+'.':'')+'"><style>'+CSS+'</style></head><body><header class="site-header"><div class="container"><a href="/index.html" class="logo">'+S+'</a><nav><ul class="nav-links"><li><a href="/index.html">Home</a></li><li><a href="/section-tech.html">Tech</a></li><li><a href="/section-ai.html">AI</a></li><li><a href="/finance.html">Finance</a></li><li><a href="/section-world-news.html">World</a></li><li><a href="/section-science.html">Science</a></li></ul></nav>'+LANG+'</div></header><div class="breaking-news-bar"><div class="container"><span class="breaking-label">'+sec.n.toUpperCase()+'</span><span class="breaking-text">Latest developments — '+today()+'</span></div></div><div class="sec-header container"><div class="breadcrumb"><a href="/index.html">Home</a> &rsaquo; '+sec.n+(page>1?' &rsaquo; Page '+page:'')+'</div><h1>'+sec.n+'</h1><p>Expert analysis, latest coverage, and comprehensive reporting '+(page>1?'— Page '+page+' of '+tp:'')+' — '+TAS+' articles total.</p></div><main class="container"><div class="article-list">'+arts+'</div>'+pag+'</main>'+FOOTER+'</body></html>';
}

// Article page
function articlePage(sec,num){
const author=getA(sec.s);
const titles=['Industry transformation accelerates','Global investment reaches record levels','Regulatory shifts open new opportunities','Market leaders announce innovations','Research reveals surprising sector trends','Consumer behavior drives evolution','Policies reshape competitive landscape','International collaboration yields success','Startup ecosystem thrives in new era','Sustainability becomes central strategy','Expert panel discusses future at summit','New data challenges conventional wisdom'];
const t=titles[(num-1)%12];
const d='2026-07-'+String(15-(num%14)).padStart(2,'0');
const rt=Math.floor(Math.random()*6)+3;
const content='<p><strong>'+sec.n.toUpperCase()+'</strong> — The landscape of <strong>'+sec.n.toLowerCase()+'</strong> continues to evolve at a rapid pace, with significant developments reshaping the industry. Analysts and experts are closely monitoring emerging trends that promise to transform the sector in the months ahead.</p><p>According to the latest data, the '+sec.n.toLowerCase()+' sector has experienced a <strong>47% increase in investment</strong> during the most recent quarter. This surge reflects growing confidence among stakeholders and signals robust growth potential, market researchers indicate.</p><h2>Key Developments</h2><p>Several notable breakthroughs have been announced in recent weeks. Leading research institutions and major corporations have unveiled initiatives that could fundamentally alter the competitive dynamics of the industry, amid broader shifts in the global economic landscape.</p><p>"We are witnessing a fundamental transformation," said '+author.name+', '+author.title+' at '+S+'. "The convergence of multiple trends is creating opportunities that were difficult to imagine just a few years ago. Organizations that position themselves correctly now will be well-placed for sustained success."</p><blockquote>"The convergence of multiple trends is creating unprecedented opportunities. We are at the beginning of a new chapter in '+sec.n.toLowerCase()+'."<br>— <strong>'+author.name+'</strong>, '+author.title+'</blockquote><h2>Industry Implications</h2><p>The implications for businesses and consumers are significant. Companies that adapt swiftly to the changing landscape stand to gain substantial competitive advantages, while those that delay may find themselves facing considerable challenges in maintaining their market position.</p><p>Market analysts project that the '+sec.n.toLowerCase()+' sector could reach a valuation of <strong>$500 billion by 2030</strong>, driven by accelerating adoption across healthcare, finance, manufacturing, consumer applications, and other key verticals globally.</p><h2>Outlook</h2><p>Looking ahead, experts anticipate several key trends that will define the next phase of evolution. These include deeper integration with advanced systems, improved accessibility for organizations of all sizes, and the development of more robust regulatory frameworks designed to protect stakeholders and ensure sustainable growth across the sector.</p><p>For continued coverage of these developments, stay tuned to <strong>'+S+'</strong>. Our team of expert editors and correspondents provides comprehensive, fact-based reporting on the stories that matter most to our readers around the globe.</p>';
return'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+t+' – '+S+'</title><meta name="description" content="'+t+'. Expert analysis by '+author.name+', '+author.title+' at '+S+'."><meta name="author" content="'+author.name+'"><meta name="robots" content="index,follow"><meta property="og:title" content="'+t+'"><meta property="og:type" content="article"><link rel="canonical" href="https://'+D+'/'+sec.s+'/article-'+num+'"><script type="application/ld+json">{"@context":"https://schema.org","@type":"NewsArticle","headline":"'+t+'","author":{"@type":"Person","name":"'+author.name+'"},"datePublished":"'+d+'","publisher":{"@type":"Organization","name":"'+S+'"}}</script><style>'+CSS+'</style></head><body><header class="site-header"><div class="container"><a href="/index.html" class="logo">'+S+'</a><nav><ul class="nav-links"><li><a href="/index.html">Home</a></li><li><a href="/section-'+sec.s+'.html">'+sec.n+'</a></li><li><a href="/finance.html">Finance</a></li><li><a href="/section-world-news.html">World</a></li></ul></nav>'+LANG+'</div></header><div class="breaking-news-bar"><div class="container"><span class="breaking-label">'+sec.n.toUpperCase()+'</span><span class="breaking-text">'+t+' — '+today()+'</span></div></div><main><article class="article-detail"><div class="breadcrumb"><a href="/index.html">Home</a> &rsaquo; <a href="/section-'+sec.s+'.html">'+sec.n+'</a> &rsaquo; Article</div><div class="sec-tag">'+sec.n+' · ANALYSIS</div><h1>'+t+'</h1><div class="byline"><div class="author-box"><div class="author-avatar">'+author.av+'</div><div><strong>'+author.name+'</strong><br><span style="font-size:0.65rem;color:var(--tm)">'+author.title+'</span></div></div><span>📅 '+d+'</span><span>⏱ '+rt+' min read</span></div><div class="content">'+content+'</div><div class="key-takeaways"><h4>Key Takeaways</h4><ul><li>'+sec.n+' market projected to reach $500B by 2030</li><li>47% increase in sector investment this quarter</li><li>Converging trends creating unprecedented opportunities</li><li>Experts recommend strategic positioning for sustained growth</li></ul></div><div class="editor-note"><span>✎</span><div><strong>Editor\'s Note</strong> — Reviewed by '+author.name+', '+author.title+'. Based on publicly available reporting from trusted news sources and wire services. Last edited: '+d+'.</div></div><div class="author-bio"><div class="author-avatar" style="width:44px;height:44px;font-size:0.85rem">'+author.av+'</div><div><h4>'+author.name+'</h4><p style="font-size:0.68rem;color:var(--tm);margin-bottom:0.15rem">'+author.title+'</p><p style="font-size:0.75rem">Experienced journalist and analyst covering '+sec.n.toLowerCase()+' developments, industry analysis, and breaking news for '+S+'.</p></div></div></article></main>'+FOOTER+'</body></html>';
}

// Legal
const disc='<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Disclaimer – '+S+'</title><style>'+CSS+'body{padding:2rem}h2{margin-top:2rem;font:800 1.2rem var(--heading);color:var(--accent)}p{color:var(--ts);margin-bottom:1rem}.site-header{margin:-2rem -2rem 2rem}</style></head><body><header class="site-header"><a href="/index.html" class="logo">'+S+'</a></header><div class="container"><h1>Disclaimer & Legal Notice</h1><p><strong>Last Updated: July 13, 2026</strong></p><h2>Content Sources</h2><p>'+S+' aggregates and rewrites news from publicly available sources. We do not guarantee accuracy or completeness. Readers should independently verify facts before relying on any information.</p><h2>Liability</h2><p>'+S+' shall not be liable for damages arising from errors, omissions, or reliance on content. This website is for informational purposes only and does not constitute professional advice.</p></div>'+FOOTER+'</body></html>';
const priv='<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Privacy – '+S+'</title><style>'+CSS+'body{padding:2rem}h2{margin-top:2rem;font:800 1.2rem var(--heading);color:var(--accent)}p{color:var(--ts);margin-bottom:1rem}.site-header{margin:-2rem -2rem 2rem}</style></head><body><header class="site-header"><a href="/index.html" class="logo">'+S+'</a></header><div class="container"><h1>Privacy Policy</h1><p>Minimal data collection for site functionality. No personal information is sold. GDPR/CCPA rights apply.</p></div>'+FOOTER+'</body></html>';
const terms='<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Terms – '+S+'</title><style>'+CSS+'body{padding:2rem}h2{margin-top:2rem;font:800 1.2rem var(--heading);color:var(--accent)}p{color:var(--ts);margin-bottom:1rem}.site-header{margin:-2rem -2rem 2rem}</style></head><body><header class="site-header"><a href="/index.html" class="logo">'+S+'</a></header><div class="container"><h1>Terms of Service</h1><p>By using this website you agree to these terms. Content is provided "as is" without warranties.</p></div>'+FOOTER+'</body></html>';

// ══ WRITE ══
if(fs.existsSync(O))fs.rmSync(O,{recursive:true,force:true});fs.mkdirSync(O,{recursive:true});
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
console.log('\n🎉 Complete! '+String(3+1+1+sc+ac)+' vintage newspaper pages.');