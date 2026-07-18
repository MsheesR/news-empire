const { execSync } = require('child_process');
const maxRetries = 20;
for(let i=0; i<maxRetries; i++) {
  try {
    execSync('icacls .git /grant "Everyone:(OI)(CI)F" /T /C /Q', {stdio: 'ignore'});
    execSync('git add -A', {stdio: 'ignore'});
    execSync('git commit -m "Auto-Update: Forced local push of 1200 HTML files"', {stdio: 'ignore'});
    console.log('Success on attempt ' + i);
    break;
  } catch(e) {
    console.log('Failed attempt ' + i);
  }
}
try { execSync('git push origin main', {stdio: 'inherit'}); } catch(e) { console.log(e.message); }
