import * as THREE from 'three';
import './style.css';

// ---------------------------------------------------------------------------
// DOM
// ---------------------------------------------------------------------------

const $ = <T extends HTMLElement>(selector: string) => document.querySelector(selector) as T;

const app = $('#app');
const compassEl = $('#compass');
const promptEl = $('#prompt');
const winEl = $('#win');
const startEl = $('#start');
const soundBtn = $('#btn-sound');

// ---------------------------------------------------------------------------
// Renderer / scene / first-person camera
// ---------------------------------------------------------------------------

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0806);
scene.fog = new THREE.FogExp2(0x0b0806, 0.014);

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.05, 100);
camera.rotation.order = 'YXZ';

// ---------------------------------------------------------------------------
// Lights
// ---------------------------------------------------------------------------

scene.add(new THREE.HemisphereLight(0xffe2b8, 0x1a110b, 0.9));

const keyLight = new THREE.DirectionalLight(0xffd39a, 3.2);
keyLight.position.set(7, 12, 6);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(2048, 2048);
keyLight.shadow.camera.left = -10;
keyLight.shadow.camera.right = 10;
keyLight.shadow.camera.top = 10;
keyLight.shadow.camera.bottom = -10;
keyLight.shadow.camera.near = 1;
keyLight.shadow.camera.far = 40;
scene.add(keyLight);

const rimLight = new THREE.PointLight(0xff8b42, 35, 22, 2);
rimLight.position.set(-6, 5.5, -6);
scene.add(rimLight);

// ---------------------------------------------------------------------------
// Materials
// ---------------------------------------------------------------------------

const wallMat = new THREE.MeshStandardMaterial({
  color: 0xcfc0a8,
  roughness: 0.95,
  transparent: true,
  opacity: 0.72,
  side: THREE.DoubleSide,
});
const floorMat = new THREE.MeshStandardMaterial({ color: 0x6a4a2e, roughness: 0.86, metalness: 0.04 });
const ceilingMat = new THREE.MeshStandardMaterial({
  color: 0x2b1d13,
  roughness: 1,
  transparent: true,
  opacity: 0.6,
  side: THREE.DoubleSide,
});
const frameMat = new THREE.MeshStandardMaterial({ color: 0x4a2f1b, roughness: 0.7 });
const brassMat = new THREE.MeshStandardMaterial({ color: 0xc9974f, roughness: 0.3, metalness: 0.75 });
const darkWoodMat = new THREE.MeshStandardMaterial({ color: 0x5b3a20, roughness: 0.62, metalness: 0.06 });
const chairMat = new THREE.MeshStandardMaterial({ color: 0x7b4f2d, roughness: 0.8 });
const crateMat = new THREE.MeshStandardMaterial({ color: 0x8a6740, roughness: 0.85 });

// ---------------------------------------------------------------------------
// Room shell
// ---------------------------------------------------------------------------

const room = new THREE.Group();
// A rectangular room (not a cube): 7.5m x 4.9m x 4.2m in world scale.
room.position.set(0, 2.1, 0);
room.scale.set(1.25, 0.7, 0.82);
scene.add(room);

const ROOM = 6;
const HALF = ROOM / 2;
const PLAYER_LIMIT_X = 3.1;
const PLAYER_LIMIT_Z = 1.9;

const pedestal = new THREE.Mesh(
  new THREE.CylinderGeometry(5.4, 5.7, 0.25, 64),
  new THREE.MeshStandardMaterial({ color: 0x24170f, roughness: 0.9 }),
);
pedestal.position.set(0, -0.22, 0);
pedestal.receiveShadow = true;
scene.add(pedestal);

const pedestalRing = new THREE.Mesh(new THREE.TorusGeometry(5.35, 0.06, 8, 64), brassMat);
pedestalRing.rotation.x = Math.PI / 2;
pedestalRing.position.y = -0.08;
scene.add(pedestalRing);

const worldGrid = new THREE.GridHelper(18, 36, 0x3a2a1a, 0x24170f);
worldGrid.position.y = -0.09;
(worldGrid.material as THREE.Material).transparent = true;
(worldGrid.material as THREE.Material).opacity = 0.35;
scene.add(worldGrid);

function makeLabelSprite(text: string, color = '#d6a85f') {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 128;
  const ctx = canvas.getContext('2d')!;
  ctx.clearRect(0, 0, 128, 128);
  ctx.fillStyle = color;
  ctx.font = 'bold 72px Georgia, serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 64, 68);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false }));
  sprite.scale.set(0.9, 0.9, 1);
  return sprite;
}

for (const [text, x, z] of [
  ['N', 0, -5.35],
  ['E', 5.35, 0],
  ['S', 0, 5.35],
  ['W', -5.35, 0],
] as Array<[string, number, number]>) {
  const label = makeLabelSprite(text);
  label.position.set(x, 0.15, z);
  scene.add(label);
}

function addSlab(
  parent: THREE.Object3D,
  width: number,
  height: number,
  depth: number,
  x: number,
  y: number,
  z: number,
  material: THREE.Material,
  cast = false,
) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), material);
  mesh.position.set(x, y, z);
  mesh.castShadow = cast;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

