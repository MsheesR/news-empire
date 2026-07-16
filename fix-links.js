/**
 * LOPINUZE - Fix broken nav links, article links, and image prompts
 */
const fs = require('fs');
const path = require('path');

const NEWS_DIR = path.join(__dirname, 'news-empire');

// ─── Fix 1: All header nav links must use absolute paths ───
function fixHeaderNavLinks() {
  const allFiles = [];
  function collect(dir) {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if (e.isDirectory()) collect(path.join(dir, e.name));
      else if (e.name.endsWith('.html')) allFiles.push(path.join(dir, e.name));
    }
  }
  collect(NEWS_DIR);

  let count = 0;
  for (const filePath of allFiles) {
    let html = fs.readFileSync(filePath, 'utf-8');
    let changed = false;

    // Fix nav links - make them root-relative
    // Pattern: <a href="index.html"> → <a href="/index.html">
    // Pattern: <a href="section-tech.html"> → <a href="/section-tech.html">
    // Pattern: <a href="finance.html"> → <a href="/finance.html">
    
    const navReplacements = [
      [/href="index\.html"/g, 'href="/index.html"'],
      [/href="section-tech\.html"/g, 'href="/section-tech.html"'],
      [/href="section-ai\.html"/g, 'href="/section-ai.html"'],
      [/href="section-gaming\.html"/g, 'href="/section-gaming.html"'],
      [/href="finance\.html"/g, 'href="/finance.html"'],
      [/href="section-world-news\.html"/g, 'href="/section-world-news.html"'],
      [/href="section-science\.html"/g, 'href="/section-science.html"'],
    ];

    for (const [pattern, replacement] of navReplacements) {
      if (pattern.test(html)) {
        html = html.replace(pattern, replacement);
        changed = true;
      }
    }

    if (changed) {
      fs.writeFileSync(filePath, html);
      count++;
    }
  }
  console.log(`✅ Fixed header nav links in ${count} files`);
}

// ─── Fix 2: Landing page article links must point to real files ───
function fixLandingPageLinks() {
  const landingFile = path.join(NEWS_DIR, 'index.html');
  if (!fs.existsSync(landingFile)) return;

  const articlesDir_abs = path.join(NEWS_DIR, 'articles');
  let html = fs.readFileSync(landingFile, 'utf-8');

  // Fix all links pointing to non-existent "latest" files
  html = html.replace(/href="articles\/article-([a-z-]+)-latest\.html"/g, (match, section) => {
    if (fs.existsSync(articlesDir_abs)) {
      const files = fs.readdirSync(articlesDir_abs)
        .filter(f => f.startsWith(`article-${section}-`) && f.endsWith('.html'))
        .sort()
        .reverse();
      if (files.length > 0) {
        return `href="/articles/${files[0]}"`;
      }
    }
    // Fallback: point to section page
    return `href="/section-${section}.html"`;
  });

  // Fix onclick handlers too
  html = html.replace(/onclick="location\.href='articles\/article-([a-z-]+)-latest\.html'"/g, (match, section) => {
    if (fs.existsSync(articlesDir_abs)) {
      const files = fs.readdirSync(articlesDir_abs)
        .filter(f => f.startsWith(`article-${section}-`) && f.endsWith('.html'))
        .sort()
        .reverse();
      if (files.length > 0) {
        return `onclick="location.href='/articles/${files[0]}'"`;
      }
    }
    return `onclick="location.href='/section-${section}.html'"`;
  });

  fs.writeFileSync(landingFile, html);
  console.log('✅ Fixed landing page article links');
}

// ─── Fix 3: Fix Pollinations image prompt to avoid human faces ───
function fixImagePrompts() {
  const allFiles = [];
  function collect(dir) {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if (e.isDirectory()) collect(path.join(dir, e.name));
      else if (e.name.endsWith('.html')) allFiles.push(path.join(dir, e.name));
    }
  }
  collect(NEWS_DIR);

  let count = 0;
  for (const filePath of allFiles) {
    let html = fs.readFileSync(filePath, 'utf-8');
    if (!html.includes('pollinations.ai')) continue;

    // Fix the prompt to generate abstract/news images without human faces
    const oldPrompt = /journalistic\+photo\+professional/g;
    const newPrompt = 'abstract+news+illustration+technology+clean+minimal+no+faces+no+people+no+humans+diagram+chart+data+visualization';

    if (oldPrompt.test(html)) {
      html = html.replace(oldPrompt, newPrompt);
      fs.writeFileSync(filePath, html);
      count++;
    }
  }
  console.log(`✅ Fixed image prompts in ${count} files`);
}

