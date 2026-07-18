const fs = require('fs');
const path = require('path');

let code = fs.readFileSync('pipeline.js', 'utf-8');

// 1. Fix runPipeline to save actualFile in articleData
code = code.replace(
  `    const jsonFile = path.join(articlesDir, \`article-\${raw.targetSection}-\${Date.now()}.json\`);
    fs.writeFileSync(jsonFile, JSON.stringify(articleData, null, 2));

    // Save as HTML
    const htmlFile = jsonFile.replace('.json', '.html');`,
  `    const jsonFile = path.join(articlesDir, \`article-\${raw.targetSection}-\${Date.now()}.json\`);
    
    // Save as HTML
    const htmlFile = jsonFile.replace('.json', '.html');
    articleData.actualFile = path.basename(htmlFile); // ADDED SO WE KNOW THE FILE NAME
    fs.writeFileSync(jsonFile, JSON.stringify(articleData, null, 2));`
);


// 2. Fix updateSectionPage to actually insert the articles and save the file
const sectionRegex = /function updateSectionPage\([\s\S]*?\n\}/;
code = code.replace(sectionRegex, `function updateSectionPage(section, articles) {
  const sectionFile = path.join(NEWS_DIR, \`section-\${section}.html\`);
  if (!fs.existsSync(sectionFile)) return;

  try {
    let html = fs.readFileSync(sectionFile, 'utf-8');
    const articlesDir = path.join(NEWS_DIR, 'articles');
    let savedFiles = [];
    if (fs.existsSync(articlesDir)) {
      savedFiles = fs.readdirSync(articlesDir)
        .filter(f => f.startsWith(\`article-\${section}-\`) && f.endsWith('.html'))
        .sort().reverse().slice(0, 10); // Show up to 10 latest
    }

    const articleCards = articles.slice(0, 10).map((a, i) => {
      const seo = a.seo || {};
      const actualFile = a.actualFile || savedFiles[i];
      return \`<article class="article-card" onclick="location.href='articles/\${actualFile}'">
<img class="card-img" src="https://images.unsplash.com/photo-1504711434969-e33886168d6c?w=800&h=450&fit=crop" alt="\${a.title}" loading="lazy" />
<div class="card-body"><span class="card-tag">\${seo.category || 'News'}</span>
<h3><a href="articles/\${actualFile}">\${a.title}</a></h3>
<div class="meta"><span class="author-avatar">\${(seo.author||'N')[0]}</span> \${seo.author || 'Staff'} · \${seo.date || ''}</div>
<p>\${a.content.substring(0, 150).replace(/<[^>]+>/g,'')}...</p></div></article>\`;
    }).join('');

    // Replace the contents inside <div class="article-list">...</div>
    const listStart = html.indexOf('<div class="article-list">');
    const listEnd = html.indexOf('</div></main>');
    if (listStart !== -1 && listEnd !== -1) {
      html = html.substring(0, listStart + 26) + articleCards + html.substring(listEnd);
      fs.writeFileSync(sectionFile, html);
      log(\`✅ Updated section page: \${section}\`);
    } else {
      log(\`Could not find article-list container in section-\${section}.html\`, 'WARN');
    }
  } catch (e) {
    log(\`Failed to update section page \${section}: \${e.message}\`, 'WARN');
  }
}`);


// 3. Fix updateLandingPage to correctly insert recent articles and use actualFile
const landingRegex = /function updateLandingPage\([\s\S]*?\n\}/;
code = code.replace(landingRegex, `function updateLandingPage(recentArticles) {
  const landingFile = path.join(NEWS_DIR, 'index.html');
  if (!fs.existsSync(landingFile) || recentArticles.length === 0) return;

  try {
    let html = fs.readFileSync(landingFile, 'utf-8');
    const articleCards = recentArticles.map(a => {
      const seo = a.seo || {};
      return \`<article class="article-card" onclick="location.href='/articles/\${a.actualFile}'">
<img class="card-img" src="https://images.unsplash.com/photo-1504711434969-e33886168d6c?w=800&h=450&fit=crop" alt="\${a.title}" loading="lazy" />
<div class="card-body"><span class="card-tag">LATEST</span>
<h3><a href="/articles/\${a.actualFile}">\${a.title}</a></h3>
<div class="meta"><span class="author-avatar">\${(seo.author||'N')[0]}</span> \${seo.author || 'Staff'} · \${seo.date || ''}</div>
<p>\${a.content.substring(0, 120).replace(/<[^>]+>/g,'')}...</p></div></article>\`;
    }).join('');

    const articlesSection = \`
<div class="cat-group"><h2>🔥 Latest Breaking News</h2>
<p style="color:var(--tm);margin-bottom:1.5rem;font-size:0.9rem;">Updated \${new Date().toLocaleString()}</p>
<div class="section-grid">\${articleCards}</div></div>\`;

    // Try to remove old "Latest Breaking News" block if it exists to avoid duplicates
    if (html.includes('🔥 Latest Breaking News')) {
      html = html.replace(/<div class="cat-group"><h2>🔥 Latest Breaking News[\s\S]*?<\/div><\/div>/, articlesSection);
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
    log(\`Failed to update landing page: \${e.message}\`, 'WARN');
  }
}`);

fs.writeFileSync('pipeline.js', code);
console.log('Fixed pipeline.js!');
