# ESkillVisor logo drawn in the reel's marker style: the ESV mark is outlined, then coloured in
# with a smooth sweep of the pen; the wordmark is hand-lettered with "Visor" in the brand orange.
import json, os
import skia
from engine import Text, Stroke, ease, INK

ORANGE = 0xFFF27125
HERE = os.path.dirname(os.path.abspath(__file__))
MARK = json.load(open(os.path.join(HERE, 'mark.json')))
MX0, MX1, MY0, MY1 = 108, 337, 469, 554     # mark bounds in the source logo


class ColorFill:
    """Colours a shape in, revealed left to right under the pen."""

    def __init__(self, path, color, speed=900.0):
        self.path, self.color = path, color
        r = path.computeTightBounds()
        self.r = r
        self.dur = max(0.35, r.width() / speed)
        self.start = (r.left() + 4, r.centerY())
        self.end = (r.right() - 4, r.centerY())

    def pen(self, p):
        q = ease(p)
        return (self.r.left() + 4 + (self.r.width() - 8) * q, self.r.centerY())

    def draw(self, c, p, alpha=1.0):
        if p <= 0:
            return
        c.save()
        if p < 1:
            c.clipRect(skia.Rect(-10, -10000, self.pen(p)[0] + 6, 10000))
        pt = skia.Paint(AntiAlias=True, Color=self.color)
        pt.setAlphaf(pt.getAlphaf() * alpha)
        c.drawPath(self.path, pt)
        c.restore()


def _poly(pts, cx, top, s):
    p = skia.Path()
    w = (MX1 - MX0) * s
    for i, (x, y) in enumerate(pts):
        X, Y = cx - w / 2 + (x - MX0) * s, top + (y - MY0) * s
        (p.moveTo if i == 0 else p.lineTo)(X, Y)
    p.close()
    return p


def mark(cx, top, s):
    """ESV mark: outline each piece, then colour it in."""
    items = []
    shapes = [(MARK['orange'][1], ORANGE), (MARK['black'][0], INK), (MARK['orange'][0], ORANGE), (MARK['black'][1], INK)]
    for pts, col in shapes:
        path = _poly(pts, cx, top, s)
        items.append(Stroke(path, INK, 4, speed=1400))
        items.append(ColorFill(path, col))
    return items


def wordmark(cx, y, size):
    a = Text('eSkill', 0, y, size, INK, align='left', caps=False)
    b = Text('Visor', 0, y, size, ORANGE, align='left', caps=False)
    x0 = cx - (a.w + b.w) / 2
    a.x0, b.x0 = x0, x0 + a.w
    return [a, b]


def height(s):
    return (MY1 - MY0) * s
