import React, { useRef } from 'react';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';
import { SplitText } from '../kit/SplitText.jsx';

// EXAMPLE (GSAP): one timeline choreographs the whole scene - word-by-word
// headline, an SVG underline drawing itself, bars growing in sequence.
const bars = [38, 62, 51, 88, 73];

export default function ExampleGsap() {
  const root = useRef(null);

  useGSAP(() => {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    tl.from('.split-word', { yPercent: 120, opacity: 0, duration: 0.8, stagger: 0.09 }, 0.3)
      .from('.bar', { scaleY: 0, duration: 0.9, stagger: 0.5, ease: 'back.out(1.4)' }, 3)
      .from('.bar-label', { opacity: 0, y: 20, duration: 0.4, stagger: 0.5 }, 3.5)
      .fromTo('.trend', { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.2, ease: 'power2.inOut' }, 1.2)
      .to('.bar', { backgroundColor: '#3ddc97', duration: 0.6, stagger: 0.15 }, 12);
  }, { scope: root });

  return (
    <div className="scene" ref={root}>
      <div className="safe">
        <div>
          <SplitText className="title" text="GSAP timelines keep long scenes in sync" />
          <svg viewBox="0 0 600 24" style={{ width: '60%', display: 'block', marginTop: 'calc(var(--u) * 1.5)' }}>
            <path className="trend" d="M 4 14 C 120 2, 220 24, 330 12 S 520 4, 596 14" pathLength="1" fill="none" stroke="var(--accent)" strokeWidth="5" strokeDasharray="1" />
          </svg>
        </div>
        <div style={{ position: 'relative', height: '45%', display: 'flex', alignItems: 'flex-end', gap: 'calc(var(--u) * 3)' }}>
          {bars.map((v, i) => (
            <div key={i} style={{ flex: 1, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', alignItems: 'center', gap: 'calc(var(--u) * 1)' }}>
              <span className="bar-label" style={{ fontSize: 'calc(var(--u) * 3)', fontWeight: 700 }}>{v}</span>
              <div className="bar" style={{ width: '100%', height: `${v}%`, background: 'var(--accent)', transformOrigin: 'bottom' }} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