addSlab(room, ROOM, 0.2, ROOM, 0, -3.1, 0, floorMat);
addSlab(room, ROOM, 0.1, ROOM, 0, 3.05, 0, ceilingMat);

// Four walls. East wall has a door opening.
addSlab(room, ROOM, ROOM, 0.1, 0, 0, -3.05, wallMat);
addSlab(room, ROOM, ROOM, 0.1, 0, 0, 3.05, wallMat);
addSlab(room, 0.1, ROOM, ROOM, -3.05, 0, 0, wallMat);

// East wall pieces around the door opening (opening: z -0.6..0.6, y -3..-0.6)
addSlab(room, 0.1, ROOM, 2.4, 3.05, 0, -1.8, wallMat);
addSlab(room, 0.1, ROOM, 2.4, 3.05, 0, 1.8, wallMat);
addSlab(room, 0.1, 3.6, 1.2, 3.05, 1.2, 0, wallMat);

// Colored inner face plates make it obvious which surface is currently "down".
const facePlateData: Array<{ color: number; position: [number, number, number]; rotation: [number, number, number]; opacity: number }> = [
  { color: 0x3f5863, position: [0, 0, -2.97], rotation: [0, 0, 0], opacity: 0.22 },
  { color: 0x8a6f45, position: [0, 0, 2.97], rotation: [0, Math.PI, 0], opacity: 0.22 },
  { color: 0x5f6b50, position: [-2.97, 0, 0], rotation: [0, Math.PI / 2, 0], opacity: 0.22 },
  { color: 0x2b1d13, position: [0, 2.97, 0], rotation: [Math.PI / 2, 0, 0], opacity: 0.16 },
];
for (const plate of facePlateData) {
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(5.9, 5.9),
    new THREE.MeshBasicMaterial({ color: plate.color, transparent: true, opacity: plate.opacity, side: THREE.DoubleSide, depthWrite: false }),
  );
  mesh.position.set(...plate.position);
  mesh.rotation.set(...plate.rotation);
  room.add(mesh);
}

// Door frame
addSlab(room, 0.12, 2.52, 0.12, 2.97, -1.74, -0.66, frameMat, true);
addSlab(room, 0.12, 2.52, 0.12, 2.97, -1.74, 0.66, frameMat, true);
addSlab(room, 0.12, 0.12, 1.44, 2.97, -0.54, 0, frameMat, true);

// Room outline + floor grid
const outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(ROOM, ROOM, ROOM)),
  new THREE.LineBasicMaterial({ color: 0xb08a54, transparent: true, opacity: 0.55 }),
);
room.add(outline);

const grid = new THREE.GridHelper(ROOM, 12, 0xb08a54, 0x4b3624);
grid.position.y = -2.985;
(grid.material as THREE.Material).transparent = true;
(grid.material as THREE.Material).opacity = 0.28;
room.add(grid);

// ---------------------------------------------------------------------------
// Door
// ---------------------------------------------------------------------------

