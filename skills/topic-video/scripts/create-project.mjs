#!/usr/bin/env node
/*
 * Scaffolds a video project from assets/template.
 *
 *   node scripts/create-project.mjs <target-dir> --ratio 9:16 --title "Why we sleep"
 *
 * Copies the template, writes video.config.json, runs `npm install`
 * (skip with --no-install) and reports whether Chrome and ffmpeg are available.
 */
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const argv = process.argv.slice(2);
const target = argv[0] && !argv[0].startsWith('--') ? path.resolve(argv[0]) : null;
const opt = (name, fallback) => {
  const i = argv.indexOf(`--${name}`);
  return i !== -1 && argv[i + 1] !== undefined ? argv[i + 1] : fallback;
};
const ratio = opt('ratio');
const title = opt('title', 'Untitled video');
const RATIOS = ['16:9', '9:16', '1:1'];

if (!target || !RATIOS.includes(ratio)) {
  console.error('Usage: node create-project.mjs <target-dir> --ratio <16:9|9:16|1:1> [--title "..."] [--no-install]');
  process.exit(1);
}
if (fs.existsSync(target) && fs.readdirSync(target).length) {
  console.error(`Target ${target} already exists and is not empty.`);
  process.exit(1);
}

const template = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'assets', 'template');
const skip = new Set(['node_modules', 'dist', 'out']);
fs.cpSync(template, target, { recursive: true, filter: (src) => !skip.has(path.basename(src)) });
fs.writeFileSync(
  path.join(target, 'video.config.json'),
  `${JSON.stringify({ title, ratio, fps: 30, duration: 60 }, null, 2)}\n`,
);
console.log(`Created ${target}  (${ratio}, "${title}")`);

if (!argv.includes('--no-install')) {
  console.log('Installing dependencies...');
  const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  const r = spawnSync(npm, ['install', '--no-audit', '--no-fund'], { cwd: target, stdio: 'inherit', shell: process.platform === 'win32' });
  if (r.status !== 0) { console.error('npm install failed'); process.exit(1); }
}

const { findChrome } = await import(pathToFileURL(path.join(target, 'tools', 'find-chrome.mjs')).href);
const chrome = findChrome();
const hasFfmpeg = spawnSync('ffmpeg', ['-version']).status === 0;
console.log(`Chrome: ${chrome || 'NOT FOUND -> run `npx puppeteer browsers install chrome` in the project, or set CHROME_PATH'}`);
const hasEdgeTts = [['edge-tts'], ['python3', '-m', 'edge_tts'], ['python', '-m', 'edge_tts'], ['uvx', 'edge-tts']]
  .some(([cmd, ...rest]) => spawnSync(cmd, [...rest, '--version']).status === 0);
console.log(`edge-tts (voiceover): ${hasEdgeTts ? 'ok' : 'NOT FOUND -> pip install edge-tts'}`);
console.log(`ffmpeg: ${hasFfmpeg ? 'ok' : 'NOT FOUND -> install ffmpeg, or run `npm i -D ffmpeg-static` in the project'}`);
