import React from 'react';
import { createRoot } from 'react-dom/client';
import '@fontsource-variable/inter';
import './theme.css';
import { Player } from './engine/Player.jsx';
import { scenes } from './scenes/index.js';
import {imageFiles} from './scenes/Story.jsx';

// No <StrictMode>: its double-mount in dev would start every scene animation twice.
async function start(){
 await Promise.all(imageFiles.map(file=>new Promise((resolve,reject)=>{const img=new Image();img.onload=resolve;img.onerror=()=>reject(new Error('Image failed: '+file));img.src='/images/'+file})));
 createRoot(document.getElementById('root')).render(<Player scenes={scenes} />);
}
start().catch(e=>{console.error(e);document.body.textContent=e.message});
