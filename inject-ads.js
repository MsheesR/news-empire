/**
 * Ad Injector — post-processes HTML files to inject ads
 * FIXED: targets docs/ directory, uses ads.js module
 */
const fs = require('fs');
const path = require('path');
const ads = require('./ads.js');

const adHead = ads.getAdHead();
const adMeta = ads.getAdMeta();
const adFooter = ads.getAdFooter();
const dir = path.join(__dirname, 'docs');

function walk(d) {
  const files = fs.readdirSync(d, { withFileTypes: true });
  for (const f of files) {
    const fp = path.join(d, f.name);
    if (f.isDirectory()) walk(fp);
    else if (f.name.endsWith('.html')) {
      let c = fs.readFileSync(fp, 'utf8');
      c = c.replace('<meta charset="UTF-8"><meta name="viewport"', adMeta + '<meta charset="UTF-8"><meta name="viewport"');
      c = c.replace('</head>', adHead + '</head>');
      c = c.replace('</body>', adFooter + '</body>');
      fs.writeFileSync(fp, c);
    }
  }
}
walk(dir);
console.log('Ads injected into all docs/ pages');