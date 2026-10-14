"""Synthesises the soundtrack (music bed + SFX) for the Walmart opportunity video.
Timeline mirrors T in scene.html. Output: 48 kHz stereo WAV."""
import sys, wave
import numpy as np

SR = 48000
DUR = 21.0
N = int(SR * DUR)
BPM = 120
BEAT = 60 / BPM
rng = np.random.default_rng(7)

def t_arr(d): return np.arange(int(SR * d)) / SR
def midi(n): return 440 * 2 ** ((n - 69) / 12)

def lowpass(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** 4), len(x))

def highpass(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * (1 / np.sqrt(1 + (fc / np.maximum(f, 1)) ** 4)), len(x))

def bandpass(x, lo, hi): return highpass(lowpass(x, hi), lo)

def place(buf, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= len(buf): return
    sig = sig[: len(buf) - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * gain * l * 1.414
    buf[i:i + len(sig), 1] += sig * gain * r * 1.414

# ------------------------------------------------------------------ music
music = np.zeros((N, 2))
CHORDS = [  # F maj7, G add9, E m7, A m7  (1 bar = 4 beats = 2 s each)
    [53, 57, 60, 64], [55, 59, 62, 69], [52, 55, 59, 62], [57, 60, 64, 67]]
ROOTS = [41, 43, 40, 45]
BAR = 4 * BEAT
nbars = int(np.ceil(DUR / BAR))

def saw(f, t, det=0.0):
    ph = (f * (1 + det) * t) % 1.0
    return 2 * ph - 1

# pad
pad = np.zeros(N)
for b in range(nbars):
    ch = CHORDS[b % 4]; t = t_arr(BAR + 0.3)
    env = np.minimum(1, t / 0.35) * np.exp(-np.maximum(0, t - BAR) * 12)
    s = sum(saw(midi(n), t, d) for n in ch for d in (-0.004, 0, 0.005)) / 12
    seg = s * env
    i = int(b * BAR * SR); seg = seg[: N - i]; pad[i:i + len(seg)] += seg
pad = lowpass(pad, 1400)

# pluck arpeggio (16ths) with ping-pong delay
pl = np.zeros((N, 2))
pattern = [0, 1, 2, 3, 2, 1, 2, 3, 0, 2, 1, 3, 2, 3, 1, 2]
for b in range(nbars):
    ch = CHORDS[b % 4]
    for k in range(16):
        at = b * BAR + k * BEAT / 4
        if at >= DUR: break
        n = ch[pattern[k]] + 12
        t = t_arr(0.35)
        tone = (np.sin(2 * np.pi * midi(n) * t) + 0.3 * np.sin(4 * np.pi * midi(n) * t)) * np.exp(-t * 14)
        g = 0.55 if k % 4 == 0 else 0.38
        place(pl, tone, at, g, pan=0.25 * np.sin(k))
        place(pl, tone, at + 3 * BEAT / 4, g * 0.3, pan=-0.6)
        place(pl, tone, at + 6 * BEAT / 4, g * 0.15, pan=0.6)

# bass (8ths)
bass = np.zeros(N)
for b in range(nbars):
    for k in range(8):
        at = b * BAR + k * BEAT / 2
        if at >= DUR or at < 4.0: continue
        f = midi(ROOTS[b % 4] - (0 if k % 2 == 0 else -12)) if k in (3, 7) else midi(ROOTS[b % 4])
        t = t_arr(BEAT / 2)
        s = np.tanh(2.2 * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)))
        env = np.minimum(1, t / 0.005) * np.exp(-t * 4) * np.minimum(1, (BEAT / 2 - t) / 0.01)
        seg = s * env; i = int(at * SR); seg = seg[: N - i]; bass[i:i + len(seg)] += seg

# drums
def kick():
    t = t_arr(0.45); f = 45 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) + 0.3 * np.exp(-t * 300) * rng.standard_normal(len(t)) * 0.3
def clap():
    t = t_arr(0.25); n = bandpass(rng.standard_normal(len(t)), 900, 5000)
    env = np.exp(-t * 22) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0) * (t < 0.03))
    return n * env / np.max(np.abs(n))
def hat(open_=False):
    t = t_arr(0.18 if open_ else 0.05); n = highpass(rng.standard_normal(len(t)), 7000)
    return n * np.exp(-t * (18 if open_ else 80)) / np.max(np.abs(n))

drums = np.zeros((N, 2)); duck = np.ones(N)
K = kick(); C = clap()
for b in range(nbars):
    for k in range(4):
        at = b * BAR + k * BEAT
        if at < 4.0 or at >= DUR: continue
        if 15.0 <= at < 15.4: continue                      # break before the CTA drop
        place(drums, K, at, 0.95)
        i = int(at * SR); dl = min(int(0.25 * SR), N - i)
        duck[i:i + dl] = np.minimum(duck[i:i + dl], 1 - 0.55 * np.exp(-np.arange(dl) / SR * 9))
        if k in (1, 3): place(drums, C, at, 0.32)
        place(drums, hat(), at + BEAT / 2, 0.16, pan=0.3)
        place(drums, hat(), at + BEAT / 4, 0.07, pan=-0.3)
        place(drums, hat(), at + 3 * BEAT / 4, 0.07, pan=-0.3)
# soft hats + shaker during the hook so it never feels empty
for k in range(16):
    place(drums, hat(), k * BEAT / 2 + BEAT / 2, 0.06, pan=0.4 * (-1) ** k)

