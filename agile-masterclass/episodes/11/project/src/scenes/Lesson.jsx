import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';
import { ArrowUpRight, Check, FlaskConical, ShieldCheck, Target } from 'lucide-react';
import lesson from '../../lesson.json';

const MAP = {
 'What is Agile Testing?':['Continuous feedback','Early collaboration','Quality throughout delivery'],
 'Agile versus traditional testing':['Sequential handoffs','Iterative delivery','Earlier opportunities to learn'],
 'Five core principles':['Shared responsibility','Early feedback','Working software'],
 'Agile Testing in Scrum':['Clarify acceptance examples','Verify within the sprint','Inspect the increment'],
 'Four Agile Testing quadrants':['Business ↔ Technology','Support ↔ Critique','Complementary perspectives'],
 'Tools and automation':['Track work','Repeat reliable checks','Investigate with judgment'],
 'Scrum':['Sprint Goal','Usable increment','Inspect & adapt'],
 'Kanban':['Visualize work','Control work in progress','Improve flow'],
 'Extreme Programming':['RED • failing check','GREEN • smallest change','REFACTOR • improve design'],
 'Lean Software Development':['Find customer value','Expose unnecessary waiting','Try an improvement'],
 'Choosing an approach':['Understand the constraint','Choose useful practices','Inspect actual outcomes'],
 'Requirements refinement':['Business rules','Boundary examples','Failure & recovery'],
 'Developer collaboration':['API contract','Positive & negative cases','Early technical feedback'],
 'Test execution':['Functional & integration','Regression checks','Exploratory investigation'],
 'Communication':['Progress & evidence','Blockers & impact','Help & next action'],
 'Technical skills':['APIs & SQL','Version control','Browser automation'],
 'Effectiveness':['Feedback speed','Important risks investigated','Reliable evidence'],
 'Planning':['Acceptance criteria','Environment & test data','Dependencies & risks'],
 'Execution status':['28 passed • 6 failed','4 blocked • 2 not run','40 planned checks'],
 'Defects':['Reproduction steps','Expected vs actual','Impact & evidence'],
 'Metrics':['Meaningful denominator','Blocked work & age','Risk behind the numbers'],
 'Reporting':['What was tested?','What remains uncertain?','What decision is needed?'],
 'Tool walkthrough':['Story → Test','Failure → Defect','Fix → Retest evidence'],
 'Continuous quality':['Clarify before building','Check small changes','Protect existing behavior'],
 'Shared responsibility':['Product expectations','Technical investigation','Operational evidence'],
 'Adaptability and feedback':['Changed business rule','Updated examples','Aligned checks & messages'],
 'Risk-based testing':['Likelihood','Business consequences','Proportionate investigation'],
 'Maintainable automation':['Stable locators','Independent data','Meaningful assertions'],
 'Continuous improvement':['One clear experiment','An owner & action','Inspect what changed'],
 'Quadrant 1':['Technology-facing','Supports development','Unit & component checks'],
 'Quadrant 2':['Business-facing','Supports development','Acceptance examples'],
 'Quadrant 3':['Business-facing','Critiques the product','Exploration & usability'],
 'Quadrant 4':['Technology-facing','Critiques the product','Performance & security'],
 'Combined example':['Calculations & rules','Real customer journeys','Load, resilience & security'],
 'Accountabilities':['Product Owner','Scrum Master','Developers, including testers'],
 'Refinement and planning':['Clarify booking rules','Select a coherent goal','Include verification effort'],
 'During the sprint':['Small usable slices','API & integrated feedback','Collaborative defect resolution'],
 'Definition of Done':['Shared quality baseline','Required checks complete','Usable increment'],
 'Review and retrospective':['Review: inspect outcome','Retrospective: improve work','Adapt using evidence'],
 'Sprint walkthrough':['Clarify & implement','Test continuously','Inspect & improve'],
 'TDD':['RED • write a failing test','GREEN • make it pass','REFACTOR • keep it clear'],
 'BDD':['GIVEN • starting context','WHEN • an action','THEN • observable outcome'],
 'ATDD':['Agree acceptance examples','Build toward the examples','Verify business outcomes'],
 'Exploratory testing':['Set a charter','Follow observations','Record & debrief'],
 'Test design':['Equivalence partitions','Boundary values','Decision tables'],
 'Combining methods':['Clarify the rule','Select useful examples','Investigate interactions'],
 'Stories and criteria':['Customer goal','Observable outcomes','Authorization rules'],
 'Test cases':['Precondition & action','Expected result','Build & execution evidence'],
 'Defect reports':['Reproducible steps','Sanitized evidence','Linked requirement'],
 'Plans and charters':['Scope & risks','Focused mission','Coverage & observations'],
 'Traceability':['Requirement → Test','Defect → Fix','Retest → Release evidence'],
 'Practical document set':['Keep artifacts useful','Identify the current rule','Remove redundant copies'],
 'Visual workflow':['Ready → Development','Testing → Done','Visible queues & blockers'],
 'WIP limits':['Testing capacity: 3','Finish or unblock work','Pull when capacity exists'],
 'Flow metrics':['Cycle time','Work item age','Throughput & work in progress'],
 'Bottlenecks':['Inspect waiting','Find the contributing cause','Improve overall completion'],
 'Classes of service':['Explicit urgency policy','Visible interruptions','Protect ordinary flow'],
 'Maintenance example':['Assess the incident','Make the tradeoff visible','Fix, verify & learn'],
 'Issue tracking':['Story & expected behavior','Defect & sanitized evidence','Retest against a build'],
 'API testing':['Request & contract','Response & resulting state','Permissions & failure paths'],
 'Web and mobile automation':['Stable locators','Isolated setup','Critical customer journeys'],
 'Performance and security':['Realistic workload','Errors & response distributions','Authorized investigation'],
 'Continuous integration':['Commit → Build','Unit → Integration','Critical end-to-end checks'],
 'Automation strategy':['Risk & repeatability','Useful testing layers','Ownership & maintenance'],
 'Requirements':['Customer journey','Shared state & dependencies','High-impact failure examples'],
 'Sprint 1: Authentication':['Valid & invalid input','Concurrent registration','Sessions & recovery'],
 'Sprint 2: Booking':['One available slot','Competing requests','Exactly one reservation'],
 'Sprint 3: Payments':['Sandbox outcomes','Delayed & repeated callbacks','Safe retry & recovery'],
 'Regression and nonfunctional quality':['Protect earlier behavior','Load & accessibility','Authorization & resilience'],
 'Release and monitoring':['Evidence for this build','Outstanding risks','Deploy, observe & recover'],
};

