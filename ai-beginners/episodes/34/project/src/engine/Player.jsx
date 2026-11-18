import React, { useEffect, useMemo, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { video, isCapture, startAtScene, startAtTime } from './config.js';
import { transitions } from './transitions.js';

/**
 * Plays the scene list back to back on one clock.
 *
 * Each scene mounts at its start time and unmounts at its end, so a scene's
 * animations simply start "on mount" - no global frame math inside scenes.
 * The clock is performance.now(); during recording tools/time-shim.js replaces
 * it with a virtual clock, which is what makes the capture frame-exact.
 */
export function Player({ scenes }) {
  const timeline = useMemo(() => {
    let start = 0;
    return scenes.map((s) => {
      const item = { ...s, start };
      start += s.duration;
      return item;
    });
  }, [scenes]);
  const total = timeline.reduce((sum, s) => sum + s.duration, 0);

  const sceneAt = (t) => {
    let i = timeline.findIndex((s) => t < s.start + s.duration);
    if (i === -1) i = timeline.length - 1; // hold the last scene after the end
    return i;
  };

  const offset = useMemo(() => {
    if (isCapture) return 0;
    if (startAtScene > 0) return timeline[Math.min(startAtScene, timeline.length) - 1].start;
    return Math.max(0, Math.min(startAtTime, total - 0.1));
  }, [timeline, total]);

  const [ready, setReady] = useState(false);
  const [index, setIndex] = useState(() => sceneAt(offset));
  const indexRef = useRef(index);
  const hudRef = useRef(null);
  const barRef = useRef(null);

  // Wait for fonts so the first frame never renders in a fallback face.
  useEffect(() => {
    let alive = true;
    document.fonts.ready.then(() => alive && setReady(true));
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    if (!ready) return undefined;
    const t0 = performance.now() - offset * 1000;
    let raf;
    const tick = () => {
      const t = (performance.now() - t0) / 1000;
      const i = sceneAt(t);
      if (i !== indexRef.current) {
        indexRef.current = i;
        // Synchronous so the new scene is in the DOM within this very frame.
        flushSync(() => setIndex(i));
      }
      if (hudRef.current) {
        const s = timeline[i];
        hudRef.current.textContent =
          `${i + 1}/${timeline.length}  ${s.id}  ${Math.min(t, total).toFixed(1)}s / ${total}s`;
        barRef.current.style.width = `${Math.min(100, (t / total) * 100)}%`;
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    window.__VIDEO__ = {
      ready: true,
      fps: video.fps,
      width: video.width,
      height: video.height,
      duration: total,
      targetDuration: video.duration,
      scenes: timeline.map(({ id, start, duration }) => ({ id, start, duration })),
    };
    return () => cancelAnimationFrame(raf);
  }, [ready]); // eslint-disable-line react-hooks/exhaustive-deps

  const scene = timeline[index];
  const Scene = scene.component;
  const t = transitions[scene.transition || 'fade'] || transitions.fade;

  const stageStyle = {
    width: video.width,
    height: video.height,
    '--w': `${video.width}px`,
    '--h': `${video.height}px`,
    '--u': `${Math.min(video.width, video.height) / 100}px`,
    '--safe-top': `${video.safe.top}px`,
    '--safe-right': `${video.safe.right}px`,
    '--safe-bottom': `${video.safe.bottom}px`,
    '--safe-left': `${video.safe.left}px`,
  };

  return (
    <div className={isCapture ? 'viewport capture' : 'viewport preview'}>
      <FitToWindow enabled={!isCapture}>
        <div className="stage" data-ratio={video.ratio} style={stageStyle}>
          {ready && (
            <AnimatePresence initial>
              <motion.div
                key={scene.id}
                className="scene-frame"
                style={{ zIndex: index + 1 }}
                initial={t.initial}
                animate={t.animate}
                exit={t.exit}
              >
                <Scene duration={scene.duration} />
              </motion.div>
            </AnimatePresence>
          )}
        </div>
      </FitToWindow>
      {!isCapture && (
        <div className="hud">
          <div className="hud-bar"><div ref={barRef} /></div>
          <span ref={hudRef} />
          {total !== video.duration && (
            <b className="hud-warn">scenes add up to {total}s, target is {video.duration}s</b>
          )}
        </div>
      )}
    </div>
  );
}

/** Preview only: scales the fixed-size stage down to fit the browser window. */
function FitToWindow({ enabled, children }) {
  const [scale, setScale] = useState(1);
  useEffect(() => {
    if (!enabled) return undefined;
    const fit = () =>
      setScale(Math.min(window.innerWidth / video.width, (window.innerHeight - 40) / video.height));
    fit();
    window.addEventListener('resize', fit);
    return () => window.removeEventListener('resize', fit);
  }, [enabled]);
  if (!enabled) return children;
  return (
    <div style={{ width: video.width * scale, height: video.height * scale }}>
      <div style={{ transform: `scale(${scale})`, transformOrigin: '0 0' }}>{children}</div>
    </div>
  );
}
