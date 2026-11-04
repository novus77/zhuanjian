import * as THREE from 'three';

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------

const params = new URLSearchParams(location.search);
const ROOM_ID = Number(params.get('room') ?? '1');
const VIEW = (params.get('view') ?? 'iso') as 'iso' | 'fp';

const container = document.getElementById('app')!;
const legendEl = document.getElementById('legend')!;
const titleEl = document.getElementById('room-title')!;

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.32;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();

function makeDuskSky() {
  const canvas = document.createElement('canvas');
  canvas.width = 8;
  canvas.height = 256;
  const ctx = canvas.getContext('2d')!;
  const gradient = ctx.createLinearGradient(0, 0, 0, 256);
  gradient.addColorStop(0, '#1d2233');
  gradient.addColorStop(0.45, '#4a3a48');
  gradient.addColorStop(0.72, '#96603c');
  gradient.addColorStop(1, '#c98448');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 8, 256);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.mapping = THREE.EquirectangularReflectionMapping;
  return texture;
}

scene.background = makeDuskSky();
scene.fog = new THREE.Fog(0x3a2b28, 26, 64);

const camera = new THREE.PerspectiveCamera(VIEW === 'iso' ? 34 : 72, window.innerWidth / window.innerHeight, 0.05, 200);

// ---------------------------------------------------------------------------
// Palette
// ---------------------------------------------------------------------------

const MAT = {
  walnut: new THREE.MeshStandardMaterial({ color: 0x5b3a20, roughness: 0.72, metalness: 0.04 }),
  walnutDark: new THREE.MeshStandardMaterial({ color: 0x42291a, roughness: 0.78 }),
  beech: new THREE.MeshStandardMaterial({ color: 0x8a6740, roughness: 0.8 }),
  cream: new THREE.MeshStandardMaterial({ color: 0xf0e6d8, roughness: 0.9 }),
  white: new THREE.MeshStandardMaterial({ color: 0xf5f0e6, roughness: 0.92 }),
  brass: new THREE.MeshStandardMaterial({ color: 0xc9974f, roughness: 0.32, metalness: 0.78 }),
  iron: new THREE.MeshStandardMaterial({ color: 0xd8d8d8, roughness: 0.42, metalness: 0.6 }),
  glass: new THREE.MeshStandardMaterial({ color: 0xd8e4e8, roughness: 0.06, metalness: 0.1, transparent: true, opacity: 0.28 }),
  paper: new THREE.MeshStandardMaterial({ color: 0xe5d6b8, roughness: 0.95 }),
  greenVelvet: new THREE.MeshStandardMaterial({ color: 0x4d5c40, roughness: 0.95 }),
  pink: new THREE.MeshStandardMaterial({ color: 0xe8c4bf, roughness: 0.95 }),
  skyBlue: new THREE.MeshStandardMaterial({ color: 0x9fc0d2, roughness: 0.9 }),
  kidBlue: new THREE.MeshStandardMaterial({ color: 0x8ab4c8, roughness: 0.9 }),
  leaf: new THREE.MeshStandardMaterial({ color: 0x4a5a38, roughness: 1 }),
  leafLight: new THREE.MeshStandardMaterial({ color: 0x718045, roughness: 1 }),
  bark: new THREE.MeshStandardMaterial({ color: 0x2f251d, roughness: 1 }),
  glowWarm: new THREE.MeshStandardMaterial({ color: 0xffd08a, emissive: 0xffb257, emissiveIntensity: 1.6, roughness: 0.6 }),
};

type WallSpec = { opacity: number };

function wallMaterial(color: number, opacity: number) {
  return new THREE.MeshStandardMaterial({
    color,
    roughness: 0.94,
    transparent: opacity < 1,
    opacity,
    side: THREE.DoubleSide,
    depthWrite: opacity > 0.8,
  });
}

function box(group: THREE.Object3D, w: number, h: number, d: number, x: number, y: number, z: number, material: THREE.Material) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  group.add(mesh);
  return mesh;
}

function onFloor(group: THREE.Object3D, w: number, h: number, d: number, x: number, z: number, material: THREE.Material) {
  return box(group, w, h, d, x, h / 2, z, material);
}

function cylinder(group: THREE.Object3D, rt: number, rb: number, h: number, x: number, y: number, z: number, material: THREE.Material, segments = 20) {
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, segments), material);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  group.add(mesh);
  return mesh;
}

// ---------------------------------------------------------------------------
// Room shell
// ---------------------------------------------------------------------------

type RoomSpec = {
  id: number;
  title: string;
  subtitle: string;
  width: number;
  depth: number;
  height: number;
  wallColor: number;
  floorColor: number;
  ceilColor: number;
  windowWidth: number;
  windowHeight: number;
  windowZ: number;
  legend: Array<{ n: number; text: string }>;
  build: (room: THREE.Group, markers: MarkerSpec[]) => void;
  fp: { position: [number, number, number]; look: [number, number, number] };
  treeScale: number;
  treeLeaf: 'thin' | 'full' | 'bare';
};

type MarkerSpec = { n: number; pos: [number, number, number] };

const markers: MarkerSpec[] = [];
let spec: RoomSpec | undefined;