function makeSymbolTexture(symbol: string, color = '#e7c07a') {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 256;
  const ctx = canvas.getContext('2d')!;
  ctx.clearRect(0, 0, 256, 256);
  ctx.strokeStyle = color;
  ctx.lineWidth = 10;
  ctx.beginPath();
  ctx.arc(128, 128, 100, 0, Math.PI * 2);
  ctx.stroke();
  ctx.fillStyle = color;
  ctx.font = 'bold 118px Georgia, serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(symbol, 128, 138);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

const doorPivot = new THREE.Group();
doorPivot.position.set(3.0, -3, -0.6);
room.add(doorPivot);

const doorLeaf = new THREE.Mesh(new THREE.BoxGeometry(0.08, 2.4, 1.2), darkWoodMat);
doorLeaf.position.set(0.04, 1.2, 0.6);
doorLeaf.castShadow = true;
doorPivot.add(doorLeaf);

const doorHandle = new THREE.Mesh(new THREE.SphereGeometry(0.07, 12, 10), brassMat);
doorHandle.position.set(0.12, 1.1, 1.05);
doorPivot.add(doorHandle);

const doorSymbol = new THREE.Mesh(
  new THREE.PlaneGeometry(0.46, 0.46),
  new THREE.MeshBasicMaterial({ map: makeSymbolTexture('☀'), transparent: true, side: THREE.DoubleSide }),
);
doorSymbol.position.set(0.095, 1.55, 0.6);
doorSymbol.rotation.y = Math.PI / 2;
doorPivot.add(doorSymbol);

// ---------------------------------------------------------------------------
// Corridor (fixed at north)
// ---------------------------------------------------------------------------

const corridor = new THREE.Group();
corridor.position.set(0, 0, -4.8);
scene.add(corridor);

addSlab(corridor, 4.2, 0.2, 3.4, 0, -0.1, 0, floorMat);
addSlab(corridor, 0.15, 1.1, 3.4, -2.05, 0.45, 0, wallMat);
addSlab(corridor, 0.15, 1.1, 3.4, 2.05, 0.45, 0, wallMat);
addSlab(corridor, 4.2, 3.4, 0.15, 0, 2.0, -1.6, wallMat);

const portalGlow = new THREE.Mesh(
  new THREE.PlaneGeometry(2.2, 3.0),
  new THREE.MeshBasicMaterial({ color: 0xffc57a, transparent: true, opacity: 0.22, side: THREE.DoubleSide }),
);
portalGlow.position.set(0, 1.6, -1.51);
corridor.add(portalGlow);

const corridorLight = new THREE.PointLight(0xffb066, 25, 12, 2);
corridorLight.position.set(0, 2, -1);
corridor.add(corridorLight);

// ---------------------------------------------------------------------------
// Player: first-person explorer + third-person avatar
// ---------------------------------------------------------------------------

const PLAYER_HEIGHT = 0.5;
const EYE_HEIGHT = 0.45;
const MOVE_SPEED = 1.2;
const PLAYER_START = new THREE.Vector3(-1.35, 0, 0.8);

// Invisible world-space anchor for movement/collision.
const player = new THREE.Object3D();
player.position.copy(PLAYER_START);
scene.add(player);

// Visible only in third-person mode.
const avatar = new THREE.Group();
avatar.position.copy(PLAYER_START);
scene.add(avatar);
const avatarBody = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.2, 0.5, 12), brassMat);
avatarBody.position.y = 0.25;
avatarBody.castShadow = true;
avatar.add(avatarBody);
const avatarHead = new THREE.Mesh(new THREE.SphereGeometry(0.14, 16, 12), brassMat);
avatarHead.position.y = 0.62;
avatarHead.castShadow = true;
avatar.add(avatarHead);
const avatarKey = new THREE.Mesh(new THREE.TorusGeometry(0.09, 0.018, 8, 16), brassMat);
avatarKey.position.set(0, 0.28, -0.2);
avatarKey.rotation.x = Math.PI / 2;
avatar.add(avatarKey);
const avatarEyeMat = new THREE.MeshBasicMaterial({ color: 0xffe9b0 });
const avatarEyeGeo = new THREE.SphereGeometry(0.022, 8, 8);
const avatarEyeL = new THREE.Mesh(avatarEyeGeo, avatarEyeMat);
avatarEyeL.position.set(0.055, 0.66, 0.12);
avatar.add(avatarEyeL);
const avatarEyeR = new THREE.Mesh(avatarEyeGeo, avatarEyeMat);
avatarEyeR.position.set(-0.055, 0.66, 0.12);
avatar.add(avatarEyeR);
avatar.visible = false;

let mode: 'first' | 'third' = 'first';
let yaw = -Math.PI / 2;
let pitch = -0.05;
let thirdYaw = Math.PI * 0.25;
let thirdPitch = 0.85;
const THIRD_RADIUS = 3.6;

function getFirstCameraPose() {
  const position = new THREE.Vector3(player.position.x, EYE_HEIGHT, player.position.z);
  const quaternion = new THREE.Quaternion().setFromEuler(new THREE.Euler(pitch, yaw, 0, 'YXZ'));
  return { position, quaternion };
}

function getThirdCameraPose() {
  // Whole-room view from just under the ceiling, inside the room (not outside).
  const target = new THREE.Vector3(0, 0.8, 0);
  const position = new THREE.Vector3(
    target.x + Math.sin(thirdYaw) * Math.cos(thirdPitch) * THIRD_RADIUS,
    target.y + Math.sin(thirdPitch) * THIRD_RADIUS,
    target.z + Math.cos(thirdYaw) * Math.cos(thirdPitch) * THIRD_RADIUS,
  );
  const quaternion = new THREE.Quaternion();
  const matrix = new THREE.Matrix4().lookAt(position, target, new THREE.Vector3(0, 1, 0));
  quaternion.setFromRotationMatrix(matrix);
  return { position, quaternion };
}

function updateCamera() {
  const pose = mode === 'first' ? getFirstCameraPose() : getThirdCameraPose();
  const targetFov = mode === 'first' ? 70 : 95;
  if (camera.fov !== targetFov) {
    camera.fov = targetFov;
    camera.updateProjectionMatrix();
  }
  camera.position.copy(pose.position);
  camera.quaternion.copy(pose.quaternion);
}

function applyViewMaterials() {
  const third = mode === 'third';
  wallMat.opacity = third ? 0.14 : 0.72;
  ceilingMat.opacity = third ? 0.15 : 0.6;
}

function toggleView() {
  if (isRotating) return;
  mode = mode === 'first' ? 'third' : 'first';
  if (mode === 'third') {
    if (document.pointerLockElement === renderer.domElement) document.exitPointerLock();
    avatar.visible = true;
    document.body.classList.add('third-person');
  } else {
    avatar.visible = false;
    document.body.classList.remove('third-person');
  }
  applyViewMaterials();
  refreshGizmo();
  updateCompass();
  updateLookHint();
  updateCamera();
}

// ---------------------------------------------------------------------------
// Loose furniture
// ---------------------------------------------------------------------------

