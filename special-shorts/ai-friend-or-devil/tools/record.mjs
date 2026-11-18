#!/usr/bin/env node
/*
 * Records the built video (dist/) in headless Chrome and encodes it to MP4.
 *
 *   node tools/record.mjs                  full render  -> out/<title>.mp4
 *   node tools/record.mjs --stills         one PNG per scene + out/stills/contact.png
 *   node tools/record.mjs --at 2.5,31      PNGs at specific seconds
 *   node tools/record.mjs --from 20 --to 30   partial render (for checking one scene's motion)
 *
 * Options: --out <file>  --audio <music file>  --no-voice  --music-volume <0..1>
 *          --crf <n=18>  --png  --allow-duration-mismatch
 *
 * Voiceover: if voice/manifest.json exists (written by tools/voiceover.mjs) each
 * clip is placed at the start of its scene and mixed into the MP4. With voice
 * present, --audio becomes background music underneath it.
 *
 * Run `npm run build` first (the npm scripts `render` and `stills` do it for you).
 */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import puppeteer from 'puppeteer-core';
import { findChrome } from './find-chrome.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dist = path.join(root, 'dist');
const cfg = JSON.parse(fs.readFileSync(path.join(root, 'video.config.json'), 'utf8'));

// ---------------------------------------------------------------- arguments
const argv = process.argv.slice(2);
const flag = (name) => argv.includes(`--${name}`);
const opt = (name, fallback) => {
  const i = argv.indexOf(`--${name}`);
  return i !== -1 && argv[i + 1] !== undefined ? argv[i + 1] : fallback;
};
const fail = (msg) => { console.error(`\nERROR: ${msg}\n`); process.exit(1); };

const SIZES = { '16:9': [1920, 1080], '9:16': [1080, 1920], '1:1': [1080, 1080] };
if (!SIZES[cfg.ratio]) fail(`video.config.json ratio "${cfg.ratio}" must be 16:9, 9:16 or 1:1`);
const [width, height] = SIZES[cfg.ratio];
const fps = cfg.fps || 30;

const stillTimes = opt('at') ? opt('at').split(',').map(Number) : null;
const stillsMode = flag('stills') || !!stillTimes;
const slug = (cfg.title || 'video').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'video';
const outFile = path.resolve(root, opt('out', path.join('out', `${slug}.mp4`)));
const stillsDir = path.join(root, 'out', 'stills');

if (!fs.existsSync(path.join(dist, 'index.html'))) fail('dist/ not found. Run `npm run build` first.');

// ---------------------------------------------------------------- tools
const chromePath = findChrome();
if (!chromePath) {
  fail('No Chrome/Chromium found. Install one with `npx puppeteer browsers install chrome` or set CHROME_PATH.');
}

async function findFfmpeg() {
  if (process.env.FFMPEG_PATH) return process.env.FFMPEG_PATH;
  if (spawnSync('ffmpeg', ['-version']).status === 0) return 'ffmpeg';
  try { return (await import('ffmpeg-static')).default; } catch { return null; }
}
const ffmpeg = await findFfmpeg();
if (!ffmpeg) fail('ffmpeg not found. Install ffmpeg, or run `npm i -D ffmpeg-static`, or set FFMPEG_PATH.');

// ---------------------------------------------------------------- static server for dist/
const MIME = {
  '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.woff': 'font/woff',
  '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.otf': 'font/otf',
};
const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  let file = path.join(dist, urlPath === '/' ? 'index.html' : urlPath);
  if (!file.startsWith(dist) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404); res.end('not found'); return;
  }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const url = `http://127.0.0.1:${server.address().port}/?capture=1`;

// ---------------------------------------------------------------- browser
const browser = await puppeteer.launch({
  executablePath: chromePath,
  headless: true,
  args: [
    '--no-sandbox', '--disable-setuid-sandbox', '--hide-scrollbars', '--mute-audio',
    '--force-device-scale-factor=1', '--font-render-hinting=none', '--disable-dev-shm-usage',
    `--window-size=${width},${height}`,
  ],
});
const cleanup = async () => { await browser.close().catch(() => {}); server.close(); };

const page = await browser.newPage();
await page.setViewport({ width, height, deviceScaleFactor: 1 });
const pageErrors = [];
page.on('pageerror', (e) => pageErrors.push(e.message));
page.on('console', (m) => { if (m.type() === 'error') pageErrors.push(m.text()); });
page.on('requestfailed', (r) => pageErrors.push(`request failed: ${r.url()}`));
await page.evaluateOnNewDocument(fs.readFileSync(path.join(root, 'tools', 'time-shim.js'), 'utf8'));
await page.goto(url, { waitUntil: 'load' });

