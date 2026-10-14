# Warm SaaS / corporate bed, 15 s, 120 BPM. Cuts at 3.2, 7.0, 11.6; click at 14.45.
import numpy as np, wave
SR = 44100; T = 15.0; N = int(SR * T); B = 0.5
rng = np.random.default_rng(11)
dry = np.zeros((N, 2)); send = np.zeros((N, 2))

def place(buf, sig, t, g=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[:j - i] * g
    buf[i:j, 0] += s * (1 - max(pan, 0)); buf[i:j, 1] += s * (1 + min(pan, 0))
def add(sig, t, g=1.0, pan=0.0, rev=0.0):
    place(dry, sig, t, g, pan)
    if rev: place(send, sig, t, g * rev, pan)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lp(x, c):
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s += c * (x[i] - s); y[i] = s
    return y
def hp(x, c): return x - lp(x, c)
def m2f(m): return 440 * 2 ** ((m - 69) / 12)

# --- instruments ---
def pad(notes, dur, bright=0.06):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for m in notes:
        f = m2f(m)
        for d in (-0.08, 0.0, 0.08):                          # detuned saws
            x += 2 * ((t * f * 2 ** (d / 12) + rng.random()) % 1) - 1
    x = lp(lp(x / (3 * len(notes)), bright), bright * 1.5)
    a = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.5)
    return x * a * 2.2
def keys(m, dur=0.9, vel=1.0):                                 # soft electric-piano tone
    n = int(dur * SR); t = np.arange(n) / SR; f = m2f(m)
    x = np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.25))
    x += 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.15)
    return x * env(n, 0.006, 0.45) * vel
def sub(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.tanh(1.4 * np.sin(2 * np.pi * m2f(m) * t))
    return x * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.05)
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(45 + 55 * np.exp(-t / 0.04)) / SR) * np.exp(-t / 0.18)
def clap():
    n = int(0.3 * SR); x = hp(rng.standard_normal(n), 0.25); e = np.zeros(n)
    for o in (0, 0.009, 0.018): k = int(o * SR); e[k:] += env(n - k, 0.001, 0.07)
    return lp(x * e, 0.5) * 0.5
def shaker(): n = int(0.07 * SR); return hp(rng.standard_normal(n), 0.4) * env(n, 0.01, 0.025)
def swell(dur):                                                 # reverse-cymbal style rise into a cut
    n = int(dur * SR); t = np.arange(n) / SR
    x = hp(rng.standard_normal(n), 0.15); return lp(x, 0.35) * (t / dur) ** 3
def boom():
    n = int(2.0 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(40 + 30 * np.exp(-t / 0.1)) / SR) * np.exp(-t / 0.7)

# --- harmony: Fmaj7 - G6 - Am7 - Em7 (bright, confident) ---
CH = [[53, 57, 60, 64], [55, 59, 62, 64], [57, 60, 64, 67], [52, 55, 59, 62]]
BS = [41, 43, 45, 40]
ARP = [0, 2, 1, 3, 2, 1, 3, 2]
for bar in range(8):                                            # 2 s bars
    t0 = bar * 2.0; c = CH[bar % 4]
    if t0 < 15: add(pad([m + 12 for m in c], 2.1, 0.06 if t0 < 3 else 0.075), t0, 0.55 if t0 < 3 else 0.32, 0, 0.5)
    for k, idx in enumerate(ARP):
        tt = t0 + k * 0.25
        if tt >= 14.4: break
        add(keys(c[idx] + 24, 0.8, 0.55 + 0.25 * (k % 2 == 0)), tt, 0.2 if tt < 3.2 else 0.11, 0.35 * (-1) ** k, 0.6)
    if 3.2 <= t0 + 2 and t0 < 14:
        add(sub(BS[bar % 4], 0.9), max(t0, 3.2), 0.30); add(sub(BS[bar % 4], 0.45), t0 + 1.5, 0.22)

# drums: enter at the first cut, half-time break before the CTA lands
for b in range(int(T / B)):
    t = b * B
    if t < 3.2 or t >= 14.4: continue
    half = 11.6 <= t < 12.5
    if not half or b % 2 == 0: add(kick(), t, 0.55)
    if b % 2 == 1 and not half: add(clap(), t, 0.45, 0, 0.35)
    add(shaker(), t + 0.25, 0.16, 0.3); add(shaker(), t + 0.125, 0.07, -0.3); add(shaker(), t + 0.375, 0.07, -0.3)

for c in (3.2, 7.0, 11.6): add(swell(1.2), c - 1.2, 0.22, 0, 0.4)
add(boom(), 11.6, 0.35, 0, 0.3)
add(keys(72, 2.4, 1.0), 14.45, 0.18, 0, 1.0); add(keys(76, 2.4, 0.8), 14.45, 0.12, 0.2, 1.0); add(keys(79, 2.4, 0.8), 14.45, 0.12, -0.2, 1.0)

# sidechain pump on everything but drums would need stems; apply gentle pump to whole bus instead
pump = np.ones(N)
for b in range(int(3.2 / B), int(14.4 / B)):
    i = int(b * B * SR); n = int(0.22 * SR)
    pump[i:i + n] = np.minimum(pump[i:i + n], 0.78 + 0.22 * np.linspace(0, 1, n) ** 0.5)

# reverb send: decaying-noise impulse response via FFT convolution
irn = int(1.6 * SR); ir_t = np.arange(irn) / SR
out = dry.copy()
for ch in range(2):
    ir = rng.standard_normal(irn) * np.exp(-ir_t / 0.45); ir = lp(ir, 0.3); ir /= np.sqrt(np.sum(ir ** 2))
    L = N + irn; F = 1 << (L - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(send[:, ch], F) * np.fft.rfft(ir, F), F)[:N]
    out[:, ch] += wet * 0.35
out *= pump[:, None]
x = out / np.max(np.abs(out)) * 0.95; x = np.tanh(x * 1.15) / np.tanh(1.15)
f = np.ones(N); fn = int(0.6 * SR); f[-fn:] = np.linspace(1, 0, fn); fi = int(0.03 * SR); f[:fi] = np.linspace(0, 1, fi); x *= f[:, None]
x = (x * 0.89 * 32767).astype(np.int16)
w = wave.open('music_v3.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes()); w.close(); print('ok')