function makeCrate() {
  const group = new THREE.Group();
  const box = new THREE.Mesh(new THREE.BoxGeometry(0.68, 0.68, 0.68), crateMat);
  box.castShadow = true;
  box.receiveShadow = true;
  group.add(box);
  const bandMat = new THREE.MeshStandardMaterial({ color: 0x3e2a18, roughness: 0.8 });
  for (const z of [-0.25, 0.25]) {
    const band = new THREE.Mesh(new THREE.BoxGeometry(0.72, 0.08, 0.08), bandMat);
    band.position.set(0, 0, z);
    group.add(band);
  }
  group.position.set(2.0, -3 + 0.34, 1.45);
  group.userData.halfHeight = 0.34;
  return group;
}

function makeChair() {
  const group = new THREE.Group();
  const seat = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.08, 0.5), chairMat);
  seat.position.y = 0.18;
  seat.castShadow = true;
  group.add(seat);
  const back = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.62, 0.07), chairMat);
  back.position.set(0, 0.49, -0.215);
  back.castShadow = true;
  group.add(back);
  for (const [x, z] of [
    [-0.19, -0.19],
    [0.19, -0.19],
    [-0.19, 0.19],
    [0.19, 0.19],
  ]) {
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.36, 0.05), chairMat);
    leg.position.set(x, -0.03, z);
    group.add(leg);
  }
  group.position.set(-1.9, -3 + 0.45, 1.3);
  group.userData.halfHeight = 0.45;
  return group;
}

function makeRug() {
  const rug = new THREE.Mesh(
    new THREE.PlaneGeometry(3.4, 2.2),
    new THREE.MeshStandardMaterial({ color: 0x6b3f2a, roughness: 0.95 }),
  );
  rug.rotation.x = -Math.PI / 2;
  rug.position.set(0.2, -2.97, 0.4);
  rug.receiveShadow = true;
  return rug;
}

function makeBed() {
  const group = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.38, 1.45), chairMat);
  body.position.y = 0.19;
  body.castShadow = true;
  group.add(body);
  const mattress = new THREE.Mesh(new THREE.BoxGeometry(2.05, 0.16, 1.3), new THREE.MeshStandardMaterial({ color: 0xd9c7aa, roughness: 0.9 }));
  mattress.position.y = 0.44;
  group.add(mattress);
  const pillow = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.12, 0.6), new THREE.MeshStandardMaterial({ color: 0xf0e2c8, roughness: 0.95 }));
  pillow.position.set(-0.75, 0.57, 0);
  group.add(pillow);
  group.position.set(-2.1, -3, -1.35);
  return group;
}

function makeDesk() {
  const group = new THREE.Group();
  const top = new THREE.Mesh(new THREE.BoxGeometry(1.45, 0.1, 0.65), darkWoodMat);
  top.position.y = 0.72;
  top.castShadow = true;
  group.add(top);
  for (const x of [-0.58, 0.58]) {
    for (const z of [-0.24, 0.24]) {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.7, 0.07), darkWoodMat);
      leg.position.set(x, 0.35, z);
      group.add(leg);
    }
  }
  const paper = new THREE.Mesh(new THREE.PlaneGeometry(0.38, 0.5), new THREE.MeshStandardMaterial({ color: 0xeadcc0, roughness: 1 }));
  paper.rotation.x = -Math.PI / 2;
  paper.position.set(0.1, 0.78, 0.05);
  group.add(paper);
  group.position.set(1.75, -3, -1.7);
  return group;
}

function makeBookshelf() {
  const group = new THREE.Group();
  const frame = new THREE.Mesh(new THREE.BoxGeometry(1.3, 2.2, 0.38), darkWoodMat);
  frame.position.y = 1.1;
  frame.castShadow = true;
  group.add(frame);
  const bookColors = [0x8f3f2c, 0x3f5a4a, 0x6b5a8e, 0xc9974f];
  for (let i = 0; i < 4; i += 1) {
    const book = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.35, 0.24), new THREE.MeshStandardMaterial({ color: bookColors[i], roughness: 0.9 }));
    book.position.set(-0.35 + i * 0.22, 1.45, 0.1);
    group.add(book);
  }
  group.position.set(-2.65, -3, 0.9);
  return group;
}

function makeWindow() {
  const group = new THREE.Group();
  const frame = new THREE.Mesh(new THREE.BoxGeometry(1.7, 1.5, 0.08), frameMat);
  frame.position.y = 0.45;
  group.add(frame);
  const glass = new THREE.Mesh(
    new THREE.PlaneGeometry(1.5, 1.3),
    new THREE.MeshBasicMaterial({ color: 0xffd28a, transparent: true, opacity: 0.55, side: THREE.DoubleSide }),
  );
  glass.position.set(0, 0.45, 0.05);
  group.add(glass);
  group.position.set(0.8, -3, -2.96);
  return group;
}

const rug = makeRug();
const bed = makeBed();
const desk = makeDesk();
const bookshelf = makeBookshelf();
const windowProp = makeWindow();
room.add(rug, bed, desk, bookshelf, windowProp);

