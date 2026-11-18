/*
 * Virtual clock, injected into the page by record.mjs before any app code runs.
 *
 * Recording a browser in real time drops and duplicates frames whenever the
 * machine is busy. Instead the recorder owns time: it moves the clock forward
 * exactly one video frame (1000/fps ms), lets every animation library update
 * once, takes a screenshot, and repeats. Whether a frame takes 5ms or 5s to
 * draw, the video comes out perfectly smooth.
 *
 * What is virtualised:
 *   - performance.now(), Date.now(), new Date()
 *   - requestAnimationFrame / cancelAnimationFrame   (GSAP, Framer Motion, react-spring, lottie...)
 *   - setTimeout / setInterval and their clear* twins
 *   - CSS animations and transitions (paused and scrubbed via document.getAnimations())
 * element.animate() is removed so Framer Motion falls back to its JS (rAF)
 * driver instead of handing transforms to the compositor, which we cannot step.
 */
(() => {
  if (window.__vt) return;

  const real = {
    setTimeout: window.setTimeout.bind(window),
  };
  const EPOCH = 1767225600000; // fixed wall-clock origin, so renders are repeatable
  let now = 0;
  let seq = 0;
  let timers = new Map();
  let rafs = new Map();

  performance.now = () => now;
  const RealDate = Date;
  class VirtualDate extends RealDate {
    constructor(...args) {
      if (args.length === 0) super(EPOCH + now);
      else super(...args);
    }
    static now() { return EPOCH + now; }
  }
  window.Date = VirtualDate;

  const addTimer = (cb, delay, args, interval) => {
    if (typeof cb !== 'function') return 0;
    const id = ++seq;
    const ms = Math.max(0, Number(delay) || 0);
    timers.set(id, { id, due: now + ms, cb, args, interval: interval ? Math.max(1, ms) : 0 });
    return id;
  };
  window.setTimeout = (cb, delay, ...args) => addTimer(cb, delay, args, false);
  window.setInterval = (cb, delay, ...args) => addTimer(cb, delay, args, true);
  window.clearTimeout = window.clearInterval = (id) => { timers.delete(id); };
  window.requestAnimationFrame = (cb) => { const id = ++seq; rafs.set(id, cb); return id; };
  window.cancelAnimationFrame = (id) => { rafs.delete(id); };

  try { delete Element.prototype.animate; } catch (e) { /* keep going */ }

  const safely = (fn, ...args) => {
    try { fn(...args); } catch (e) { console.error('[time-shim]', e); }
  };

  const runTimers = (target) => {
    for (let guard = 0; guard < 100000; guard++) {
      let next = null;
      for (const t of timers.values()) {
        if (t.due <= target && (!next || t.due < next.due || (t.due === next.due && t.id < next.id))) next = t;
      }
      if (!next) return;
      now = Math.max(now, next.due);
      if (next.interval) next.due += next.interval;
      else timers.delete(next.id);
      safely(next.cb, ...next.args);
    }
  };

  const runFrame = () => {
    const callbacks = rafs;
    rafs = new Map();
    for (const [id, cb] of callbacks) {
      if (callbacks.has(id)) safely(cb, now);
    }
  };

  // Real (not virtual) macrotask: gives React, promises and layout a chance to flush.
  const settle = () => new Promise((resolve) => real.setTimeout(resolve, 0));

  const seen = new WeakMap();
  const syncCssAnimations = () => {
    if (!document.getAnimations) return;
    for (const a of document.getAnimations()) {
      let start = seen.get(a);
      if (start === undefined) { start = now; seen.set(a, start); }
      const local = now - start;
      try {
        const end = a.effect && a.effect.getComputedTiming().endTime;
        if (Number.isFinite(end) && local >= end) a.finish();
        else { a.pause(); a.currentTime = local; }
      } catch (e) { /* animation was removed mid-loop */ }
    }
  };

  window.__vt = {
    get now() { return now; },
    /** Move the clock to `target` ms and bring the page fully up to date. */
    async advance(target) {
      runTimers(target);
      now = Math.max(now, target);
      runFrame();
      await settle();
      await settle();
      syncCssAnimations();
      await settle();
    },
  };
})();
