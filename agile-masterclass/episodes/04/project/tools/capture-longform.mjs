// Frame-exact React capture. Static holds use ffconcat durations rather than
// screenshotting an identical screen thousands of times. Output remains 30 fps.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import puppeteer from 'puppeteer-core';
import {findChrome} from './find-chrome.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const lesson=JSON.parse(fs.readFileSync(path.join(root,'lesson.json'),'utf8'));
const dest=process.env.AGILE_EPISODE_DIR?path.resolve(process.env.AGILE_EPISODE_DIR):path.resolve(root,'../episodes',String(lesson.episode).padStart(2,'0'));
const stills=process.argv.includes('--stills');
const out=path.join(dest,stills?'stills':'frames');fs.mkdirSync(out,{recursive:true});
const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.woff2':'font/woff2','.json':'application/json'};
const server=http.createServer((req,res)=>{
 const pathname=decodeURIComponent(new URL(req.url,'http://x').pathname);
 const file=path.resolve(root,'dist','.'+(pathname==='/'?'/index.html':pathname));
 if(!file.startsWith(path.join(root,'dist')+path.sep)||!fs.existsSync(file)){res.writeHead(404);res.end();return;}
 res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream'});fs.createReadStream(file).pipe(res);
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await puppeteer.launch({executablePath:findChrome(),headless:true,args:['--no-sandbox','--hide-scrollbars','--mute-audio','--force-device-scale-factor=1']});
const page=await browser.newPage();await page.setViewport({width:1920,height:1080,deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.url()));
await page.evaluateOnNewDocument(fs.readFileSync(path.join(root,'tools/time-shim.js'),'utf8'));
await page.goto(`http://127.0.0.1:${server.address().port}/?capture=1`,{waitUntil:'load'});
let info;
for(let i=0;i<100;i++){info=await page.evaluate(()=>window.__VIDEO__?.ready?window.__VIDEO__:null);if(info)break;await new Promise(r=>setTimeout(r,50));}
if(!info||Math.abs(info.duration-600)>.001)throw Error('Invalid player timeline');
const client=await page.createCDPSession();
const advance=t=>page.evaluate(ms=>window.__vt.advance(ms),t*1000);
const grab=async(file,png=false)=>{
 const {data}=await client.send('Page.captureScreenshot',{format:png?'png':'jpeg',quality:png?undefined:93,optimizeForSpeed:true,captureBeyondViewport:false});
 fs.writeFileSync(file,Buffer.from(data,'base64'));
};
async function layout(){
 const problems=await page.evaluate(()=>{
  const issues=[];
  const safe=[...document.querySelectorAll('.safe')].at(-1);
  if(!safe)return ['Missing scene'];
  for(const el of safe.querySelectorAll('h1,.context,.flow-card,.insight,.quadrant,.chapter-index')){
   const r=el.getBoundingClientRect();
   if(r.left<70||r.right>1850||r.top<135||r.bottom>965)issues.push(el.className||el.tagName);
   if(el.scrollWidth>el.clientWidth+4||el.scrollHeight>el.clientHeight+4)issues.push('Overflow '+el.className);
  }return issues;
 });
 if(problems.length)throw Error('Layout failed: '+problems.join(', '));
}
try{
 let captures=[];
 for(const [ci,c] of lesson.chapters.entries()){
  const views=stills?[0,1,2]:[0,1,2];
  for(const v of views){
   const begin=c.start+c.duration*v/3;
   await advance(begin);
   const frames=stills?73:73;
   for(let f=0;f<=frames;f++){
    const t=begin+f/30;
    if(t>=600)break;
    await advance(t);
    if(stills&&f!==frames&&!(ci===0&&v===0&&f===12))continue;
    if(!stills&&f%2===1&&f!==frames)continue;
    const name=stills?`${String(ci+1).padStart(2,'0')}-${v}-${f===12?'motion':'settled'}.png`:`${String(captures.length).padStart(5,'0')}.jpg`;
    const file=path.join(out,name);await grab(file,stills);
    if(!stills)captures.push({file,t});
   }
   await layout();
  }
  console.log(`E${lesson.episode} ${stills?'stills':'captured'} ${ci+1}/${lesson.chapters.length}: ${c.title}`);
 }
 if(errors.length)throw Error('Browser errors: '+[...new Set(errors)].join('; '));
 await browser.close();await new Promise(r=>server.close(r));
 if(stills){
  const selected=lesson.chapters.map((_,i)=>path.join(out,`${String(i+1).padStart(2,'0')}-0-settled.png`));
  const list=path.join(out,'contact.ffconcat');
  fs.writeFileSync(list,'ffconcat version 1.0\n'+selected.map(f=>`file '${f.replaceAll("'","'\\''")}'\nduration 1\n`).join(''));
  const r=spawnSync('ffmpeg',['-y','-v','error','-safe','0','-f','concat','-i',list,'-vf',`scale=640:360,tile=3x${Math.ceil(selected.length/3)}:padding=10:margin=10:color=0x203044`,'-frames:v','1',path.join(dest,'contact.png')],{encoding:'utf8'});
  if(r.status)throw Error(r.stderr);console.log('STILLS PASSED',dest);
 }else{
  const list=path.join(out,'frames.ffconcat');
  let content='ffconcat version 1.0\n';
  captures.forEach((shot,i)=>{const end=captures[i+1]?.t??600;content+=`file '${shot.file.replaceAll("'","'\\''")}'\noption framerate 30\nduration ${(end-shot.t).toFixed(9)}\n`;});
  content+=`file '${captures.at(-1).file.replaceAll("'","'\\''")}'\noption framerate 30\n`;
  fs.writeFileSync(list,content);
  console.log('CAPTURE COMPLETE',list);
 }
}catch(error){await browser.close().catch(()=>{});server.close();throw error;}
process.exit(0);
