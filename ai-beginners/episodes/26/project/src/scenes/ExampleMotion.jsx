import React from 'react';
import { motion } from 'framer-motion';
import { stagger, rise, pop } from '../kit/motion.js';

// EXAMPLE (Framer Motion): staggered entrance, then points revealed one by one
// across the scene with `delay` so the screen keeps changing for the whole 20s.
const points = ['Declarative enter and exit', 'Springs that feel physical', 'Stagger children with variants'];

export default function ExampleMotion() {
  return (
    <div className="scene">
      <div className="safe">
        <motion.div variants={stagger(0.15, 0.3)} initial="hidden" animate="show">
          <motion.p className="body" variants={rise} style={{ color: 'var(--accent)' }}>
            Example scene 1
          </motion.p>
          <motion.h1 className="display" variants={rise}>Framer Motion</motion.h1>
        </motion.div>
        <div style={{ display: 'grid', gap: 'calc(var(--u) * 2)', marginTop: 'calc(var(--u) * 3)' }}>
          {points.map((p, i) => (
            <motion.div
              key={p}
              variants={pop}
              initial="hidden"
              animate="show"
              transition={{ delay: 2 + i * 4 }}
              style={{
                background: 'var(--surface)',
                borderLeft: 'calc(var(--u) * 0.8) solid var(--accent)',
                padding: 'calc(var(--u) * 2.4) calc(var(--u) * 3)',
                fontSize: 'calc(var(--u) * 4)',
                transformOrigin: 'left center',
              }}
            >
              {p}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