const crate = makeCrate();
const chair = makeChair();
room.add(crate, chair);
const looseObjects = [crate, chair];

for (const object of looseObjects) {
  object.userData.initialPosition = object.position.clone();
  object.userData.initialQuaternion = object.quaternion.clone();
}

// ---------------------------------------------------------------------------
// Dust
// ---------------------------------------------------------------------------

const DUST_COUNT = 220;
const dustPositions = new Float32Array(DUST_COUNT * 3);
for (let i = 0; i < DUST_COUNT; i += 1) {
  dustPositions[i * 3] = (Math.random() - 0.5) * 5.6;
  dustPositions[i * 3 + 1] = (Math.random() - 0.5) * 5.6;
  dustPositions[i * 3 + 2] = (Math.random() - 0.5) * 5.6;
}
const dustGeometry = new THREE.BufferGeometry();
dustGeometry.setAttribute('position', new THREE.BufferAttribute(dustPositions, 3));
const dust = new THREE.Points(
  dustGeometry,
  new THREE.PointsMaterial({ color: 0xffddaa, size: 0.022, transparent: true, opacity: 0.45, depthWrite: false }),
);
room.add(dust);

// ---------------------------------------------------------------------------
// Audio (procedural placeholder)
// ---------------------------------------------------------------------------

let audioCtx: AudioContext | null = null;
let soundEnabled = true;

function ensureAudio() {
  if (!audioCtx) audioCtx = new AudioContext();
  if (audioCtx.state === 'suspended') void audioCtx.resume();
}

function tone(freq: number, duration: number, type: OscillatorType, gain: number, delay = 0) {
  if (!soundEnabled || !audioCtx) return;
  const ctx = audioCtx;
  const start = ctx.currentTime + delay;
  const oscillator = ctx.createOscillator();
  const volume = ctx.createGain();
  oscillator.type = type;
  oscillator.frequency.setValueAtTime(freq, start);
  volume.gain.setValueAtTime(0.0001, start);
  volume.gain.exponentialRampToValueAtTime(gain, start + 0.008);
  volume.gain.exponentialRampToValueAtTime(0.0001, start + duration);
  oscillator.connect(volume);
  volume.connect(ctx.destination);
  oscillator.start(start);
  oscillator.stop(start + duration + 0.02);
}

function noise(duration: number, gain: number, delay = 0, frequency = 420) {
  if (!soundEnabled || !audioCtx) return;
  const ctx = audioCtx;
  const start = ctx.currentTime + delay;
  const buffer = ctx.createBuffer(1, Math.ceil(ctx.sampleRate * duration), ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < data.length; i += 1) data[i] = (Math.random() * 2 - 1) * (1 - i / data.length);
  const source = ctx.createBufferSource();
  source.buffer = buffer;
  const filter = ctx.createBiquadFilter();
  filter.type = 'bandpass';
  filter.frequency.value = frequency;
  filter.Q.value = 0.8;
  const volume = ctx.createGain();
  volume.gain.setValueAtTime(gain, start);
  volume.gain.exponentialRampToValueAtTime(0.0001, start + duration);
  source.connect(filter);
  filter.connect(volume);
  volume.connect(ctx.destination);
  source.start(start);
}

function playGear() {
  tone(120, 0.045, 'square', 0.035);
  tone(90, 0.05, 'square', 0.03, 0.07);
  tone(70, 0.06, 'square', 0.025, 0.14);
  noise(0.5, 0.035, 0.05, 340);
}

function playThud() {
  tone(58, 0.18, 'sine', 0.09);
  noise(0.14, 0.04, 0, 160);
}

function playDoor() {
  tone(523, 0.2, 'triangle', 0.05);
  tone(659, 0.24, 'triangle', 0.045, 0.08);
  noise(0.28, 0.03, 0, 900);
}

function playStep() {
  tone(95, 0.035, 'triangle', 0.014);
  noise(0.04, 0.01, 0, 500);
}

// ---------------------------------------------------------------------------
// Rotation state
// ---------------------------------------------------------------------------

const AXIS_X = new THREE.Vector3(1, 0, 0);
const AXIS_Y = new THREE.Vector3(0, 1, 0);
const WORLD_UP = new THREE.Vector3(0, 1, 0);
const WORLD_DOWN = new THREE.Vector3(0, -1, 0);

type RotationState = { start: number; duration: number; from: THREE.Quaternion; to: THREE.Quaternion };
let rotation: RotationState | null = null;
let isRotating = false;
let doorOpen = false;
let winVisible = false;
let turnCount = 0;

type Tween = {
  object: THREE.Object3D;
  fromPosition: THREE.Vector3;
  toPosition: THREE.Vector3;
  fromQuaternion: THREE.Quaternion;
  toQuaternion: THREE.Quaternion;
  start: number;
  duration: number;
};
const tweens: Tween[] = [];

type DoorAnimation = { start: number; duration: number; from: number; to: number };
let doorAnimation: DoorAnimation | null = null;

