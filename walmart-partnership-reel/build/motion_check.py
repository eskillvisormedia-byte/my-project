import scenes, math
S = scenes.build(); pts = []
for sc in S: print(f'{sc.t0}-{sc.t1} kmin={sc.k:.2f}')
for i in range(int(95 * 30)):
    t = i / 30; sc = next((s for s in S if s.t0 <= t < s.t1), S[-1]); pts.append(sc.pen_at(t))
acc = [(math.dist((pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1]), (pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1])), i / 30) for i in range(1, len(pts) - 1)]
acc.sort(reverse=True); print([(round(a), round(t, 2)) for a, t in acc[:12]])
