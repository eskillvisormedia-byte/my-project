# Soft, warm background bed: slow piano-like arpeggios over a gentle pad. Synthesized, no samples.
import numpy as np, sys, wave
SR = 48000; DUR = 95.0
N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.default_rng(3)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
bpm = 72; beat = 60 / bpm; bar = 4 * beat
chords = [[48, 55, 60, 64], [43, 55, 59, 62], [45, 57, 60, 64], [41, 53, 57, 60]]  # C G Am F
L = np.zeros(N); R = np.zeros(N)
def note(start, m, dur, amp, pan):
    i0 = int(start * SR); n = min(int(dur * SR), N - i0)
    if n <= 0: return
    tt = np.arange(n) / SR; f = hz(m)
    env = (1 - np.exp(-tt / 0.008)) * np.exp(-tt / (0.9 + 0.4 * (60 - m) / 24))
    s = sum(a * np.sin(2 * np.pi * f * k * tt) for k, a in [(1, 1), (2, 0.35), (3, 0.12), (4, 0.05)])
    s *= env * amp
    L[i0:i0 + n] += s * (1 - pan); R[i0:i0 + n] += s * pan
nb = int(DUR / bar) + 1
for b in range(nb):
    ch = chords[b % 4]; t0 = b * bar
    # pad
    i0 = int(t0 * SR); n = min(int(bar * 1.15 * SR), N - i0)
    if n > 0:
        tt = np.arange(n) / SR
        env = np.minimum(1, tt / 1.2) * np.minimum(1, (bar * 1.15 - tt) / 0.8).clip(0, 1)
        pad = sum(np.sin(2 * np.pi * hz(m) * tt) + 0.5 * np.sin(2 * np.pi * hz(m) * 1.003 * tt) for m in ch[1:])
        L[i0:i0 + n] += pad * env * 0.035; R[i0:i0 + n] += pad * env * 0.035
    note(t0, ch[0] - 12, bar, 0.22, 0.5)
    pattern = [ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[2] + 12, ch[1] + 12, ch[3] + 12, ch[2] + 12, ch[3] + 12]
    for k, m in enumerate(pattern):
        if b % 8 == 7 and k > 3: break
        note(t0 + k * beat / 2, m, 1.6, 0.11 * (0.85 + 0.3 * rng.random()), 0.35 + 0.3 * (k % 2))
# simple reverb
ir_n = int(2.2 * SR); ir = rng.normal(0, 1, ir_n) * np.exp(-np.arange(ir_n) / SR / 0.55); ir /= np.sqrt((ir ** 2).sum())
from numpy.fft import rfft, irfft
def conv(x):
    m = len(x) + ir_n; nf = 1 << (m - 1).bit_length()
    return irfft(rfft(x, nf) * rfft(ir, nf), nf)[:len(x)]
L = 0.75 * L + 0.35 * conv(L); R = 0.75 * R + 0.35 * conv(R)
fade = np.minimum(1, t / 2.0) * np.minimum(1, (DUR - t) / 3.5).clip(0, 1)
L *= fade; R *= fade
st = np.stack([L, R], 1)
rms = np.sqrt((st ** 2).mean()); st *= 10 ** (-27 / 20) / rms   # soft: about -27 dBFS RMS
st = np.clip(st, -0.9, 0.9)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
