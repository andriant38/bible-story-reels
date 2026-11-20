// Render the 3D background of every scene to its own MP4 (no text, no audio).
// Usage:
//   node render3d.cjs <story.json> --durs 4.1,6.3,... --out-dir <dir>      -> <dir>/bg01.mp4, bg02.mp4, ...
//   node render3d.cjs <story.json> --stills <dir> [--at 0.2,0.8]           -> <dir>/s01_a.jpg ... (quick visual check)
//   add --scenes 3,5 to render only some scenes (1-based)
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const args = process.argv.slice(2); const story = JSON.parse(fs.readFileSync(args[0], 'utf8'));
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const FPS = +opt('--fps', 30);
const durs = (opt('--durs', '') || '').split(',').filter(Boolean).map(Number);
const outDir = opt('--out-dir'), stillDir = opt('--stills');
const at = opt('--at', '0.15,0.85').split(',').map(Number);
const only = opt('--scenes', '') ? opt('--scenes').split(',').map((x) => +x - 1) : null;
const TYPES = { '.js': 'text/javascript', '.html': 'text/html', '.otf': 'font/otf', '.json': 'application/json' };

(async () => {
  const srv = http.createServer((q, r) => {
    const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
    if (!p.startsWith(ROOT)) { r.writeHead(403); return r.end(); }
    fs.readFile(p, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' }); r.end(d); });
  }).listen(0);
  const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.error('[page]', m.text()); });
  page.on('pageerror', (e) => { console.error('[page error]', e.message); process.exitCode = 1; });
  await page.goto(`http://localhost:${port}/konstruksi/engine/scene.html`);
  await page.waitForFunction('window.kitReady === true', null, { timeout: 60000 });
  const canvas = page.locator('canvas');
  const shot = () => canvas.screenshot({ type: 'jpeg', quality: 93 });

  for (let i = 0; i < story.scenes.length; i++) {
    if (only && !only.includes(i)) continue;
    const sc = story.scenes[i]; const tag = String(i + 1).padStart(2, '0');
    const dur = durs[i] || sc.dur || 5;
    await page.evaluate(([s, d]) => window.setupScene(s, d), [sc, dur]);
    if (stillDir) {
      fs.mkdirSync(stillDir, { recursive: true });
      for (let k = 0; k < at.length; k++) { await page.evaluate((t) => window.frame(t), at[k] * dur); fs.writeFileSync(path.join(stillDir, `s${tag}_${'abcdefgh'[k]}.jpg`), await shot()); }
      console.log(`scene ${i + 1}: stills`); continue;
    }
    fs.mkdirSync(outDir, { recursive: true });
    const out = path.join(outDir, `bg${tag}.mp4`);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(FPS), out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const n = Math.ceil(dur * FPS); const t0 = Date.now();
    for (let f = 0; f < n; f++) {
      await page.evaluate((t) => window.frame(t), f / FPS);
      const buf = await shot();
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    }
    ff.stdin.end(); await new Promise((r) => ff.on('close', r));
    console.log(`scene ${i + 1}/${story.scenes.length}: ${n} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  await browser.close(); srv.close();
})().catch((e) => { console.error(e); process.exit(1); });
