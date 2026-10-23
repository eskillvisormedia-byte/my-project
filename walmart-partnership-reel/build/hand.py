# Vector drawing hand holding a marker. Local frame: marker tip at (0,0), barrel along +x.
import skia, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
SC = 2.0
W, H = 1500, 1000
OX, OY = 40, 420
ANG = 36
PAD = 200   # tip lands at (PAD, PAD) in the output image

SKIN = 0xFFE0A987; SKIN_D = 0xFFBF8261; SKIN_L = 0xFFF3CFB1; LINE = 0xFF8E5A40; NAIL = 0xFFF6DCCD

def P(*cmds):
    p = skia.Path()
    for c in cmds:
        op, a = c[0], c[1:]
        getattr(p, {'M':'moveTo','L':'lineTo','C':'cubicTo','Q':'quadTo','Z':'close'}[op])(*a)
    return p

def lin(x0,y0,x1,y1,cols,pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(x0,y0),skia.Point(x1,y1)], cols, pos)

def paint(col=None, shader=None):
    p = skia.Paint(AntiAlias=True)
    if col is not None: p.setColor(col)
    if shader: p.setShader(shader)
    return p

def stroke(c, path, col=LINE, w=2.0):
    c.drawPath(path, skia.Paint(AntiAlias=True, Color=col, Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                                StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join))

BW = 21  # marker half-width

def arm_path():
    # back of hand + forearm; top edge (y<0) is knuckle side
    return P(('M',175,-40),('C',200,-95,260,-120,330,-122),('C',400,-124,470,-105,540,-92),
             ('L',1500,-40),('L',1500,150),('L',560,118),
             ('C',470,112,380,120,320,118),('C',260,116,215,90,190,50),('C',175,25,168,-10,175,-40),('Z',))

