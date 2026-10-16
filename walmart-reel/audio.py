"""Original music bed + sound effects for the Walmart reel, synthesized from scratch.

All cue times match the animation timeline in reel.html.
Usage: python3 audio.py  ->  writes soundtrack.wav (48 kHz stereo, 18 s)
"""
import wave
import numpy as np
from scipy import signal

SR = 48000
DUR = 18.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

mus = np.zeros((N, 2))
sfx = np.zeros((N, 2))


def add(buf, t, x, gain=1.0, pan=0.0):
    i = int(t * SR)
    if x.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        x = np.stack([x * l, x * r], 1) * np.sqrt(2)
    j = min(N, i + len(x))
    if j > i:
        buf[i:j] += x[: j - i] * gain


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)


def tsec(s):
    return np.arange(int(s * SR)) / SR


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, 'low', fs=SR, output='sos'), x)


def hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, 'high', fs=SR, output='sos'), x)


def bp(x, lo, hi):
    return signal.sosfilt(signal.butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)


def reverb(x, secs=1.8, mix=0.25):
    n = int(secs * SR)
    ir = rng.standard_normal((n, 2)) * np.exp(-np.arange(n) / SR * 4.5)[:, None]
    ir[:, 0] = lp(ir[:, 0], 6000); ir[:, 1] = lp(ir[:, 1], 6000)
    ir /= np.sqrt((ir ** 2).sum(0))
    wet = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - mix) + wet * mix


# ------------------------------------------------------------------ MUSIC
# 114.3 BPM so bars (2.1 s) land on the scene cuts at 4.4 / 8.6 / 12.8 s.
BEAT = 0.525
T0 = 0.2
BAR = BEAT * 4

# Cmaj9 - Am9 - Fmaj9 - G6/9 : bright, optimistic, minimal
CHORDS = [[48, 55, 64, 71, 74], [45, 52, 60, 67, 71], [41, 48, 57, 64, 67], [43, 50, 59, 64, 69]]


def pluck(m, dur=0.9, bright=1.0):
    t = tsec(dur); f = hz(m)
    x = sum((0.6 ** k) * np.sin(2 * np.pi * f * (k + 1) * t) for k in range(5))
    return x * env(len(t), 0.003, 0.18 * bright + 0.1)


def pad(notes, dur):
    t = tsec(dur)
    x = np.zeros(len(t))
    for m in notes:
        for det in (-0.08, 0.08):
            x += signal.sawtooth(2 * np.pi * hz(m + det) * t)
    x = lp(x, 1400) / len(notes)
    a = np.minimum(t / 0.4, 1) * np.minimum((dur - t) / 0.4, 1)
    return x * a


def kick():
    t = tsec(0.4)
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    return hp(rng.standard_normal(n), 8000) * env(n, 0.001, 0.06 if open_ else 0.012)


def clap():
    n = int(0.25 * SR)
    x = bp(rng.standard_normal(n), 900, 3000)
    e = np.zeros(n)
    for o in (0, 0.01, 0.02):
        k = int(o * SR); e[k:] += env(n - k, 0.001, 0.07 if o == 0.02 else 0.008)
    return x * e


nbars = int((DUR - T0) / BAR) + 1
for b in range(nbars):
    tb = T0 + b * BAR
    ch = CHORDS[b % 4]
    add(mus, tb, pad(ch, BAR + 0.3), 0.10)
    add(mus, tb, np.sin(2 * np.pi * hz(ch[0] - 12) * tsec(BAR)) * env(int(BAR * SR), 0.01, 1.2), 0.22)
    # arpeggiated pluck, 8th notes
    arp = [ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[3] + 12, ch[2] + 24, ch[4] + 12, ch[3] + 12, ch[1] + 12]
    for k, m in enumerate(arp):
        add(mus, tb + k * BEAT / 2, pluck(m, 0.6), 0.07, pan=0.35 if k % 2 else -0.35)
    if b >= 1:  # drums come in after the intro bar
        for k in range(4):
            if k in (0, 2):
                add(mus, tb + k * BEAT, kick(), 0.55)
            if k in (1, 3):
                add(mus, tb + k * BEAT, clap(), 0.16)
        for k in range(8):
            add(mus, tb + k * BEAT / 2, hat(k == 7), 0.07 if k % 2 else 0.04, pan=0.2)

mus = reverb(mus, 1.6, 0.18)
fade = np.ones(N); fo = int(1.0 * SR); fade[-fo:] = np.linspace(1, 0, fo)
fi = int(0.15 * SR); fade[:fi] = np.linspace(0, 1, fi)
mus *= fade[:, None]

# ------------------------------------------------------------------ SFX


