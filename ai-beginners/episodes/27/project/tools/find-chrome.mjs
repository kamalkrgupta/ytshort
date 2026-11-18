import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const exists = (p) => { try { return fs.statSync(p).isFile(); } catch { return false; } };

// Walk a browser cache folder (puppeteer / playwright layouts) looking for a binary.
function findIn(dir, names, depth = 4) {
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return null; }
  entries.sort((a, b) => b.name.localeCompare(a.name, undefined, { numeric: true })); // newest first
  for (const e of entries) {
    if (e.isFile() && names.includes(e.name)) return path.join(dir, e.name);
  }
  if (depth === 0) return null;
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    const hit = findIn(path.join(dir, e.name), names, depth - 1);
    if (hit) return hit;
  }
  return null;
}

/** Returns a path to Chrome/Chromium/Edge, or null. Override with CHROME_PATH. */
export function findChrome() {
  for (const v of ['CHROME_PATH', 'PUPPETEER_EXECUTABLE_PATH']) {
    if (process.env[v] && exists(process.env[v])) return process.env[v];
  }
  const home = os.homedir();
  const fixed = {
    darwin: [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
      '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
    ],
    win32: [
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      path.join(home, 'AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'),
      'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
      'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    ],
    linux: [
      '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium',
      '/usr/bin/chromium-browser', '/snap/bin/chromium', '/opt/google/chrome/chrome',
    ],
  }[process.platform] || [];
  for (const p of fixed) if (exists(p)) return p;

  const names = process.platform === 'win32'
    ? ['chrome.exe']
    : process.platform === 'darwin'
      ? ['Google Chrome for Testing', 'Chromium', 'chrome']
      : ['chrome'];
  const caches = [
    process.env.PLAYWRIGHT_BROWSERS_PATH,
    process.env.PUPPETEER_CACHE_DIR,
    path.join(home, '.cache', 'puppeteer'),
    path.join(home, '.cache', 'ms-playwright'),
    path.join(home, 'Library', 'Caches', 'ms-playwright'),
    path.join(home, 'AppData', 'Local', 'ms-playwright'),
  ].filter(Boolean);
  for (const dir of caches) {
    const hit = findIn(dir, names, 6);
    if (hit) return hit;
  }
  return null;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const p = findChrome();
  console.log(p || 'NOT FOUND - run: npx puppeteer browsers install chrome  (or set CHROME_PATH)');
  process.exit(p ? 0 : 1);
}