// Poll from Node: in-page timers are virtual, so page.waitForFunction is unreliable here.
let info = null;
for (let i = 0; i < 200 && !info; i++) {
  info = await page.evaluate(() => (window.__VIDEO__ && window.__VIDEO__.ready ? window.__VIDEO__ : null));
  if (!info) await new Promise((r) => setTimeout(r, 50));
}
if (!info) {
  await cleanup();
  fail(`The app never became ready.\n${pageErrors.join('\n') || '(no page errors captured - check src/main.jsx renders <Player>)'}`);
}

const total = info.duration;
const target = cfg.duration ?? 60;
const partial = opt('from') !== undefined || opt('to') !== undefined;
if (Math.abs(total - target) > 1e-6 && !flag('allow-duration-mismatch') && !stillsMode && !partial) {
  await cleanup();
  const list = info.scenes.map((s) => `  ${s.id.padEnd(24)} ${s.duration}s`).join('\n');
  fail(`Scene durations add up to ${total}s but the video must be ${target}s.\n${list}\nFix the durations in src/scenes/index.js.`);
}

// ---------------------------------------------------------------- voiceover
// Clips are matched to scenes by id, using the start times the running app reports.
const voiceDir = path.join(root, 'voice');
const voiceClips = [];
let voiceLeadIn = 0.35;
if (!flag('no-voice') && fs.existsSync(path.join(voiceDir, 'manifest.json'))) {
  const manifest = JSON.parse(fs.readFileSync(path.join(voiceDir, 'manifest.json'), 'utf8'));
  voiceLeadIn = manifest.leadIn ?? voiceLeadIn;
  const issues = [];
  for (const [id, clip] of Object.entries(manifest.clips || {})) {
    const scene = info.scenes.find((s) => s.id === id);
    const file = path.join(voiceDir, clip.file);
    if (!scene) { issues.push(`voice clip "${id}" has no scene with that id`); continue; }
    if (!fs.existsSync(file)) { issues.push(`voice/${clip.file} is missing`); continue; }
    const over = voiceLeadIn + clip.duration - scene.duration;
    if (over > 0.05) issues.push(`scene "${id}" is ${scene.duration}s but its voice needs ${(voiceLeadIn + clip.duration).toFixed(2)}s (over by ${over.toFixed(2)}s)`);
    voiceClips.push({ id, file, at: scene.start + voiceLeadIn, duration: clip.duration });
  }
  // A narration line edited after its clip was generated would put old words in the video.
  try {
    const narration = JSON.parse(fs.readFileSync(path.join(root, 'narration.json'), 'utf8'));
    const { createHash } = await import('node:crypto');
    for (const [id, text] of Object.entries(narration.scenes || {})) {
      if (typeof text !== 'string' || !text.trim()) continue;
      const clip = (manifest.clips || {})[id];
      const hash = createHash('sha1')
        .update([narration.voice || 'en-US-AriaNeural', narration.rate || '+0%', narration.pitch || '+0Hz', text.trim()].join('\n'))
        .digest('hex').slice(0, 12);
      if (!clip) issues.push(`narration for "${id}" has no clip yet`);
      else if (clip.source === 'edge-tts' && clip.hash !== hash) issues.push(`narration for "${id}" changed since its clip was generated`);
    }
  } catch { /* no narration.json: hand-recorded clips only */ }
  if (issues.length) {
    const text = `Voiceover problems:\n  ${issues.join('\n  ')}\nRun \`npm run voice\` and fix the durations in src/scenes/index.js (or pass --no-voice).`;
    if (stillsMode) console.log(`\nWARNING: ${text}\n`);
    else { await cleanup(); fail(text); }
  }
  voiceClips.sort((a, b) => a.at - b.at);
}

const client = await page.createCDPSession();
const frameMs = 1000 / fps;
const advanceTo = (frame) => page.evaluate((t) => window.__vt.advance(t), frame * frameMs);
const grab = async (format) => {
  const params = format === 'png'
    ? { format: 'png', optimizeForSpeed: true }
    : { format: 'jpeg', quality: 96, optimizeForSpeed: true };
  const { data } = await client.send('Page.captureScreenshot', { ...params, captureBeyondViewport: false });
  return Buffer.from(data, 'base64');
};

const started = Date.now();

