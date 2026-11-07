// Smoke-test the actual Unity Web player with native browser input in an isolated profile.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {spawn,spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';

const out=path.resolve('docs/production/validation/unity-art');
const profile=await fs.mkdtemp(path.join(os.tmpdir(),'roomturn-web-art-'));
const chrome=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',[
  '--headless=new','--no-first-run','--no-default-browser-check','--remote-debugging-port=0',
  `--user-data-dir=${profile}`,'--enable-unsafe-swiftshader','--use-angle=swiftshader','about:blank',
],{stdio:['ignore','ignore','pipe']});
chrome.stderr.resume();
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let socket;
try {
  let port;
  for(let i=0;i<150;i++) {
    const data=await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8').catch(()=>null);
    if(data){port=Number(data.split('\n')[0]);break;}
    if(chrome.exitCode!==null)throw new Error('Chrome exited at startup');
    await sleep(100);
  }
  if(!port)throw new Error('No isolated Chrome endpoint');
  const targets=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  socket=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
  let next=0;
  const pending=new Map();
  const exceptions=[];
  const consoleErrors=[];
  const messages=[];
  socket.onmessage=event=>{
    const data=JSON.parse(event.data);
    if(data.id){const request=pending.get(data.id);if(request){clearTimeout(request.timer);pending.delete(data.id);data.error?request.reject(new Error(JSON.stringify(data.error))):request.resolve(data.result);}}
    if(data.method==='Runtime.exceptionThrown')exceptions.push(data.params.exceptionDetails);
    if(data.method==='Runtime.consoleAPICalled'){
      const value=data.params.args.map(a=>a.value??a.description??'').join(' ');
      if(data.params.type==='error')consoleErrors.push(value);
      if(messages.length<200)messages.push(value.slice(0,1600));
    }
  };
  const call=(method,params={})=>new Promise((resolve,reject)=>{
    const id=++next;const timer=setTimeout(()=>{pending.delete(id);reject(new Error('CDP timeout: '+method));},90000);
    pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params}));
  });
  const evaluate=async expression=>{
    const result=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
    if(result.exceptionDetails)throw new Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  await call('Runtime.enable');await call('Page.enable');
  await call('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
  await call('Emulation.setFocusEmulationEnabled',{enabled:true});
  await call('Page.bringToFront');
  await call('Page.navigate',{url:'http://127.0.0.1:18769/'});
  const started=Date.now();
  let ready=false;
  for(let i=0;i<480;i++){
    ready=await evaluate(`document.getElementById('loading')?.style.display==='none'`).catch(()=>false);
    if(ready)break;
    if(exceptions.length)throw new Error('Unity page exception: '+JSON.stringify(exceptions));
    if(i%30===0)console.log('Waiting for Unity player',Math.round((Date.now()-started)/1000),'s');
    await sleep(500);
  }
  if(!ready)throw new Error('Unity player did not become ready: '+await evaluate(`document.getElementById('status')?.textContent`));
  const loadSeconds=(Date.now()-started)/1000;
  const shots=[];
  const ocr=async name=>{
    const result=spawnSync('/usr/bin/swift',['-module-cache-path','/tmp/roomturn-web-vision-cache','tools/ocr_web.swift',path.join(out,name+'.png')],{encoding:'utf8',timeout:60000});
    if(result.status!==0)throw new Error('Screenshot OCR failed: '+JSON.stringify({status:result.status,signal:result.signal,error:result.error?.message,stderr:result.stderr}));
    return JSON.parse(result.stdout);
  };
  const capture=async name=>{
    const data=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    const bytes=Buffer.from(data.data,'base64');
    await fs.writeFile(path.join(out,name+'.png'),bytes);
    const result={name,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')};shots.push(result);return result;
  };
  let sceneRendered=false;
  for(let i=0;i<20;i++){
    const frame=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    const pixels=Buffer.from(frame.data,'base64');
    await fs.writeFile(path.join(out,'browser-ready.png'),pixels);
    // This textured fixture is >100 KB; the Unity splash is a nearly flat 23 KB image.
    if(pixels.length>100000){sceneRendered=true;break;}
    await sleep(500);
  }
  if(!sceneRendered)throw new Error('Unity startup completed but the playable scene was not rendered');
  console.log('Playable scene rendered after',Math.round((Date.now()-started)/1000),'s');
  await evaluate(`document.getElementById('unity-canvas').focus()`);
  await call('Input.dispatchMouseEvent',{type:'mousePressed',x:720,y:450,button:'left',clickCount:1});
  await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:720,y:450,button:'left',clickCount:1});
  await sleep(300);
  let pointerLocked=await evaluate(`document.pointerLockElement?.id==='unity-canvas'`);
  for(let i=0;i<3&&!pointerLocked;i++){
    await call('Input.dispatchMouseEvent',{type:'mousePressed',x:720,y:450,button:'left',clickCount:1});
    await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:720,y:450,button:'left',clickCount:1});
    await sleep(500);
    pointerLocked=await evaluate(`document.pointerLockElement?.id==='unity-canvas'`);
  }
  await capture('browser-start');
  const key=async(code,key,virtual,duration=100)=>{
    await call('Input.dispatchKeyEvent',{type:'keyDown',code,key,windowsVirtualKeyCode:virtual,nativeVirtualKeyCode:virtual});
    await sleep(duration);
    await call('Input.dispatchKeyEvent',{type:'keyUp',code,key,windowsVirtualKeyCode:virtual,nativeVirtualKeyCode:virtual});
    await sleep(800);
  };
  await key('KeyW','w',87,500);await capture('browser-moved');
  await key('ArrowRight','ArrowRight',39);await capture('browser-turned');
  await key('KeyR','r',82);await sleep(1200);
  await key('ArrowRight','ArrowRight',39);
  await key('KeyW','w',87,350);
  await key('KeyD','d',68,150);
  await capture('browser-interaction-aim');
  const aimText=await ocr('browser-interaction-aim');
  await key('KeyE','e',69);
  await capture('browser-interacted');
  const interactionText=await ocr('browser-interacted');
  const interactionObserved=interactionText.some(line=>line.includes('门锁着')||line.includes('先寻找出口钥匙'));
  await key('KeyR','r',82);await sleep(1800);await capture('browser-restarted');
  const resetText=await ocr('browser-restarted');
  const imageResult=spawnSync('python3',['-c',`from PIL import Image,ImageChops
import json,sys
from pathlib import Path
p=Path(sys.argv[1]); a=Image.open(p/'browser-start.png').convert('RGB'); b=Image.open(p/'browser-restarted.png').convert('RGB'); c=Image.open(p/'browser-moved.png').convert('RGB')
def fraction(x,y):
 d=ImageChops.difference(x,y).convert('L');return sum(n for i,n in enumerate(d.histogram()) if i>12)/(d.width*d.height)
print(json.dumps({'restartChangedFraction':fraction(a,b),'movementChangedFraction':fraction(a,c)}))`,out],{encoding:'utf8'});
  if(imageResult.status!==0)throw new Error('Image comparison failed: '+imageResult.stderr);
  const imageMetrics=JSON.parse(imageResult.stdout);
  const restartObserved=imageMetrics.restartChangedFraction<.02&&resetText.some(line=>line.includes('照片背面')||line.includes('爷爷总从太阳'));
  const result={ready,sceneRendered,pointerLocked,loadSeconds,shots,exceptions,consoleErrors,messages,
    movementFrameChanged:shots[0].sha256!==shots[1].sha256,turnFrameChanged:shots[1].sha256!==shots[2].sha256,
    aimText,interactionText,interactionObserved,resetText,restartObserved,imageMetrics,
    scope:'Actual Unity Web loading, Chinese UI, pointer lock, movement, 90-degree turn, E interaction with a real locked door, and restart restoring the starting view/message. Full puzzle chain is separately verified by Unity PlayMode.'};
  result.passed=ready&&pointerLocked&&result.movementFrameChanged&&result.turnFrameChanged&&imageMetrics.movementChangedFraction>.02&&interactionObserved&&restartObserved&&exceptions.length===0&&consoleErrors.length===0;
  await fs.writeFile(path.join(out,'browser-check.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({...result,messages:undefined}));
  if(!result.passed)throw new Error('Unity browser acceptance failed; inspect browser-check.json and screenshots');
}finally{
  socket?.close();chrome.kill('SIGTERM');
  await new Promise(resolve=>chrome.exitCode!==null?resolve():chrome.once('exit',resolve));
  await fs.rm(profile,{recursive:true,force:true});
}
