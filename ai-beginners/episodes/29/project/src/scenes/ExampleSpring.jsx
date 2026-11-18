import React from 'react';
import { useTrail, animated } from '@react-spring/web';
import { Counter } from '../kit/Counter.jsx';

// EXAMPLE (react-spring + CSS keyframes): a big counting number, a spring trail,
// and a plain CSS @keyframes loop for ambient background motion.
const facts = ['react-spring for numbers', 'CSS keyframes for loops', 'All three libraries record frame-exact'];

export default function ExampleSpring() {
  const trail = useTrail(facts.length, {
    from: { opacity: 0, x: -80 },
    to: { opacity: 1, x: 0 },
    delay: 3000,
    config: { tension: 120, friction: 18 },
  });

  return (
    <div className="scene">
      <style>{`
        @keyframes example-drift { from { transform: translate(-10%, -10%) scale(1); } to { transform: translate(10%, 10%) scale(1.3); } }
        .example-glow { position: absolute; width: 70%; aspect-ratio: 1; right: -20%; top: -20%; border-radius: 50%;
          background: radial-gradient(circle, color-mix(in srgb, var(--accent) 45%, transparent), transparent 65%);
          animation: example-drift 6s ease-in-out infinite alternate; }
      `}</style>
      <div className="example-glow" />
      <div className="safe">
        <Counter className="display" to={60} suffix=" sec" delay={500} duration={2500} style={{ color: 'var(--accent)' }} />
        <p className="title">One minute, every frame accounted for</p>
        <div style={{ display: 'grid', gap: 'calc(var(--u) * 1.5)' }}>
          {trail.map((style, i) => (
            <animated.p key={facts[i]} className="body" style={style}>{facts[i]}</animated.p>
          ))}
        </div>
      </div>
    </div>
  );
}