function buildShell(room: THREE.Group, s: RoomSpec) {
  const wallOpacity = VIEW === 'iso' ? 0.42 : 1;
  const nearOpacity = VIEW === 'iso' ? 0.06 : 1;
  const W = s.width;
  const D = s.depth;
  const H = s.height;
  const halfW = W / 2;
  const halfD = D / 2;

  const floorMat = new THREE.MeshStandardMaterial({ color: s.floorColor, roughness: 0.86, metalness: 0.03 });
  const ceilMat = new THREE.MeshStandardMaterial({ color: s.ceilColor, roughness: 1, transparent: true, opacity: VIEW === 'iso' ? 0.05 : 1, depthWrite: VIEW !== 'iso', side: THREE.DoubleSide });

  const floor = box(room, W, 0.12, D, 0, -0.06, 0, floorMat);
  floor.castShadow = false;
  box(room, W, 0.1, D, 0, H + 0.05, 0, ceilMat);

  // North / South walls (z), East / West walls (x). Window on West, opening cut.
  box(room, W, H, 0.12, 0, H / 2, -halfD, wallMaterial(s.wallColor, wallOpacity));
  box(room, W, H, 0.12, 0, H / 2, halfD, wallMaterial(s.wallColor, nearOpacity));
  box(room, 0.12, H, D, halfW, H / 2, 0, wallMaterial(s.wallColor, nearOpacity));

  // West wall with window opening
  const ww = s.windowWidth;
  const wh = s.windowHeight;
  const sill = 0.85;
  const side = (D - ww) / 2;
  box(room, 0.12, H, side, -halfW, H / 2, -(ww / 2 + side / 2), wallMaterial(s.wallColor, wallOpacity));
  box(room, 0.12, H, side, -halfW, H / 2, ww / 2 + side / 2, wallMaterial(s.wallColor, wallOpacity));
  box(room, 0.12, sill, ww, -halfW, sill / 2, s.windowZ, wallMaterial(s.wallColor, wallOpacity));
  box(room, 0.12, H - sill - wh, ww, -halfW, sill + wh + (H - sill - wh) / 2, s.windowZ, wallMaterial(s.wallColor, wallOpacity));

  // Window frame + glass + light shaft
  const frameMat = new THREE.MeshStandardMaterial({ color: 0x4a2f1b, roughness: 0.7 });
  box(room, 0.16, 0.08, ww, -halfW, sill, s.windowZ, frameMat);
  box(room, 0.16, 0.08, ww, -halfW, sill + wh, s.windowZ, frameMat);
  box(room, 0.16, wh, 0.08, -halfW, sill + wh / 2, s.windowZ - ww / 2, frameMat);
  box(room, 0.16, wh, 0.08, -halfW, sill + wh / 2, s.windowZ + ww / 2, frameMat);
  // mullions
  for (const t of [-1 / 3, 0, 1 / 3]) {
    box(room, 0.1, wh, 0.04, -halfW, sill + wh / 2, s.windowZ + t * ww, frameMat);
  }

  const glass = new THREE.Mesh(
    new THREE.PlaneGeometry(ww, wh),
    new THREE.MeshBasicMaterial({ color: 0xffc47a, transparent: true, opacity: 0.22, side: THREE.DoubleSide }),
  );
  glass.position.set(-halfW - 0.02, sill + wh / 2, s.windowZ);
  glass.rotation.y = Math.PI / 2;
  room.add(glass);

  // Light shaft volume
  const shaft = new THREE.Mesh(
    new THREE.ConeGeometry(2.6, 7, 4, 1, true),
    new THREE.MeshBasicMaterial({ color: 0xffb469, transparent: true, opacity: 0.055, side: THREE.DoubleSide, depthWrite: false }),
  );
  shaft.position.set(-halfW + 2.4, sill + wh / 2 + 0.9, s.windowZ);
  shaft.rotation.z = -Math.PI / 2.6;
  shaft.rotation.y = Math.PI / 4;
  room.add(shaft);

  // Tree outside
  buildTree(room, -halfW - 1.9, s.windowZ - 0.35, s);
}

function buildTree(room: THREE.Object3D, x: number, z: number, s: RoomSpec) {
  const tree = new THREE.Group();
  const scale = s.treeScale * 0.92;
  cylinder(tree, 0.16 * scale, 0.24 * scale, 5.2 * scale, 0, 2.6 * scale, 0, MAT.bark, 10);

  const clusters: Array<[number, number, number, number, THREE.Material]> = s.treeLeaf === 'thin'
    ? [
        [0.5, 4.6, 0.1, 0.9, MAT.leafLight],
        [-0.4, 5.0, -0.2, 0.75, MAT.leaf],
        [0.1, 5.5, 0.3, 0.6, MAT.leafLight],
      ]
    : s.treeLeaf === 'full'
      ? [
          [1.1, 4.6, 0.3, 1.5, MAT.leaf],
          [-1.0, 4.9, -0.1, 1.35, MAT.leafLight],
          [0.2, 5.6, 0.2, 1.15, MAT.leaf],
          [0.7, 5.2, -0.9, 0.95, MAT.leafLight],
        ]
      : [
          [1.0, 4.8, 0.2, 1.1, MAT.leaf],
          [-0.9, 5.3, -0.2, 0.85, MAT.leafLight],
          [0.2, 5.6, 0.3, 0.6, MAT.leaf],
        ];

  for (const [cx, cy, cz, r, mat] of clusters) {
    const sphere = new THREE.Mesh(new THREE.SphereGeometry(r * scale, 10, 8), mat);
    sphere.position.set(cx * scale, cy * scale, cz * scale);
    sphere.scale.y = 0.82;
    tree.add(sphere);
  }
  tree.position.set(x, 0, z);
  room.add(tree);
}

// ---------------------------------------------------------------------------
// Room 1 — 爷爷的书房 1930s
// ---------------------------------------------------------------------------

