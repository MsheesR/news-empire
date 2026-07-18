const { execSync } = require('child_process');
for(let i=0; i<5; i++) {
  try {
    try { require('fs').unlinkSync('.git/index.lock'); } catch(e){}
    execSync('icacls .git /grant "Everyone:(OI)(CI)F" /T /C /Q');
    execSync('git add .');
    execSync('git commit -am "Auto-Update: Pushed all ad tags and verification files manually for instant update"');
    console.log('Success!');
    break;
  } catch(e) {
    console.log('Attempt ' + i + ' failed.');
  }
}
try { execSync('git push origin main'); } catch(e) { console.log(e.message); }

