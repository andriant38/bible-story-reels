// 3D scene kit for construction & mining reels.
// Every scene is described in JSON (see konstruksi/PIPELINE.md); this file turns it into a three.js scene
// and renders any moment of it deterministically: window.setupScene(scene, duration) then window.frame(t).
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const W = 1080, H = 1920;
const V3 = THREE.Vector3;
const DEG = Math.PI / 180;

// ---------------------------------------------------------------- helpers
const C = {
  cat: 0xf2b705, catDark: 0xc98f00, dark: 0x2a2b2e, tire: 0x1c1c1e, steel: 0x8b929b, steelDark: 0x585e66,
  concrete: 0xc4beb3, concreteDark: 0x9a948a, rebar: 0x8a4b2c, glass: 0x6f9fc4, soil: 0x9a6a43, gravel: 0x8c8378,
  vest: 0xff6a00, skin: 0xd9a27a, white: 0xf3f3f0, red: 0xd23a2a, water: 0x2a6f99, grass: 0x6f8f3a, road: 0x3a3a3d,
};
const matCache = new Map();
function mat(color, o = {}) {
  const key = color + JSON.stringify(o);
  if (!matCache.has(key)) {
    matCache.set(key, new THREE.MeshStandardMaterial({
      color, roughness: o.rough ?? 0.75, metalness: o.metal ?? 0.05, flatShading: o.flat ?? false,
      transparent: o.opacity !== undefined, opacity: o.opacity ?? 1, emissive: o.emissive ?? 0x000000,
      emissiveIntensity: o.ei ?? 1, side: o.side ?? THREE.FrontSide, depthWrite: o.opacity === undefined || o.opacity > 0.6,
    }));
  }
  return matCache.get(key);
}
function mesh(geo, m, shadow = true) {
  const x = new THREE.Mesh(geo, m);
  x.castShadow = shadow; x.receiveShadow = true;
  return x;
}
function box(w, h, d, m, x = 0, y = 0, z = 0) {
  const b = mesh(new THREE.BoxGeometry(w, h, d), m); b.position.set(x, y, z); return b;
}
function cyl(rt, rb, h, m, seg = 20) { return mesh(new THREE.CylinderGeometry(rt, rb, h, seg), m); }
// beam between two points (for lattices, cables, rebar)
function beamGeo(a, b, r) {
  const dir = new V3().subVectors(b, a); const len = dir.length();
  const g = new THREE.BoxGeometry(r, len, r);
  const q = new THREE.Quaternion().setFromUnitVectors(new V3(0, 1, 0), dir.clone().normalize());
  g.applyQuaternion(q); const mid = a.clone().add(b).multiplyScalar(0.5); g.translate(mid.x, mid.y, mid.z);
  return g;
}
function rng(seed) { let s = (seed * 9301 + 49297) % 233280 || 1; return () => (s = (s * 9301 + 49297) % 233280) / 233280; }
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
const easeIO = (x) => 0.5 - 0.5 * Math.cos(Math.PI * clamp(x));
const lerp = (a, b, t) => a + (b - a) * t;

function strataTexture(kind) {
  const pal = {
    laterite: ['#a4532a', '#c06a35', '#b25f30', '#cf8a4e', '#b98a5e', '#9c8068', '#8d7a68', '#7e7064'],
    coal: ['#6d5a45', '#8a7458', '#2b2623', '#7a6a55', '#1f1c1a', '#6a5c4b', '#26221f', '#5b5046'],
    rock: ['#a6977f', '#b5a68e', '#998a76', '#bfae95', '#8e8070', '#a29280', '#857a6c', '#968878'],
    soil: ['#9a6e45', '#b08458', '#a07a52', '#c09a6c', '#9c8670', '#a8957e', '#8a7c6c', '#7a6e62'],
  }[kind] || null;
  const p = pal || ['#7a5534', '#8f6a45', '#a07d55', '#7d6a55', '#8c7b66', '#6a5d50', '#57504a', '#4d4741'];
  const c = document.createElement('canvas'); c.width = 4; c.height = 512;
  const g = c.getContext('2d'); const r = rng(kind ? kind.length * 7 : 3);
  let y = 0, i = 0;
  while (y < 512) { const h = 55 + r() * 70; g.fillStyle = p[i % p.length]; g.fillRect(0, y, 4, h + 1); y += h; i++; }
  for (let k = 0; k < 400; k++) { g.fillStyle = `rgba(0,0,0,${r() * 0.07})`; g.fillRect(0, r() * 512, 4, 1 + r() * 3); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapT = THREE.RepeatWrapping;
  t.magFilter = THREE.LinearFilter; return t;
}
// v = 1 at ytop, 0 at ybottom; top band of texture = top of ground
function strataUV(geo, ybot, ytop) {
  const pos = geo.attributes.position; const uv = new Float32Array(pos.count * 2);
  for (let i = 0; i < pos.count; i++) { uv[2 * i] = 0.5; uv[2 * i + 1] = (pos.getY(i) - ybot) / (ytop - ybot); }
  geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); return geo;
}
function textSprite(text, opts = {}) {
  const c = document.createElement('canvas'); const fs = 96;
  const g = c.getContext('2d'); g.font = `800 ${fs}px Inter, sans-serif`;
  const w = Math.ceil(g.measureText(text).width) + 60; c.width = w; c.height = fs + 50;
  g.font = `800 ${fs}px Inter, sans-serif`;
  g.fillStyle = opts.bg || 'rgba(20,20,22,0.85)';
  g.beginPath(); g.roundRect(0, 0, w, c.height, 24); g.fill();
  g.fillStyle = opts.color || '#ffc400'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(text, w / 2, c.height / 2 + 4);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, depthTest: false, transparent: true }));
  const h = opts.size || 3; s.scale.set(h * w / c.height, h, 1); s.renderOrder = 999; return s;
}

// ---------------------------------------------------------------- objects
// Each factory: (spec, ctx) => { group, update(p, t) }   p = anim progress 0..1 (already mapped), t = seconds.
const F = {};

F.worker = (s) => {
  const g = new THREE.Group(); const vest = s.color ?? C.vest;
  const legL = box(0.2, 0.85, 0.22, mat(0x2d3a55)); legL.geometry.translate(0, -0.42, 0); legL.position.set(-0.13, 0.88, 0);
  const legR = legL.clone(); legR.position.x = 0.13;
  const torso = box(0.52, 0.62, 0.3, mat(vest), 0, 1.2, 0);
  const stripe = box(0.54, 0.06, 0.32, mat(0xe8e8e8, { emissive: 0x555555 }), 0, 1.12, 0);
  const head = mesh(new THREE.SphereGeometry(0.14, 16, 12), mat(C.skin)); head.position.y = 1.62;
  const hat = mesh(new THREE.SphereGeometry(0.17, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), mat(s.hat ?? 0xffd000, { rough: 0.4 }));
  hat.position.y = 1.66; const brim = cyl(0.21, 0.21, 0.02, mat(s.hat ?? 0xffd000)); brim.position.y = 1.66;
  const armL = box(0.13, 0.62, 0.14, mat(vest)); armL.geometry.translate(0, -0.3, 0); armL.position.set(-0.33, 1.48, 0);
  const armR = armL.clone(); armR.position.x = 0.33;
  g.add(legL, legR, torso, stripe, head, hat, brim, armL, armR);
  return {
    group: g, update(p, t) {
      if (s.anim === 'walk' || s.anim === 'wave') {
        const sw = s.anim === 'walk' ? Math.sin(t * 7) * 0.5 : 0;
        legL.rotation.x = sw; legR.rotation.x = -sw; armL.rotation.x = -sw; armR.rotation.x = sw;
        if (s.anim === 'wave') armR.rotation.z = Math.PI * 0.85 + Math.sin(t * 8) * 0.25;
      }
    },
  };
};

F.excavator = (s) => {
  const g = new THREE.Group(); const yel = mat(s.color ?? C.cat, { rough: 0.45 }); const dk = mat(C.dark, { rough: 0.6 });
  for (const z of [-1.3, 1.3]) {
    const tr = box(4.6, 0.95, 0.8, dk, 0, 0.48, z); g.add(tr);
    for (let i = 0; i < 5; i++) { const w = cyl(0.3, 0.3, 0.85, mat(C.steelDark)); w.rotation.x = Math.PI / 2; w.position.set(-1.8 + i * 0.9, 0.42, z); g.add(w); }
  }
  g.add(box(2.4, 0.5, 2.0, dk, 0, 0.95, 0));
  const house = new THREE.Group(); house.position.y = 1.2; g.add(house);
  house.add(box(3.4, 1.25, 2.6, yel, -0.35, 0.62, 0));
  house.add(box(1.0, 1.1, 2.6, mat(0x3a3a3a), -1.95, 0.55, 0)); // counterweight
  const cab = box(1.25, 1.35, 1.0, yel, 0.6, 1.9, 0.75); house.add(cab);
  house.add(box(1.0, 1.0, 0.04, mat(C.glass, { rough: 0.1, metal: 0.3 }), 0.68, 1.95, 1.26));
  house.add(box(0.04, 1.0, 0.8, mat(C.glass, { rough: 0.1, metal: 0.3 }), 1.24, 1.95, 0.75));
  const exh = cyl(0.07, 0.07, 0.6, dk); exh.position.set(-1.4, 1.5, -0.7); house.add(exh);
  // boom -> stick -> bucket (pivot groups)
  const boom = new THREE.Group(); boom.position.set(1.0, 0.9, -0.15); house.add(boom);
  const bl = 5.7, sl = 2.9;
  const bm = box(bl, 0.55, 0.5, yel); bm.geometry.translate(bl / 2, 0, 0); boom.add(bm);
  const cylH = cyl(0.11, 0.11, 2.6, mat(C.steel, { metal: 0.6, rough: 0.3 })); cylH.rotation.z = -1.1; cylH.position.set(1.3, -0.25, 0); boom.add(cylH);
  const stick = new THREE.Group(); stick.position.set(bl, 0, 0); boom.add(stick);
  const st = box(sl, 0.42, 0.4, yel); st.geometry.translate(sl / 2, 0, 0); stick.add(st);
  const bucket = new THREE.Group(); bucket.position.set(sl, 0, 0); stick.add(bucket);
  const bk = box(0.9, 1.0, 1.1, dk); bk.position.set(0.25, -0.45, 0); bucket.add(bk);
  for (let i = -2; i <= 2; i++) { const tooth = box(0.25, 0.12, 0.1, mat(C.steel, { metal: 0.6 })); tooth.position.set(0.75, -0.9, i * 0.22); bucket.add(tooth); }
  const pose = (b, k, c) => { boom.rotation.z = b; stick.rotation.z = k; bucket.rotation.z = c; };
  pose(0.6, -1.9, -0.9);
  return {
    group: g, update(p, t) {
      if (s.anim === 'dig' || s.anim === 'load') {
        const P = s.period ?? 7; const ph = ((t + (s.phase ?? 0)) % P) / P;
        // 0-.35 dig (boom down, stick in), .35-.5 lift, .5-.7 swing, .7-.8 dump, .8-1 swing back
        let b, k, c, sw;
        const swingTo = (s.swing ?? 70) * DEG;
        if (ph < 0.35) { const q = easeIO(ph / 0.35); b = lerp(0.35, -0.15, q); k = lerp(-1.3, -2.3, q); c = lerp(-0.2, -1.6, q); sw = 0; }
        else if (ph < 0.5) { const q = easeIO((ph - 0.35) / 0.15); b = lerp(-0.15, 0.55, q); k = -2.3; c = -1.6; sw = 0; }
        else if (ph < 0.7) { const q = easeIO((ph - 0.5) / 0.2); b = 0.55; k = -2.3; c = -1.6; sw = q * swingTo; }
        else if (ph < 0.8) { const q = easeIO((ph - 0.7) / 0.1); b = 0.55; k = lerp(-2.3, -1.4, q); c = lerp(-1.6, 0.3, q); sw = swingTo; }
        else { const q = easeIO((ph - 0.8) / 0.2); b = lerp(0.55, 0.35, q); k = lerp(-1.4, -1.3, q); c = lerp(0.3, -0.2, q); sw = lerp(swingTo, 0, q); }
        pose(b, k, c); house.rotation.y = sw;
      }
    },
  };
};

