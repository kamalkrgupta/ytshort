import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';
import { ArrowUpRight, Check, FlaskConical, ShieldCheck, Target } from 'lucide-react';
import lesson from '../../lesson.json';

const MAP = {};

export function Lesson({ chapter, duration }) {
 const root=useRef(null);
 const [view,setView]=useState(0);
 useEffect(()=>{
   const timers=[1,2].map(v=>setTimeout(()=>setView(v),duration*v/3*1000));
   return ()=>timers.forEach(clearTimeout);
 },[duration]);
 const concept=chapter.cards||lesson.visual.steps;
 const labels=concept;
 const isMatrix=/quadrant/i.test(chapter.title);
 useGSAP(()=>{gsap.fromTo('.path-line',{strokeDashoffset:1},{strokeDashoffset:0,duration:1.1,ease:'power2.out',delay:.2});},{scope:root,dependencies:[view]});
 const chapterNumber=lesson.chapters.findIndex(c=>c.id===chapter.id)+1;
 const displayTitle=/^(Hook and introduction|Introduction|Hook and promise)$/.test(chapter.title)?lesson.topic:chapter.title;
 const summary=chapter.summary||(chapter.text.match(/^.*?[.!?](?:\s|$)/)?.[0]||lesson.visual.result).trim();
 return <div className="scene" ref={root}>
   <div className="safe">
    <header><div className="brand"><FlaskConical size={32}/><span>TECH AT <b>60</b></span></div><div className="course">AI FOR BEGINNERS <span>EP {String(lesson.episode).padStart(2,'0')} / 50</span></div></header>
    <div className="lesson-content" key={view}>
     <section className="title-area">
      <motion.div className="eyebrow" initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} transition={{duration:.5}}><span className="dot"/> {view===0?'UNDERSTAND':view===1?'WORKED EXAMPLE':'TRY IT YOURSELF'}</motion.div>
      <motion.h1 initial={{opacity:0,y:22}} animate={{opacity:1,y:0}} transition={{duration:.65,delay:.1}}>{displayTitle}</motion.h1>
      <motion.p className="context" initial={{opacity:0}} animate={{opacity:1}} transition={{duration:.6,delay:.35}}>{view===1?lesson.visual.example:view===2?lesson.visual.question:summary}</motion.p>
      <div className="case-label"><Target size={24}/><span>{lesson.visual.example}</span></div>
      <div className="chapter-index"><span>{String(chapterNumber).padStart(2,'0')}</span><div><b>CHAPTER {chapterNumber} OF {lesson.chapters.length}</b><p>{lesson.topic}</p></div></div>
     </section>
     <section className={'diagram '+(isMatrix?'matrix-mode':'')}>
      <div className="diagram-header"><span>{view===1?'WORKED EXAMPLE':'INPUT → AI → HUMAN CHECK'}</span><ArrowUpRight size={26}/></div>
      {isMatrix?<div className="quadrants">{[['Q1','Unit & component','Technology • Support'],['Q2','Acceptance examples','Business • Support'],['Q3','Exploration & usability','Business • Critique'],['Q4','Performance & security','Technology • Critique']].map(([n,label,sub],i)=><motion.div className={'quadrant q'+i} key={n} initial={{opacity:0,scale:.95}} animate={{opacity:1,scale:1}} transition={{duration:.55,delay:.15+i*.2}}><b>{n}</b><strong>{label}</strong><small>{sub}</small></motion.div>)}</div>:
      <div className="flow">
       <svg className="connectors" width="50" height="390" viewBox="0 0 50 390"><path className="path-line" d="M25 25 L25 365" pathLength="1" strokeDasharray="1" fill="none" stroke="#5BE7C4" strokeWidth="2"/></svg>
       {labels.map((label,i)=><motion.div className={'flow-card card-'+i} key={i} initial={{opacity:0,x:26}} animate={{opacity:1,x:0}} transition={{duration:.6,delay:.15+i*.35}}><span className="step">{view===1?<Check size={25}/>:String(i+1).padStart(2,'0')}</span><strong>{label}</strong><span className="status-dot"/></motion.div>)}
      </div>}
      <motion.div className="insight" initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} transition={{duration:.6,delay:1.4}}><ShieldCheck size={32}/><span>{view===1?lesson.visual.question:lesson.visual.result}</span></motion.div>
     </section>
    </div>
    <footer><span>EXAMPLES USE FICTIONAL APPLICATIONS & SYNTHETIC DATA</span><span>LEARN · PRACTICE · VERIFY</span></footer>
   </div>
 </div>;
}
