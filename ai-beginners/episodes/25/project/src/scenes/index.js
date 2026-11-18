import React from 'react';
import { Lesson } from './Lesson.jsx';
import lesson from '../../lesson.json';
export const scenes=lesson.chapters.map(chapter=>({id:chapter.id,duration:chapter.duration,transition:'cut',component:({duration})=>React.createElement(Lesson,{chapter,duration})}));