def whoosh(dur=0.7, lo=300, hi=4000, up=True):
    n = int(dur * SR); t = np.arange(n) / n
    noise = rng.standard_normal(n)
    # crossfade between filtered bands to fake a sweeping filter
    bands = [bp(noise, f, f * 2.2) for f in np.geomspace(lo, hi, 6)]
    pos = (t if up else 1 - t) * (len(bands) - 1)
    x = np.zeros(n)
    for i, bnd in enumerate(bands):
        x += bnd * np.clip(1 - np.abs(pos - i), 0, 1)
    shape = np.sin(np.pi * t) ** 1.5
    return x * shape / (np.abs(x).max() + 1e-9)


def pop(m=79, dur=0.18):
    t = tsec(dur)
    f = hz(m) * (1 + 0.6 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.045)


def tick():
    n = int(0.04 * SR)
    return hp(rng.standard_normal(n), 3000) * env(n, 0.0005, 0.006)


def impact():
    t = tsec(0.9)
    sub = np.sin(2 * np.pi * np.cumsum(60 + 80 * np.exp(-t * 20)) / SR) * np.exp(-t * 5)
    return sub + 0.3 * lp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 18)


def chime(notes, dur=1.6):
    x = np.zeros(int(dur * SR))
    for k, m in enumerate(notes):
        t = tsec(dur - k * 0.06); f = hz(m)
        s = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t)) * env(len(t), 0.002, 0.5)
        x[int(k * 0.06 * SR):] += s
    return x / len(notes)


def click():
    n = int(0.03 * SR)
    return bp(rng.standard_normal(n), 2000, 6000) * env(n, 0.0003, 0.004) + \
        0.6 * np.sin(2 * np.pi * 1800 * tsec(0.03)) * env(n, 0.0003, 0.003)


# Scene 1 (0 - 4.4)
add(sfx, 0.0, whoosh(0.9, 400, 5000), 0.30, pan=0.5)    # cart
add(sfx, 0.15, whoosh(1.0, 200, 3000), 0.30, pan=-0.5)  # bag
for t in (0.55, 0.85, 1.15, 1.4):
    add(sfx, t, tick(), 0.18)
add(sfx, 1.8, impact(), 0.45)
add(sfx, 1.8, pop(84), 0.22)
add(sfx, 2.35, whoosh(0.6, 1500, 8000), 0.14, pan=0.3)  # underline swish

# Scene cuts
for t in (4.4, 8.6, 12.8):
    add(sfx, t - 0.25, whoosh(0.5, 600, 9000), 0.28)

# Scene 2 (4.4 - 8.6): category chips, rising pentatonic pops
for i, m in enumerate([76, 79, 81, 84, 88]):
    add(sfx, 4.4 + 0.4 + i * 0.55, pop(m), 0.28, pan=-0.3)
    add(sfx, 4.4 + 0.5 + i * 0.55, tick(), 0.10)

# Scene 3 (8.6 - 12.8): 20 stores pop in by distance from centre
scale = [72, 74, 76, 79, 81, 84, 86, 88]
for r in range(4):
    for c in range(5):
        d = np.hypot(c - 2, r - 1.5)
        add(sfx, 8.6 + 0.05 + d * 0.17, pop(scale[min(int(d * 2.6), 7)], 0.12), 0.09,
            pan=(c - 2) / 2.5)
for t in (0.9, 1.1, 1.25, 1.5, 1.65, 1.85, 2.1):
    add(sfx, 8.6 + t, tick(), 0.14)
add(sfx, 8.6 + 2.4, impact(), 0.38)
add(sfx, 8.6 + 2.7, pop(84), 0.2)

# Scene 4 (12.8 - 18): CTA
add(sfx, 12.8, whoosh(1.0, 300, 4000), 0.32, pan=0.6)   # laptop
for t in (0.6, 0.8, 0.95):
    add(sfx, 12.8 + t, tick(), 0.16)
for t in (1.25, 1.45):
    add(sfx, 12.8 + t, pop(81), 0.16)
add(sfx, 12.8 + 1.7, impact(), 0.42)
add(sfx, 12.8 + 1.9, whoosh(1.0, 200, 2500, up=False), 0.16, pan=0.4)  # arc
add(sfx, 12.8 + 2.2, pop(76, 0.25), 0.3)                              # button
add(sfx, 12.8 + 2.8, whoosh(0.75, 2000, 9000), 0.06, pan=0.6)        # cursor glide
add(sfx, 12.8 + 3.55, click(), 0.5)
add(sfx, 12.8 + 3.6, chime([84, 88, 91, 96]), 0.35)

sfx = reverb(sfx, 1.2, 0.15)

# ------------------------------------------------------------------ MIX
mix = mus * 0.9 + sfx
mix = np.tanh(mix * 1.6) / np.tanh(1.6)  # gentle glue / limiting
mix *= 0.89 / np.abs(mix).max()
pcm = (mix * 32767).astype('<i2')
with wave.open('soundtrack.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote soundtrack.wav', mix.shape)
