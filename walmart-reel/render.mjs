// Renders reel.html frame-by-frame with Playwright and pipes PNGs into ffmpeg.
// Usage: node render.mjs [out.mp4] [--preview t1,t2,...]
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import path from 'path';
const args = process.argv.slice(2);
const out = args.find(a => a.endsWith('.mp4')) || 'walmart-reel.mp4';
const pv = args.indexOf('--preview');
const FPS = 30;
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto('file://' + path.resolve('reel.html'));
await page.evaluate(() => document.fonts.ready);
if (pv >= 0) {
  for (const t of args[pv + 1].split(',')) {
    await page.evaluate(t => render(t), +t);
    await page.screenshot({ path: `preview_${t}.png` });
  }
} else {
  const dur = await page.evaluate(() => DURATION);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round(dur * FPS);
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => render(t), i / FPS);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
}
await browser.close();
