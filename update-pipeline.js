const fs = require('fs');
let code = fs.readFileSync('pipeline.js', 'utf8');

// Remove HTML generating functions completely
code = code.replace(/function updateLandingPage[\s\S]*?\/\/\s*─── Watch mode ───/, '// ─── Watch mode ───');
code = code.replace(/function buildArticleHTML[\s\S]*?\/\/\s*─── Step 7: Update section index page ───/, '// ─── Step 7: Removed HTML building ───\n');
code = code.replace(/function updateSectionPage[\s\S]*?\/\/\s*─── Step 8: Main pipeline execution ───/, '// ─── Step 8: Main pipeline execution ───');

// Replace the end of runPipeline
code = code.replace(/\/\/ 3\. Update section index pages[\s\S]*?const duration/, 'const { buildSite } = require(\'./build-newspaper-module.js\');\n  log(\'Rebuilding 1200+ vintage pages with Monetag scripts...\');\n  buildSite();\n\n  const duration');

// Inside runPipeline, remove the HTML generation step
code = code.replace(/\/\/ Save as HTML[\s\S]*?processedArticles\.push\(articleData\);/, 'processedArticles.push(articleData);');

fs.writeFileSync('pipeline.js', code);