const FLOOR_FACES = [
  { name: '地板', normal: new THREE.Vector3(0, -1, 0), axis: 'y' as const, sign: -1 },
  { name: '天花板', normal: new THREE.Vector3(0, 1, 0), axis: 'y' as const, sign: 1 },
  { name: '北墙', normal: new THREE.Vector3(0, 0, -1), axis: 'z' as const, sign: -1 },
  { name: '南墙', normal: new THREE.Vector3(0, 0, 1), axis: 'z' as const, sign: 1 },
  { name: '西墙', normal: new THREE.Vector3(-1, 0, 0), axis: 'x' as const, sign: -1 },
  { name: '东墙', normal: new THREE.Vector3(1, 0, 0), axis: 'x' as const, sign: 1 },
];

type FloorInfo = (typeof FLOOR_FACES)[number] & { localUp: THREE.Vector3 };

function getFloorInfo(): FloorInfo {
  let best = FLOOR_FACES[0];
  let bestDot = -Infinity;
  for (const face of FLOOR_FACES) {
    const worldNormal = face.normal.clone().applyQuaternion(room.quaternion);
    const dot = worldNormal.dot(WORLD_DOWN);
    if (dot > bestDot) {
      bestDot = dot;
      best = face;
    }
  }
  return { ...best, localUp: best.normal.clone().negate() };
}

function clampTangential(position: THREE.Vector3, axis: 'x' | 'y' | 'z') {
  const limit = HALF - 0.5;
  if (axis !== 'x') position.x = THREE.MathUtils.clamp(position.x, -limit, limit);
  if (axis !== 'y') position.y = THREE.MathUtils.clamp(position.y, -limit, limit);
  if (axis !== 'z') position.z = THREE.MathUtils.clamp(position.z, -limit, limit);
}

function settleLooseObjects() {
  const info = getFloorInfo();
  for (const object of looseObjects) {
    const halfHeight = (object.userData.halfHeight as number) ?? 0.3;
    const targetPosition = object.position.clone();
    if (info.axis === 'x') targetPosition.x = info.sign * (HALF - halfHeight);
    if (info.axis === 'y') targetPosition.y = info.sign * (HALF - halfHeight);
    if (info.axis === 'z') targetPosition.z = info.sign * (HALF - halfHeight);
    clampTangential(targetPosition, info.axis);

    const targetQuaternion = new THREE.Quaternion().setFromUnitVectors(WORLD_UP, info.localUp);
    tweens.push({
      object,
      fromPosition: object.position.clone(),
      toPosition: targetPosition,
      fromQuaternion: object.quaternion.clone(),
      toQuaternion: targetQuaternion,
      start: performance.now(),
      duration: 520,
    });
  }
}

function updateTweens(now: number) {
  for (let i = tweens.length - 1; i >= 0; i -= 1) {
    const tween = tweens[i];
    const t = Math.min(1, (now - tween.start) / tween.duration);
    const eased = easeInOutCubic(t);
    tween.object.position.lerpVectors(tween.fromPosition, tween.toPosition, eased);
    tween.object.quaternion.slerpQuaternions(tween.fromQuaternion, tween.toQuaternion, eased);
    if (t >= 1) {
      tween.object.position.copy(tween.toPosition);
      tween.object.quaternion.copy(tween.toQuaternion);
      tweens.splice(i, 1);
    }
  }
}

// ---------------------------------------------------------------------------
// Rotation
// ---------------------------------------------------------------------------

function easeInOutCubic(t: number) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function startRotation(direction: 1 | -1) {
  if (isRotating || winVisible) return;
  const delta = new THREE.Quaternion().setFromAxisAngle(AXIS_Y, direction * Math.PI * 0.5);
  const from = room.quaternion.clone();
  const to = from.clone().multiply(delta);
  rotation = { start: performance.now(), duration: 650, from, to };
  isRotating = true;
  turnCount += 1;
  refreshGizmo();
  playGear();
}

function updateRotation(now: number) {
  if (!rotation) return;
  const t = Math.min(1, (now - rotation.start) / rotation.duration);
  const eased = easeInOutCubic(t);
  room.quaternion.slerpQuaternions(rotation.from, rotation.to, eased);
  if (t < 1) return;

  room.quaternion.copy(rotation.to);
  rotation = null;
  isRotating = false;
  playThud();
  room.updateMatrixWorld(true);
  placePlayer();
  updateCompass();
  refreshGizmo();
  checkDoorPrompt();
}

function refreshGizmo() {
  const disabled = isRotating;
  for (const id of ['#btn-y-minus', '#btn-y-plus']) {
    ($(id) as HTMLButtonElement).disabled = disabled;
  }
}

// ---------------------------------------------------------------------------
// Player movement / camera
// ---------------------------------------------------------------------------

const keys = new Set<string>();
let stepTimer = 0;

function placePlayer() {
  player.position.x = THREE.MathUtils.clamp(player.position.x, -PLAYER_LIMIT_X, PLAYER_LIMIT_X);
  player.position.z = THREE.MathUtils.clamp(player.position.z, -PLAYER_LIMIT_Z, PLAYER_LIMIT_Z);
  player.position.y = 0;
  avatar.position.copy(player.position);
  avatar.rotation.y = yaw + Math.PI;
}