function truck(s, big) {
  const g = new THREE.Group(); const yel = mat(s.color ?? C.cat, { rough: 0.45 }); const dk = mat(C.dark);
  const L = big ? 14.5 : 7.5, Wd = big ? 8.5 : 2.5, R = big ? 1.95 : 0.55, wW = big ? 1.4 : 0.35;
  const wheels = [];
  const axles = big ? [[L * 0.32, [Wd / 2 - wW / 2]], [-L * 0.25, [Wd / 2 - wW / 2, Wd / 2 - wW * 1.5 - 0.05]]]
    : [[L * 0.33, [Wd / 2 - wW / 2]], [-L * 0.12, [Wd / 2 - wW / 2]], [-L * 0.3, [Wd / 2 - wW / 2]]];
  for (const [x, zs] of axles) for (const zz of zs) for (const sg of [-1, 1]) {
    const w = new THREE.Group(); w.position.set(x, R, sg * zz);
    const tire = cyl(R, R, wW, mat(C.tire, { rough: 0.95 }), 28); tire.rotation.x = Math.PI / 2; w.add(tire);
    const hub = cyl(R * 0.5, R * 0.5, wW + 0.04, mat(s.color ?? C.cat, { rough: 0.5 }), 16); hub.rotation.x = Math.PI / 2; w.add(hub);
    for (let i = 0; i < 6; i++) { const lug = box(R * 0.15, wW + 0.06, R * 0.15, dk); lug.position.set(Math.cos(i) * R * 0.3, 0, Math.sin(i) * R * 0.3); lug.rotation.x = Math.PI / 2; hub.add(lug); }
    g.add(w); wheels.push(w);
  }
  const fy = R * 1.15;
  const chassis = box(L * 0.9, R * 0.5, Wd * 0.45, dk, 0, fy, 0); g.add(chassis);
  // front deck + cab
  if (big) {
    g.add(box(2.6, 2.4, Wd - 0.6, yel, L * 0.36, fy + 1.4, 0));
    g.add(box(1.4, 0.15, Wd + 0.2, yel, L * 0.42, fy + 2.7, 0));
    g.add(box(2.0, 2.0, 2.0, yel, L * 0.38, fy + 3.8, -Wd / 2 + 1.4));
    g.add(box(0.05, 1.2, 1.7, mat(C.glass, { rough: 0.1, metal: 0.3 }), L * 0.38 + 1.02, fy + 4.0, -Wd / 2 + 1.4));
    g.add(box(0.3, 1.6, Wd - 1.2, mat(0x333333), L * 0.36 + 1.35, fy + 1.4, 0)); // grille
    for (const z of [-1.5, 1.5]) { const hl = box(0.1, 0.35, 0.6, mat(0xffffff, { emissive: 0xffffee, ei: 0.8 }), L * 0.36 + 1.5, fy + 2.2, z); g.add(hl); }
  } else {
    g.add(box(2.0, 2.2, Wd, yel, L * 0.36, fy + 1.15, 0));
    g.add(box(0.05, 0.9, Wd - 0.3, mat(C.glass, { rough: 0.1, metal: 0.3 }), L * 0.36 + 1.01, fy + 1.6, 0));
  }
  // dump bed pivoting at rear
  const bed = new THREE.Group(); bed.position.set(-L * 0.45, fy + R * 0.3, 0); g.add(bed);
  const bl = big ? L * 0.78 : L * 0.62, bh = big ? 3.2 : 1.4, bw = big ? Wd + 0.4 : Wd;
  const bedM = mat(s.bed ?? (big ? C.cat : 0xb8bcc2), { rough: 0.55 });
  bed.add(box(bl, 0.25, bw, bedM, bl / 2, 0.12, 0));
  bed.add(box(bl, bh, 0.25, bedM, bl / 2, bh / 2, bw / 2));
  bed.add(box(bl, bh, 0.25, bedM, bl / 2, bh / 2, -bw / 2));
  bed.add(box(0.25, bh * 1.25, bw, bedM, bl, bh * 0.62, 0));
  if (big) bed.add(box(2.6, 0.25, bw, bedM, bl + 1.2, bh * 1.25, 0)); // canopy over cab
  let load = null;
  if (s.loaded) { load = mesh(new THREE.ConeGeometry(Math.min(bl, bw) * 0.55, bh * 0.9, 9), mat(s.load_color ?? 0x8b4a2b, { flat: true, rough: 1 })); load.scale.set(bl / bw, 1, 1); load.position.set(bl / 2, bh * 0.75, 0); bed.add(load); }
  if (s.tarp) { const tp = box(bl * 0.98, 0.12, bw + 0.1, mat(s.tarp_color ?? 0x2f5d8a, { rough: 0.9 }), bl / 2, bh + 0.05, 0); bed.add(tp); }
  const steam = [];
  if (s.steam) { const sm = new THREE.MeshStandardMaterial({ color: 0xf2f2f2, transparent: true, opacity: 0.4, depthWrite: false, roughness: 1 }); for (let k = 0; k < 10; k++) { const m = new THREE.Mesh(new THREE.IcosahedronGeometry(0.5, 1), sm.clone()); m.userData.k = k; bed.add(m); steam.push(m); } }
  // parts for the 'assemble' animation: start scattered on the ground, then get lifted into place
  const cabParts = g.children.filter((c) => c !== chassis && c !== bed && !wheels.includes(c));
  const home = new Map(); [...wheels, ...cabParts, bed].forEach((o) => home.set(o, o.position.clone()));
  const scatter = (o) => {
    if (wheels.includes(o)) { const h = home.get(o); return new V3(h.x * 1.3, R, Math.sign(h.z) * (Wd * 1.5 + Math.abs(h.z))); }
    if (o === bed) return new V3(-L * 0.75, R * 0.3 - fy, -Wd * 1.7);
    const h = home.get(o); return new V3(h.x + L * 0.75, h.y - fy, h.z - Wd * 0.4);
  };
  const assemble = (p) => {
    const seq = [[wheels, 0, 0.4], [cabParts, 0.35, 0.65], [[bed], 0.6, 0.95]];
    for (const [list, a, b] of seq) for (const o of list) {
      const q = easeIO((p - a) / (b - a)); const h = home.get(o);
      o.position.lerpVectors(scatter(o), h, q); o.position.y += Math.sin(Math.PI * q) * (list === wheels ? 2 : 6);
    }
  };
  const from = new V3(...(s.pos || [0, 0, 0])); const to = s.to ? new V3(...s.to) : null;
  if (to) g.rotation.y = Math.atan2(-(to.z - from.z), to.x - from.x);
  return {
    group: g, update(p, t) {
      if (to) {
        const q = s.ease === false ? p : easeIO(p); g.position.lerpVectors(from, to, q);
        const dist = from.distanceTo(to) * q; for (const w of wheels) w.rotation.z = -dist / R;
      }
      steam.forEach((m) => { const k = m.userData.k; const ph = (t * 0.35 + k / 10) % 1; m.position.set(bl * (0.15 + 0.7 * ((k * 0.37) % 1)), bh + 0.4 + ph * 4, ((k * 0.61) % 1 - 0.5) * bw * 0.7); m.scale.setScalar(0.6 + ph * 2.2); m.material.opacity = 0.45 * (1 - ph); });
      if (s.anim === 'assemble') assemble(p);
      if (s.anim === 'fill' && load) { const k = Math.max(smooth(p), 0.02); load.scale.set((bl / bw) * k, k, k); load.position.y = bh * (0.3 + 0.45 * k); }
      if (s.anim === 'dump') { const q = smooth(p / 0.6) - smooth((p - 0.8) / 0.2); bed.rotation.z = q * 0.85; if (load) load.visible = p < 0.55; }
    },
  };
}
F.haul_truck = (s) => truck(s, true);
F.dump_truck = (s) => truck(s, false);

F.car = (s) => {
  const g = new THREE.Group(); const body = mat(s.color ?? 0xd8dde3, { rough: 0.3, metal: 0.4 });
  g.add(box(4.4, 0.8, 1.8, body, 0, 0.75, 0));
  g.add(box(2.4, 0.65, 1.6, mat(0x334455, { rough: 0.15, metal: 0.5 }), -0.2, 1.45, 0));
  for (const x of [-1.4, 1.4]) for (const z of [-0.85, 0.85]) { const w = cyl(0.36, 0.36, 0.25, mat(C.tire)); w.rotation.x = Math.PI / 2; w.position.set(x, 0.36, z); g.add(w); }
  return { group: g, update(p) { moveAlong(s, g, p); } };
};

F.house = (s) => {
  const g = new THREE.Group(); const w = s.w ?? 8, d = s.d ?? 7, h = s.h ?? 6;
  g.add(box(w, h, d, mat(s.color ?? 0xece3d2), 0, h / 2, 0));
  const roof = mesh(new THREE.ConeGeometry(Math.max(w, d) * 0.78, 3, 4), mat(0xa4472f, { flat: true })); roof.rotation.y = Math.PI / 4; roof.scale.set(w / Math.max(w, d), 1, d / Math.max(w, d)); roof.position.y = h + 1.5; g.add(roof);
  for (const x of [-w / 4, w / 4]) for (const y of [h * 0.3, h * 0.72]) g.add(box(1.2, 1.2, 0.05, mat(C.glass, { rough: 0.2 }), x, y, d / 2 + 0.03));
  return { group: g, update() {} };
};