// ---------------------------------------------------------------- stills mode
if (stillsMode) {
  fs.rmSync(stillsDir, { recursive: true, force: true });
  fs.mkdirSync(stillsDir, { recursive: true });
  // Default: 85% through each scene, when its layout is fully built and overflow shows.
  const shots = stillTimes
    ? stillTimes.map((t) => ({ t, label: `${t}s` }))
    : info.scenes.map((s) => ({ t: s.start + s.duration * 0.85, label: s.id }));
  shots.sort((a, b) => a.t - b.t);
  const files = [];
  let frame = 0;
  for (const [n, shot] of shots.entries()) {
    const targetFrame = Math.min(Math.round(shot.t * fps), Math.round(total * fps) - 1);
    for (; frame <= targetFrame; frame++) await advanceTo(frame);
    const name = `${String(n + 1).padStart(2, '0')}.png`;
    const overflow = await page.evaluate(() => {
      const issues=[];
      for (const el of document.querySelectorAll('.safe h1,.eyebrow,.tag,.phone,.answer,.task,.step,.choices,.comment,.signature,.endline')) {
        const r=el.getBoundingClientRect();
        if(r.left<75 || r.right>1005 || r.top<120 || r.bottom>1575) issues.push(el.className.baseVal || el.className || el.tagName);
        if(el.scrollWidth>el.clientWidth+3) issues.push('text overflow '+el.tagName);
      }
      return issues;
    });
    if(overflow.length){await cleanup();fail('Safe-area check: '+overflow.join(', '));}
    fs.writeFileSync(path.join(stillsDir, name), await grab('png'));
    files.push(name);
    console.log(`still ${name}  t=${(targetFrame / fps).toFixed(2)}s  ${shot.label}`);
  }
  await cleanup();

  // Contact sheet: every still side by side in one image, quick to review in one look.
  const cols = Math.min(files.length, width > height ? 3 : width === height ? 4 : 5);
  const rows = Math.ceil(files.length / cols);
  const thumbW = Math.floor(1800 / cols / 2) * 2;
  const sheet = path.join(stillsDir, 'contact.png');
  const r = spawnSync(ffmpeg, [
    '-y', '-loglevel', 'error', '-framerate', '1', '-start_number', '1', '-i', path.join(stillsDir, '%02d.png'),
    '-vf', `scale=${thumbW}:-2,tile=${cols}x${rows}:padding=12:margin=12:color=0x333333`,
    '-frames:v', '1', sheet,
  ], { encoding: 'utf8' });
  if (r.status === 0) console.log(`contact sheet: ${path.relative(root, sheet)} (${cols}x${rows}, scenes in reading order)`);
  else console.log(`(contact sheet skipped: ${r.stderr.trim()})`);
  if (pageErrors.length) console.log(`\nPage errors:\n${[...new Set(pageErrors)].join('\n')}`);
  if (Math.abs(total - target) > 1e-6) console.log(`\nWARNING: scenes add up to ${total}s, target is ${target}s.`);
  process.exit(0);
}

// ---------------------------------------------------------------- full render
const from = Number(opt('from', 0));
const to = Math.min(Number(opt('to', total)), total);
const firstFrame = Math.round(from * fps);
const lastFrame = Math.round(to * fps); // exclusive
const frameCount = lastFrame - firstFrame;
const usePng = flag('png');
const audio = opt('audio');
if (audio && !fs.existsSync(audio)) { await cleanup(); fail(`audio file not found: ${audio}`); }