pad_st = np.stack([pad, np.roll(pad, 600)], 1)
music += pad_st * 0.30 * duck[:, None]
music += pl * 0.22
music += (bass * 0.30 * duck)[:, None]
music += drums * 0.55
# hook intro: filtered (muffled) until drums hit, then open up
t = np.arange(N) / SR
open_ = np.clip((t - 3.0) / 1.0, 0, 1)
muff = np.stack([lowpass(music[:, 0], 900), lowpass(music[:, 1], 900)], 1)
music = muff * (1 - open_[:, None]) + music * open_[:, None]
# dip during the break, fade out at end
music *= np.where((t > 15.0) & (t < 15.4), 0.35, 1.0)[:, None]
music *= np.clip((DUR - t) / 2.0, 0, 1)[:, None]
music *= np.clip(t / 0.4, 0, 1)[:, None]

# ------------------------------------------------------------------ SFX
sfx = np.zeros((N, 2))

def pop(f0=900, f1=260, d=0.12):
    t = t_arr(d); f = f1 + (f0 - f1) * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
def tick(f=2600):
    t = t_arr(0.04); return np.sin(2 * np.pi * f * t) * np.exp(-t * 120)
def whoosh(d=0.6, peak=0.6, lo=300, hi=4000):
    t = t_arr(d); n = rng.standard_normal(len(t))
    env = np.where(t < d * peak, (t / (d * peak)) ** 2, np.exp(-(t - d * peak) * 9))
    a = bandpass(n, lo, hi) * env
    return a / np.max(np.abs(a))
def riser(d=1.5):
    t = t_arr(d); f = 180 * (8 ** (t / d))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + highpass(rng.standard_normal(len(t)), 2000) * 0.5 * (t / d)
    return tone * (t / d) ** 2
def impact():
    t = t_arr(1.8); f = 35 + 80 * np.exp(-t * 18)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5)
    crash = highpass(rng.standard_normal(len(t)), 4000) * np.exp(-t * 2.6) * 0.35
    return boom + crash
def chime(base=88):
    t = t_arr(1.6); s = np.zeros(len(t))
    for i, n in enumerate([base, base + 4, base + 7, base + 12]):
        tt = np.clip(t - i * 0.06, 0, None)
        s += (np.sin(2 * np.pi * midi(n) * tt) + 0.2 * np.sin(2 * np.pi * midi(n) * 2.76 * tt)) * np.exp(-tt * 3.5) * (t >= i * 0.06)
    return s / 4

# scene A — hook
place(sfx, whoosh(0.9, 0.7, 250, 3500), 0.05, 0.45, pan=-0.4)   # bag tumbles in
place(sfx, pop(380, 70, 0.3), 1.15, 0.8)                         # bag lands
place(sfx, tick(2200), 0.55, 0.3)
place(sfx, pop(520, 110, 0.22), 0.85, 0.5)                       # "Walmart"
place(sfx, whoosh(0.8, 0.55, 400, 5000), 1.1, 0.4, pan=-0.6)     # ribbon sweep
place(sfx, pop(1300, 600, 0.08), 1.65, 0.25, pan=0.7)            # minis
place(sfx, pop(1200, 550, 0.08), 1.95, 0.25, pan=-0.7)
place(sfx, tick(2400), 1.55, 0.3)
place(sfx, pop(700, 200, 0.2), 1.8, 0.5)                         # "Opportunity?"
# vertical whip transitions through the five cards
CHAIN = [4.0, 5.4, 6.8, 8.2, 9.6, 11.0]
for i, b in enumerate(CHAIN):
    place(sfx, whoosh(0.55, 0.62, 300, 6000), b - 0.36, 0.6, pan=0.3 * (-1) ** i)
    if i < 5:
        place(sfx, pop(760 + i * 80, 230 + i * 25), b + 0.12, 0.55)
        place(sfx, tick(2600), b + 0.3, 0.2)
# scene C — ecosystem
place(sfx, tick(2000), 11.15, 0.25)
place(sfx, tick(2000), 11.55, 0.25)
for i in range(5):
    place(sfx, pop(900 + i * 70, 300, 0.1), 11.72 + i * 0.13, 0.4, pan=-0.6 + i * 0.3)
place(sfx, tick(2000), 12.55, 0.25)
place(sfx, pop(450, 90, 0.3), 12.95, 0.7)                        # "the seller."
place(sfx, chime(84), 13.0, 0.22)
place(sfx, whoosh(0.4, 0.6, 1500, 8000), 13.6, 0.25, pan=0.4)    # underline
# push-in to the close-up + CTA
place(sfx, riser(1.4), 14.0, 0.35)
place(sfx, whoosh(0.5, 0.85, 200, 2500), 15.0, 0.55)
place(sfx, impact(), 15.4, 0.7)
place(sfx, pop(1100, 380, 0.12), 15.6, 0.4)                       # spark blooms
for at in (15.75, 16.3, 16.85): place(sfx, tick(2300), at, 0.22)
place(sfx, pop(520, 110, 0.22), 17.15, 0.5)                      # "Walmart"
place(sfx, chime(91), 17.55, 0.32)                               # "Marketplace."
place(sfx, whoosh(0.5, 0.6, 1500, 8000), 18.3, 0.25, pan=0.5)    # underline

# ------------------------------------------------------------------ mix
mix = music * 0.9 + sfx * 0.55
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.6) / np.tanh(1.6) * 0.89          # soft limiter
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
