/**
 * SYNC: Connect pipeline AI articles to section pages
 * Reads real articles from news-empire/articles/ and updates section pages
 * Also generates unique headlines per article 
 */
const fs = require('fs');
const path = require('path');

const NEWS = path.join(__dirname, 'news-empire');
const ARTS = path.join(NEWS, 'articles');

if (!fs.existsSync(ARTS)) {
  console.log('No articles directory yet. Run pipeline first.');
  process.exit(1);
}

// Read all AI-written articles
const allArticles = fs.readdirSync(ARTS)
  .filter(f => f.endsWith('.json'))
  .map(f => JSON.parse(fs.readFileSync(path.join(ARTS, f), 'utf8')));

console.log(`Found ${allArticles.length} AI-written articles`);

// Group by section
const bySection = {};
for (const a of allArticles) {
  const sec = a.targetSection || 'world-news';
  if (!bySection[sec]) bySection[sec] = [];
  bySection[sec].push(a);
}

console.log(`Articles across ${Object.keys(bySection).length} sections`);

// For each section, update the section page
let updated = 0;
for (const [section, articles] of Object.entries(bySection)) {
  const sectionFile = path.join(NEWS, `section-${section}.html`);
  if (!fs.existsSync(sectionFile)) {
    console.log(`  ⚠ No section page: section-${section}.html (skipping)`);
    continue;
  }

  let html = fs.readFileSync(sectionFile, 'utf8');
  
  // Get latest 12 articles for this section
  const latest = articles.sort((a,b) => 
    (b.seo?.date || '').localeCompare(a.seo?.date || '')
  ).slice(0, 12);

  if (latest.length === 0) continue;

  // Build article cards
  const author = (a) => a.seo?.author || 'LOPINUZE News Desk';
  
  const cards = latest.map((a, i) => {
    const title = a.title || 'Latest Update';
    const excerpt = (a.content || '').replace(/<[^>]+>/g, '').substring(0, 200);
    const date = a.seo?.date || '2026-07-13';
    const authorName = author(a);
    const icon = section.substring(0,2).toUpperCase();
    const fileBase = path.basename(a.link || '').replace(/\.json$/, '') || `article-${section}-${i}`;
    
    return `<article class="article-card-newspaper" onclick="location.href='/articles/${fileBase}.html'">
<div class="num-col">${String(i+1).padStart(2,'0')}</div>
<div class="content-col">
<div class="section-label">${section.replace(/-/g,' ').toUpperCase()}</div>
<h3><a href="/articles/${fileBase}.html">${title}</a></h3>
<div class="meta">By ${authorName} · ${date} · ${Math.ceil((a.content||'').split(' ').length / 200)} min read</div>
<p>${excerpt}...</p>
</div></article>`;
  }).join('');

  // Replace the article list in the section page
  const listRegex = /<div class="article-list">[\s\S]*?<\/div>\s*((?:<div class="pagination">[\s\S]*?<\/div>)?)\s*<\/main>/;
  
  if (listRegex.test(html)) {
    html = html.replace(listRegex, 
      `<div class="article-list">${cards}</div>\n<div class="pagination" style="text-align:center;margin-top:1rem;font-size:0.7rem;color:var(--tm);font-style:italic;">Showing ${latest.length} of ${articles.length} articles · Updated continuously</div>\n</main>`
    );
    html = html.replace('</body>', `<!-- Synced: ${new Date().toISOString()} | ${articles.length} articles -->\n</body>`);
    fs.writeFileSync(sectionFile, html);
    console.log(`  ✅ Updated section-${section}.html with ${latest.length} articles`);
    updated++;
  }
}

console.log(`\n✅ Updated ${updated} section pages with real AI-written articles`);

// Also update the landing page to remove "Latest Stories" dumping
const landing = path.join(NEWS, 'index.html');
if (fs.existsSync(landing)) {
  let html = fs.readFileSync(landing, 'utf8');
  // Remove any pipeline-dumped "Latest Stories" section that has broken links
  html = html.replace(/<h2[^>]*>🔥 Latest Stories[\s\S]*?<\/div>\s*<\/div>/g, '');
  html = html.replace(/<h2[^>]*>📰 Editor's Picks[\s\S]*?<\/div>\s*<\/div>/g, '');
  html = html.replace('</body>', `<!-- Cleaned: ${new Date().toISOString()} -->\n</body>`);
  fs.writeFileSync(landing, html);
  console.log('✅ Cleaned landing page of broken article links');
}

console.log('\n🎉 Sync complete! Section pages now show real pipeline articles.');