import React,{useEffect,useState} from 'react';
import {flushSync} from 'react-dom';
import {AnimatePresence,motion} from 'framer-motion';
export const imageFiles=['01-hook.png','02-help.png','03-doubt.png','04-call.png','05-privacy.png','06-check.png','07-control.png','08-choice.png'];
function PhotoScene({index,title,duration,cta,focus='50% 55%'}){
 const [shot,setShot]=useState(0);
 useEffect(()=>{const a=setTimeout(()=>flushSync(()=>setShot(1)),duration*380);const b=setTimeout(()=>flushSync(()=>setShot(2)),duration*720);return()=>{clearTimeout(a);clearTimeout(b)}},[duration]);
 const views=[{scale:1.08,to:1.14,x:-10,end:8,y:8,endy:-8,time:duration*.38},{scale:1.24,to:1.29,x:10,end:-6,y:0,endy:-10,time:duration*.34},{scale:1.13,to:1.19,x:-8,end:5,y:-7,endy:5,time:duration*.28}];
 const v=views[shot];
 return <div className={'scene image-story scene-'+index}>
  <AnimatePresence initial={false}>
   <motion.div className="photo-layer" key={shot} initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} transition={{duration:.14}}>
    <motion.img className="story-image" alt="Fictional photographic illustration" src={'/images/'+imageFiles[index]} style={{transformOrigin:focus}} initial={{scale:v.scale,x:v.x,y:v.y}} animate={{scale:v.to,x:v.end,y:v.endy}} transition={{duration:v.time,ease:'linear'}}/>
   </motion.div>
  </AnimatePresence>
  <div className="photo-shade"/>
  <div className="photo-safe">
   <motion.h1 initial={{opacity:0,y:18}} animate={{opacity:1,y:0}} transition={{duration:.45,delay:.14}}>{title}</motion.h1>
   {cta&&<motion.div className="photo-cta" initial={{opacity:0,y:15}} animate={{opacity:1,y:0}} transition={{delay:2.7,duration:.45}}>{cta}</motion.div>}
   <div className="photo-brand">TECH AT 60{index===7&&<span>Illustrative scenes</span>}</div>
  </div>
 </div>
}
export function Hook({duration}){return <PhotoScene index={0} duration={duration} title={<>Friend…<br/><em>or devil?</em></>} focus="55% 54%"/>}
export function Friend({duration}){return <PhotoScene index={1} duration={duration} title={<>A useful<br/><em>assistant.</em></>} focus="52% 60%"/>}
export function Trap({duration}){return <PhotoScene index={2} duration={duration} title={<>Confidence<br/>isn’t <em>proof.</em></>} focus="55% 62%"/>}
export function Fake({duration}){return <PhotoScene index={3} duration={duration} title={<>Call back.<br/><em>Verify.</em></>} focus="61% 53%"/>}
export function Privacy({duration}){return <PhotoScene index={4} duration={duration} title={<>Pause before<br/><em>sharing.</em></>} focus="48% 65%"/>}
export function Rule({duration}){return <PhotoScene index={5} duration={duration} title={<>You make<br/><em>the call.</em></>} focus="61% 62%"/>}
export function Payoff({duration}){return <PhotoScene index={6} duration={duration} title={<>Keep<br/><em>control.</em></>} focus="55% 58%"/>}
export function Close({duration}){return <PhotoScene index={7} duration={duration} title={<>Where’s<br/><em>your line?</em></>} cta="Tell us in the comments." focus="54% 52%"/>}