function buildRoom1(room: THREE.Group) {
  const W = 9.6;
  const D = 6.4;
  const H = 4.6;
  const halfW = W / 2;
  const halfD = D / 2;

  // North wall bookshelf, full width
  const shelf = new THREE.Group();
  box(shelf, 5.6, 2.95, 0.4, 0, 1.475, 0, MAT.walnut);
  for (let i = 1; i < 7; i += 1) {
    box(shelf, 5.5, 0.04, 0.36, 0, i * 0.42, 0.02, MAT.walnutDark);
  }
  // Books
  const bookColors = [0xa05440, 0x5a7458, 0x6a5684, 0xb08a52, 0x8f6a42, 0xc09a62];
  const bookMats = bookColors.map((c) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.9 }));
  for (let row = 0; row < 6; row += 1) {
    let cursor = -2.55;
    while (cursor < 2.5) {
      const bw = 0.09 + Math.random() * 0.07;
      const bh = 0.26 + Math.random() * 0.1;
      const mat = bookMats[Math.floor(Math.random() * bookMats.length)];
      box(shelf, bw, bh, 0.26, cursor + bw / 2, row * 0.42 + 0.04 + bh / 2, 0.03, mat);
      cursor += bw + 0.015;
    }
  }
  shelf.position.set(-1.0, 0, -halfD + 0.24);
  room.add(shelf);

  // Glass cabinet on north wall east segment
  const cabinet = new THREE.Group();
  box(cabinet, 1.4, 2.0, 0.42, 0, 1.0, 0, MAT.walnut);
  box(cabinet, 1.28, 1.7, 0.06, 0, 1.05, 0.2, MAT.glass);
  box(cabinet, 0.06, 1.7, 0.06, 0, 1.05, 0.2, MAT.walnutDark);
  cabinet.position.set(3.3, 0, -halfD + 0.26);
  room.add(cabinet);

  // Desk (center-south)
  const desk = new THREE.Group();
  box(desk, 1.6, 0.08, 0.85, 0, 0.76, 0, MAT.walnut);
  for (const dx of [-0.7, 0.7]) {
    for (const dz of [-0.32, 0.32]) {
      box(desk, 0.08, 0.76, 0.08, dx, 0.38, dz, MAT.walnutDark);
    }
  }
  // drawer block
  box(desk, 0.62, 0.34, 0.72, 0.3, 0.56, 0, MAT.walnutDark);
  for (const dy of [0.46, 0.58, 0.68]) {
    box(desk, 0.56, 0.02, 0.04, 0.3, dy, 0.37, MAT.brass);
  }
  // paper + inkstone
  box(desk, 0.42, 0.01, 0.3, -0.35, 0.805, 0.05, MAT.paper);
  box(desk, 0.12, 0.03, 0.09, 0.2, 0.815, -0.2, MAT.walnutDark);
  desk.position.set(1.0, 0, 1.3);
  room.add(desk);

  // Brass desk lamp
  const lamp = new THREE.Group();
  cylinder(lamp, 0.02, 0.02, 0.34, 0, 0.17, 0, MAT.brass);
  const shade = new THREE.Mesh(new THREE.ConeGeometry(0.19, 0.18, 16, 1, true), new THREE.MeshStandardMaterial({ color: 0x3f5a34, roughness: 0.5, side: THREE.DoubleSide, emissive: 0x4a6a2a, emissiveIntensity: 0.4 }));
  shade.position.y = 0.4;
  shade.rotation.x = Math.PI;
  lamp.add(shade);
  lamp.position.set(-0.35, 0.8, 0.15);
  const lampLight = new THREE.PointLight(0xffb466, 6, 5, 2);
  lampLight.position.set(-0.35, 1.28, 0.2);
  room.add(lamp, lampLight);

  // Rattan chair
  const chair = new THREE.Group();
  box(chair, 0.4, 0.06, 0.38, 0, 0.3, 0, MAT.beech);
  box(chair, 0.4, 0.4, 0.06, 0, 0.5, -0.16, MAT.beech);
  for (const dx of [-0.16, 0.16]) {
    for (const dz of [-0.14, 0.14]) {
      box(chair, 0.04, 0.3, 0.04, dx, 0.15, dz, MAT.beech);
    }
  }
  const cushion = box(chair, 0.36, 0.04, 0.34, 0, 0.34, 0, MAT.greenVelvet);
  cushion.castShadow = false;
  chair.position.set(1.0, 0, 2.15);
  chair.rotation.y = Math.PI;
  room.add(chair);

  // Gramophone (SW corner)
  const phono = new THREE.Group();
  box(phono, 0.55, 0.5, 0.5, 0, 0.25, 0, MAT.walnutDark);
  box(phono, 0.5, 0.06, 0.45, 0, 0.52, 0, MAT.walnut);
  const horn = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.42, 20, 1, true), new THREE.MeshStandardMaterial({ color: 0xc9974f, roughness: 0.34, metalness: 0.8, side: THREE.DoubleSide }));
  horn.position.set(0, 0.78, 0);
  horn.rotation.x = -0.4;
  phono.add(horn);
  cylinder(phono, 0.03, 0.03, 0.2, 0, 0.62, 0.05, MAT.brass);
  phono.position.set(-halfW + 0.95, 0, halfD - 0.95);
  phono.rotation.y = 0.5;
  room.add(phono);

  // Small table by gramophone
  box(room, 0.5, 0.02, 0.5, -halfW + 1.9, 0.56, halfD - 0.9, MAT.walnut);
  cylinder(room, 0.035, 0.035, 0.56, -halfW + 1.9, 0.28, halfD - 0.9, MAT.walnutDark);

  // Floor clock
  const clock = new THREE.Group();
  box(clock, 0.36, 1.95, 0.28, 0, 0.975, 0, MAT.walnut);
  box(clock, 0.3, 0.4, 0.02, 0, 1.62, 0.15, MAT.glass);
  const face = new THREE.Mesh(new THREE.CircleGeometry(0.1, 20), MAT.cream);
  face.position.set(0, 1.62, 0.16);
  clock.add(face);
  cylinder(clock, 0.012, 0.012, 0.5, 0, 0.8, 0.15, MAT.brass);
  clock.position.set(halfW - 1.8, 0, -halfD + 0.4);
  clock.rotation.y = -0.3;
  room.add(clock);

  // Globe
  const globe = new THREE.Group();
  cylinder(globe, 0.05, 0.09, 0.08, 0, 0.04, 0, MAT.walnutDark);
  cylinder(globe, 0.012, 0.012, 0.22, 0, 0.18, 0, MAT.brass);
  const ball = new THREE.Mesh(new THREE.SphereGeometry(0.18, 18, 14), new THREE.MeshStandardMaterial({ color: 0x6b7f8a, roughness: 0.8 }));
  ball.position.y = 0.42;
  globe.add(ball);
  globe.position.set(-2.6, 0.8, -halfD + 1.0);
  room.add(globe);
  // plinth under globe
  box(room, 0.5, 0.8, 0.4, -2.6, 0.4, -halfD + 1.1, MAT.walnutDark);

  // Rug
  const rug = new THREE.Mesh(new THREE.PlaneGeometry(4.2, 2.8), new THREE.MeshStandardMaterial({ color: 0x6b3f2a, roughness: 1 }));
  rug.rotation.x = -Math.PI / 2;
  rug.position.set(0.4, 0.012, 0.8);
  rug.receiveShadow = true;
  room.add(rug);

  // Four doors on east wall
  const doorGroup = new THREE.Group();
  const symbols = ['☀', '☾', '✦', '⚷'];
  for (let i = 0; i < 4; i += 1) {
    const z = -2.1 + i * 1.4;
    box(doorGroup, 0.08, 2.15, 0.52, 0, 1.075, z, MAT.walnutDark);
    // handle
    box(doorGroup, 0.05, 0.05, 0.05, -0.07, 1.05, z + 0.18, MAT.brass);
    // transom above (glimpse to corridor mirror)
    box(doorGroup, 0.05, 0.28, 0.5, 0, 2.3, z, new THREE.MeshStandardMaterial({ color: 0xffd6a0, emissive: 0xffb469, emissiveIntensity: 0.25, roughness: 0.4, transparent: true, opacity: 0.5 }));
    const symbolCanvas = document.createElement('canvas');
    symbolCanvas.width = symbolCanvas.height = 64;
    const cctx = symbolCanvas.getContext('2d')!;
    cctx.fillStyle = '#e7c07a';
    cctx.font = 'bold 46px Georgia, serif';
    cctx.textAlign = 'center';
    cctx.textBaseline = 'middle';
    cctx.fillText(symbols[i], 32, 34);
    const texture = new THREE.CanvasTexture(symbolCanvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    const plate = new THREE.Mesh(new THREE.PlaneGeometry(0.26, 0.26), new THREE.MeshBasicMaterial({ map: texture, transparent: true }));
    plate.position.set(-0.05, 1.85, z);
    plate.rotation.y = -Math.PI / 2;
    doorGroup.add(plate);
  }
  doorGroup.position.set(halfW - 0.06, 0, 0);
  room.add(doorGroup);

  // Corridor beyond east wall + mirror
  const corridor = new THREE.Group();
  box(corridor, 1.6, H, 4.6, 0, H / 2, 0, wallMaterial(0x8a7a68, 0.5));
  const mirror = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 1.2), new THREE.MeshStandardMaterial({ color: 0xb9c7c9, roughness: 0.08, metalness: 0.7 }));
  mirror.position.set(-0.78, 1.75, 0);
  mirror.rotation.y = Math.PI / 2;
  corridor.add(mirror);
  const cLight = new THREE.PointLight(0xffc07a, 8, 7, 2);
  cLight.position.set(0.3, 2.2, 0);
  corridor.add(cLight);
  corridor.position.set(halfW + 0.9, 0, 0);
  room.add(corridor);

  // Window tree already built by shell

  markers.push({ n: 1, pos: [-0.6, 2.9, -halfD + 0.3] });
  markers.push({ n: 2, pos: [2.5, 2.1, -halfD + 0.3] });
  markers.push({ n: 3, pos: [0.85, 1.0, 1.0] });
  markers.push({ n: 4, pos: [-halfW + 0.7, 0.95, halfD - 0.75] });
  markers.push({ n: 5, pos: [halfW - 1.4, 2.1, -halfD + 0.4] });
  markers.push({ n: 6, pos: [-1.85, 1.1, -halfD + 1.0] });
  markers.push({ n: 7, pos: [halfW - 0.4, 2.6, 0] });
}