fs.mkdirSync(path.dirname(outFile), { recursive: true });
const seconds = frameCount / fps;
const hasVoice = voiceClips.length > 0;
const audioInputs = [];
let audioArgs = ['-an'];
if (hasVoice || audio) {
  // Input 0 is the frame pipe; voice clips and then the music file follow.
  const chains = [];
  let bus = null;
  if (hasVoice) {
    voiceClips.forEach((clip, i) => {
      audioInputs.push('-i', clip.file);
      chains.push(`[${i + 1}:a]aresample=48000,aformat=channel_layouts=stereo,adelay=delays=${Math.round(clip.at * 1000)}:all=1[v${i}]`);
    });
    const labels = voiceClips.map((_, i) => `[v${i}]`).join('');
    const mix = voiceClips.length > 1 ? `amix=inputs=${voiceClips.length}:normalize=0:dropout_transition=0,` : '';
    // apad first so the loudness pass sees the whole timeline, silence included.
    chains.push(`${labels}${mix}apad=whole_dur=${total},loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[voice]`);
    bus = '[voice]';
  }
  if (audio) {
    audioInputs.push('-stream_loop', '-1', '-i', audio);
    const idx = voiceClips.length + 1;
    const vol = Number(opt('music-volume', hasVoice ? 0.14 : 1));
    chains.push(`[${idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume=${vol},atrim=end=${total}[music]`);
    if (bus) { chains.push(`${bus}[music]amix=inputs=2:normalize=0:duration=first:dropout_transition=0[bed]`); bus = '[bed]'; }
    else bus = '[music]';
  }
  const fade = audio ? `,afade=t=out:st=${Math.max(0, seconds - 1.5)}:d=1.5` : '';
  chains.push(`${bus}atrim=start=${from}:end=${to},asetpts=PTS-STARTPTS,apad${fade}[aout]`);
  audioArgs = ['-filter_complex', chains.join(';'), '-map', '0:v', '-map', '[aout]', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000'];
}
const ffArgs = [
  '-y', '-loglevel', 'error',
  '-f', 'image2pipe', '-framerate', String(fps), '-c:v', usePng ? 'png' : 'mjpeg', '-i', 'pipe:0',
  ...audioInputs,
  '-c:v', 'libx264', '-preset', 'medium', '-crf', String(opt('crf', 18)),
  // yuv420p + even dimensions + faststart = plays everywhere (phones, WhatsApp, browsers, editors)
  '-pix_fmt', 'yuv420p', '-vf', 'scale=in_range=full:out_range=tv,format=yuv420p', '-colorspace', 'bt709',
  '-color_primaries', 'bt709', '-color_trc', 'bt709', '-r', String(fps), '-movflags', '+faststart',
  ...audioArgs,
  '-frames:v', String(frameCount), '-t', String(seconds),
  outFile,
];
if (hasVoice) console.log(`Voiceover: ${voiceClips.length} clip(s)${audio ? ' over music' : ''}`);
const ff = spawn(ffmpeg, ffArgs, { stdio: ['pipe', 'inherit', 'pipe'] });
let ffErr = '';
ff.stderr.on('data', (d) => { ffErr += d; });
const ffDone = new Promise((resolve) => ff.on('close', resolve));
ff.stdin.on('error', () => {}); // surfaced through the exit code below

console.log(`Recording ${frameCount} frames  ${width}x${height} @ ${fps}fps  (${cfg.ratio}, ${(frameCount / fps).toFixed(2)}s)`);
let nextReport = 0.1;
for (let frame = 0; frame < lastFrame; frame++) {
  await advanceTo(frame);
  if (frame < firstFrame) continue; // fast-forward: step the clock, skip the screenshot
  const buf = await grab(usePng ? 'png' : 'jpeg');
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  const done = (frame - firstFrame + 1) / frameCount;
  if (done >= nextReport) {
    const elapsed = (Date.now() - started) / 1000;
    console.log(`  ${Math.round(done * 100)}%  (${elapsed.toFixed(0)}s elapsed, ~${(elapsed / done - elapsed).toFixed(0)}s left)`);
    nextReport += 0.1;
  }
}
ff.stdin.end();
const code = await ffDone;
await cleanup();
if (code !== 0) fail(`ffmpeg exited with code ${code}\n${ffErr}`);

// ---------------------------------------------------------------- verify
const probe = spawnSync('ffprobe', [
  '-v', 'error', '-select_streams', 'v:0', '-show_entries',
  'stream=width,height,r_frame_rate,nb_frames,codec_name,pix_fmt:format=duration,size', '-of', 'json', outFile,
], { encoding: 'utf8' });
const sizeMb = (fs.statSync(outFile).size / 1048576).toFixed(1);
console.log(`\nDone in ${((Date.now() - started) / 1000).toFixed(0)}s -> ${path.relative(process.cwd(), outFile)} (${sizeMb} MB)`);
if (probe.status === 0) {
  const p = JSON.parse(probe.stdout);
  const s = p.streams[0];
  const a = spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_name,channels', '-of', 'csv=p=0', outFile], { encoding: 'utf8' }).stdout.trim();
  console.log(`ffprobe: ${s.codec_name} ${s.pix_fmt} ${s.width}x${s.height} ${s.r_frame_rate}fps ${s.nb_frames} frames ${Number(p.format.duration).toFixed(2)}s  audio: ${a ? a.replace(',', ' ch=') : 'none'}`);
}
if (pageErrors.length) console.log(`\nPage errors during capture:\n${[...new Set(pageErrors)].join('\n')}`);
