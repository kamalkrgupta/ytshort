#!/usr/bin/env node
/*
 * Voiceover: turns narration.json into one audio clip per scene with Edge TTS,
 * then reports how long each clip is and whether it fits its scene.
 *
 *   node tools/voiceover.mjs                 generate missing or changed clips, print the fit table
 *   node tools/voiceover.mjs --force         regenerate every clip
 *   node tools/voiceover.mjs --measure       no TTS: just (re)measure the clips already in voice/
 *                                            (use this for clips you recorded yourself)
 *   node tools/voiceover.mjs --voices hi-IN  list available voices, filtered by text
 *
 * Clips land in voice/<scene-id>.wav and are described in voice/manifest.json.
 * tools/record.mjs reads that manifest and places each clip at its scene's start.
 *
 * Edge TTS is Microsoft Edge's online read-aloud service, reached through the
 * `edge-tts` Python package. It is free and needs no key, but it needs internet.
 * Install: pip install edge-tts      (or: pipx install edge-tts / uvx edge-tts)
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const voiceDir = path.join(root, 'voice');
const manifestPath = path.join(voiceDir, 'manifest.json');
const argv = process.argv.slice(2);
const flag = (name) => argv.includes(`--${name}`);
const opt = (name) => { const i = argv.indexOf(`--${name}`); return i !== -1 ? argv[i + 1] ?? '' : undefined; };
const fail = (msg) => { console.error(`\nERROR: ${msg}\n`); process.exit(1); };
const AUDIO_EXT = ['.wav', '.mp3', '.m4a', '.aac', '.ogg', '.flac'];

// ---------------------------------------------------------------- tools
function findEdgeTts() {
  const candidates = [
    process.env.EDGE_TTS ? [process.env.EDGE_TTS] : null,
    ['edge-tts'],
    ['python3', '-m', 'edge_tts'],
    ['python', '-m', 'edge_tts'],
    ['py', '-m', 'edge_tts'],
    ['uvx', 'edge-tts'],
  ].filter(Boolean);
  for (const cmd of candidates) {
    const r = spawnSync(cmd[0], [...cmd.slice(1), '--version'], { encoding: 'utf8' });
    if (r.status === 0) return cmd;
  }
  return null;
}
const run = (cmd, args, opts = {}) => spawnSync(cmd[0], [...cmd.slice(1), ...args], { encoding: 'utf8', ...opts });

async function findFfmpeg() {
  if (process.env.FFMPEG_PATH) return process.env.FFMPEG_PATH;
  if (spawnSync('ffmpeg', ['-version']).status === 0) return 'ffmpeg';
  try { return (await import('ffmpeg-static')).default; } catch { return null; }
}

// Duration in seconds. Decodes the file with ffmpeg, so it needs no ffprobe and
// is exact even for formats whose headers only estimate the length.
function measure(ffmpeg, file) {
  const r = spawnSync(ffmpeg, ['-hide_banner', '-i', file, '-f', 'null', '-'], { encoding: 'utf8' });
  const times = [...r.stderr.matchAll(/time=(\d+):(\d+):(\d+(?:\.\d+)?)/g)];
  if (r.status !== 0 || !times.length) return null;
  const [, h, m, s] = times[times.length - 1];
  return Number(h) * 3600 + Number(m) * 60 + Number(s);
}

// ---------------------------------------------------------------- list voices
if (opt('voices') !== undefined) {
  const edge = findEdgeTts();
  if (!edge) fail('edge-tts not found. Install it with: pip install edge-tts');
  const r = run(edge, ['--list-voices']);
  if (r.status !== 0) fail(`Could not list voices (is the machine online?)\n${r.stderr.trim().split('\n').pop()}`);
  const needle = opt('voices').toLowerCase();
  const lines = r.stdout.split('\n');
  console.log(lines.filter((l, i) => i < 2 || l.toLowerCase().includes(needle)).join('\n'));
  process.exit(0);
}

// ---------------------------------------------------------------- inputs
const narrationPath = path.join(root, 'narration.json');
if (!fs.existsSync(narrationPath)) fail('narration.json not found in the project root.');
let narration;
try { narration = JSON.parse(fs.readFileSync(narrationPath, 'utf8')); } catch (e) { fail(`narration.json is not valid JSON: ${e.message}`); }
const voice = narration.voice || 'en-US-AriaNeural';
const rate = narration.rate || '+0%';
const pitch = narration.pitch || '+0Hz';
const leadIn = narration.leadIn ?? 0.35;
const lines = Object.entries(narration.scenes || {}).filter(([, text]) => typeof text === 'string' && text.trim());

const ffmpeg = await findFfmpeg();
if (!ffmpeg) fail('ffmpeg not found. Install ffmpeg, or run `npm i -D ffmpeg-static`, or set FFMPEG_PATH.');

fs.mkdirSync(voiceDir, { recursive: true });
let manifest = { clips: {} };
try { manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8')); } catch { /* first run */ }
manifest.clips ||= {};
const hashOf = (text) => crypto.createHash('sha1').update([voice, rate, pitch, text.trim()].join('\n')).digest('hex').slice(0, 12);

