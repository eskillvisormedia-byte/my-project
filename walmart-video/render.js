// Usage: node render.js <out.mp4|stills-dir> [--stills t1,t2,...]
const { chromium } = require("/opt/node22/lib/node_modules/playwright");
const { spawn } = require("child_process");
const path = require("path"), fs = require("fs");
const FPS = 60;
(async () => {
  const out = process.argv[2];
  const stillsArg = process.argv.indexOf("--stills");
  const browser = await chromium.launch({ args: ["--allow-file-access-from-files"] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto("file://" + path.join(__dirname, "scene.html"));
  await page.evaluate(() => window.ready);
  const grab = async t => Buffer.from(await page.evaluate(t => { render(t); return document.getElementById("c").toDataURL("image/png").split(",")[1]; }, t), "base64");
  if (stillsArg > 0) {
    fs.mkdirSync(out, { recursive: true });
    for (const t of process.argv[stillsArg + 1].split(",").map(Number)) fs.writeFileSync(path.join(out, `t${t.toFixed(2)}.png`), await grab(t));
  } else {
    const dur = await page.evaluate(() => T.end);
    const ff = spawn("ffmpeg", ["-y", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", out], { stdio: ["pipe", "inherit", "inherit"] });
    const n = Math.round(dur * FPS);
    for (let i = 0; i < n; i++) { const b = await grab(i / FPS); if (!ff.stdin.write(b)) await new Promise(r => ff.stdin.once("drain", r)); }
    ff.stdin.end(); await new Promise(r => ff.on("close", r));
  }
  await browser.close();
})();