F.tower_crane = (s) => {
  const g = new THREE.Group(); const red = mat(s.color ?? 0xf2b705, { rough: 0.5, metal: 0.2 });
  const sec = 3, mw = 2;
  const mastGeo = (h) => {
    const gs = []; const n = Math.ceil(h / sec);
    for (let i = 0; i < n; i++) {
      const y0 = i * sec, y1 = y0 + sec; const c = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([a, b]) => [a * mw / 2, b * mw / 2]);
      for (let k = 0; k < 4; k++) {
        const [x0, z0] = c[k], [x1, z1] = c[(k + 1) % 4];
        gs.push(beamGeo(new V3(x0, y0, z0), new V3(x0, y1, z0), 0.16));
        gs.push(beamGeo(new V3(x0, y0, z0), new V3(x1, y1, z1), 0.08));
        gs.push(beamGeo(new V3(x0, y1, z0), new V3(x1, y1, z1), 0.08));
      }
    }
    return mergeGeometries(gs);
  };
  const h0 = s.height ?? 40, h1 = s.height_to ?? h0;
  const mastFull = mesh(mastGeo(Math.max(h0, h1)), red); g.add(mastFull);
  g.add(box(4, 1, 4, mat(C.concrete), 0, -0.5, 0));
  const top = new THREE.Group(); g.add(top);
  const slew = new THREE.Group(); top.add(slew);
  const JL = s.jib ?? 45, CJ = 14;
  const jibGeo = () => {
    const gs = []; const n = Math.ceil(JL / sec);
    for (let i = 0; i < n; i++) {
      const x0 = i * sec, x1 = x0 + sec;
      for (const z of [-0.8, 0.8]) { gs.push(beamGeo(new V3(x0, 0, z), new V3(x1, 0, z), 0.14)); gs.push(beamGeo(new V3(x0, 0, z), new V3(x1, 1.6, 0), 0.07)); }
      gs.push(beamGeo(new V3(x0, 1.6, 0), new V3(x1, 1.6, 0), 0.12)); gs.push(beamGeo(new V3(x1, 0, -0.8), new V3(x1, 0, 0.8), 0.07));
    }
    return mergeGeometries(gs);
  };
  slew.add(mesh(jibGeo(), red));
  slew.add(box(CJ, 0.6, 2.2, red, -CJ / 2, 0.3, 0));
  for (let i = 0; i < 4; i++) slew.add(box(1.0, 2.6, 2.2, mat(C.concrete), -CJ + 1 + i * 1.05, -1.0, 0));
  const apexGeo = mergeGeometries([beamGeo(new V3(-1, 0, -0.8), new V3(0, 7, 0), 0.18), beamGeo(new V3(1, 0, -0.8), new V3(0, 7, 0), 0.18),
    beamGeo(new V3(-1, 0, 0.8), new V3(0, 7, 0), 0.18), beamGeo(new V3(1, 0, 0.8), new V3(0, 7, 0), 0.18),
    beamGeo(new V3(0, 7, 0), new V3(JL * 0.7, 1.6, 0), 0.05), beamGeo(new V3(0, 7, 0), new V3(-CJ, 0.6, 0), 0.05)]);
  slew.add(mesh(apexGeo, red));
  slew.add(box(2.0, 2.0, 1.8, mat(s.color ?? 0xf2b705), 1.6, -1.3, 1.6));
  slew.add(box(0.05, 1.3, 1.5, mat(C.glass, { rough: 0.1 }), 2.62, -1.2, 1.6));
  const trolley = new THREE.Group(); slew.add(trolley); trolley.add(box(1.6, 0.5, 1.8, mat(C.dark), 0, -0.3, 0));
  const cable = cyl(0.04, 0.04, 1, mat(0x222222), 6); cable.geometry.translate(0, -0.5, 0); trolley.add(cable);
  const hook = new THREE.Group(); trolley.add(hook); hook.add(box(0.7, 0.9, 0.5, mat(C.cat)));
  let loadObj = null;
  if (s.load === 'beam') { loadObj = box(10, 0.6, 0.4, mat(0xb4462d, { metal: 0.4, rough: 0.5 }), 0, -2.4, 0); }
  else if (s.load === 'bucket') { loadObj = cyl(0.9, 0.6, 1.8, mat(0x6b737c, { metal: 0.4 }), 16); loadObj.position.y = -1.6; }
  else if (s.load === 'panel') { loadObj = box(6, 3.2, 0.3, mat(C.glass, { rough: 0.15, metal: 0.3 }), 0, -2.6, 0); }
  if (loadObj) hook.add(loadObj);
  return {
    group: g, update(p, t) {
      const h = s.anim === 'climb' ? lerp(h0, h1, easeIO(p)) : h0;
      const n = Math.max(h0, h1); mastFull.scale.y = h / n; top.position.y = h;
      const sw = s.anim === 'swing' ? (s.swing ?? 90) * easeIO(p) : 0;
      slew.rotation.y = (s.slew ?? 0) * DEG + sw * DEG + (s.anim === 'idle' ? Math.sin(t * 0.3) * 0.05 : 0);
      const tr = lerp(s.trolley_from ?? JL * 0.75, s.trolley_to ?? (s.trolley_from ?? JL * 0.75), easeIO(p));
      trolley.position.x = tr;
      const drop = lerp(s.drop_from ?? h * 0.4, s.drop_to ?? (s.drop_from ?? h * 0.4), easeIO(p));
      cable.scale.y = drop; hook.position.y = -drop - 0.6;
      if (loadObj) loadObj.rotation.y = Math.sin(t * 0.7) * 0.15;
    },
  };
};

F.building = (s, ctx) => {
  const g = new THREE.Group(); const N = s.floors ?? 12, fh = s.floor_h ?? 3.6, w = s.w ?? 24, d = s.d ?? 18, span = s.span ?? 6;
  const conc = mat(C.concrete, { rough: 0.9 }); const glassM = mat(s.glass ?? C.glass, { rough: 0.12, metal: 0.55, emissive: ctx.night ? 0xffcc77 : 0x000000, ei: 0.35 });
  const nx = Math.round(w / span), nz = Math.round(d / span);
  const colGeo = []; for (let i = 0; i <= nx; i++) for (let j = 0; j <= nz; j++) { const c = new THREE.BoxGeometry(0.6, fh, 0.6); c.translate(-w / 2 + i * w / nx, fh / 2, -d / 2 + j * d / nz); colGeo.push(c); }
  const colsG = mergeGeometries(colGeo);
  const floors = [];
  for (let k = 0; k < N; k++) {
    const fl = new THREE.Group(); fl.position.y = k * fh; g.add(fl);
    const cols = mesh(colsG, conc); fl.add(cols);
    const slab = box(w + 0.6, 0.35, d + 0.6, conc, 0, fh, 0); fl.add(slab);
    const fac = new THREE.Group(); fl.add(fac);
    fac.add(box(w + 0.4, fh - 0.4, 0.12, glassM, 0, fh / 2, d / 2 + 0.25)); fac.add(box(w + 0.4, fh - 0.4, 0.12, glassM, 0, fh / 2, -d / 2 - 0.25));
    fac.add(box(0.12, fh - 0.4, d + 0.4, glassM, w / 2 + 0.25, fh / 2, 0)); fac.add(box(0.12, fh - 0.4, d + 0.4, glassM, -w / 2 - 0.25, fh / 2, 0));
    // formwork + rebar look on the floor being built
    const form = box(w + 1.2, 0.5, d + 1.2, mat(0x8a5a2b), 0, fh + 0.05, 0); fl.add(form);
    floors.push({ fl, cols, slab, fac, form });
  }
  g.add(box(w + 4, 0.8, d + 4, mat(C.concreteDark), 0, -0.4, 0));
  return {
    group: g, height: N * fh, update(p) {
      if (s.anim !== 'build') { floors.forEach((f) => { f.fl.visible = true; f.form.visible = false; f.fac.visible = s.facade !== false; }); return; }
      const fb = p * (N + 3); // floors built (facade lags 3 floors behind)
      floors.forEach((f, k) => {
        const q = clamp(fb - k); f.fl.visible = q > 0;
        f.cols.scale.y = clamp(q / 0.6) || 0.001; f.slab.visible = q > 0.6; f.form.visible = q > 0.55 && q < 1;
        f.fac.visible = s.facade !== false && fb - k > 3; f.fac.scale.y = clamp(fb - k - 3) || 0.001;
      });
    },
  };
};

F.bridge = (s, ctx) => {
  const g = new THREE.Group(); const n = s.spans ?? 4, L = s.span_len ?? 40, hgt = s.deck_h ?? 16, dw = s.deck_w ?? 14;
  const conc = mat(C.concrete, { rough: 0.85 });
  const total = n * L; const piers = [], segs = [];
  for (let i = 0; i <= n; i++) {
    const x = -total / 2 + i * L; const pg = new THREE.Group(); pg.position.x = x; g.add(pg);
    const depth = ctx.world === 'sea' ? 12 : 0;
    for (const z of [-dw * 0.28, dw * 0.28]) { const c = cyl(1.3, 1.5, hgt + depth, conc); c.position.set(0, (hgt - depth) / 2, z); pg.add(c); }
    pg.add(box(3.4, 1.8, dw + 1, conc, 0, hgt - 0.9, 0));
    piers.push(pg);
  }
  const segL = 5; const nseg = Math.round(L / segL);
  for (let i = 0; i < n; i++) for (let k = 0; k < nseg; k++) {
    const x = -total / 2 + i * L + (k + 0.5) * segL;
    const sg = box(segL - 0.05, 2.0, dw, conc, x, hgt + 1.0, 0);
    const half = k < nseg / 2 ? k : nseg - 1 - k; // balanced cantilever order
    segs.push({ m: sg, order: half, span: i }); g.add(sg);
  }
  const rail = [];
  for (const z of [-dw / 2 + 0.3, dw / 2 - 0.3]) { const r = box(total, 1.0, 0.3, mat(0xdedad2), 0, hgt + 2.5, z); g.add(r); rail.push(r); }
  const road = box(total, 0.05, dw - 1.5, mat(C.road, { rough: 0.9 }), 0, hgt + 2.03, 0); g.add(road);
  let pylon = null;
  if (s.style === 'cable') {
    pylon = new THREE.Group(); g.add(pylon);
    const ph = s.pylon_h ?? 55;
    pylon.add(mesh(mergeGeometries([beamGeo(new V3(0, 0, -dw / 2 - 1), new V3(0, hgt + ph, 0), 1.6), beamGeo(new V3(0, 0, dw / 2 + 1), new V3(0, hgt + ph, 0), 1.6)]), conc));
    const cg = []; for (const z of [-dw / 2 + 0.5, dw / 2 - 0.5]) for (let k = 1; k <= 8; k++) for (const sg2 of [-1, 1]) cg.push(beamGeo(new V3(0, hgt + ph - k * 2.2, z * 0.15), new V3(sg2 * k * (total * 0.45 / 8), hgt + 2.5, z), 0.12));
    const cables = mesh(mergeGeometries(cg), mat(0xf0f0f0, { rough: 0.3 })); pylon.add(cables); pylon.userData.cables = cables;
  }
  return {
    group: g, update(p) {
      if (s.anim !== 'build') return;
      const pp = clamp(p / 0.35); piers.forEach((pg, i) => { const q = clamp(pp * (n + 1) - i * 0.6); pg.scale.y = q || 0.001; pg.visible = q > 0; });
      const dp = clamp((p - 0.35) / 0.55); const maxO = Math.ceil(nseg / 2);
      segs.forEach((sg) => { sg.m.visible = dp * (maxO + n * 0.5) - sg.span * 0.5 > sg.order; });
      const done = p > 0.92; rail.forEach((r) => (r.visible = done)); road.visible = done;
      if (pylon) { pylon.scale.y = clamp(p / 0.5) || 0.001; pylon.userData.cables.visible = p > 0.6; }
    },
  };
};

