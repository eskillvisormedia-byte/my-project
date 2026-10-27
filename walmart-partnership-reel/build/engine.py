# Whiteboard / marker-on-paper animation engine (skia). Elements are drawn progressively
# while a hand holding a marker follows the pen tip.
import math, os
import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', 'fonts')
W, H, FPS = 1080, 1920, 30

INK = 0xFF222222
BLUE = 0xFF0071CE
YELLOW = 0xFFFFC220
GREY = 0xFF6B6B6B

TF_CAPS = skia.Typeface.MakeFromFile(os.path.join(FONTS, 'patrick-hand-sc.ttf'))
TF_HAND = skia.Typeface.MakeFromFile(os.path.join(FONTS, 'patrick-hand.ttf'))

REST = (1250.0, 2250.0)        # hand parked off-screen, bottom right
TEXT_SPEED = 7.5               # px/s per px of font size
LINE_SPEED = 750.0            # px/s along strokes
TRAVEL_SPEED = 1800.0          # px/s pen-up glide
ENTER, EXIT, FADE, HOLD = 0.6, 0.8, 0.35, 0.35
MAX_SLOW = 1.3
HAND_SCALE = 1.3
CHARS_PER_S = 13.0


def ease(p):
    p = min(max(p, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * p)


def soft(p):
    # mostly linear, eased at the ends: smooth but never stalls
    # eased in and out so the pen never jerks when it starts or stops
    p = min(max(p, 0.0), 1.0)
    return ease(p)


def glide(a, b, p):
    e = ease(p)
    return (a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e)


def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


class _Contour:
    def __init__(self, path):
        self.pm = skia.PathMeasure(path, False, 1.0)
        self.L = self.pm.getLength()

    def length(self):
        return self.L

    def getPosTan(self, d):
        pos, tan = self.pm.getPosTan(min(max(d, 0), self.L))
        return (pos.x(), pos.y()), tan

    def getSegment(self, a, b, dst, move):
        return self.pm.getSegment(a, b, dst, move)


def contours(path):
    pm = skia.PathMeasure(path, False, 1.0)
    out = []
    while True:
        L = pm.getLength()
        if L > 0:
            sub = skia.Path()
            pm.getSegment(0, L, sub, True)
            out.append(_Contour(sub))
        if not pm.nextContour():
            break
    return out


# ---------------------------------------------------------------- elements
class Text:
    def __init__(self, s, x, y, size=72, color=INK, align='center', caps=True, maxw=960):
        self.s, self.color = s, color
        tf = TF_CAPS if caps else TF_HAND
        self.font = skia.Font(tf, size)
        w = self.font.measureText(s)
        while w > maxw:
            size *= 0.96
            self.font = skia.Font(tf, size)
            w = self.font.measureText(s)
        self.size = size
        self.w = w
        self.x0 = x - w / 2 if align == 'center' else (x - w if align == 'right' else x)
        self.y = y
        self.dur = max(0.45, (len(s.replace(' ', '')) + 0.5 * s.count(' ')) / CHARS_PER_S)

    @property
    def start(self):
        return (self.x0, self.y - self.size * 0.3)

    @property
    def end(self):
        return (self.x0 + self.w, self.y - self.size * 0.3)

    def pen(self, p):
        q = soft(p)
        x = self.x0 + self.w * q
        # a straight, steady line along the text (no per-letter wobble)
        y = self.y - self.size * 0.32
        return (x, y)

    def draw(self, c, p, alpha=1.0):
        if p <= 0:
            return
        c.save()
        if p < 1:
            x = self.pen(p)[0]
            c.clipRect(skia.Rect(-10, -H, x, 2 * H))
        pt = skia.Paint(AntiAlias=True, Color=self.color)
        pt.setAlphaf(pt.getAlphaf() * alpha)
        c.drawString(self.s, self.x0, self.y, self.font, pt)
        c.restore()


class Stroke:
    """A path drawn by following its contours; pen-up travel between contours is part of the timeline."""

    def __init__(self, path, color=INK, width=6.0, cap='round', alpha=1.0, speed=LINE_SPEED, fill=None):
        self.path, self.color, self.width, self.alpha, self.fill = path, color, width, alpha, fill
        self.cap = skia.Paint.kRound_Cap if cap == 'round' else skia.Paint.kButt_Cap
        self.segs = []  # (kind, data, time)
        prev = None
        for cm in contours(path):
            L = cm.length()
            p0 = tuple(cm.getPosTan(0)[0])
            if prev is not None and dist(prev, p0) > 1:
                self.segs.append(('move', (prev, p0), max(0.08, dist(prev, p0) / TRAVEL_SPEED)))
            self.segs.append(('draw', cm, max(0.18, L / speed)))
            prev = tuple(cm.getPosTan(L)[0])
        self.dur = sum(s[2] for s in self.segs)
        first = self.segs[0][1]
        self.start = tuple(first.getPosTan(0)[0])
        self.end = prev

    def _locate(self, p):
        t = p * self.dur
        for i, s in enumerate(self.segs):
            if t <= s[2] or i == len(self.segs) - 1:
                return i, min(1.0, t / s[2])
            t -= s[2]

    def pen(self, p):
        i, q = self._locate(min(max(p, 0), 1))
        kind, d, _ = self.segs[i]
        if kind == 'move':
            return glide(d[0], d[1], q)
        return tuple(d.getPosTan(d.length() * soft(q))[0])

    def paint(self, alpha):
        pt = skia.Paint(AntiAlias=True, Color=self.color, Style=skia.Paint.kStroke_Style,
                        StrokeWidth=self.width, StrokeCap=self.cap, StrokeJoin=skia.Paint.kRound_Join)
        pt.setAlphaf(pt.getAlphaf() * self.alpha * alpha)
        return pt

    def draw(self, c, p, alpha=1.0):
        if p <= 0:
            return
        pt = self.paint(alpha)
        if p >= 1:
            if self.fill is not None:
                fp = skia.Paint(AntiAlias=True, Color=self.fill)
                fp.setAlphaf(fp.getAlphaf() * alpha)
                c.drawPath(self.path, fp)
            c.drawPath(self.path, pt)
            return
        i, q = self._locate(p)
        out = skia.Path()
        for j in range(i + 1):
            kind, d, _ = self.segs[j]
            if kind != 'draw':
                continue
            frac = 1.0 if j < i else soft(q)
            seg = skia.Path()   # getSegment overwrites its target, so collect each piece separately
            d.getSegment(0, d.length() * frac, seg, True)
            out.addPath(seg)
        c.drawPath(out, pt)


class Pause:
    """Hand rests (stays where it is) for a moment."""

    def __init__(self, dur):
        self.dur = dur


# ---------------------------------------------------------------- scenes
class Scene:
    """Items are drawn one after another inside [t0, t1]. The hand glides in from where the previous
    scene left it, and after the last item it eases back a little to rest while the page holds."""

    def __init__(self, t0, t1, items, gap=0.15, fade=True, final=False):
        self.t0, self.t1, self.fade, self.final = t0, t1, fade, final
        self.came_from = REST
        self.gap = gap
        self.src = items
        self.items, end, k = self._schedule(t1 - (FADE if fade else 0) - (EXIT if final else 0) - HOLD)
        self.k = k
        # centre the scene's content vertically (a little above middle, clear of the reel UI)
        top, bot = 1e9, -1e9
        for el, _, _ in self.items:
            if isinstance(el, Text):
                a, b = el.y - el.size * 0.75, el.y + el.size * 0.2
            else:
                r = el.path.computeTightBounds(); a, b = r.top(), r.bottom()
            top, bot = min(top, a), max(bot, b)
        self.dy = max(220 - top, 900 - (top + bot) / 2)
        self.draw_end = end
        last = self.items[-1][0].end
        self.park = REST if final else (last[0] + 330, last[1] + self.dy + 520)

    def _schedule(self, scene_end):
        """Lay items out in time. An item with an `at` time (seconds in the video, matched to the
        voiceover) starts exactly then; the items between two such cues are drawn at a pace that fills
        the gap (never slower than MAX_SLOW x natural, and as fast as needed to keep in sync)."""
        groups, cur = [], []
        for it in self.src:
            if getattr(it, 'at', None) is not None and cur:
                groups.append(cur)
                cur = []
            cur.append(it)
        groups.append(cur)
        rows, prev_end, t = [], None, self.t0 + ENTER
        ks = []
        for gi, g in enumerate(groups):
            start = max(t, getattr(g[0], 'at', None) or t)
            nxt = groups[gi + 1][0].at if gi + 1 < len(groups) else scene_end
            # natural layout of the group
            lay, tt, pe = [], 0.0, prev_end
            for it in g:
                if isinstance(it, Pause):
                    tt += it.dur
                    continue
                if pe is not None and lay:
                    tt += max(self.gap, dist(pe, it.start) / TRAVEL_SPEED)
                lay.append([it, tt, it.dur])
                tt += it.dur
                pe = it.end
            # leave the pen enough time to glide calmly to the next cued item
            reserve = 0.0
            if gi + 1 < len(groups):
                reserve = max(0.3, dist(pe, groups[gi + 1][0].start) / (TRAVEL_SPEED * 0.6))
            k = min(MAX_SLOW, max(0.3, (nxt - start - reserve) / max(tt, 1e-3)))
            ks.append(k)
            for it, s0, d in lay:
                rows.append([it, start + s0 * k, d * k])
            t = start + tt * k
            prev_end = pe
        return rows, t, min(ks)

    def pen_at(self, t):
        dy = self.dy
        sh = lambda p: (p[0], p[1] + dy)
        first = self.items[0]
        if t < first[1]:
            return glide(self.came_from, sh(first[0].start), (t - self.t0) / (first[1] - self.t0))
        for i, (el, s, d) in enumerate(self.items):
            if s <= t <= s + d:
                return sh(el.pen((t - s) / d))
            nxt = self.items[i + 1] if i + 1 < len(self.items) else None
            if nxt and s + d < t < nxt[1]:
                return sh(glide(el.end, nxt[0].start, (t - s - d) / (nxt[1] - s - d)))
        return glide(sh(self.items[-1][0].end), self.park, (t - self.draw_end) / (EXIT if self.final else 0.8))

    def draw(self, c, t):
        alpha = 1.0
        if self.fade and t > self.t1 - FADE:
            alpha = max(0.0, (self.t1 - t) / FADE)
        c.save()
        c.translate(0, self.dy)
        for el, s, d in sorted(self.items, key=lambda r: getattr(r[0], 'z', 0)):
            el.draw(c, (t - s) / d, alpha)
        c.restore()


def chain(scenes):
    for a, b in zip(scenes, scenes[1:]):
        b.came_from = a.park
    return scenes


# ---------------------------------------------------------------- paper + hand
def make_paper():
    rng = np.random.default_rng(7)
    base = np.array([241, 240, 236], np.float32)
    img = np.ones((H, W, 3), np.float32) * base
    n = rng.normal(0, 3.2, (H, W, 1)).astype(np.float32)
    # low-frequency mottling
    lo = rng.normal(0, 1, (H // 40 + 2, W // 40 + 2)).astype(np.float32)
    lo = np.kron(lo, np.ones((40, 40), np.float32))[:H, :W]
    from PIL import Image, ImageFilter
    lo = np.asarray(Image.fromarray(((lo + 4) * 30).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(30)), np.float32) / 30 - 4
    img += n + lo[..., None] * 2.0
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2
    img *= (1 - 0.10 * v)[..., None]
    rgba = np.dstack([img.clip(0, 255).astype(np.uint8), np.full((H, W), 255, np.uint8)])
    return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)


class Hand:
    def __init__(self):
        import hand
        self.img, self.shadow = hand.build()
        self.pad = hand.PAD
        self.samp = skia.SamplingOptions(skia.FilterMode.kLinear)

    def draw(self, c, pos):
        if pos is None:
            return
        x, y = pos
        # the wrist turns a touch as the pen travels across the page
        rot = -5.0 * (x - 540) / 540 + 2.0 * (y - 960) / 960
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.scale(HAND_SCALE, HAND_SCALE)
        c.drawImage(self.shadow, -self.pad + 16, -self.pad + 24, self.samp)
        c.drawImage(self.img, -self.pad, -self.pad, self.samp)
        c.restore()
