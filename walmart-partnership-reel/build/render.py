import sys, subprocess, os
import numpy as np, skia
from engine import W, H, FPS, make_paper, Hand
import scenes

def main():
    mode = sys.argv[1]
    S = scenes.build()
    for sc in S:
        print(f'scene {sc.t0:5.1f}-{sc.t1:5.1f} k={sc.k:.2f} draw_end={sc.draw_end:.2f}')
    paper, hand = make_paper(), Hand()
    surf = skia.Surface(W, H); c = surf.getCanvas()
    def frame(t):
        c.drawImage(paper, 0, 0)
        sc = next((s for s in S if s.t0 <= t < s.t1), S[-1])
        sc.draw(c, t)
        hand.draw(c, sc.pen_at(t))
    if mode == 'stills':
        ts = [float(x) for x in sys.argv[3:]]
        for t in ts:
            frame(t); surf.makeImageSnapshot().save(f'{sys.argv[2]}/f_{t:06.2f}.png')
        return
    out = sys.argv[2]; dur = S[-1].t1
    ff = subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgra','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
                           '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart', out], stdin=subprocess.PIPE)
    n = int(round(dur * FPS))
    for i in range(n):
        frame(i / FPS)
        ff.stdin.write(surf.makeImageSnapshot().tobytes())
    ff.stdin.close(); ff.wait()

main()
