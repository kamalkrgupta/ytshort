// The storyboard, in play order. Durations are in seconds and MUST add up to
// `duration` in video.config.json (60). tools/record.mjs refuses to render otherwise.
//
// transition: how the scene enters - cut | fade | slideLeft | slideUp | zoom | wipe
//
// The three Example* scenes are recipes for each animation library. Replace them
// with the real scenes and delete the example files.
import ExampleMotion from './ExampleMotion.jsx';
import ExampleGsap from './ExampleGsap.jsx';
import ExampleSpring from './ExampleSpring.jsx';

export const scenes = [
  { id: 'example-motion', duration: 20, transition: 'fade', component: ExampleMotion },
  { id: 'example-gsap', duration: 20, transition: 'slideLeft', component: ExampleGsap },
  { id: 'example-spring', duration: 20, transition: 'zoom', component: ExampleSpring },
];