// ---------------------------------------------------------------------------
// Room 2 — 妈妈的卧室 1970s
// ---------------------------------------------------------------------------

function buildRoom2(room: THREE.Group) {
  const W = 9.0;
  const D = 6.0;
  const H = 4.4;
  const halfW = W / 2;
  const halfD = D / 2;

  // Wardrobe (north wall, east segment) — with mirror inside door
  const wardrobe = new THREE.Group();
  box(wardrobe, 1.5, 2.2, 0.62, 0, 1.1, 0, MAT.cream);
  box(wardrobe, 0.72, 2.0, 0.05, -0.37, 1.05, 0.32, MAT.cream);
  box(wardrobe, 0.72, 2.0, 0.05, 0.37, 1.05, -0.32, MAT.cream);
  // mirror on left door, angled open a bit
  const wardMirror = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.95), new THREE.MeshStandardMaterial({ color: 0xc3d0d2, roughness: 0.1, metalness: 0.65 }));
  wardMirror.position.set(-0.36, 1.5, 0.36);
  wardrobe.add(wardMirror);
  box(wardrobe, 0.05, 0.4, 0.05, 0, 1.1, 0.33, MAT.brass);
  wardrobe.position.set(2.4, 0, -halfD + 0.33);
  room.add(wardrobe);

  // Five-drawer chest in NE corner (the "same corner")
  const chest = new THREE.Group();
  box(chest, 1.1, 0.9, 0.5, 0, 0.45, 0, MAT.beech);
  for (let i = 0; i < 4; i += 1) {
    box(chest, 1.0, 0.16, 0.04, 0, 0.2 + i * 0.19, 0.26, MAT.cream);
    box(chest, 0.16, 0.03, 0.03, 0, 0.2 + i * 0.19, 0.29, MAT.brass);
  }
  chest.position.set(halfW - 1.3, 0, -halfD + 0.4);
  room.add(chest);

  // Bed (center-west)
  const bed = new THREE.Group();
  box(bed, 2.0, 0.32, 1.25, 0, 0.16, 0, MAT.cream);
  box(bed, 1.9, 0.16, 1.15, 0, 0.4, 0, MAT.pink);
  // pillow
  box(bed, 0.5, 0.1, 0.7, 0.55, 0.53, 0, MAT.white);
  // headboard
  for (let i = 0; i < 6; i += 1) {
    cylinder(bed, 0.018, 0.018, 0.55, -0.95 + i * 0.38, 0.5, -0.58, MAT.iron, 8);
  }
  box(bed, 2.0, 0.04, 0.04, 0, 0.78, -0.58, MAT.iron);
  // legs
  for (const dx of [-0.9, 0.9]) {
    for (const dz of [-0.55, 0.55]) {
      cylinder(bed, 0.02, 0.02, 0.16, dx, 0.08, dz, MAT.iron, 8);
    }
  }
  bed.position.set(-2.5, 0, 0.2);
  bed.rotation.y = Math.PI / 2;
  room.add(bed);

  // Vanity (NW)
  const vanity = new THREE.Group();
  box(vanity, 0.95, 0.05, 0.42, 0, 0.74, 0, MAT.cream);
  box(vanity, 0.8, 0.6, 0.36, 0, 0.42, 0, MAT.beech);
  box(vanity, 0.06, 0.06, 0.06, -0.42, 0.72, 0.18, MAT.cream);
  box(vanity, 0.06, 0.06, 0.06, 0.42, 0.72, 0.18, MAT.cream);
  const roundMirror = new THREE.Mesh(new THREE.CircleGeometry(0.28, 28), new THREE.MeshStandardMaterial({ color: 0xc3d0d2, roughness: 0.1, metalness: 0.65, side: THREE.DoubleSide }));
  roundMirror.position.set(0, 1.0, -0.2);
  roundMirror.rotation.x = Math.PI / 12;
  vanity.add(roundMirror);
  cylinder(vanity, 0.02, 0.02, 0.22, 0, 0.86, -0.2, MAT.brass);
  vanity.position.set(-2.2, 0, -halfD + 0.35);
  room.add(vanity);

  // Sewing machine (NE area, beside chest)
  const sew = new THREE.Group();
  box(sew, 0.95, 0.05, 0.5, 0, 0.72, 0, MAT.walnut);
  for (const dx of [-0.4, 0.4]) {
    box(sew, 0.07, 0.7, 0.07, dx, 0.35, -0.18, MAT.walnutDark);
    box(sew, 0.07, 0.7, 0.07, dx, 0.35, 0.18, MAT.walnutDark);
  }
  box(sew, 0.3, 0.22, 0.18, 0.18, 0.85, 0, MAT.walnutDark);
  const wheel = new THREE.Mesh(new THREE.TorusGeometry(0.09, 0.015, 8, 18), MAT.brass);
  wheel.position.set(-0.15, 0.85, 0.16);
  sew.add(wheel);
  sew.position.set(0.7, 0, -halfD + 0.45);
  room.add(sew);

  // Small stool
  box(room, 0.34, 0.05, 0.34, 0.7, 0.42, -halfD + 1.0, MAT.beech);
  for (const dx of [-0.13, 0.13]) for (const dz of [-0.13, 0.13]) cylinder(room, 0.018, 0.018, 0.42, 0.7 + dx, 0.21, -halfD + 1.0 + dz, MAT.walnutDark, 8);

  // Window curtains (over west window)
  const curtainMat = new THREE.MeshStandardMaterial({ color: 0xf2e7dc, roughness: 1, transparent: true, opacity: 0.55, side: THREE.DoubleSide });
  for (const cz of [-0.75, 0.75]) {
    const curtain = new THREE.Mesh(new THREE.PlaneGeometry(0.55, 2.2), curtainMat);
    curtain.position.set(-halfW + 0.14, 1.95, -0.4 + cz);
    curtain.rotation.y = Math.PI / 2;
    room.add(curtain);
  }

  // Radio / tape recorder on chest
  const radio = new THREE.Group();
  box(radio, 0.42, 0.16, 0.22, 0, 0.08, 0, new THREE.MeshStandardMaterial({ color: 0x9a9a94, roughness: 0.6, metalness: 0.3 }));
  box(radio, 0.16, 0.1, 0.02, -0.1, 0.1, 0.12, MAT.walnutDark);
  box(radio, 0.16, 0.1, 0.02, 0.1, 0.1, 0.12, MAT.walnutDark);
  cylinder(radio, 0.004, 0.004, 0.3, 0.18, 0.28, -0.06, MAT.brass, 6);
  radio.position.set(halfW - 1.35, 0.9, -halfD + 0.4);
  room.add(radio);

  // Thermos + cup on vanity
  cylinder(room, 0.06, 0.06, 0.3, -2.55, 0.92, -halfD + 0.35, new THREE.MeshStandardMaterial({ color: 0xb5533c, roughness: 0.7 }), 14);
  cylinder(room, 0.04, 0.04, 0.1, -1.95, 0.82, -halfD + 0.35, MAT.white, 14);

  // Rug
  const rug = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 2.3), new THREE.MeshStandardMaterial({ color: 0xd8b9ad, roughness: 1 }));
  rug.rotation.x = -Math.PI / 2;
  rug.position.set(0.6, 0.012, 1.2);
  rug.receiveShadow = true;
  room.add(rug);

  // East door (fake — leads to a wall)
  box(room, 0.08, 2.1, 0.9, halfW - 0.06, 1.05, -0.4, MAT.beech);
  box(room, 0.05, 0.05, 0.05, halfW - 0.14, 1.02, -0.05, MAT.brass);

  // Hidden door behind wardrobe (revealed later)
  box(room, 0.06, 1.95, 0.78, halfW - 0.03, 0.975, 2.05, new THREE.MeshStandardMaterial({ color: 0x2a1d14, roughness: 0.9 }));

  // Desk lamp warm accent
  const lampLight = new THREE.PointLight(0xffa860, 5, 4.5, 2);
  lampLight.position.set(-1.7, 1.2, -halfD + 0.5);
  room.add(lampLight);

  markers.push({ n: 1, pos: [1.85, 2.5, -halfD + 0.4] });
  markers.push({ n: 2, pos: [halfW - 1.0, 1.1, -halfD + 0.4] });
  markers.push({ n: 3, pos: [-1.9, 0.85, 0.15] });
  markers.push({ n: 4, pos: [-1.7, 1.5, -halfD + 0.4] });
  markers.push({ n: 5, pos: [0.55, 1.15, -halfD + 0.5] });
  markers.push({ n: 6, pos: [halfW - 0.4, 2.4, 1.55] });
}

