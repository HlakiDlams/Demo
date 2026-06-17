// Converts the 512px PNG app icon into build/icon.ico for the Windows installer.
const fs = require('fs');
const path = require('path');
const pngToIco = require('png-to-ico');

pngToIco(path.join(__dirname, 'icons', 'icon-512.png')).then(buf => {
  fs.mkdirSync(path.join(__dirname, 'build'), { recursive: true });
  fs.writeFileSync(path.join(__dirname, 'build', 'icon.ico'), buf);
  console.log('build/icon.ico generated.');
});
