const O = "#FF6A00", OT = "#FFF1E7", K = "#111111", G = "#6B6B6B", W = "#FFFFFF";
const SW = 1080, SH = 1920;
const LOGO = process.env.LOGO || "";
const smooth = [0.22, 1, 0.36, 1];
const soft = { kind: "spring", stiffness: 140, damping: 20 };

const Head = ({ t, y, size = 100, color = K, at = 0 }) => (
  <text x={20} y={y} width={SW - 40} align="center" fontFamily="Inter" fontWeight={900} fontSize={size}
    letterSpacing={-2} lineHeight={1.0} color={color}
    motion={{ by: "word", from: { opacity: 0, y: 50 }, at, duration: 0.5, overlap: 0.6, easing: "house" }}>{t}</text>
);

const cats = [
  { s: "Electronics", i: "smartphone" },
  { s: "Beauty", i: "sparkles" },
  { s: "Home", i: "house" },
  { s: "Fashion", i: "shirt" },
  { s: "Health & Wellness", i: "heart-pulse" },
];

export default async ({ project, icon }) => {
  const p = await project({ size: `${SW}x${SH}`, fps: 30, background: W });
  const logo = LOGO ? await p.add(LOGO) : null;

  // ---------- persistent background ----------
  p.compose(
    <frame width={SW} height={SH} layout="none">
      <rect x={0} y={0} width={SW} height={SH} fill={W} />
      <rect x={520} y={-380} width={1000} height={1000} radius={500}
        fill={{ kind: "radial", stops: [{ offset: 0, color: O, opacity: 0.14 }, { offset: 1, color: O, opacity: 0 }] }}
        animate={[{ property: "offsetX", keyframes: [{ at: 0, value: 0 }, { at: 7.5, value: -120, easing: "ease-in-out" }, { at: 14.9, value: 0 }] },
                  { property: "offsetY", keyframes: [{ at: 0, value: 0 }, { at: 7.5, value: 160, easing: "ease-in-out" }, { at: 14.9, value: 0 }] }]} />
      <rect x={-500} y={1250} width={1000} height={1000} radius={500}
        fill={{ kind: "radial", stops: [{ offset: 0, color: O, opacity: 0.10 }, { offset: 1, color: O, opacity: 0 }] }}
        animate={[{ property: "offsetX", keyframes: [{ at: 0, value: 0 }, { at: 7.5, value: 140, easing: "ease-in-out" }, { at: 14.9, value: 0 }] }]} />
    </frame>,
    { at: 0, dur: 15, name: "Background" }
  );

  // ---------- 1. HOOK 0.0 - 3.0 ----------
  p.compose(
    <frame width={SW} height={SH} layout="none"
      motion={{ exit: { to: { y: -80, opacity: 0 }, duration: 0.4, easing: "ease-in" } }}>
      <frame x={SW / 2 - 270} y={580} width={540} height={76} layout="none" origin="center"
        motion={{ enter: { from: { y: 20, opacity: 0 }, duration: 0.5, easing: smooth } }}>
        <rect x={0} y={0} width={540} height={76} radius={38} fill={OT} strokeColor={O} strokeWidth={2} />
        {icon("store", { x: 34, y: 20, size: 36, color: O, strokeWidth: 2.4 })}
        <text x={84} y={23} width={440} fontFamily="Inter" fontWeight={700} fontSize={27} letterSpacing={3} color={O}>WALMART MARKETPLACE</text>
      </frame>
      <Head t="WALMART ISN'T" y={730} at={0.2} />
      <Head t="JUST ABOUT" y={850} at={0.5} />
      <Head t="GROCERIES" y={970} color={O} size={128} at={0.85} />
      <frame x={250} y={1130} width={580} height={14} layout="none" clip={true}
        reveal={{ from: "left", at: 1.35, duration: 0.6, easing: smooth }}>
        <rect x={0} y={0} width={580} height={14} radius={7} fill={O} />
      </frame>
    </frame>,
    { at: 0, dur: 3.0, name: "Hook" }
  );

  // ---------- 2+3. CATEGORY CARDS -> HUB 3.0 - 11.6 ----------
  const D = 8.6, MOVE = 3.5;            // local time cards glide into the hub
  const cw = 440, ch = 150;
  const grid = [
    { x: 90, y: 700, w: cw }, { x: 550, y: 700, w: cw },
    { x: 90, y: 880, w: cw }, { x: 550, y: 880, w: cw },
    { x: 90, y: 1060, w: 900 },
  ];
  const cx = 540, cy = 900;
  const hubC = [ [300, 560], [780, 560], [215, 900], [865, 900], [540, 1235] ];
  const S = 0.72;
  const cards = cats.map((c, j) => {
    const g = grid[j];
    const gx = g.x + g.w / 2, gy = g.y + ch / 2;
    const [hx, hy] = hubC[j];
    return (
      <frame x={g.x} y={g.y} width={g.w} height={ch} layout="none" origin="center"
        motion={{
          enter: { from: { y: 70, opacity: 0, scale: 0.96 }, duration: 0.55, at: 0.15 + j * 0.42, easing: smooth },
          settle: { to: { x: hx - gx, y: hy - gy, scale: S }, at: MOVE + j * 0.05 - (0.7 + j * 0.42), duration: 0.9, easing: smooth },
        }}>
        <rect x={0} y={0} width={g.w} height={ch} radius={34} fill={W} strokeColor="#EFEFEF" strokeWidth={2}
          shadow={{ x: 0, y: 18, blur: 44, color: "#1111111A" }} />
        <rect x={28} y={30} width={90} height={90} radius={24} fill={OT} />
        {icon(c.i, { x: 46, y: 48, size: 54, color: O, strokeWidth: 2.2 })}
        <text x={146} y={52} width={g.w - 170} fontFamily="Inter" fontWeight={700} fontSize={44} color={K}>{c.s}</text>
      </frame>
    );
  });
  const T0 = MOVE + 0.2;
  p.compose(
    <frame width={SW} height={SH} layout="none"
      motion={{ exit: { to: { y: -80, opacity: 0 }, duration: 0.4, easing: "ease-in" } }}>
      {/* hub ring + connectors (appear as cards glide) */}
      <frame x={cx - 330} y={cy - 330} width={660} height={660} layout="none" origin="center" at={T0}
        motion={{ enter: { from: { scale: 0.7, opacity: 0 }, duration: 0.8, easing: smooth } }}>
        <rect x={0} y={0} width={660} height={660} radius={330} fill={{ kind: "radial", stops: [{ offset: 0, color: O, opacity: 0.10 }, { offset: 1, color: O, opacity: 0 }] }}
          strokeColor="#FFD2B3" strokeWidth={3} />
      </frame>
      {hubC.map(([hx, hy], j) => (
        <path d={`M ${cx} ${cy} L ${hx} ${hy}`} width={SW} height={SH} x={0} y={0} at={T0 + 0.5}
          stroke={{ width: 3, color: O, cap: "round" }} dash={[2, 12]}
          animate={[{ property: "opacity", from: 0, to: 0.7, at: j * 0.08, duration: 0.4 }]} />
      ))}
      <frame x={cx - 140} y={cy - 140} width={280} height={280} layout="none" origin="center" at={T0 + 0.1}
        motion={{ enter: { from: { scale: 0 }, duration: 0.7, easing: soft } }}>
        <rect x={0} y={0} width={280} height={280} radius={140} fill={W} strokeColor={O} strokeWidth={6}
          shadow={{ x: 0, y: 20, blur: 50, color: "#FF6A0040" }} />
        {logo
          ? <media file={logo} x={40} y={40} width={200} height={200} fit="contain" />
          : icon("shopping-cart", { x: 75, y: 75, size: 130, color: O, strokeWidth: 2 })}
      </frame>
      {cards}
      <text x={110} y={1380} width={860} align="center" fontFamily="Inter" fontWeight={700} fontSize={48} lineHeight={1.3} color={K}
        motion={{ by: "word", from: { opacity: 0, y: 24 }, at: T0 + 1.0, duration: 0.35, overlap: 0.75, easing: "house" }}>
        Thousands of businesses sell across categories through
      </text>
      <text x={0} y={1540} width={SW} align="center" fontFamily="Inter" fontWeight={900} fontSize={68} letterSpacing={-1} color={O}
        motion={{ by: "word", from: { opacity: 0, y: 36 }, at: T0 + 2.0, duration: 0.5, overlap: 0.5, easing: "house" }}>
        WALMART MARKETPLACE
      </text>
    </frame>,
    { at: 3.0, dur: D, name: "Categories" }
  );

  // ---------- 4. CTA 11.6 - 15.0 ----------
  const bx = SW / 2 - 330, by = 1220;
  p.compose(
    <frame width={SW} height={SH} layout="none">
      <Head t="SEE WHERE" y={660} at={0.1} />
      <Head t="YOUR PRODUCT" y={780} at={0.35} />
      <Head t="COULD FIT" y={900} color={O} size={128} at={0.65} />
      <frame x={bx} y={by} width={660} height={130} layout="none" origin="center"
        motion={{ enter: { from: { y: 40, opacity: 0 }, duration: 0.6, at: 1.2, easing: smooth },
                  timeline: { sequence: [
                    { to: { scale: 0.95 }, duration: 0.12, at: 2.9, easing: "ease-out" },
                    { to: { scale: 1 }, duration: 0.3, easing: smooth } ] } }}>
        <rect x={0} y={0} width={660} height={130} radius={65} fill={O} shadow={{ x: 0, y: 18, blur: 40, color: "#FF6A0055" }} />
        <text x={60} y={42} width={480} fontFamily="Inter" fontWeight={700} fontSize={44} color={W}>www.eskillvisor.com</text>
        {icon("arrow-right", { x: 560, y: 41, size: 48, color: W, strokeWidth: 2.6 })}
      </frame>
      <frame x={760} y={1560} width={72} height={72} layout="none"
        motion={{ enter: { from: { opacity: 0, x: 120, y: 140 }, duration: 0.8, at: 1.5, easing: smooth },
                  settle: { to: { x: -110, y: -230 }, duration: 0.6, at: 0, easing: smooth } }}>
        {icon("mouse-pointer-2", { x: 0, y: 0, size: 72, color: K, strokeWidth: 2 })}
      </frame>
    </frame>,
    { at: 11.6, dur: 3.4, name: "CTA" }
  );

  const t = (process.env.FRAMES || "").split(",").filter(Boolean).map(Number);
  for (const s of t) await p.frame(s, `renders/f_${s}.png`);
  if (process.env.RENDER) await p.render("renders/wm.mp4");
};