// ---------------------------------------------------------------------------
// Room 3 — 我的儿童房 2000s
// ---------------------------------------------------------------------------

function buildRoom3(room: THREE.Group) {
  const W = 10.4;
  const D = 7.0;
  const H = 4.8;
  const halfW = W / 2;
  const halfD = D / 2;

  // Star stickers on ceiling
  const starGeo = new THREE.CircleGeometry(0.09, 5);
  const starMat = new THREE.MeshStandardMaterial({ color: 0xffe9a8, emissive: 0xffd473, emissiveIntensity: 1.2, roughness: 0.8, side: THREE.DoubleSide });
  for (let i = 0; i < 26; i += 1) {
    const star = new THREE.Mesh(starGeo, starMat);
    star.position.set((Math.random() - 0.5) * (W - 1.2), H - 0.02, (Math.random() - 0.5) * (D - 1.2));
    star.rotation.x = Math.PI / 2;
    star.rotation.z = Math.random() * Math.PI;
    star.scale.setScalar(0.7 + Math.random() * 0.7);
    room.add(star);
  }

  // Star lamp (center ceiling)
  const starLamp = new THREE.Group();
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.16, 14, 12), MAT.glowWarm);
  starLamp.add(bulb);
  cylinder(starLamp, 0.01, 0.01, 0.5, 0, 0.35, 0, MAT.brass, 6);
  starLamp.position.set(0, H - 0.7, 0);
  room.add(starLamp);
  const lampLight = new THREE.PointLight(0xffd08a, 7, 7, 2);
  lampLight.position.set(0, H - 0.85, 0);
  room.add(lampLight);

  // Small bed (west-center)
  const bed = new THREE.Group();
  box(bed, 1.9, 0.24, 1.1, 0, 0.12, 0, MAT.cream);
  box(bed, 1.8, 0.14, 1.02, 0, 0.31, 0, MAT.kidBlue);
  box(bed, 0.45, 0.1, 0.6, 0.6, 0.43, 0, MAT.white);
  box(bed, 1.9, 0.5, 0.06, 0, 0.4, -0.55, MAT.cream);
  bed.position.set(-3.1, 0, 0.15);
  bed.rotation.y = Math.PI / 2;
  room.add(bed);

  // Low table with dollhouse (center)
  const table = new THREE.Group();
  box(table, 1.25, 0.06, 0.85, 0, 0.44, 0, MAT.beech);
  for (const dx of [-0.55, 0.55]) {
    for (const dz of [-0.35, 0.35]) {
      box(table, 0.06, 0.44, 0.06, dx, 0.22, dz, MAT.beech);
    }
  }
  table.position.set(1.0, 0, 0.5);
  room.add(table);

  // Dollhouse on the table — the core prop
  const doll = new THREE.Group();
  box(doll, 0.78, 0.62, 0.66, 0, 0.31, 0, MAT.cream);
  // roof
  const roof = new THREE.Mesh(new THREE.ConeGeometry(0.62, 0.3, 4), new THREE.MeshStandardMaterial({ color: 0x8a4a3a, roughness: 0.85 }));
  roof.rotation.y = Math.PI / 4;
  roof.position.y = 0.77;
  doll.add(roof);
  // front window (glowing)
  const dWindow = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.16), new THREE.MeshStandardMaterial({ color: 0xffd08a, emissive: 0xffb257, emissiveIntensity: 1.8, roughness: 0.5 }));
  dWindow.position.set(0.0, 0.42, 0.335);
  doll.add(dWindow);
  // tiny door
  box(doll, 0.12, 0.2, 0.02, -0.24, 0.2, 0.335, MAT.walnutDark);
  // chimney
  box(doll, 0.09, 0.2, 0.09, 0.24, 0.86, -0.15, new THREE.MeshStandardMaterial({ color: 0x6b4a3a, roughness: 0.9 }));
  // base turntable
  const platter = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.52, 0.05, 28), MAT.walnut);
  platter.position.y = 0.5;
  doll.add(platter);
  doll.position.set(1.0, 0.47, 0.5);
  room.add(doll);

  // Toy box in NE corner (the "same corner")
  const toybox = new THREE.Group();
  box(toybox, 1.05, 0.55, 0.6, 0, 0.275, 0, MAT.walnut);
  box(toybox, 1.05, 0.06, 0.62, 0, 0.58, -0.02, MAT.kidBlue);
  box(toybox, 0.5, 0.045, 0.28, 0.2, 0.62, 0, MAT.brass);
  toybox.position.set(halfW - 1.3, 0, -halfD + 0.42);
  room.add(toybox);

  // Small desk + bookshelf (north wall east)
  const desk = new THREE.Group();
  box(desk, 1.1, 0.05, 0.55, 0, 0.62, 0, MAT.white);
  for (const dx of [-0.48, 0.48]) {
    for (const dz of [-0.22, 0.22]) box(desk, 0.05, 0.62, 0.05, dx, 0.31, dz, MAT.white);
  }
  box(desk, 0.3, 0.02, 0.22, -0.2, 0.65, 0, MAT.paper);
  desk.position.set(2.4, 0, -halfD + 0.45);
  room.add(desk);

  const shelf = new THREE.Group();
  box(shelf, 0.95, 1.2, 0.3, 0, 0.6, 0, MAT.white);
  for (let i = 0; i < 3; i += 1) {
    box(shelf, 0.9, 0.03, 0.26, 0, 0.3 + i * 0.3, 0.01, MAT.cream);
  }
  const kidsBooks = [0xd45a4a, 0x4a7ad4, 0xe8b84a, 0x5aa87a];
  for (let i = 0; i < 4; i += 1) {
    box(shelf, 0.06, 0.2, 0.18, -0.3 + i * 0.09, 0.42, 0.02, new THREE.MeshStandardMaterial({ color: kidsBooks[i], roughness: 0.9 }));
  }
  shelf.position.set(halfW - 0.95, 0, -halfD + 0.3);
  room.add(shelf);

  // Rug (colorful)
  const rug = new THREE.Mesh(new THREE.PlaneGeometry(3.8, 2.6), new THREE.MeshStandardMaterial({ color: 0x8ab4c8, roughness: 1 }));
  rug.rotation.x = -Math.PI / 2;
  rug.position.set(-0.3, 0.012, 2.0);
  rug.receiveShadow = true;
  room.add(rug);

  // Sealed door (east wall) with planks
  const sealed = new THREE.Group();
  box(sealed, 0.08, 2.05, 0.9, 0, 1.025, 0, MAT.walnut);
  const plankMat = new THREE.MeshStandardMaterial({ color: 0x8a6740, roughness: 0.9 });
  for (let i = 0; i < 3; i += 1) {
    const plank = box(sealed, 0.06, 0.14, 1.05, -0.08, 0.6 + i * 0.45, 0, plankMat);
    plank.rotation.x = 0.04 * (i % 2 === 0 ? 1 : -1);
  }
  sealed.position.set(halfW - 0.06, 0, 0.3);
  room.add(sealed);

  // Window curtains (roller blind)
  const blind = new THREE.Mesh(new THREE.PlaneGeometry(1.7, 1.5), new THREE.MeshStandardMaterial({ color: 0xd8cbb4, roughness: 1, transparent: true, opacity: 0.65, side: THREE.DoubleSide }));
  blind.position.set(-halfW + 0.12, 2.1, -0.4);
  blind.rotation.y = Math.PI / 2;
  room.add(blind);

  // Lamprope (the manual sunset trigger)
  cylinder(room, 0.008, 0.008, 1.4, -1.8, 3.7, halfD - 0.4, MAT.brass, 6);
  cylinder(room, 0.05, 0.05, 0.12, -1.8, 3.0, halfD - 0.4, MAT.brass, 10);

  markers.push({ n: 1, pos: [0.75, 1.6, 0.35] });
  markers.push({ n: 2, pos: [-2.4, 0.9, 0.1] });
  markers.push({ n: 3, pos: [halfW - 1.0, 0.95, -halfD + 0.42] });
  markers.push({ n: 4, pos: [1.9, 1.0, -halfD + 0.45] });
  markers.push({ n: 5, pos: [0, H - 1.0, 0] });
  markers.push({ n: 6, pos: [-1.4, 3.9, halfD - 0.35] });
  markers.push({ n: 7, pos: [halfW - 0.4, 2.5, 0.2] });
}