function updateMovement(dt: number) {
  const forward = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
  const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
  const direction = new THREE.Vector3();
  if (keys.has('w')) direction.add(forward);
  if (keys.has('s')) direction.sub(forward);
  if (keys.has('d')) direction.add(right);
  if (keys.has('a')) direction.sub(right);
  if (direction.lengthSq() === 0) return;

  direction.normalize().multiplyScalar(MOVE_SPEED * dt);
  player.position.add(direction);
  placePlayer();

  stepTimer += dt;
  if (stepTimer > 0.34) {
    stepTimer = 0;
    playStep();
  }
}

const PITCH_LIMIT = Math.PI / 2 - 0.05;

let draggingThird = false;
let draggingFirst = false;

document.addEventListener('mousemove', (event) => {
  if (mode !== 'first') return;
  if (document.pointerLockElement !== renderer.domElement) return;
  yaw -= event.movementX * 0.0022;
  pitch -= event.movementY * 0.0022;
  pitch = THREE.MathUtils.clamp(pitch, -PITCH_LIMIT, PITCH_LIMIT);
});

window.addEventListener('pointermove', (event) => {
  if (mode !== 'first' || !draggingFirst || document.pointerLockElement === renderer.domElement) return;
  yaw -= event.movementX * 0.003;
  pitch -= event.movementY * 0.003;
  pitch = THREE.MathUtils.clamp(pitch, -PITCH_LIMIT, PITCH_LIMIT);
});

window.addEventListener('pointermove', (event) => {
  if (!draggingThird || mode !== 'third') return;
  thirdYaw -= event.movementX * 0.005;
  thirdPitch = THREE.MathUtils.clamp(thirdPitch + event.movementY * 0.004, 0.15, 1.25);
});

renderer.domElement.addEventListener('pointerdown', (event) => {
  if (event.button !== 0) return;
  if (document.pointerLockElement === renderer.domElement) return;
  if (mode === 'third') {
    draggingThird = true;
    renderer.domElement.setPointerCapture(event.pointerId);
    return;
  }
  draggingFirst = true;
  renderer.domElement.setPointerCapture(event.pointerId);
});

window.addEventListener('pointerup', () => {
  draggingThird = false;
  draggingFirst = false;
});

renderer.domElement.addEventListener('click', () => {
  if (mode === 'first' && !document.pointerLockElement) {
    void renderer.domElement.requestPointerLock();
  }
});

document.addEventListener('pointerlockchange', () => {
  updateLookHint();
});

// ---------------------------------------------------------------------------
// Door prompt / interaction
// ---------------------------------------------------------------------------

function isDoorAligned() {
  const doorOutward = new THREE.Vector3(1, 0, 0).applyQuaternion(room.quaternion);
  return doorOutward.dot(new THREE.Vector3(0, 0, -1)) > 0.9;
}

function doorDistanceToPlayer() {
  room.updateMatrixWorld(true);
  const doorWorld = room.localToWorld(new THREE.Vector3(3, -1.8, 0));
  return doorWorld.distanceTo(player.position);
}

function checkDoorPrompt() {
  if (mode !== 'first' || doorOpen || winVisible) {
    promptEl.classList.add('hidden');
    return;
  }
  if (isDoorAligned() && doorDistanceToPlayer() < 2.6) {
    promptEl.classList.remove('hidden');
  } else {
    promptEl.classList.add('hidden');
  }
}

function openDoor() {
  if (mode !== 'first') return;
  if (doorOpen) return;
  if (!isDoorAligned()) return;
  if (doorDistanceToPlayer() >= 2.6) return;
  doorOpen = true;
  promptEl.classList.add('hidden');
  playDoor();
  doorAnimation = { start: performance.now(), duration: 800, from: 0, to: -Math.PI * 0.58 };
  window.setTimeout(() => {
    winVisible = true;
    winEl.classList.remove('hidden');
    if (document.pointerLockElement === renderer.domElement) document.exitPointerLock();
  }, 900);
}

function updateDoor(now: number) {
  if (!doorAnimation) return;
  const t = Math.min(1, (now - doorAnimation.start) / doorAnimation.duration);
  const eased = easeInOutCubic(t);
  doorPivot.rotation.y = doorAnimation.from + (doorAnimation.to - doorAnimation.from) * eased;
  if (t >= 1) doorAnimation = null;
}

// ---------------------------------------------------------------------------
// Compass
// ---------------------------------------------------------------------------

function updateCompass() {
  const info = getFloorInfo();
  const aligned = isDoorAligned() ? ' · 门已对齐北侧' : '';
  const view = mode === 'first' ? '第一人称' : '第三人称';
  compassEl.textContent = `视角：${view} · 当前地面：${info.name} · 旋转 ${turnCount} 次${aligned}`;
}