F.tbm = (s, ctx) => {
  // axis along +x. Origin = start of tunnel. Machine head advances from `pos` by `advance` m.
  const g = new THREE.Group(); const R = s.radius ?? 3.3, Lm = 11, adv = s.advance ?? 30;
  const machine = new THREE.Group(); g.add(machine);
  const shield = mesh(new THREE.CylinderGeometry(R, R, Lm, 40, 1, true), mat(s.color ?? 0x3d7fc4, { metal: 0.5, rough: 0.35, side: THREE.DoubleSide }));
  shield.rotation.z = Math.PI / 2; shield.position.x = -Lm / 2; machine.add(shield);
  const head = new THREE.Group(); head.position.x = 0.2; machine.add(head);
  const disk = cyl(R * 0.98, R * 0.98, 0.6, mat(0xd8a21c, { metal: 0.6, rough: 0.35 }), 40); disk.rotation.z = Math.PI / 2; head.add(disk);
  for (let i = 0; i < 6; i++) { const sp = box(0.3, R * 1.9, 0.5, mat(0x555a60, { metal: 0.6 })); sp.position.x = 0.35; sp.rotation.x = (i * Math.PI) / 6; head.add(sp); }
  for (let i = 0; i < 30; i++) { const a = i * 2.4, r = (0.3 + (i / 30) * 0.65) * R; const c = cyl(0.18, 0.18, 0.2, mat(C.steel, { metal: 0.8, rough: 0.2 }), 10); c.rotation.z = Math.PI / 2; c.position.set(0.7, Math.cos(a) * r, Math.sin(a) * r); head.add(c); }
  // gantry train
  for (let i = 0; i < 4; i++) { const gy = box(9, R * 0.9, R * 1.1, mat(i % 2 ? 0xe0e0e0 : 0x3d7fc4, { metal: 0.3, rough: 0.5 }), -Lm - 5 - i * 10, -R * 0.35, 0); machine.add(gy); }
  // tunnel lining rings (back half only, so we see inside) — appear behind the shield
  const ringW = 1.5, nRings = Math.ceil((adv + Lm + 45) / ringW);
  const rg = new THREE.CylinderGeometry(R * 0.97, R * 0.97, ringW - 0.08, 40, 1, true, Math.PI, Math.PI); rg.rotateZ(Math.PI / 2);
  const ringM = mat(0xb9b3a8, { side: THREE.DoubleSide, rough: 0.9 });
  const rings = []; for (let i = 0; i < nRings; i++) { const r = mesh(rg, ringM); r.position.x = -i * ringW - Lm; g.add(r); rings.push(r); }
  const rail = box(nRings * ringW, 0.15, 1.6, mat(0x444444), 0, -R * 0.82, 0); g.add(rail);
  // soil plug ahead of the machine (fills the half-tunnel notch in the cutaway)
  let plug = null;
  if (ctx.world === 'cutaway') {
    const pg = new THREE.CylinderGeometry(R + 0.02, R + 0.02, 1, 40, 1, false, Math.PI, Math.PI); pg.rotateZ(Math.PI / 2);
    pg.translate(0.5, 0, 0); strataUV(pg, -R - 4, R + 4);
    plug = mesh(pg, new THREE.MeshStandardMaterial({ map: ctx.strata, roughness: 1 })); g.add(plug);
  }
  const len = ctx.tunnelLen ?? 140;
  return {
    group: g, update(p, t) {
      const x = adv * (s.anim === 'bore' ? p : 1); machine.position.x = x; head.rotation.x = t * (s.spin ?? 1.4);
      rings.forEach((r, i) => { r.visible = r.position.x < x - Lm + 0.5 && r.position.x > -len; });
      rail.position.x = x - Lm - (nRings * ringW) / 2;
      if (plug) { const st = x + 0.8; plug.position.x = st; plug.scale.x = Math.max(0.01, len - st - g.position.x); }
    },
  };
};

F.blast = (s) => {
  const g = new THREE.Group(); const r = rng(s.seed ?? 7); const n = s.count ?? 160, sz = s.size ?? 1;
  const rocks = new THREE.InstancedMesh(new THREE.DodecahedronGeometry(0.6 * sz, 0), mat(s.rock ?? 0x7d6a58, { flat: true }), n);
  rocks.castShadow = true; g.add(rocks);
  const vel = []; for (let i = 0; i < n; i++) { const a = r() * Math.PI * 2, up = 8 + r() * 18; const out = 4 + r() * 12; vel.push([Math.cos(a) * out * (s.dir_x ?? 1) + (s.push ?? 6), up, Math.sin(a) * out, r() * 5, r()]); }
  const dust = []; const dm = new THREE.MeshStandardMaterial({ color: s.dust ?? 0xb59d80, transparent: true, opacity: 0.8, roughness: 1, depthWrite: false });
  for (let i = 0; i < 26; i++) { const d = new THREE.Mesh(new THREE.IcosahedronGeometry(1, 1), dm.clone()); d.userData = { x: (r() - 0.5) * 18 * sz, z: (r() - 0.5) * 10 * sz, sp: 0.6 + r(), up: 0.3 + r() * 1.2 }; g.add(d); dust.push(d); }
  const flash = new THREE.PointLight(0xffaa55, 0, 60 * sz, 1.5); flash.position.y = 4; g.add(flash);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
  const holes = []; for (let i = 0; i < 12; i++) { const h = cyl(0.25, 0.25, 0.1, mat(0x222222)); h.position.set(-7 * sz + (i % 6) * 2.8 * sz, 0.05, (Math.floor(i / 6) - 0.5) * 4 * sz); g.add(h); holes.push(h); }
  return {
    group: g, update(p, t) {
      const t0 = (s.at ?? 0.3) * ctx_dur(); const tt = t - t0;
      holes.forEach((h) => (h.visible = tt < 0));
      for (let i = 0; i < n; i++) {
        const [vx, vy, vz, spin, dl] = vel[i];
        if (tt < 0) { m4.makeScale(0.0001, 0.0001, 0.0001); }
        else {
          const ts = Math.max(0, tt - dl * 0.15) * (s.slowmo ? 0.45 : 1);
          let y = vy * ts - 4.9 * ts * ts; let k = 1; if (y < 0) { y = 0; k = 0; }
          const tl = k ? ts : Math.max(vy / 4.9, 0);
          e.set(spin * tl, spin * 0.7 * tl, 0); q.setFromEuler(e);
          m4.compose(new V3(vx * tl * sz, y * sz + 0.5, vz * tl * sz), q, new V3(1, 1, 1).multiplyScalar(0.5 + vel[i][4]));
        }
        rocks.setMatrixAt(i, m4);
      }
      rocks.instanceMatrix.needsUpdate = true;
      dust.forEach((d) => {
        const u = d.userData; if (tt < 0) { d.visible = false; return; } d.visible = true;
        const k = 1 - Math.exp(-tt * 0.9 * u.sp * (s.slowmo ? 0.5 : 1));
        const sc = (1.5 + 9 * k) * sz; d.scale.setScalar(sc); d.position.set(u.x * (0.5 + k), sc * 0.6 + u.up * k * 10 * sz, u.z * (0.5 + k));
        d.material.opacity = 0.85 * Math.exp(-tt * 0.12);
      });
      flash.intensity = tt >= 0 ? 4000 * sz * Math.exp(-tt * 6) : 0;
    },
  };
};
let _dur = 5; const ctx_dur = () => _dur;

F.ore_pile = (s) => {
  const g = new THREE.Group(); const r = s.radius ?? 8, h = s.h ?? r * 0.7;
  const geo = new THREE.ConeGeometry(r, h, 14, 4); const pos = geo.attributes.position; const rr = rng(s.seed ?? 3);
  for (let i = 0; i < pos.count; i++) if (pos.getY(i) < h / 2 - 0.01) { pos.setX(i, pos.getX(i) * (0.9 + rr() * 0.2)); pos.setZ(i, pos.getZ(i) * (0.9 + rr() * 0.2)); }
  geo.computeVertexNormals(); const m = mesh(geo, mat(s.color ?? 0x8b4a2b, { flat: true, rough: 1 })); m.position.y = h / 2; g.add(m);
  return { group: g, update(p) { if (s.anim === 'grow') { const k = 0.2 + 0.8 * p; m.scale.set(k, k, k); m.position.y = (h / 2) * k; } } };
};

F.conveyor = (s) => {
  const g = new THREE.Group(); const L = s.length ?? 40, inc = (s.incline ?? 12) * DEG, hgt = s.h ?? 2;
  const belt = new THREE.Group(); belt.rotation.z = inc; belt.position.y = hgt; g.add(belt);
  belt.add(box(L, 0.3, 1.4, mat(0x222222), L / 2, 0, 0));
  belt.add(box(L, 0.5, 0.15, mat(C.cat), L / 2, 0.1, 0.8)); belt.add(box(L, 0.5, 0.15, mat(C.cat), L / 2, 0.1, -0.8));
  for (let x = 2; x < L; x += 6) { const y = hgt + Math.sin(inc) * x; const leg = box(0.3, y, 0.3, mat(C.steelDark), x * Math.cos(inc), y / 2, 0); g.add(leg); }
  const n = Math.floor(L / 1.6); const lumps = new THREE.InstancedMesh(new THREE.DodecahedronGeometry(0.35, 0), mat(s.color ?? 0x8b4a2b, { flat: true }), n); belt.add(lumps);
  const m4 = new THREE.Matrix4();
  return { group: g, update(p, t) { for (let i = 0; i < n; i++) { const x = (i * 1.6 + t * (s.speed ?? 3)) % L; m4.makeTranslation(x, 0.4, ((i * 37) % 7 - 3) * 0.12); lumps.setMatrixAt(i, m4); } lumps.instanceMatrix.needsUpdate = true; } };
};

