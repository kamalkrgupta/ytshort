import React from 'react';

/**
 * Renders text as one inline-block span per word (class "split-word") so GSAP or
 * Framer Motion can stagger them. Words keep natural wrapping.
 *   <SplitText className="display" text="Sleep is a superpower" />
 *   gsap.from('.split-word', { yPercent: 110, opacity: 0, stagger: 0.08 })
 */
export function SplitText({ text, as: Tag = 'h1', className, wordClassName = '', ...rest }) {
  const words = text.split(' ');
  return (
    <Tag className={className} aria-label={text} {...rest}>
      {words.map((w, i) => (
        <span key={i} className={`split-word ${wordClassName}`}>
          {w}{i < words.length - 1 ? ' ' : ''}
        </span>
      ))}
    </Tag>
  );
}
