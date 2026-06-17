const { app, BrowserWindow } = require('electron');
const path = require('path');

const ICON = path.join(__dirname, '..', 'www', 'icons', 'icon-512.png');

let splash, main;

function createSplash() {
  splash = new BrowserWindow({
    width: 280,
    height: 280,
    frame: false,
    resizable: false,
    movable: false,
    show: false,
    backgroundColor: '#080808',
    icon: ICON,
  });
  splash.loadFile(path.join(__dirname, 'splash.html'));
  splash.once('ready-to-show', () => splash.show());
}

function createMainWindow() {
  main = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 1024,
    minHeight: 700,
    backgroundColor: '#080808',
    autoHideMenuBar: true,
    show: false,
    icon: ICON,
    webPreferences: {
      contextIsolation: true,
    },
  });
  main.loadFile(path.join(__dirname, '..', 'www', 'index.html'));

  main.once('ready-to-show', () => {
    setTimeout(() => {
      if (splash) splash.close();
      main.show();
    }, 1500);
  });
}

app.whenReady().then(() => {
  createSplash();
  createMainWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
});