F.factory = (s, ctx) => {
  const g = new THREE.Group(); const w = s.w ?? 40, d = s.d ?? 24, h = s.h ?? 14;
  g.add(box(w, h, d, mat(s.color ?? 0xb7bfc6, { metal: 0.3, rough: 0.6 }), 0, h / 2, 0));
  const roof = mesh(new THREE.CylinderGeometry(d / 2, d / 2, w, 20, 1, false, 0, Math.PI), mat(0x8d969e, { metal: 0.4 })); roof.rotation.z = Math.PI / 2; roof.rotation.y = 0; roof.scale.set(1, 1, 0.35); roof.position.y = h; g.add(roof);
  const stacks = []; for (let i = 0; i < (s.chimneys ?? 3); i++) { const c = cyl(1.4, 1.8, h * 2.6, mat(0xd8d2c8), 16); c.position.set(-w / 2 + 6 + i * 7, h * 1.3, -d / 2 - 3); g.add(c); stacks.push(c); c.add(box(3.7, 1.2, 3.7, mat(C.red), 0, h * 1.1, 0)); }
  const smoke = []; const sm = new THREE.MeshStandardMaterial({ color: 0xe8e4de, transparent: true, opacity: 0.55, depthWrite: false, roughness: 1 });
  stacks.forEach((c, i) => { for (let k = 0; k < 8; k++) { const m = new THREE.Mesh(new THREE.IcosahedronGeometry(1.6, 1), sm.clone()); m.userData = { c, k }; g.add(m); smoke.push(m); } });
  if (ctx.night) for (let i = 0; i < 8; i++) g.add(box(2, 1.2, 0.1, mat(0xffd27a, { emissive: 0xffb84d, ei: 1.5 }), -w / 2 + 4 + i * (w - 8) / 7, h * 0.6, d / 2 + 0.06));
  return { group: g, update(p, t) { smoke.forEach((m) => { const { c, k } = m.userData; const ph = (t * 0.25 + k / 8) % 1; m.position.set(c.position.x + ph * 8, h * 2.6 + ph * 18, c.position.z); m.scale.setScalar(1 + ph * 3.5); m.material.opacity = 0.55 * (1 - ph); }); } };
};

F.trees = (s) => {
  const g = new THREE.Group(); const r = rng(s.seed ?? 11); const n = s.count ?? 40; const [ax, az] = s.area ?? [120, 120]; const hole = s.clear ?? 0;
  const tg = new THREE.ConeGeometry(2.2, 6, 7); tg.translate(0, 5, 0); const kg = new THREE.CylinderGeometry(0.3, 0.4, 2.5, 6); kg.translate(0, 1.2, 0);
  const crowns = new THREE.InstancedMesh(tg, mat(s.color ?? 0x4f7a32, { flat: true }), n), trunks = new THREE.InstancedMesh(kg, mat(0x6b4a2f), n);
  crowns.castShadow = trunks.castShadow = true;
  const m4 = new THREE.Matrix4(); let i = 0, guard = 0;
  while (i < n && guard++ < n * 20) { const x = (r() - 0.5) * ax, z = (r() - 0.5) * az; if (Math.hypot(x, z) < hole) continue; const sc = 0.7 + r() * 0.8; m4.compose(new V3(x, 0, z), new THREE.Quaternion(), new V3(sc, sc, sc)); crowns.setMatrixAt(i, m4); trunks.setMatrixAt(i, m4); i++; }
  crowns.count = trunks.count = i; g.add(crowns, trunks); return { group: g, update() {} };
};

F.city = (s, ctx) => {
  const g = new THREE.Group(); const r = rng(s.seed ?? 5); const n = s.count ?? 60; const [ax, az] = s.area ?? [300, 300]; const hole = s.clear ?? 50;
  const geo = new THREE.BoxGeometry(1, 1, 1); geo.translate(0, 0.5, 0);
  const cols = [0xd9d4cc, 0xbfc7cf, 0xa9b4bf, 0xe6ddd0, 0x9aa6b2];
  const im = new THREE.InstancedMesh(geo, new THREE.MeshStandardMaterial({ roughness: 0.6, metalness: 0.2, emissive: ctx.night ? 0x332200 : 0 }), n); im.castShadow = true; im.receiveShadow = true;
  const m4 = new THREE.Matrix4(); let i = 0, guard = 0;
  while (i < n && guard++ < n * 30) { const x = (r() - 0.5) * ax, z = (r() - 0.5) * az; if (Math.hypot(x, z) < hole) continue; const w = 10 + r() * 16, h = 12 + r() ** 2 * (s.max_h ?? 90); m4.compose(new V3(x, 0, z), new THREE.Quaternion(), new V3(w, h, w * (0.7 + r() * 0.6))); im.setMatrixAt(i, m4); im.setColorAt(i, new THREE.Color(cols[i % cols.length])); i++; }
  im.count = i; g.add(im); return { group: g, update() {} };
};

F.road = (s) => {
  const g = new THREE.Group(); const L = s.length ?? 100, w = s.w ?? 10;
  g.add(box(L, 0.1, w, mat(C.road, { rough: 0.95 }), 0, 0.05, 0));
  for (let x = -L / 2 + 2; x < L / 2; x += 8) g.add(box(4, 0.02, 0.25, mat(0xf2f2f2), x, 0.11, 0));
  return { group: g, update() {} };
};

F.pile = (s, ctx) => {
  // piles driven into the ground. In the cutaway world they show below ground.
  const g = new THREE.Group(); const n = s.count ?? 4, sp = s.spacing ?? 6, len = s.length ?? 20, r = s.radius ?? 0.5;
  const piles = []; for (let i = 0; i < n; i++) { const p = cyl(r, r, len, mat(C.concrete, { rough: 0.8 }), 16); p.position.set((i - (n - 1) / 2) * sp, 0, 0); g.add(p); piles.push(p); }
  const rig = new THREE.Group(); g.add(rig);
  rig.add(box(5, 1.4, 4, mat(s.color ?? C.cat), -2.2, 1.2, 0)); rig.add(box(5.5, 0.9, 4.2, mat(C.dark), -2.2, 0.45, 0));
  rig.add(box(0.8, len + 6, 0.8, mat(C.cat), 0, (len + 6) / 2 + 1, 0));
  const hammer = box(1.4, 3, 1.4, mat(C.dark), 0, 0, 0); rig.add(hammer);
  return {
    group: g, update(p, t) {
      const per = 1 / n;
      piles.forEach((pl, i) => { const q = clamp((p - i * per) / per); const depth = s.anim === 'drive' ? easeIO(q) : 1; pl.position.y = len / 2 + 1 - depth * len; });
      const cur = Math.min(n - 1, Math.floor(p * n)); rig.position.x = piles[cur].position.x;
      const top = piles[cur].position.y + len / 2; hammer.position.y = top + 1.6 + Math.abs(Math.sin(t * 5)) * 1.2;
    },
  };
};

F.column = (s) => {
  // reinforced concrete column cutaway: rebar cage + concrete pour rising (transparent shell)
  const g = new THREE.Group(); const w = s.w ?? 1.2, h = s.h ?? 6; const n = 3;
  const rb = []; for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { if (i % (n - 1) && j % (n - 1)) continue; const x = -w * 0.38 + (i * w * 0.76) / (n - 1), z = -w * 0.38 + (j * w * 0.76) / (n - 1); rb.push(beamGeo(new V3(x, 0, z), new V3(x, h + 0.8, z), 0.06)); }
  for (let y = 0.2; y < h; y += 0.3) { const a = w * 0.4; for (const [p0, p1] of [[[-a, -a], [a, -a]], [[a, -a], [a, a]], [[a, a], [-a, a]], [[-a, a], [-a, -a]]]) rb.push(beamGeo(new V3(p0[0], y, p0[1]), new V3(p1[0], y, p1[1]), 0.03)); }
  g.add(mesh(mergeGeometries(rb), mat(C.rebar, { metal: 0.6, rough: 0.5 })));
  const form = box(w + 0.1, h, w + 0.1, mat(0x9a6b3a, { opacity: 0.18 }), 0, h / 2, 0); form.castShadow = false; g.add(form);
  const conc = box(w, h, w, mat(0xa9a49b, { rough: 0.95 }), 0, h / 2, 0); conc.geometry.translate(0, -h / 2 + h / 2, 0); g.add(conc);
  conc.geometry = new THREE.BoxGeometry(w, h, w).translate(0, h / 2, 0); conc.position.y = 0;
  return { group: g, update(p) { const q = s.anim === 'pour' ? easeIO(p) : (s.filled ?? 0); conc.visible = q > 0.01; conc.scale.y = Math.max(q, 0.001); } };
};

F.dimension = (s) => {
  // vertical measurement: line from pos up to h, with a label
  const g = new THREE.Group(); const h = s.h ?? 10;
  const line = box(0.12 * (s.thick ?? 1), 1, 0.12 * (s.thick ?? 1), mat(0xffc400, { emissive: 0xffc400, ei: 0.6 }), 0, 0, 0); line.geometry.translate(0, 0.5, 0); line.castShadow = false; g.add(line);
  const t0 = box(1.4 * (s.thick ?? 1), 0.12, 0.12, line.material, 0, 0, 0); const t1 = t0.clone(); g.add(t0, t1); t0.castShadow = t1.castShadow = false;
  const lab = textSprite(s.label ?? `${h} m`, { size: s.label_size ?? h * 0.12 + 1 }); g.add(lab);
  return { group: g, update(p) { const q = s.anim === 'grow' ? easeIO(p / 0.7) : 1; line.scale.y = Math.max(h * q, 0.01); t1.position.y = h * q; lab.position.set(s.label_side ?? 0, h * q + (s.label_size ?? h * 0.12 + 1) * 0.7, 0); lab.visible = q > 0.6; } };
};

F.label = (s) => { const g = new THREE.Group(); const l = textSprite(s.text, { size: s.size ?? 3, color: s.color, bg: s.bg }); g.add(l); return { group: g, update(p) { l.visible = p >= (s.show_at ?? 0); } }; };

F.dam = (s) => {
  const g = new THREE.Group(); const L = s.length ?? 120, h = s.h ?? 40;
  const sh = new THREE.Shape(); sh.moveTo(-h * 0.45, 0); sh.lineTo(h * 0.2, 0); sh.lineTo(-h * 0.05, h); sh.lineTo(-h * 0.15, h); sh.lineTo(-h * 0.45, 0);
  const geo = new THREE.ExtrudeGeometry(sh, { depth: L, bevelEnabled: false }); geo.translate(0, 0, -L / 2);
  const dm = mesh(geo, mat(C.concrete, { rough: 0.9 })); g.add(dm);
  const water = box(160, h * 0.85, L, mat(C.water, { rough: 0.15, metal: 0.2, opacity: 0.92 }), -80 - h * 0.3, h * 0.42, 0); g.add(water);
  const sp = box(h * 0.8, 0.6, 14, mat(0xd8f0ff, { opacity: 0.7, emissive: 0x88aacc, ei: 0.3 })); sp.position.set(h * 0.2, h * 0.3, 0); sp.rotation.z = -1.05; g.add(sp);
  return { group: g, update(p) { if (s.anim === 'build') { dm.scale.y = Math.max(easeIO(p), 0.001); water.scale.y = Math.max(clamp((p - 0.6) / 0.4), 0.001); water.position.y = h * 0.42 * water.scale.y; sp.visible = p > 0.95; } else sp.visible = s.spill !== false; } };
};