// ---------------------------------------------------------------------------
// Specs
// ---------------------------------------------------------------------------

const ROOMS: Record<number, RoomSpec> = {
  1: {
    id: 1,
    title: '第 1 关 · 爷爷的书房',
    subtitle: '1930s · 同一个黄昏的开始',
    width: 9.6,
    depth: 6.4,
    height: 4.6,
    wallColor: 0xd9c9a8,
    floorColor: 0x6b4a2e,
    ceilColor: 0xe8dfce,
    windowWidth: 1.7,
    windowHeight: 1.5,
    windowZ: -0.4,
    treeScale: 0.62,
    treeLeaf: 'thin',
    build: buildRoom1,
    fp: { position: [2.6, 1.6, 2.4], look: [-1.4, 1.9, -2.4] },
    legend: [
      { n: 1, text: '顶天立地书架 · 手搭 Mesh（书脊烫金字是谜题）' },
      { n: 2, text: '玻璃书柜 · Lux3D' },
      { n: 3, text: '大书桌 + 抽屉 · Lux3D（抽屉里是太阳门钥匙）' },
      { n: 4, text: '留声机（铜喇叭）· Lux3D（喇叭里藏小钥匙）' },
      { n: 5, text: '落地座钟 · Lux3D' },
      { n: 6, text: '地球仪 · Lux3D' },
      { n: 7, text: '东墙四扇小门（☀☾✦⚷）· 手搭 Mesh + 符号贴花' },
    ],
  },
  2: {
    id: 2,
    title: '第 2 关 · 妈妈的卧室',
    subtitle: '1970s · 同一个黄昏的中段',
    width: 9.0,
    depth: 6.0,
    height: 4.4,
    wallColor: 0xf0e6d8,
    floorColor: 0x8a6740,
    ceilColor: 0xf5efe2,
    windowWidth: 1.6,
    windowHeight: 1.4,
    windowZ: -0.4,
    treeScale: 0.86,
    treeLeaf: 'full',
    build: buildRoom2,
    fp: { position: [3.4, 1.6, 2.0], look: [-2.6, 1.4, -0.4] },
    legend: [
      { n: 1, text: '大衣柜（门内嵌穿衣镜）· 手搭 Mesh + 镜面（镜面是光路中介）' },
      { n: 2, text: '五斗橱 · Lux3D（同一个墙角的位置）' },
      { n: 3, text: '白漆铁艺床 · Lux3D（可推动，床底藏铁皮盒）' },
      { n: 4, text: '梳妆台 + 圆镜 · Lux3D' },
      { n: 5, text: '蝴蝶牌缝纫机 · Lux3D' },
      { n: 6, text: '衣柜后的暗门 · 手搭 Mesh（真正的出口）' },
    ],
  },
  3: {
    id: 3,
    title: '第 3 关 · 我的儿童房',
    subtitle: '2000s · 同一个黄昏的末尾 → 入夜',
    width: 10.4,
    depth: 7.0,
    height: 4.8,
    wallColor: 0xa8c4d0,
    floorColor: 0xc4a882,
    ceilColor: 0xf5f5f0,
    windowWidth: 1.7,
    windowHeight: 1.4,
    windowZ: -0.4,
    treeScale: 1.15,
    treeLeaf: 'bare',
    build: buildRoom3,
    fp: { position: [3.6, 1.6, 2.6], look: [0.3, 1.4, 0.3] },
    legend: [
      { n: 1, text: '娃娃屋 + 转盘底座 · Lux3D image-to-3D（核心道具）' },
      { n: 2, text: '小床 · Lux3D' },
      { n: 3, text: '玩具箱 · Lux3D（同一个墙角的位置）' },
      { n: 4, text: '小书桌 · Lux3D' },
      { n: 5, text: '星星灯 · Lux3D（通关时亮起）' },
      { n: 6, text: '灯绳 · 手搭 Mesh（玩家亲手让太阳落山）' },
      { n: 7, text: '封死的门 + 木板 · 手搭 Mesh（两灯亮后木板脱落）' },
    ],
  },
};