// ---------------------------------------------------------------- generate
const measureOnly = flag('measure');
if (!measureOnly && lines.length) {
  const todo = lines.filter(([id, text]) => {
    const clip = manifest.clips[id];
    return flag('force') || !clip || clip.source !== 'edge-tts' || clip.hash !== hashOf(text)
      || !fs.existsSync(path.join(voiceDir, clip.file));
  });
  if (todo.length) {
    const edge = findEdgeTts();
    if (!edge) fail('edge-tts not found. Install it with `pip install edge-tts` (or pipx / uvx), then run this again.');
    console.log(`Voice: ${voice}  rate ${rate}  pitch ${pitch}`);
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'voiceover-'));
    for (const [id, text] of todo) {
      const txt = path.join(tmp, `${id}.txt`);
      const raw = path.join(tmp, `${id}.mp3`);
      fs.writeFileSync(txt, text.trim());
      let ok = false;
      let lastErr = '';
      for (let attempt = 1; attempt <= 3 && !ok; attempt++) {
        const r = run(edge, ['--file', txt, '--voice', voice, `--rate=${rate}`, `--pitch=${pitch}`, '--write-media', raw], { timeout: 90000 });
        ok = r.status === 0 && fs.existsSync(raw) && fs.statSync(raw).size > 1000;
        if (!ok) lastErr = (r.stderr || r.error?.message || '').trim().split('\n').pop();
      }
      if (!ok) {
        fail(`Edge TTS failed for scene "${id}": ${lastErr}\n`
          + 'Check the internet connection and the voice name (`node tools/voiceover.mjs --voices en-`).\n'
          + 'Edge TTS is an unofficial route to a Microsoft service and is occasionally unavailable; try again in a minute.');
      }
      // Trim the silence TTS pads on both ends so a clip's length is its speech,
      // and store as 48 kHz mono WAV so placement in the mix is sample-accurate.
      for (const ext of AUDIO_EXT) fs.rmSync(path.join(voiceDir, `${id}${ext}`), { force: true });
      const trim = 'silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.03';
      const out = path.join(voiceDir, `${id}.wav`);
      const c = spawnSync(ffmpeg, ['-y', '-loglevel', 'error', '-i', raw, '-af', `${trim},areverse,${trim},areverse`, '-ar', '48000', '-ac', '1', out], { encoding: 'utf8' });
      if (c.status !== 0) fail(`ffmpeg could not convert the clip for "${id}":\n${c.stderr}`);
      manifest.clips[id] = { file: `${id}.wav`, source: 'edge-tts', hash: hashOf(text), duration: measure(ffmpeg, out) };
      console.log(`  generated ${id}.wav  ${manifest.clips[id].duration.toFixed(2)}s`);
    }
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

