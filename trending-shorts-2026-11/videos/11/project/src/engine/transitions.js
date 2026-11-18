// Scene-to-scene transitions. The outgoing scene plays `exit` while the incoming
// one plays `initial -> animate` on top of it, so a transition never adds time
// to the video. Pick one per scene with `transition: 'name'` in scenes/index.js
// (it describes how THAT scene enters, and how it leaves when the next one comes).
const ease = [0.22, 1, 0.36, 1];
const enter = { duration: 0.6, ease };
const leave = { duration: 0.45, ease: 'easeIn' };

export const transitions = {
  cut: { initial: false, animate: { opacity: 1 }, exit: { opacity: 1, transition: { duration: 0 } } },
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: enter },
    exit: { opacity: 0, transition: leave },
  },
  slideLeft: {
    initial: { x: '100%' },
    animate: { x: 0, transition: { duration: 0.7, ease } },
    exit: { x: '-30%', opacity: 0, transition: { duration: 0.7, ease } },
  },
  slideUp: {
    initial: { y: '100%' },
    animate: { y: 0, transition: { duration: 0.7, ease } },
    exit: { y: '-30%', opacity: 0, transition: { duration: 0.7, ease } },
  },
  zoom: {
    initial: { scale: 1.25, opacity: 0 },
    animate: { scale: 1, opacity: 1, transition: enter },
    exit: { scale: 0.85, opacity: 0, transition: leave },
  },
  wipe: {
    initial: { clipPath: 'inset(0 100% 0 0)' },
    animate: { clipPath: 'inset(0 0% 0 0)', transition: { duration: 0.8, ease } },
    exit: { opacity: 1, transition: { duration: 0.8 } },
  },
};