F.base_isolator = (s) => {
  // building on rubber bearings; anim quake: ground shakes, building sways less
  const g = new THREE.Group(); const ground = new THREE.Group(); g.add(ground);
  ground.add(box(30, 2, 24, mat(C.concreteDark), 0, -1, 0));
  const isos = []; for (const x of [-10, 0, 10]) for (const z of [-7, 7]) { const c = cyl(1.2, 1.2, 1.4, mat(0x222222, { rough: 0.8 }), 20); c.position.set(x, 0.7, z); g.add(c); isos.push(c); }
  const bld = new THREE.Group(); bld.position.y = 1.4; g.add(bld);
  const b = F.building({ floors: s.floors ?? 8, w: 26, d: 20 }, { night: false }); bld.add(b.group); b.update(1);
  return { group: g, update(p, t) { const on = s.anim === 'quake' ? smooth(p / 0.15) * (1 - smooth((p - 0.85) / 0.15)) : 0; const gx = Math.sin(t * 14) * 0.9 * on + Math.sin(t * 9.3) * 0.5 * on; ground.position.x = gx; isos.forEach((c) => { c.position.x = Math.round(c.position.x / 10) * 10 + gx * 0.5; c.rotation.z = -gx * 0.04; }); bld.position.x = gx * 0.12; } };
};


F.zone = (s) => {
  // translucent warning area on the ground (blind spot, danger zone)
  const g = new THREE.Group(); const w = s.w ?? 10, d = s.d ?? 8;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshBasicMaterial({ color: s.color ?? 0xff3b2f, transparent: true, opacity: 0.45, depthWrite: false }));
  m.rotation.x = -Math.PI / 2; m.position.y = 0.14; g.add(m);
  return { group: g, update(p, t) { m.material.opacity = (s.anim === 'pulse' ? 0.3 + 0.2 * Math.sin(t * 5) : 0.45) * smooth(p / 0.15); } };
};

F.flag = (s) => {
  // safety whip flag mounted on light vehicles in mines (tall pole, flag + beacon)
  const g = new THREE.Group(); const h = s.h ?? 4.2;
  const pole = cyl(0.04, 0.05, h, mat(0xf2f2f2), 8); pole.position.y = 1.4 + h / 2; g.add(pole);
  const fl = box(0.02, 0.5, 0.75, mat(s.color ?? 0xff5a00, { emissive: 0x662200 }), 0, 1.4 + h - 0.3, -0.4); g.add(fl);
  const bc = mesh(new THREE.SphereGeometry(0.12, 10, 8), mat(0xffa000, { emissive: 0xff8800, ei: 2 })); bc.position.y = 1.4 + h + 0.1; g.add(bc);
  return { group: g, update(p, t) { fl.rotation.y = Math.sin(t * 6) * 0.25; bc.material.emissiveIntensity = Math.sin(t * 9) > 0 ? 3 : 0.3; } };
};

// ---------------------------------------------------------------- road building (pengaspalan)
// layer tops (m, exaggerated for visibility): sub 0, lpb 0.35, lpa 0.65, prime 0.67, acbc 0.83, acwc 0.95
const ROAD_LAYERS = [
  ['sub', -0.6, 0, 0x8a5a36, 'TANAH DASAR'], ['lpb', 0, 0.35, 0x8f8475, 'LPB'], ['lpa', 0.35, 0.65, 0xb3aa9c, 'LPA'],
  ['prime', 0.65, 0.67, 0x3a2a1c, 'PRIME COAT'], ['acbc', 0.67, 0.83, 0x2e2e31, 'AC-BC'], ['acwc', 0.83, 0.95, 0x1d1d20, 'AC-WC'],
];
F.road_layers = (s) => {
  // a road section along x. `layers`: finished layers; `build`: the layer being laid (front advances with progress).
  const g = new THREE.Group(); const L = s.length ?? 80, Wd = s.w ?? 7; const done = new Set(s.layers ?? ['sub']);
  const parts = []; const tags = [];
  ROAD_LAYERS.forEach(([name, y0, y1, col, tag], i) => {
    if (!done.has(name) && s.build !== name) return;
    const w = Wd + (ROAD_LAYERS.length - i) * 0.35;
    const m = mesh(new THREE.BoxGeometry(1, y1 - y0, w), mat(col, { rough: name === 'prime' ? 0.25 : 0.95, metal: name === 'prime' ? 0.2 : 0 }));
    m.geometry.translate(0.5, (y0 + y1) / 2, 0); m.position.x = -L / 2; m.scale.x = L; g.add(m);
    parts.push({ name, m });
    if (s.tags && (done.has(name) || s.build === name)) { const tg = textSprite(tag, { size: s.tag_size ?? 0.55 }); tg.position.set(-L / 2 - 0.4, (y0 + y1) / 2, (i % 2 ? 1 : -1) * (Wd / 2 - 0.6)); tg.center.set(i % 2 ? 0 : 1, 0.5); tg.position.y *= (s.ey ?? 1); tg.userData.tag = true; tags.push(tg); }
  });
  // vertical exaggeration for cross-section shots (tags are kept outside so they are not stretched)
  const body = new THREE.Group(); body.scale.y = s.ey ?? 1; [...g.children].forEach((c) => body.add(c)); g.add(body); tags.forEach((t) => g.add(t));
  const marks = [];
  if (done.has('marking') || s.build === 'marking') {
    const top = 0.96; const mm = mat(0xf4f4f0, { emissive: 0x333333 });
    for (let x = -L / 2 + 1; x < L / 2 - 2; x += 6) { const d = box(3, 0.02, 0.15, mm, x + 1.5, top, 0); body.add(d); marks.push(d); }
    for (const z of [-Wd / 2 + 0.3, Wd / 2 - 0.3]) { const e = box(1, 0.02, 0.15, mm, 0, top, z); e.geometry.translate(0.5, 0, 0); e.position.x = -L / 2; e.scale.x = L; body.add(e); marks.push(e); }
  }
  return {
    group: g, update(p) {
      const front = -L / 2 + L * clamp(p);
      for (const { name, m } of parts) if (name === s.build) { m.scale.x = Math.max(front + L / 2, 0.01); m.visible = p > 0.001; }
      if (s.build === 'marking') marks.forEach((d) => { if (d.scale.x > 1.5) d.scale.x = Math.max(front + L / 2, 0.01); else d.visible = d.position.x < front; });
    },
  };
};

function shuttle(s, g, t, extra) {
  // moves back and forth between pos and `to` (period s), returns signed speed sign
  if (!s.to) return 0; const P = s.period ?? 6; const a = new V3(...s.pos), b = new V3(...s.to);
  const k = 0.5 - 0.5 * Math.cos((2 * Math.PI * (t + (s.phase ?? 0))) / P); g.position.lerpVectors(a, b, k);
  return Math.sin((2 * Math.PI * (t + (s.phase ?? 0))) / P) * a.distanceTo(b) * Math.PI / P;
}
function moveAlong(s, g, p) { if (!s.to) return; g.position.lerpVectors(new V3(...s.pos), new V3(...s.to), s.ease === false ? p : easeIO(p)); }

F.roller = (s) => {
  // kind: tandem (2 steel drums), pneumatic (rubber tyres), vibro (single drum soil compactor). anim: shuttle | drive
  const g = new THREE.Group(); const kind = s.kind ?? 'tandem'; const yel = mat(s.color ?? C.cat, { rough: 0.45 }); const steel = mat(0x9aa1a8, { metal: 0.7, rough: 0.3 });
  const spin = [];
  const drum = (x, r, w) => { const d = cyl(r, r, w, steel, 28); d.rotation.x = Math.PI / 2; d.position.set(x, r, 0); g.add(d); spin.push([d, r]); g.add(box(0.25, r * 1.3, w + 0.3, yel, x, r * 1.25, 0)); };
  if (kind === 'tandem') { drum(1.5, 0.6, 1.7); drum(-1.5, 0.6, 1.7); g.add(box(2.6, 0.9, 1.6, yel, 0, 1.3, 0)); }
  else if (kind === 'vibro') { drum(1.9, 0.8, 2.1); g.add(box(1.2, 1.0, 2.0, yel, 0.9, 1.6, 0)); g.add(box(2.6, 1.2, 1.9, yel, -1.2, 1.5, 0));
    for (const z of [-0.95, 0.95]) { const t = cyl(0.75, 0.75, 0.55, mat(C.tire, { rough: 0.95 }), 24); t.rotation.x = Math.PI / 2; t.position.set(-1.4, 0.75, z); g.add(t); spin.push([t, 0.75]); } }
  else { for (const [x, n] of [[1.3, 4], [-1.3, 3]]) for (let i = 0; i < n; i++) { const t = cyl(0.5, 0.5, 0.32, mat(C.tire, { rough: 0.95 }), 20); t.rotation.x = Math.PI / 2; t.position.set(x, 0.5, -0.8 + (1.6 * i) / (n - 1)); g.add(t); spin.push([t, 0.5]); } g.add(box(3.6, 1.0, 2.0, yel, 0, 1.3, 0)); }
  // operator platform + canopy
  const cx = kind === 'vibro' ? -1.2 : 0; const top = kind === 'vibro' ? 2.1 : 1.75;
  g.add(box(0.5, 0.8, 0.5, mat(C.dark), cx, top + 0.4, 0));
  for (const [dx, dz] of [[-0.6, -0.7], [0.6, -0.7], [-0.6, 0.7], [0.6, 0.7]]) g.add(box(0.08, 1.6, 0.08, mat(C.dark), cx + dx, top + 0.8, dz));
  g.add(box(1.5, 0.1, 1.7, yel, cx, top + 1.6, 0));
  const beacon = mesh(new THREE.SphereGeometry(0.1, 8, 6), mat(0xffa000, { emissive: 0xff8800, ei: 2 })); beacon.position.set(cx, top + 1.72, 0); g.add(beacon);
  let last = 0;
  return { group: g, update(p, t) {
    if (s.anim === 'shuttle') shuttle(s, g, t); else if (s.anim === 'drive') moveAlong(s, g, p);
    const x = g.position.x; spin.forEach(([o, r]) => { o.rotation.y = -x / r; }); last = x;
    if (s.vibrate !== false && kind !== 'pneumatic') g.position.y = (s.pos[1] ?? 0) + Math.sin(t * 90) * 0.012;
    beacon.material.emissiveIntensity = Math.sin(t * 8) > 0 ? 3 : 0.3;
  } };
};