// Clips recorded by hand: any audio file in voice/ named after a scene id.
for (const file of fs.readdirSync(voiceDir)) {
  const ext = path.extname(file).toLowerCase();
  if (!AUDIO_EXT.includes(ext)) continue;
  const id = path.basename(file, ext);
  const known = manifest.clips[id];
  if (known && known.source === 'edge-tts' && known.file === file) continue;
  const duration = measure(ffmpeg, path.join(voiceDir, file));
  if (duration === null) { console.log(`  skipped ${file}: not readable as audio`); continue; }
  manifest.clips[id] = { file, source: 'file', duration };
}
// Forget clips whose file is gone or whose narration line was removed.
for (const [id, clip] of Object.entries(manifest.clips)) {
  const lineGone = clip.source === 'edge-tts' && !lines.some(([lineId]) => lineId === id);
  if (lineGone) fs.rmSync(path.join(voiceDir, clip.file), { force: true });
  if (lineGone || !fs.existsSync(path.join(voiceDir, clip.file))) delete manifest.clips[id];
}
manifest.voice = voice;
manifest.rate = rate;
manifest.leadIn = leadIn;
fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);

// ---------------------------------------------------------------- fit table
// Scene durations are read from src/scenes/index.js with a pattern match; the
// authoritative check happens in record.mjs, which asks the running app.
const sceneDur = {};
const order = [];
try {
  const src = fs.readFileSync(path.join(root, 'src', 'scenes', 'index.js'), 'utf8');
  for (const m of src.matchAll(/id:\s*['"`]([^'"`]+)['"`]\s*,\s*duration:\s*([\d.]+)/g)) {
    sceneDur[m[1]] = Number(m[2]);
    order.push(m[1]);
  }
} catch { /* scenes not written yet */ }

const TAIL = 0.4; // breathing room after the last word before the scene changes
const need = (d) => Math.ceil((leadIn + d + TAIL) * 2) / 2; // rounded up to 0.5s
const ids = [...new Set([...order, ...Object.keys(manifest.clips)])].filter((id) => manifest.clips[id]);
if (!ids.length) {
  console.log('No narration lines in narration.json and no clips in voice/. The video will be silent.');
  process.exit(0);
}

const cfg = JSON.parse(fs.readFileSync(path.join(root, 'video.config.json'), 'utf8'));
const target = cfg.duration ?? 60;
// Before the scenes exist (index.js still lists other ids) this is a planning
// run: report what each scene will need and don't flag anything.
const planning = !ids.some((id) => id in sceneDur);
let speech = 0;
let needed = 0;
let problems = 0;
console.log(`\n${'scene'.padEnd(22)}${'voice'.padStart(8)}${'needs'.padStart(8)}${'scene is'.padStart(10)}   status`);
for (const id of ids) {
  const d = manifest.clips[id].duration;
  const n = need(d);
  speech += d;
  const cur = sceneDur[id];
  let status = 'ok';
  if (cur === undefined) { status = planning ? 'scene not built yet' : 'NO SCENE WITH THIS ID'; if (!planning) problems++; }
  else if (cur + 1e-6 < leadIn + d) { status = `TOO SHORT by ${(leadIn + d - cur).toFixed(2)}s`; problems++; }
  else if (cur < n) status = 'tight (voice ends right at the cut)';
  else if (cur - n >= 3) status = `${(cur - n).toFixed(1)}s of silence after the voice`;
  console.log(`${id.padEnd(22)}${`${d.toFixed(2)}s`.padStart(8)}${`${n}s`.padStart(8)}${(cur === undefined ? '-' : `${cur}s`).padStart(10)}   ${status}`);
}
for (const id of ids) needed += need(manifest.clips[id].duration);
const silentScenes = planning ? [] : order.filter((id) => !manifest.clips[id]);
const silentTime = silentScenes.reduce((sum, id) => sum + sceneDur[id], 0);
console.log(`\nSpeech ${speech.toFixed(1)}s. Voiced scenes need at least ${needed}s`
  + `${silentScenes.length ? ` + ${silentTime}s in ${silentScenes.length} scene(s) without voice` : ''}`
  + ` = ${needed + silentTime}s of the ${target}s video.`);
if (needed + silentTime > target) {
  console.log(`OVER by ${(needed + silentTime - target).toFixed(1)}s: shorten the narration, or raise "rate" in narration.json (e.g. "+8%"), then run this again.`);
  problems++;
}
if (problems) {
  console.log('Fix the rows above: change the scene durations in src/scenes/index.js or edit the narration.');
  process.exit(2);
}
console.log(planning
  ? 'Use the "needs" column as the minimum duration for each scene in src/scenes/index.js.'
  : 'All clips fit. tools/record.mjs will mix them into the MP4.');