function updateLookHint() {
  const hint = $('#look-hint');
  if (mode === 'third') {
    hint.textContent = '拖拽鼠标环视整个房间 · 按 V 回到第一人称';
    hint.classList.remove('hidden');
    return;
  }
  if (document.pointerLockElement === renderer.domElement) {
    hint.classList.add('hidden');
  } else {
    hint.textContent = '点击画面锁定鼠标 · 移动鼠标 360° 环视';
    hint.classList.remove('hidden');
  }
}

let toastTimer = 0;
function showToast(text: string) {
  const toast = $('#toast');
  toast.textContent = text;
  toast.classList.remove('hidden');
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toast.classList.add('hidden'), 1800);
}

// ---------------------------------------------------------------------------
// Reset
// ---------------------------------------------------------------------------

function resetRoom() {
  rotation = null;
  isRotating = false;
  doorOpen = false;
  winVisible = false;
  turnCount = 0;
  doorAnimation = null;
  tweens.length = 0;
  room.quaternion.identity();
  room.updateMatrixWorld(true);
  doorPivot.rotation.y = 0;
  player.position.copy(PLAYER_START);
  placePlayer();
  mode = 'first';
  avatar.visible = false;
  document.body.classList.remove('third-person');
  applyViewMaterials();
  yaw = -Math.PI / 2;
  pitch = -0.05;
  updateCamera();
  updateCompass();
  updateLookHint();
  winEl.classList.add('hidden');
  promptEl.classList.add('hidden');
  refreshGizmo();
}

// ---------------------------------------------------------------------------
// Dust
// ---------------------------------------------------------------------------

function updateDust(dt: number) {
  const positions = dustGeometry.getAttribute('position') as THREE.BufferAttribute;
  const array = positions.array as Float32Array;
  for (let i = 0; i < DUST_COUNT; i += 1) {
    const index = i * 3 + 1;
    array[index] -= 0.08 * dt;
    if (array[index] < -HALF) array[index] = HALF;
  }
  positions.needsUpdate = true;
}

// ---------------------------------------------------------------------------
// UI bindings
// ---------------------------------------------------------------------------

function bindButton(id: string, action: () => void) {
  ($(id) as HTMLButtonElement).addEventListener('click', action);
}

bindButton('#btn-y-minus', () => startRotation(-1));
bindButton('#btn-y-plus', () => startRotation(1));
bindButton('#btn-view', toggleView);
bindButton('#btn-reset', resetRoom);
bindButton('#btn-again', resetRoom);

($('#btn-start') as HTMLButtonElement).addEventListener('click', () => {
  ensureAudio();
  startEl.classList.add('hidden');
  updateLookHint();
  const lockResult = renderer.domElement.requestPointerLock();
  if (lockResult && typeof (lockResult as Promise<void>).catch === 'function') {
    (lockResult as Promise<void>).catch(() => updateLookHint());
  }
});

soundBtn.addEventListener('click', () => {
  soundEnabled = !soundEnabled;
  soundBtn.textContent = `声音：${soundEnabled ? '开' : '关'}`;
  if (soundEnabled) ensureAudio();
});

window.addEventListener('keydown', (event) => {
  const key = event.key.toLowerCase();
  if (['w', 'a', 's', 'd'].includes(key)) keys.add(key);
  if (event.key === 'ArrowLeft') {
    event.preventDefault();
    startRotation(-1);
  }
  if (event.key === 'ArrowRight') {
    event.preventDefault();
    startRotation(1);
  }
  if (key === 'v') toggleView();
  if (key === 'e' && !promptEl.classList.contains('hidden')) openDoor();
  if (key === 'r') resetRoom();
});

window.addEventListener('keyup', (event) => keys.delete(event.key.toLowerCase()));
window.addEventListener('blur', () => keys.clear());

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------------------------------------------------------------------------
// Main loop
// ---------------------------------------------------------------------------

let lastTime = performance.now();

function tick(now: number) {
  requestAnimationFrame(tick);
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;

  if (rotation) updateRotation(now);
  updateTweens(now);
  updateDoor(now);
  if (mode === 'first' && !isRotating && !doorOpen && !winVisible) updateMovement(dt);
  updateDust(dt);
  room.updateMatrixWorld(true);
  updateCamera();
  checkDoorPrompt();
  renderer.render(scene, camera);
}

resetRoom();
requestAnimationFrame(tick);

// Graybox debug handle for automated tests and tuning.
(window as unknown as { __zhuanjian: unknown }).__zhuanjian = {
  room,
  player,
  getFloorInfo,
  isDoorAligned,
  doorDistanceToPlayer,
  startRotation,
  resetRoom,
  openDoor,
  placePlayer,
  setView: (nextYaw: number, nextPitch: number) => {
    mode = 'first';
    avatar.visible = false;
    yaw = nextYaw;
    pitch = nextPitch;
    updateCamera();
  },
  toggleView,
  getState: () => ({
    quaternion: room.quaternion.toArray(),
    player: player.position.toArray(),
    camera: camera.position.toArray(),
    yaw,
    pitch,
    floor: getFloorInfo().name,
    aligned: isDoorAligned(),
    doorDistance: doorDistanceToPlayer(),
    turnCount,
  }),
};
