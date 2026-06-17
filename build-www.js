// Copies the published site assets into www/, which Capacitor uses as its webDir.
// Run via `npm run build` before `cap sync` so the native app always ships the latest site.
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const WWW = path.join(ROOT, 'www');
const ASSETS = ['index.html', 'manifest.json', 'sw.js'];
const DIRS = ['icons', 'images'];

fs.rmSync(WWW, { recursive: true, force: true });
fs.mkdirSync(WWW, { recursive: true });

for (const file of ASSETS) {
  fs.copyFileSync(path.join(ROOT, file), path.join(WWW, file));
}
for (const dir of DIRS) {
  fs.cpSync(path.join(ROOT, dir), path.join(WWW, dir), { recursive: true });
}

console.log('www/ rebuilt from site assets.');