F.grader = (s) => {
  const g = new THREE.Group(); const yel = mat(s.color ?? C.cat, { rough: 0.45 }); const dk = mat(C.dark);
  const wheels = [];
  for (const x of [3.9, -1.8, -3.3]) for (const z of [-1.05, 1.05]) { const w = cyl(0.65, 0.65, 0.45, mat(C.tire, { rough: 0.95 }), 22); w.rotation.x = Math.PI / 2; w.position.set(x, 0.65, z); g.add(w); wheels.push(w); }
  g.add(box(5.2, 0.45, 0.5, yel, 1.6, 1.55, 0)); // long front frame
  g.add(box(1.0, 0.6, 1.9, yel, 3.9, 1.2, 0));
  g.add(box(3.2, 1.3, 1.9, yel, -2.6, 1.55, 0)); // engine
  g.add(box(1.5, 1.6, 1.7, yel, -0.9, 2.6, 0)); // cab
  g.add(box(1.3, 1.0, 0.04, mat(C.glass, { rough: 0.1, metal: 0.3 }), -0.9, 2.8, 0.87));
  g.add(box(0.04, 1.0, 1.4, mat(C.glass, { rough: 0.1, metal: 0.3 }), -0.14, 2.8, 0));
  const blade = box(0.25, 0.6, 3.6, mat(0x555a60, { metal: 0.5 }), 1.2, 0.35, 0); blade.rotation.y = 0.45; g.add(blade);
  g.add(box(0.3, 0.9, 0.3, yel, 1.2, 0.95, 0));
  return { group: g, update(p, t) { if (s.anim === 'shuttle') shuttle(s, g, t); else moveAlong(s, g, p); wheels.forEach((w) => (w.rotation.y = -g.position.x / 0.65)); } };
};

F.paver = (s) => {
  // asphalt finisher: hopper at the front (+x), screed at the back spreading the mat. Moves with `to` (keep ease:false).
  const g = new THREE.Group(); const yel = mat(s.color ?? C.cat, { rough: 0.45 }); const dk = mat(C.dark); const W = s.screed_w ?? 7;
  for (const z of [-1.0, 1.0]) g.add(box(3.6, 0.7, 0.55, dk, 0.4, 0.35, z));
  g.add(box(3.4, 1.2, 2.6, yel, 0.2, 1.2, 0));
  // hopper (open box) at the front
  const hm = mat(s.color ?? C.cat, { rough: 0.5, side: THREE.DoubleSide });
  g.add(box(1.8, 0.12, 2.8, dk, 2.8, 1.0, 0)); g.add(box(1.8, 0.9, 0.1, hm, 2.8, 1.45, 1.45)); g.add(box(1.8, 0.9, 0.1, hm, 2.8, 1.45, -1.45));
  const mixload = box(1.6, 0.5, 2.6, mat(0x262628, { rough: 1 }), 2.8, 1.3, 0); g.add(mixload);
  // operator deck + canopy
  g.add(box(1.4, 0.15, 3.0, dk, -1.2, 1.9, 0));
  g.add(box(0.5, 0.9, 0.5, dk, -1.0, 2.4, 0.6));
  for (const [dx, dz] of [[-1.8, -1.4], [-0.6, -1.4], [-1.8, 1.4], [-0.6, 1.4]]) g.add(box(0.08, 1.8, 0.08, dk, dx, 2.8, dz));
  g.add(box(1.6, 0.1, 3.2, yel, -1.2, 3.7, 0));
  // screed at the back, as wide as the road
  g.add(box(1.0, 0.55, W, mat(0x3d3f44, { metal: 0.4 }), -2.3, 0.4, 0));
  g.add(box(0.15, 0.7, W, yel, -1.75, 0.6, 0));
  const augers = []; for (const z of [-1, 1]) { const a = cyl(0.18, 0.18, W / 2 - 1.3, mat(C.steel, { metal: 0.7 }), 10); a.rotation.x = Math.PI / 2; a.position.set(-1.6, 0.25, z * (W / 4 + 0.65)); g.add(a); augers.push(a); }
  const heat = []; const hmM = new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: 0.25, depthWrite: false });
  for (let k = 0; k < 8; k++) { const m = new THREE.Mesh(new THREE.IcosahedronGeometry(0.4, 1), hmM.clone()); m.userData.k = k; g.add(m); heat.push(m); }
  return { group: g, update(p, t) {
    moveAlong({ ...s, ease: s.ease ?? false }, g, p); augers.forEach((a) => (a.rotation.y = t * 6));
    heat.forEach((m) => { const k = m.userData.k, ph = (t * 0.4 + k / 8) % 1; m.position.set(-3.2 - ph * 2, 0.5 + ph * 2.5, ((k * 0.53) % 1 - 0.5) * W * 0.8); m.scale.setScalar(0.6 + ph * 2); m.material.opacity = 0.3 * (1 - ph); });
  } };
};

F.sprayer = (s) => {
  // asphalt distributor (or water tanker with color): tank truck with a spray bar at the back
  const g = new THREE.Group(); const dk = mat(C.dark);
  const wheels = []; for (const x of [2.4, -1.4, -2.6]) for (const z of [-1.0, 1.0]) { const w = cyl(0.5, 0.5, 0.35, mat(C.tire), 20); w.rotation.x = Math.PI / 2; w.position.set(x, 0.5, z); g.add(w); wheels.push(w); }
  g.add(box(7, 0.35, 1.2, dk, 0, 0.9, 0));
  g.add(box(1.8, 2.0, 2.4, mat(s.cab ?? 0xe8e8e8), 2.7, 1.9, 0)); g.add(box(0.05, 0.8, 2.1, mat(C.glass, { rough: 0.1 }), 3.62, 2.3, 0));
  const tank = cyl(1.05, 1.05, 4.6, mat(s.color ?? 0x2b2b2e, { metal: 0.5, rough: 0.35 }), 24); tank.rotation.z = Math.PI / 2; tank.position.set(-0.6, 2.1, 0); g.add(tank);
  g.add(box(0.15, 0.15, 2.8, mat(C.steel, { metal: 0.6 }), -3.3, 0.6, 0));
  const spray = []; const sm = new THREE.MeshStandardMaterial({ color: s.spray_color ?? 0x3a2a1c, transparent: true, opacity: 0.55, depthWrite: false });
  for (let i = 0; i < 9; i++) { const c = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.6, 8, 1, true), sm); c.position.set(-3.3, 0.28, -1.3 + i * 0.325); g.add(c); spray.push(c); }
  return { group: g, update(p, t) { moveAlong({ ...s, ease: s.ease ?? false }, g, p); wheels.forEach((w) => (w.rotation.y = -g.position.x / 0.5)); const on = s.anim !== 'idle' && p > 0.01 && p < 0.999; spray.forEach((c, i) => { c.visible = on; c.scale.y = 0.85 + 0.15 * Math.sin(t * 30 + i); }); } };
};

F.amp = (s, ctx) => {
  // asphalt mixing plant: cold bins -> conveyor -> rotating dryer drum -> hot elevator -> mixing tower -> truck below
  const g = new THREE.Group(); const yel = mat(s.color ?? 0x2f6db5, { metal: 0.3, rough: 0.5 }); const grey = mat(0xb9bec4, { metal: 0.3 });
  for (let i = 0; i < 4; i++) { const b = mesh(new THREE.CylinderGeometry(2.2, 0.7, 3, 4), mat(C.cat, { flat: true })); b.rotation.y = Math.PI / 4; b.position.set(-26 + i * 5, 4.2, 0); g.add(b); g.add(box(0.3, 2.7, 0.3, mat(C.dark), -26 + i * 5, 1.35, 0)); }
  const conv = box(22, 0.4, 1.0, mat(C.dark), -12, 3.5, -4); conv.rotation.z = 0.12; g.add(conv);
  const drum = cyl(1.6, 1.6, 11, grey, 24); drum.rotation.z = Math.PI / 2 + 0.07; drum.position.set(-2, 4.2, -6); g.add(drum);
  for (const x of [-5, 1]) g.add(box(0.8, 3.0, 3.0, yel, x, 1.5, -6));
  const elev = box(1.2, 18, 1.2, yel, 5.5, 9, -6); g.add(elev);
  g.add(box(6, 6, 6, yel, 8, 15, -1)); g.add(box(5, 3, 5, grey, 8, 10.5, -1));
  for (const x of [5.6, 10.4]) for (const z of [-3.4, 1.4]) g.add(box(0.5, 9, 0.5, yel, x, 4.5, z));
  g.add(box(3.4, 4, 3.4, grey, 16, 12, -1)); for (const x of [14.6, 17.4]) g.add(box(0.4, 10, 0.4, grey, x, 5, -1));
  const stack = cyl(0.9, 1.1, 20, grey, 16); stack.position.set(-8, 10, -12); g.add(stack); g.add(box(8, 5, 4, grey, -8, 2.5, -12));
  const smoke = []; const sm = new THREE.MeshStandardMaterial({ color: 0xeeeeee, transparent: true, opacity: 0.5, depthWrite: false, roughness: 1 });
  for (let k = 0; k < 10; k++) { const m = new THREE.Mesh(new THREE.IcosahedronGeometry(1.2, 1), sm.clone()); m.userData.k = k; g.add(m); smoke.push(m); }
  return { group: g, update(p, t) { drum.rotation.y = t * 1.5; smoke.forEach((m) => { const ph = (t * 0.22 + m.userData.k / 10) % 1; m.position.set(-8 + ph * 6, 20 + ph * 14, -12); m.scale.setScalar(1 + ph * 3); m.material.opacity = 0.5 * (1 - ph); }); } };
};

F.cones = (s) => {
  const g = new THREE.Group(); const n = s.count ?? 10, sp = s.spacing ?? 4;
  for (let i = 0; i < n; i++) { const c = mesh(new THREE.ConeGeometry(0.22, 0.75, 12), mat(0xff5a00)); c.position.set(i * sp, 0.37, 0); g.add(c); g.add(box(0.12, 0.02, 0.4, mat(0xffffff, { emissive: 0x666666 }), i * sp, 0.42, 0)); g.add(box(0.5, 0.06, 0.5, mat(0x222222), i * sp, 0.03, 0)); }
  return { group: g, update() {} };
};

// ---------------------------------------------------------------- worlds
const SKY = {
  day: { top: '#5f97d6', bottom: '#dfe9f1', sun: 3.2, hemi: 1.3, sunColor: 0xfff4e0, dir: [60, 90, 40], fog: 0xd9e4ee },
  golden: { top: '#3f5f9a', bottom: '#f6b46b', sun: 3.0, hemi: 0.9, sunColor: 0xffbb77, dir: [-90, 35, 50], fog: 0xe8b07a },
  dusk: { top: '#1d2552', bottom: '#d9776a', sun: 1.4, hemi: 0.6, sunColor: 0xff8a66, dir: [-100, 20, -40], fog: 0x8c6070 },
  night: { top: '#050914', bottom: '#1c2a44', sun: 0.6, hemi: 0.35, sunColor: 0x9fb8ff, dir: [40, 80, 60], fog: 0x1a2236 },
};
function skyTexture(sk) {
  const c = document.createElement('canvas'); c.width = 4; c.height = 256; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, sk.top); gr.addColorStop(1, sk.bottom); g.fillStyle = gr; g.fillRect(0, 0, 4, 256);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

