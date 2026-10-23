# Simple, minimal line icons as skia paths. Each takes a center (cx, cy) and a scale s (≈ half-size in px).
import math
import skia


def P():
    return skia.Path()


def rrect(p, x0, y0, x1, y1, r):
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r))
    return p


def circle(p, cx, cy, r, start=-90):
    p.addArc(skia.Rect(cx - r, cy - r, cx + r, cy + r), start, 359.9)
    return p


def line(p, *pts):
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    return p


def road(cx, cy, s):
    # winding path from bottom-left up to a flag
    p = P()
    p.moveTo(cx - 0.9 * s, cy + 0.95 * s)
    p.cubicTo(cx + 0.6 * s, cy + 0.85 * s, cx + 0.7 * s, cy + 0.35 * s, cx, cy + 0.2 * s)
    p.cubicTo(cx - 0.8 * s, cy + 0.05 * s, cx - 0.7 * s, cy - 0.5 * s, cx + 0.45 * s, cy - 0.55 * s)
    return p


def flag(cx, cy, s):
    p = P()
    line(p, (cx, cy), (cx, cy - s))
    p.moveTo(cx, cy - s)
    p.lineTo(cx + 0.7 * s, cy - 0.82 * s)
    p.lineTo(cx, cy - 0.62 * s)
    return p


def person(p, cx, cy, s):
    circle(p, cx, cy - 0.45 * s, 0.28 * s)
    p.moveTo(cx - 0.55 * s, cy + 0.6 * s)
    p.cubicTo(cx - 0.55 * s, cy - 0.05 * s, cx + 0.55 * s, cy - 0.05 * s, cx + 0.55 * s, cy + 0.6 * s)
    return p


def people(cx, cy, s, n=3):
    p = P()
    if n == 2:
        person(p, cx - 0.45 * s, cy, 0.8 * s)
        person(p, cx + 0.45 * s, cy, 0.8 * s)
    else:
        person(p, cx - 0.8 * s, cy + 0.05 * s, 0.65 * s)
        person(p, cx, cy - 0.05 * s, 0.8 * s)
        person(p, cx + 0.8 * s, cy + 0.05 * s, 0.65 * s)
    return p


def laptop(cx, cy, s):
    p = P()
    rrect(p, cx - s, cy - 0.7 * s, cx + s, cy + 0.45 * s, 0.06 * s)
    line(p, (cx - 1.25 * s, cy + 0.55 * s), (cx + 1.25 * s, cy + 0.55 * s))
    return p


def store(cx, cy, s):
    # storefront: awning with scallops, body, door
    p = P()
    line(p, (cx - s, cy - 0.35 * s), (cx - 0.85 * s, cy - 0.8 * s), (cx + 0.85 * s, cy - 0.8 * s), (cx + s, cy - 0.35 * s))
    n = 5
    w = 2 * s / n
    p.moveTo(cx - s, cy - 0.35 * s)
    for i in range(n):
        x0 = cx - s + i * w
        p.quadTo(x0 + w / 2, cy - 0.12 * s, x0 + w, cy - 0.35 * s)
    line(p, (cx - 0.85 * s, cy - 0.25 * s), (cx - 0.85 * s, cy + 0.75 * s), (cx + 0.85 * s, cy + 0.75 * s), (cx + 0.85 * s, cy - 0.25 * s))
    line(p, (cx - 0.25 * s, cy + 0.75 * s), (cx - 0.25 * s, cy + 0.15 * s), (cx + 0.25 * s, cy + 0.15 * s), (cx + 0.25 * s, cy + 0.75 * s))
    return p


def cart(cx, cy, s):
    p = P()
    line(p, (cx - s, cy - 0.6 * s), (cx - 0.7 * s, cy - 0.6 * s), (cx - 0.45 * s, cy + 0.3 * s), (cx + 0.7 * s, cy + 0.3 * s), (cx + 0.9 * s, cy - 0.35 * s), (cx - 0.6 * s, cy - 0.35 * s))
    circle(p, cx - 0.3 * s, cy + 0.6 * s, 0.13 * s)
    circle(p, cx + 0.55 * s, cy + 0.6 * s, 0.13 * s)
    return p


def spark(cx, cy, s):
    # six rounded rays (drawn short so the marker gives them their round ends)
    p = P()
    for k in range(6):
        a = math.radians(-90 + 60 * k)
        p.moveTo(cx + math.cos(a) * 0.35 * s, cy + math.sin(a) * 0.35 * s)
        p.lineTo(cx + math.cos(a) * 0.95 * s, cy + math.sin(a) * 0.95 * s)
    return p