def draw_hand(c, shadow=False):
    if shadow:
        sp = paint(0xFF000000)
        for path in [arm_path()]: c.drawPath(path, sp)
        c.drawRect(skia.Rect(40,-BW,440,BW), sp)
        return
    # curled fingers (middle, ring, pinky) tucked under the barrel
    for cx,cy,r in [(250,92,34),(310,112,33),(370,122,30)]:
        f = P(('M',cx-r*1.2,cy-r*1.1),('C',cx-r*1.5,cy+r*0.3,cx-r*0.6,cy+r*1.15,cx+r*0.3,cy+r*1.05),
              ('C',cx+r*1.2,cy+r*0.95,cx+r*1.45,cy-r*0.1,cx+r*1.15,cy-r*1.0),('Z',))
        c.drawPath(f, paint(shader=lin(cx,cy-r,cx,cy+r,[SKIN,SKIN_D])))
        stroke(c, P(('M',cx-r*1.2,cy-r*0.6),('C',cx-r*1.5,cy+r*0.3,cx-r*0.6,cy+r*1.15,cx+r*0.3,cy+r*1.05),
                    ('C',cx+r*1.0,cy+r*0.95,cx+r*1.3,cy+r*0.3,cx+r*1.3,cy-r*0.2)))
    arm = arm_path()
    c.drawPath(arm, paint(shader=lin(0,-125,0,150,[SKIN_L,SKIN,SKIN_D],[0,0.4,1])))
    stroke(c, P(('M',175,-40),('C',200,-95,260,-120,330,-122),('C',400,-124,470,-105,540,-92),('L',1500,-40)))
    stroke(c, P(('M',1500,150),('L',560,118),('C',470,112,380,120,320,118)))
    # knuckle highlights
    for kx,ky in [(300,-100),(370,-96)]:
        g = skia.GradientShader.MakeRadial(skia.Point(kx,ky),40,[0x55FFFFFF,0x00FFFFFF])
        c.drawCircle(kx,ky,40,paint(shader=g))
    # marker
    barrel = skia.RRect.MakeRectXY(skia.Rect(52,-BW,420,BW), 10, 10)
    c.drawRRect(barrel, paint(shader=lin(0,-BW,0,BW,[0xFFFFFFFF,0xFFF6F6F6,0xFFC4C4C4,0xFF9E9E9E],[0,0.35,0.85,1])))
    blk = lin(0,-BW,0,BW,[0xFF4A4A4A,0xFF1C1C1C,0xFF050505],[0,0.4,1])
    c.drawRect(skia.Rect(300,-BW+0.5,350,BW-0.5), paint(shader=blk))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(395,-BW-2,452,BW+2),10,10), paint(shader=blk))
    c.drawPath(P(('M',16,-8),('L',54,-BW+3),('L',54,BW-3),('L',16,8),('Z',)), paint(shader=blk))
    c.drawPath(P(('M',0,-3),('C',5,-6,11,-7.5,17,-8),('L',17,8),('C',11,7.5,5,6,0,3),('Z',)), paint(0xFF101010))
    stroke(c, P(('M',60,-BW+0.5),('L',395,-BW+0.5)), 0xFF8A8A8A, 1.4)
    # thumb pressing the near side (+y) of the barrel
    th = P(('M',300,70),('C',250,48,175,44,128,38),('C',96,34,82,46,88,62),('C',95,78,126,80,160,84),
           ('C',205,90,250,100,290,104),('Z',))
    c.drawPath(th, paint(shader=lin(0,34,0,104,[SKIN_L,SKIN,SKIN_D],[0,0.45,1])))
    stroke(c, P(('M',250,50),('C',210,44,170,42,128,38),('C',96,34,82,46,88,62),('C',95,78,126,80,160,84),('C',205,90,240,98,270,102)))
    nail = P(('M',94,46),('C',104,40,120,41,124,49),('C',120,57,106,58,95,54),('Z',))
    c.drawPath(nail, paint(NAIL)); stroke(c, nail, LINE, 1.2)
    # index finger lying along the far side (-y) of the barrel
    ix = P(('M',340,-118),('C',280,-92,205,-62,140,-46),('C',104,-37,80,-34,76,-20),('C',72,-4,90,0,116,-2),
           ('C',175,-6,240,-18,320,-36),('Z',))
    c.drawPath(ix, paint(shader=lin(0,-90,0,0,[SKIN_L,SKIN,SKIN_D],[0,0.5,1])))
    stroke(c, P(('M',300,-104),('C',255,-84,205,-62,140,-46),('C',104,-37,80,-34,76,-20),('C',72,-4,90,0,116,-2),('C',160,-5,200,-12,240,-20)))
    nail2 = P(('M',80,-24),('C',84,-34,100,-37,110,-30),('C',108,-20,96,-15,82,-15),('Z',))
    c.drawPath(nail2, paint(NAIL)); stroke(c, nail2, LINE, 1.2)
    cr = 0x889A6247
    stroke(c, P(('M',190,-66),('Q',196,-52,190,-38)), cr, 1.6)
    stroke(c, P(('M',178,46),('Q',184,60,178,74)), cr, 1.6)

def render(shadow=False):
    surf = skia.Surface(int(W*SC), int(H*SC)); c = surf.getCanvas(); c.clear(0)
    c.scale(SC, SC); c.translate(OX, OY)
    draw_hand(c, shadow)
    img = surf.makeImageSnapshot()
    out = skia.Surface(1500, 1500); o = out.getCanvas(); o.clear(0)
    o.translate(PAD, PAD); o.rotate(ANG)
    o.drawImageRect(img, skia.Rect(-OX,-OY,W-OX,H-OY), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    return out.makeImageSnapshot()

def build():
    hand = render(); sh = render(True)
    # soft shadow image: blurred, low alpha
    s = skia.Surface(1500,1500); c = s.getCanvas(); c.clear(0)
    p = skia.Paint(ImageFilter=skia.ImageFilters.Blur(14,14), ColorFilter=skia.ColorFilters.Blend(0x33000000, skia.BlendMode.kSrcIn))
    c.drawImage(sh, 0, 0, skia.SamplingOptions(), p)
    return hand, s.makeImageSnapshot()

if __name__ == '__main__':
    hand, shadow = build()
    s = skia.Surface(1080, 1500); c = s.getCanvas(); c.clear(0xFFEDEDEA)
    c.drawImage(shadow, 300-PAD+18, 300-PAD+26); c.drawImage(hand, 300-PAD, 300-PAD)
    c.drawCircle(300,300,3,paint(0xFFFF0000))
    s.makeImageSnapshot().save(os.path.join(HERE, 'hand_prev.png'))