export function Lesson({ chapter, duration }) {
 const root=useRef(null);
 const [view,setView]=useState(0);
 useEffect(()=>{
   const timers=[1,2].map(v=>setTimeout(()=>setView(v),duration*v/3*1000));
   return ()=>timers.forEach(clearTimeout);
 },[duration]);
 const concept=MAP[chapter.title]||lesson.visual.steps;
 const labels=view===1?lesson.visual.checks:view===2?[...concept.slice(0,2),lesson.visual.result]:concept;
 const isMatrix=/quadrant/i.test(chapter.title);
 useGSAP(()=>{gsap.fromTo('.path-line',{strokeDashoffset:1},{strokeDashoffset:0,duration:1.1,ease:'power2.out',delay:.2});},{scope:root,dependencies:[view]});
 const chapterNumber=lesson.chapters.findIndex(c=>c.id===chapter.id)+1;
 const displayTitle=/^(Hook and introduction|Introduction)$/.test(chapter.title)?lesson.topic:chapter.title;
 const summary=(chapter.text.match(/^.*?[.!?](?:\s|$)/)?.[0]||lesson.visual.result).trim();
 return <div className="scene" ref={root}>
   <div className="safe">
    <header><div className="brand"><FlaskConical size={32}/><span>TECH IN <b>60</b></span></div><div className="course">AGILE TESTING MASTERCLASS <span>EP {String(lesson.episode).padStart(2,'0')} / 12</span></div></header>
    <div className="lesson-content" key={view}>
     <section className="title-area">
      <motion.div className="eyebrow" initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} transition={{duration:.5}}><span className="dot"/> {view===0?'UNDERSTAND':view===1?'WORKED EXAMPLE':'CONNECT THE EVIDENCE'}</motion.div>
      <motion.h1 initial={{opacity:0,y:22}} animate={{opacity:1,y:0}} transition={{duration:.65,delay:.1}}>{displayTitle}</motion.h1>
      <motion.p className="context" initial={{opacity:0}} animate={{opacity:1}} transition={{duration:.6,delay:.35}}>{view===1?lesson.visual.example:view===2?lesson.visual.question:summary}</motion.p>
      <div className="case-label"><Target size={24}/><span>{lesson.visual.example}</span></div>
      <div className="chapter-index"><span>{String(chapterNumber).padStart(2,'0')}</span><div><b>CHAPTER {chapterNumber} OF {lesson.chapters.length}</b><p>{lesson.topic}</p></div></div>
     </section>
     <section className={'diagram '+(isMatrix?'matrix-mode':'')}>
      <div className="diagram-header"><span>{view===1?'FICTIONAL SCENARIO':'RISK → EXAMPLES → EVIDENCE'}</span><ArrowUpRight size={26}/></div>
      {isMatrix?<div className="quadrants">{[['Q1','Unit & component','Technology • Support'],['Q2','Acceptance examples','Business • Support'],['Q3','Exploration & usability','Business • Critique'],['Q4','Performance & security','Technology • Critique']].map(([n,label,sub],i)=><motion.div className={'quadrant q'+i} key={n} initial={{opacity:0,scale:.95}} animate={{opacity:1,scale:1}} transition={{duration:.55,delay:.15+i*.2}}><b>{n}</b><strong>{label}</strong><small>{sub}</small></motion.div>)}</div>:
      <div className="flow">
       <svg className="connectors" width="50" height="390" viewBox="0 0 50 390"><path className="path-line" d="M25 25 L25 365" pathLength="1" strokeDasharray="1" fill="none" stroke="#5BE7C4" strokeWidth="2"/></svg>
       {labels.map((label,i)=><motion.div className={'flow-card card-'+i} key={i} initial={{opacity:0,x:26}} animate={{opacity:1,x:0}} transition={{duration:.6,delay:.15+i*.35}}><span className="step">{view===1?<Check size={25}/>:String(i+1).padStart(2,'0')}</span><strong>{label}</strong><span className="status-dot"/></motion.div>)}
      </div>}
      <motion.div className="insight" initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} transition={{duration:.6,delay:1.4}}><ShieldCheck size={32}/><span>{view===1?lesson.visual.question:lesson.visual.result}</span></motion.div>
     </section>
    </div>
    <footer><span>EXAMPLES USE FICTIONAL APPLICATIONS & SYNTHETIC DATA</span><span>LEARN · PRACTICE · INSPECT</span></footer>
   </div>
 </div>;
}
