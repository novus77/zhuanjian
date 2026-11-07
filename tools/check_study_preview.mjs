// Inspect the packaged offline viewer in an isolated headless Chrome profile.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {spawn} from 'node:child_process';
import {pathToFileURL} from 'node:url';

const out=path.resolve('models/blender/study-room-v1');
const profile=await fs.mkdtemp(path.join(os.tmpdir(),'roomturn-preview-'));
const chrome=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',[
  '--headless=new','--no-first-run','--no-default-browser-check',
  '--remote-debugging-port=0',`--user-data-dir=${profile}`,
  '--enable-unsafe-swiftshader','--use-angle=swiftshader','about:blank',
],{stdio:['ignore','ignore','pipe']});
const errors=[];
chrome.stderr.on('data',chunk=>{
  const value=chunk.toString();
  if(value.includes('ERROR') && errors.length<12) errors.push(value.slice(0,600));
});
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let socket;
try {
  let port;
  for(let i=0;i<150;i++) {
    const value=await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8').catch(()=>null);
    if(value) {port=Number(value.split('\n')[0]);break;}
    if(chrome.exitCode!==null) throw new Error('Headless Chrome exited during startup');
    await sleep(100);
  }
  if(!port) throw new Error('No isolated DevTools endpoint');
  const targets=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  socket=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
  let sequence=0;
  const pending=new Map();
  const pageErrors=[];
  socket.onmessage=event=>{
    const message=JSON.parse(event.data);
    if(message.id) {
      const waiter=pending.get(message.id);
      if(waiter) {
        clearTimeout(waiter.timer);pending.delete(message.id);
        if(message.error) waiter.reject(new Error(JSON.stringify(message.error)));
        else waiter.resolve(message.result);
      }
    }
    if(message.method==='Runtime.exceptionThrown') pageErrors.push(message.params.exceptionDetails.text);
  };
  const call=(method,params={})=>new Promise((resolve,reject)=>{
    const id=++sequence;
    const timer=setTimeout(()=>{pending.delete(id);reject(new Error('CDP timeout: '+method));},90000);
    pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params}));
  });
  const evaluate=async expression=>{
    const result=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
    if(result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  await call('Runtime.enable');
  await call('Page.enable');
  await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:pathToFileURL(path.join(out,'delivery-v2/preview.html')).href});
  let states=[];
  for(let i=0;i<180;i++) {
    states=await evaluate(`Array.from(document.querySelectorAll('.viewport')).map(v=>({state:v.dataset.previewState,label:v.getAttribute('aria-label')}))`).catch(()=>[]);
    if(states.length===10 && states.every(v=>v.state==='ready'||v.state==='loading')) {
      const allReady=await evaluate(`Array.from(document.querySelectorAll('.viewport')).every(v=>v.dataset.previewState==='ready'||v.querySelector('.reset'))`);
      if(allReady)break;
    }
    if(states.some(v=>v.state==='error')) throw new Error('Viewer reported model error: '+JSON.stringify(states));
    await sleep(500);
  }
  const interactions=[];
  // Scroll each individual source and the assembled scene into view, then rotate and zoom.
  for(let i=0;i<10;i++) {
    const rect=await evaluate(`(()=>{const v=document.querySelectorAll('.viewport')[${i}];v.scrollIntoView({block:'center'});const r=v.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()`);
    await sleep(200);
    const before=await evaluate(`Number(document.querySelectorAll('.viewport')[${i}].dataset.interactions||0)`);
    await call('Input.dispatchMouseEvent',{type:'mousePressed',x:rect.x,y:rect.y,button:'left',clickCount:1});
    await call('Input.dispatchMouseEvent',{type:'mouseMoved',x:rect.x+65,y:rect.y+18,button:'left',buttons:1});
    await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:rect.x+65,y:rect.y+18,button:'left',clickCount:1});
    await call('Input.dispatchMouseEvent',{type:'mouseWheel',x:rect.x,y:rect.y,deltaX:0,deltaY:-100});
    await sleep(300);
    const after=await evaluate(`({count:Number(document.querySelectorAll('.viewport')[${i}].dataset.interactions||0),state:document.querySelectorAll('.viewport')[${i}].dataset.previewState})`);
    interactions.push({index:i,before,after:after.count,state:after.state,passed:after.count>before&&after.state==='ready'});
  }
  await evaluate(`document.querySelector('.scene-card').scrollIntoView({block:'center'})`);
  await sleep(1000);
  const screenshot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  await fs.writeFile(path.join(out,'renders/offline-preview-check.png'),Buffer.from(screenshot.data,'base64'));
  const result={views:states,interactions,pageErrors,passed:interactions.length===10&&interactions.every(v=>v.passed)&&pageErrors.length===0,scope:'Isolated headless Chrome; model load, orbit and wheel verified. Mirrors here are generic PBR surfaces, not Unity puzzle reflections.'};
  await fs.writeFile(path.join(out,'records/preview-check.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result));
} finally {
  socket?.close();
  chrome.kill('SIGTERM');
  await new Promise(resolve=>chrome.exitCode!==null?resolve():chrome.once('exit',resolve));
  await fs.rm(profile,{recursive:true,force:true});
}