def flowchart(cx, cy, s):
    # "business model": three small boxes connected
    p = P()
    rrect(p, cx - 0.35 * s, cy - s, cx + 0.35 * s, cy - 0.5 * s, 0.08 * s)
    line(p, (cx, cy - 0.5 * s), (cx, cy - 0.2 * s))
    line(p, (cx - 0.7 * s, cy + 0.15 * s), (cx - 0.7 * s, cy - 0.2 * s), (cx + 0.7 * s, cy - 0.2 * s), (cx + 0.7 * s, cy + 0.15 * s))
    rrect(p, cx - s, cy + 0.15 * s, cx - 0.4 * s, cy + 0.65 * s, 0.08 * s)
    rrect(p, cx + 0.4 * s, cy + 0.15 * s, cx + s, cy + 0.65 * s, 0.08 * s)
    return p


def signpost(cx, cy, s):
    p = P()
    line(p, (cx, cy + s), (cx, cy - 0.9 * s))
    line(p, (cx - 0.1 * s, cy - 0.75 * s), (cx + 0.75 * s, cy - 0.75 * s), (cx + s, cy - 0.55 * s), (cx + 0.75 * s, cy - 0.35 * s), (cx - 0.1 * s, cy - 0.35 * s))
    line(p, (cx - 0.5 * s, cy + s), (cx + 0.5 * s, cy + s))
    return p


def arrow_down(cx, cy, s):
    p = P()
    line(p, (cx, cy - s), (cx, cy + s))
    line(p, (cx - 0.35 * s, cy + 0.6 * s), (cx, cy + s), (cx + 0.35 * s, cy + 0.6 * s))
    return p


def arrow_right(x0, y, x1, s=18):
    p = P()
    line(p, (x0, y), (x1, y))
    line(p, (x1 - s, y - s * 0.8), (x1, y), (x1 - s, y + s * 0.8))
    return p


def check(cx, cy, s):
    p = P()
    line(p, (cx - 0.5 * s, cy), (cx - 0.12 * s, cy + 0.38 * s), (cx + 0.55 * s, cy - 0.42 * s))
    return p


def check_circle(cx, cy, s):
    p = P()
    circle(p, cx, cy, s)
    line(p, (cx - 0.45 * s, cy + 0.02 * s), (cx - 0.12 * s, cy + 0.35 * s), (cx + 0.5 * s, cy - 0.35 * s))
    return p


def wallet(cx, cy, s):
    p = P()
    rrect(p, cx - s, cy - 0.6 * s, cx + s, cy + 0.7 * s, 0.15 * s)
    line(p, (cx - 0.85 * s, cy - 0.6 * s), (cx + 0.5 * s, cy - 0.95 * s), (cx + 0.65 * s, cy - 0.6 * s))
    rrect(p, cx + 0.45 * s, cy - 0.15 * s, cx + s, cy + 0.25 * s, 0.1 * s)
    return p


def target(cx, cy, s):
    p = P()
    circle(p, cx, cy, s)
    circle(p, cx, cy, 0.6 * s)
    circle(p, cx, cy, 0.2 * s)
    line(p, (cx + 1.0 * s, cy - 1.0 * s), (cx + 0.08 * s, cy - 0.08 * s))
    line(p, (cx + 0.75 * s, cy - 1.05 * s), (cx + 1.0 * s, cy - 1.0 * s), (cx + 1.05 * s, cy - 0.75 * s))
    return p


def boxes(cx, cy, s):
    # three stacked cartons: two on the bottom, one on top
    p = P()
    b = 0.5 * s          # half width of a carton
    h = 0.42 * s         # half height
    for (x, y) in [(cx - b - 4, cy + 0.5 * s), (cx + b + 4, cy + 0.5 * s), (cx, cy + 0.5 * s - 2 * h - 4)]:
        rrect(p, x - b, y - h, x + b, y + h, 0.04 * s)
        line(p, (x, y - h), (x, y - h + 0.35 * h))
    return p