// ─── Fix 4: Section page article links pointing to wrong path ───
function fixSectionPageLinks() {
  const sectionFiles = fs.readdirSync(NEWS_DIR).filter(f => f.startsWith('section-') && f.endsWith('.html'));

  let count = 0;
  for (const file of sectionFiles) {
    const filePath = path.join(NEWS_DIR, file);
    let html = fs.readFileSync(filePath, 'utf-8');
    let changed = false;

    // Fix article links that start with "articles/" but need to be absolute
    if (html.includes('href="articles/')) {
      html = html.replace(/href="articles\//g, 'href="/articles/');
      changed = true;
    }
    if (html.includes("onclick=\"location.href='articles/")) {
      html = html.replace(/onclick="location\.href='articles\//g, "onclick=\"location.href='/articles/");
      changed = true;
    }

    if (changed) {
      fs.writeFileSync(filePath, html);
      count++;
    }
  }
  console.log(`✅ Fixed section page links in ${count} files`);
}

// ─── Fix 5: Articles dir page links - fix the hrefs in pipeline-generated articles ───
function fixArticlesDirLinks() {
  const articlesDir = path.join(NEWS_DIR, 'articles');
  if (!fs.existsSync(articlesDir)) return;

  const files = fs.readdirSync(articlesDir).filter(f => f.endsWith('.html'));
  let count = 0;

  for (const file of files) {
    const filePath = path.join(articlesDir, file);
    let html = fs.readFileSync(filePath, 'utf-8');
    let changed = false;

    // Fix header nav links in articles
    const navReplacements = [
      [/href="index\.html"/g, 'href="/index.html"'],
      [/href="section-tech\.html"/g, 'href="/section-tech.html"'],
      [/href="section-ai\.html"/g, 'href="/section-ai.html"'],
      [/href="section-gaming\.html"/g, 'href="/section-gaming.html"'],
      [/href="finance\.html"/g, 'href="/finance.html"'],
      [/href="section-world-news\.html"/g, 'href="/section-world-news.html"'],
      [/href="section-science\.html"/g, 'href="/section-science.html"'],
    ];

    for (const [pattern, replacement] of navReplacements) {
      if (pattern.test(html)) {
        html = html.replace(pattern, replacement);
        changed = true;
      }
    }

    // Fix breadcrumb links
    if (html.includes('href="section-') && !html.includes('href="/section-')) {
      html = html.replace(/href="section-/g, 'href="/section-');
      changed = true;
    }

    if (changed) {
      fs.writeFileSync(filePath, html);
      count++;
    }
  }
  console.log(`✅ Fixed article page links in ${count} files`);
}

// ─── Fix 6: Remove "face" showing images - fix article featured image ───
function fixArticleFeaturedImages() {
  const articlesDir = path.join(NEWS_DIR, 'articles');
  if (!fs.existsSync(articlesDir)) return;

  const files = fs.readdirSync(articlesDir).filter(f => f.endsWith('.html'));
  let count = 0;

  for (const file of files) {
    const filePath = path.join(articlesDir, file);
    let html = fs.readFileSync(filePath, 'utf-8');
    
    // Replace unsplash images that might show faces with abstract ones
    if (html.includes('images.unsplash.com') && html.includes('pollinations.ai')) {
      // Make pollinations the primary source, unsplash as fallback
      if (html.includes('onerror=')) {
        // Swap: make pollinations primary
        html = html.replace(
          /src="(https:\/\/images\.unsplash\.com\/[^"]+)"([^>]*?)onerror="this\.onerror=null;this\.src='(https:\/\/image\.pollinations\.ai\/[^']+)'"/g,
          'src="$3" onerror="this.onerror=null;this.src=\'$1\'"'
        );
        count++;
        fs.writeFileSync(filePath, html);
      }
    }
  }
  console.log(`✅ Swapped to Pollinations primary images in ${count} articles`);
}

// ─── MAIN ───
console.log('🔧 Fixing navigation links, image prompts, and article paths...\n');

fixHeaderNavLinks();
fixSectionPageLinks();
fixArticlesDirLinks();
fixLandingPageLinks();
fixImagePrompts();
fixArticleFeaturedImages();

console.log('\n🎉 All link fixes applied!');