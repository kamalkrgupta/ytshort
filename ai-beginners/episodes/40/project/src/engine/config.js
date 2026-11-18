import cfg from '../../video.config.json';

export const RATIOS = {
  '16:9': { width: 1920, height: 1080 },
  '9:16': { width: 1080, height: 1920 },
  '1:1': { width: 1080, height: 1080 },
};

// Margins (px) that keep text clear of platform chrome (captions, like/share
// rails, progress bars). Backgrounds bleed to the edge; text and logos stay inside.
const SAFE = {
  '16:9': { top: 70, right: 110, bottom: 70, left: 110 },
  '9:16': { top: 230, right: 80, bottom: 340, left: 80 },
  '1:1': { top: 80, right: 80, bottom: 80, left: 80 },
};

if (!RATIOS[cfg.ratio]) {
  throw new Error(`video.config.json: ratio must be one of ${Object.keys(RATIOS).join(', ')}`);
}

export const video = {
  title: cfg.title,
  ratio: cfg.ratio,
  fps: cfg.fps ?? 30,
  duration: cfg.duration ?? 60,
  ...RATIOS[cfg.ratio],
  safe: SAFE[cfg.ratio],
};

const params = new URLSearchParams(window.location.search);
// ?capture=1 is added by tools/record.mjs: no HUD, no scaling, virtual clock.
export const isCapture = params.has('capture');
export const startAtScene = Number(params.get('scene') || 0); // 1-based, preview only
export const startAtTime = Number(params.get('t') || 0); // seconds, preview only