def warehouse(cx, cy, s):
    p = P()
    line(p, (cx - s, cy + 0.8 * s), (cx - s, cy - 0.3 * s), (cx, cy - 0.85 * s), (cx + s, cy - 0.3 * s), (cx + s, cy + 0.8 * s), (cx - s, cy + 0.8 * s))
    line(p, (cx - 0.55 * s, cy + 0.8 * s), (cx - 0.55 * s, cy - 0.05 * s), (cx + 0.55 * s, cy - 0.05 * s), (cx + 0.55 * s, cy + 0.8 * s))
    for k in range(1, 3):
        y = cy - 0.05 * s + k * 0.28 * s
        line(p, (cx - 0.55 * s, y), (cx + 0.55 * s, y))
    return p


def tag(cx, cy, s):
    p = P()
    line(p, (cx - s, cy - 0.45 * s), (cx + 0.45 * s, cy - 0.45 * s), (cx + s, cy), (cx + 0.45 * s, cy + 0.45 * s), (cx - s, cy + 0.45 * s), (cx - s, cy - 0.45 * s))
    circle(p, cx + 0.42 * s, cy, 0.1 * s)
    return p


def star(cx, cy, s):
    p = P()
    pts = []
    for k in range(10):
        a = math.radians(-90 + 36 * k)
        r = s if k % 2 == 0 else 0.45 * s
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    line(p, *pts, pts[0])
    return p


def growth(cx, cy, s):
    p = P()
    line(p, (cx - s, cy - s), (cx - s, cy + s), (cx + s, cy + s))
    line(p, (cx - 0.75 * s, cy + 0.55 * s), (cx - 0.25 * s, cy + 0.05 * s), (cx + 0.15 * s, cy + 0.3 * s), (cx + 0.8 * s, cy - 0.65 * s))
    line(p, (cx + 0.45 * s, cy - 0.68 * s), (cx + 0.8 * s, cy - 0.65 * s), (cx + 0.78 * s, cy - 0.3 * s))
    return p


def stairs(cx, cy, s):
    p = P()
    n = 4
    w = 2 * s / n
    pts = [(cx - s, cy + s)]
    for i in range(n):
        x = cx - s + i * w
        y = cy + s - (i + 1) * w * 0.8
        pts += [(x, y), (x + w, y)]
    line(p, *pts)
    return p


def chat(cx, cy, s):
    p = P()
    p.moveTo(cx - 0.6 * s, cy + 0.55 * s)
    p.lineTo(cx - 0.75 * s, cy + 0.95 * s)
    p.lineTo(cx - 0.25 * s, cy + 0.55 * s)
    p.lineTo(cx + 0.85 * s, cy + 0.55 * s)
    p.quadTo(cx + s, cy + 0.55 * s, cx + s, cy + 0.4 * s)
    p.lineTo(cx + s, cy - 0.6 * s)
    p.quadTo(cx + s, cy - 0.75 * s, cx + 0.85 * s, cy - 0.75 * s)
    p.lineTo(cx - 0.85 * s, cy - 0.75 * s)
    p.quadTo(cx - s, cy - 0.75 * s, cx - s, cy - 0.6 * s)
    p.lineTo(cx - s, cy + 0.4 * s)
    p.quadTo(cx - s, cy + 0.55 * s, cx - 0.6 * s, cy + 0.55 * s)
    for dx in (-0.4, 0, 0.4):
        circle(p, cx + dx * s, cy - 0.1 * s, 0.05 * s)
    return p


def browser(cx, cy, w, h):
    p = P()
    rrect(p, cx - w, cy - h, cx + w, cy + h, 14)
    line(p, (cx - w, cy - h + 50), (cx + w, cy - h + 50))
    return p


def cursor(x, y, s):
    p = P()
    line(p, (x, y), (x, y + s), (x + 0.28 * s, y + 0.72 * s), (x + 0.5 * s, y + 1.1 * s), (x + 0.62 * s, y + 1.03 * s),
         (x + 0.42 * s, y + 0.66 * s), (x + 0.75 * s, y + 0.66 * s), (x, y))
    return p


def underline(x0, x1, y, wobble=6):
    p = P()
    p.moveTo(x0, y)
    p.cubicTo(x0 + (x1 - x0) * 0.33, y + wobble, x0 + (x1 - x0) * 0.66, y - wobble, x1, y)
    return p


def pill(cx, cy, w, h):
    p = P()
    rrect(p, cx - w, cy - h, cx + w, cy + h, h)
    return p


def card(cx, cy, w, h):
    p = P()
    rrect(p, cx - w, cy - h, cx + w, cy + h, 16)
    return p
