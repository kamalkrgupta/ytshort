import React from 'react';
import { useSpring, animated } from '@react-spring/web';

/**
 * Number that counts up with react-spring.
 *   <Counter to={8.5} decimals={1} suffix=" hrs" delay={600} />
 */
export function Counter({ from = 0, to, decimals = 0, prefix = '', suffix = '', delay = 0, duration = 1600, className, style }) {
  const { n } = useSpring({
    from: { n: from },
    to: { n: to },
    delay,
    config: { duration, easing: (t) => 1 - Math.pow(1 - t, 3) },
  });
  return (
    <animated.span className={className} style={{ fontVariantNumeric: 'tabular-nums', ...style }}>
      {n.to((v) => `${prefix}${v.toFixed(decimals)}${suffix}`)}
    </animated.span>
  );
}