function buildWorld(scene, sc, ctx) {
  const kind = sc.world || 'site';
  const groundColor = { site: C.soil, pit: 0x9c6b47, sea: C.soil, city: 0x8d8a83, cutaway: C.grass, plain: 0x8f8a80 }[kind] ?? C.soil;
  ctx.strata = strataTexture(sc.strata || (kind === 'pit' ? 'laterite' : 'soil'));
  if (kind === 'pit') {
    const P = sc.pit || {}; const N = P.benches ?? 6, bh = P.bench_h ?? 10, berm = P.berm ?? 8, face = P.face ?? 5, fr = P.floor_r ?? 40;
    const Rtop = fr + N * face + (N - 1) * berm; ctx.pit = { N, bh, berm, face, fr, Rtop };
    const pts = [new THREE.Vector2(0, -N * bh), new THREE.Vector2(fr, -N * bh)];
    for (let k = N - 1; k >= 0; k--) {
      const rIn = fr + (N - 1 - k) * (face + berm); pts.push(new THREE.Vector2(rIn + face, -k * bh));
      if (k > 0) pts.push(new THREE.Vector2(rIn + face + berm, -k * bh));
    }
    const geo = new THREE.LatheGeometry(pts, 72); strataUV(geo, -N * bh, 0);
    const pit = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: ctx.strata, roughness: 1, flatShading: true, side: THREE.DoubleSide }));
    pit.receiveShadow = true; pit.castShadow = true; scene.add(pit);
    // water pond at the bottom (optional)
    if (P.water) { const w = new THREE.Mesh(new THREE.CircleGeometry(fr * 0.6, 40), mat(0x3f7f86, { rough: 0.1, metal: 0.3 })); w.rotation.x = -Math.PI / 2; w.position.y = -N * bh + 0.2; scene.add(w); }
    const ring = mesh(new THREE.RingGeometry(Rtop, 900, 72, 1), mat(groundColor, { rough: 1 })); ring.rotation.x = -Math.PI / 2; scene.add(ring);
  } else if (kind === 'cutaway') {
    // a slab of ground cut open at z=0; the half-tunnel notch runs along x at depth tunnel_y
    const D = sc.depth ?? 40, Lx = sc.length ?? 140, Lz = sc.width ?? 80; const ty = sc.tunnel_y ?? null, tr = (sc.tunnel_r ?? 3.3) + 0.02;
    ctx.tunnelLen = Lx / 2;
    const sh = new THREE.Shape(); // in (z, y) plane, extruded along x
    sh.moveTo(0, -D); sh.lineTo(-Lz, -D); sh.lineTo(-Lz, 0); sh.lineTo(0, 0);
    if (ty !== null) { sh.lineTo(0, ty + tr); sh.absarc(0, ty, tr, Math.PI / 2, (3 * Math.PI) / 2, false); }
    sh.lineTo(0, -D);
    const geo = new THREE.ExtrudeGeometry(sh, { depth: Lx, bevelEnabled: false, curveSegments: 40 });
    // shape coords (sx, sy) -> world (z = sx, y = sy), extrude dir -> world x
    geo.applyMatrix4(new THREE.Matrix4().set(0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1)); geo.translate(-Lx / 2, 0, 0);
    strataUV(geo, -D, 0.01); const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: ctx.strata, roughness: 1, side: THREE.DoubleSide }));
    m.receiveShadow = true; m.castShadow = true; scene.add(m);
    const top = mesh(new THREE.PlaneGeometry(Lx, Lz), mat(sc.surface ?? C.grass, { rough: 1 })); top.rotation.x = -Math.PI / 2; top.position.set(0, 0.02, -Lz / 2); scene.add(top);
    const fl = mesh(new THREE.PlaneGeometry(1200, 1200), mat(0x6c7d52, { rough: 1 })); fl.rotation.x = -Math.PI / 2; fl.position.y = -D - 0.1; scene.add(fl);
  } else if (kind === 'sea') {
    const sea = new THREE.Mesh(new THREE.PlaneGeometry(2000, 2000, 1, 1), mat(C.water, { rough: 0.12, metal: 0.25 })); sea.rotation.x = -Math.PI / 2; sea.receiveShadow = true; scene.add(sea);
    ctx.sea = sea;
  } else {
    const gr = mesh(new THREE.PlaneGeometry(2000, 2000), mat(groundColor, { rough: 1 })); gr.rotation.x = -Math.PI / 2; scene.add(gr);
    if (kind === 'site') { const r = rng(4); for (let i = 0; i < 40; i++) { const p = mesh(new THREE.CircleGeometry(3 + r() * 8, 10), mat(r() > 0.5 ? C.gravel : 0x8a5d3b, { rough: 1 })); p.rotation.x = -Math.PI / 2; p.position.set((r() - 0.5) * 160, 0.01 + i * 0.001, (r() - 0.5) * 160); p.receiveShadow = true; scene.add(p); } }
  }
}

function resolvePos(pos, ctx) {
  if (typeof pos === 'string' && pos.startsWith('pit:') && ctx.pit) {
    const [, b, a] = pos.split(':'); const P = ctx.pit; const ang = (+a || 0) * DEG; let k = b === 'floor' ? P.N : +b, r, y;
    if (k >= P.N) { r = P.fr * 0.45; y = -P.N * P.bh; } else if (k <= 0) { r = P.Rtop + 15; y = 0; }
    else { r = P.fr + (P.N - 1 - k) * (P.face + P.berm) + P.face + P.berm / 2; y = -k * P.bh; }
    return [Math.cos(ang) * r, y, -Math.sin(ang) * r];
  }
  return pos || [0, 0, 0];
}

// ---------------------------------------------------------------- scene setup + render
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
document.body.appendChild(renderer.domElement);
const camera = new THREE.PerspectiveCamera(50, W / H, 0.5, 3000);
let current = null;

function disposeScene(sc) { sc.traverse((o) => { if (o.geometry) o.geometry.dispose(); }); }

window.setupScene = (sc, duration) => {
  if (current) disposeScene(current.scene);
  matCache.clear(); _dur = duration;
  const scene = new THREE.Scene(); const sk = SKY[sc.time || 'day'] || SKY.day;
  const ctx = { world: sc.world || 'site', night: sc.time === 'night', dur: duration };
  scene.background = skyTexture(sk);
  scene.fog = new THREE.Fog(sk.fog, sc.fog_near ?? 250, sc.fog_far ?? 1400);
  scene.add(new THREE.HemisphereLight(0xdfeaff, 0x6b5a48, sk.hemi));
  const sun = new THREE.DirectionalLight(sk.sunColor, sk.sun); sun.castShadow = true;
  const ss = sc.shadow_size ?? 90; Object.assign(sun.shadow.camera, { left: -ss, right: ss, top: ss, bottom: -ss, near: 1, far: 800 });
  sun.shadow.mapSize.set(4096, 4096); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.6; scene.add(sun, sun.target);
  buildWorld(scene, sc, ctx);
  const objs = []; const byId = {};
  for (const spec of sc.objects || []) {
    const f = F[spec.type]; if (!f) { console.warn('unknown object', spec.type); continue; }
    spec.pos = resolvePos(spec.pos, ctx); if (spec.to) spec.to = resolvePos(spec.to, ctx);
    const o = f(spec, ctx); o.spec = spec;
    o.group.position.set(...spec.pos); if (spec.rot !== undefined && !spec.to) o.group.rotation.y = spec.rot * DEG;
    if (spec.scale) o.group.scale.setScalar(spec.scale);
    scene.add(o.group); objs.push(o); if (spec.id) byId[spec.id] = o;
  }
  if (ctx.night) { const l = new THREE.PointLight(0xffe2b0, 3000, 200, 1.6); l.position.set(20, 30, 30); scene.add(l); }
  current = { scene, sc, objs, byId, sun, ss, sky: sk };
  window.frame(0);
  return true;
};

function cameraAt(cam, p) {
  const c = current.sc.camera || {}; const e = easeIO(p);
  const T = new V3(...(c.target || [0, 5, 0]));
  if (c.follow && current.byId[c.follow]) T.add(current.byId[c.follow].group.position);
  if (c.target_to) T.lerp(new V3(...c.target_to), e);
  let D = c.dist ?? 60, Hh = c.height ?? 20, A = c.angle ?? 35;
  const mv = c.move || 'orbit';
  const sweep = c.sweep ?? (mv === 'orbit' ? 25 : 8);
  A += sweep * (e - 0.5);
  if (mv === 'push') D *= 1.15 - 0.4 * e;
  if (mv === 'pull') D *= 0.75 + 0.4 * e;
  if (mv === 'rise') Hh = lerp(c.height_from ?? Hh * 0.1, Hh, e);
  if (mv === 'drop') Hh = lerp(Hh, c.height_to ?? Hh * 0.15, e);
  if (mv === 'flyby') T.x += (e - 0.5) * D * 0.5;
  if (c.dist_to) D = lerp(c.dist ?? 60, c.dist_to, e);
  const shake = c.shake ? c.shake * Math.max(0, 1 - Math.abs(p - (c.shake_at ?? 0.35)) * 4) : 0;
  cam.position.set(T.x + Math.sin(A * DEG) * D, T.y + Hh, T.z + Math.cos(A * DEG) * D);
  cam.lookAt(T);
  if (shake) { cam.position.x += Math.sin(p * 300) * shake; cam.position.y += Math.cos(p * 270) * shake; }
  cam.fov = c.fov ?? 50; cam.updateProjectionMatrix();
  return T;
}

window.frame = (t) => {
  const d = Math.max(_dur, 0.01); const p = clamp(t / d);
  for (const o of current.objs) {
    const s = o.spec; let [a, b] = Array.isArray(s.progress) ? s.progress : [s.progress ?? 0, s.progress ?? 1];
    if (typeof s.progress === 'number') { a = b = s.progress; }
    const st = s.start ?? 0, en = s.end ?? 1; const local = clamp((p - st) / Math.max(en - st, 1e-3));
    o.update(lerp(a, b, local), t + (s.t_offset ?? 0));
  }
  const T = cameraAt(camera, p);
  // keep the shadow camera centred on what we look at
  const sk = current.sky; const dir = new V3(...sk.dir).normalize();
  current.sun.position.copy(T).addScaledVector(dir, 300); current.sun.target.position.copy(T);
  renderer.render(current.scene, camera);
  return true;
};
window.kitReady = true;