// ---------------------------------------------------------------------------
// Compose
// ---------------------------------------------------------------------------

const room = new THREE.Group();
scene.add(room);

function main() {
  const s = ROOMS[ROOM_ID] ?? ROOMS[1];
  spec = s;

  titleEl.textContent = s.title;
  document.getElementById('room-subtitle')!.textContent = s.subtitle;

  buildShell(room, s);
  s.build(room, markers);

  // Lighting: low dusk sun from the west
  const sun = new THREE.DirectionalLight(0xffb06a, 4.2);
  sun.position.set(-16, 4.6, -5);
  sun.target.position.set(0, 1.2, 0);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -14;
  sun.shadow.camera.right = 14;
  sun.shadow.camera.top = 14;
  sun.shadow.camera.bottom = -14;
  sun.shadow.camera.near = 1;
  sun.shadow.camera.far = 60;
  sun.shadow.bias = -0.0006;
  scene.add(sun);
  scene.add(sun.target);

  const fill = new THREE.HemisphereLight(0x9aa8c4, 0x6a4a30, 1.25);
  scene.add(fill);

  const bounce = new THREE.PointLight(0xffa860, 9, 16, 2);
  bounce.position.set(-s.width / 2 + 1.5, 1.6, s.windowZ);
  scene.add(bounce);

  const interior = new THREE.PointLight(0xffd9b0, 14, 18, 2);
  interior.position.set(0, s.height - 1.1, 0.4);
  scene.add(interior);

  // Dust motes
  const count = 320;
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i += 1) {
    positions[i * 3] = -s.width / 2 + Math.random() * s.width * 0.8;
    positions[i * 3 + 1] = Math.random() * s.height;
    positions[i * 3 + 2] = (Math.random() - 0.5) * s.depth;
  }
  const dustGeo = new THREE.BufferGeometry();
  dustGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const dust = new THREE.Points(dustGeo, new THREE.PointsMaterial({ color: 0xffd8a8, size: 0.022, transparent: true, opacity: 0.5, depthWrite: false }));
  scene.add(dust);

  // Marker sprites
  if (VIEW === 'iso') {
    for (const m of markers) {
      scene.add(makeMarker(m.n, new THREE.Vector3(...m.pos)));
    }
    legendEl.innerHTML = `<div class="legend-title">3D 资产</div>` + s.legend.map((l) => `<div class="legend-row"><span class="legend-num">${l.n}</span><span>${l.text}</span></div>`).join('');
    legendEl.classList.add('show');

    const span = Math.max(s.width, s.depth * 1.5);
    camera.position.set(span * 0.62, s.height * 1.02, span * 1.16);
    camera.lookAt(0, s.height * 0.30, -0.2);
    camera.fov = 34;
  } else {
    camera.position.set(...s.fp.position);
    camera.lookAt(...s.fp.look);
    camera.fov = 72;
  }
  camera.updateProjectionMatrix();

  // Hide HUD-ish elements for FP shot
  if (VIEW === 'fp') {
    document.body.classList.add('fp');
  }

  animate();
}

function makeMarker(n: number, pos: THREE.Vector3) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 128;
  const ctx = canvas.getContext('2d')!;
  ctx.beginPath();
  ctx.arc(64, 64, 46, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(20,14,10,0.78)';
  ctx.fill();
  ctx.lineWidth = 4;
  ctx.strokeStyle = '#d6a85f';
  ctx.stroke();
  ctx.fillStyle = '#f0c987';
  ctx.font = 'bold 58px Georgia, serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(String(n), 64, 68);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false, depthWrite: false }));
  sprite.scale.set(0.42, 0.42, 1);
  sprite.position.copy(pos);
  sprite.renderOrder = 999;
  return sprite;
}

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

void spec;
main();
