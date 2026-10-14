import numpy as np, wave
SR=44100; T=15.0; N=int(SR*T); B=0.5  # 120 BPM
out=np.zeros((N,2)); rng=np.random.default_rng(3)
def add(sig,t,g=1.0,pan=0.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if i>=N or j<=i: return
    s=sig[:j-i]*g; out[i:j,0]+=s*(1-max(pan,0)); out[i:j,1]+=s*(1+min(pan,0))
def env(n,a,d):
    t=np.arange(n)/SR; return np.minimum(1,t/max(a,1e-4))*np.exp(-t/d)
def onepole(x,c):
    y=np.empty_like(x); s=0.0
    for i in range(len(x)): s+=c*(x[i]-s); y[i]=s
    return y
def hpf(x,c): return x-onepole(x,c)
def kick():
    n=int(.3*SR); t=np.arange(n)/SR
    return np.sin(2*np.pi*np.cumsum(50+70*np.exp(-t/.03))/SR)*np.exp(-t/.12)
def shaker(): n=int(.06*SR); return hpf(rng.standard_normal(n),.5)*env(n,.004,.02)
def snap():
    n=int(.15*SR); return hpf(rng.standard_normal(n),.3)*env(n,.001,.035)*.7
def pluck(f,d=.35):
    n=int(d*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*2*f*t)+.1*np.sin(2*np.pi*3*f*t))*env(n,.002,.09)
def pad(fs,d):
    n=int(d*SR); t=np.arange(n)/SR
    x=sum(np.sin(2*np.pi*f*dt*t) for f in fs for dt in (0.996,1.0,1.004))/ (3*len(fs))
    a=np.minimum(1,t/.4)*np.minimum(1,(d-t)/.4); return x*a
def bass(f,d):
    n=int(d*SR); t=np.arange(n)/SR
    return np.sin(2*np.pi*f*t)*env(n,.005,d*.5)
def whoosh(d,rev=False):
    n=int(d*SR); t=np.arange(n)/SR; x=onepole(rng.standard_normal(n),.08)
    e=(t/d)**2 if not rev else (1-t/d)**2
    return x*e*3
def pop(f):
    n=int(.12*SR); t=np.arange(n)/SR
    return np.sin(2*np.pi*np.cumsum(f*(1+1.5*np.exp(-t/.01)))/SR)*env(n,.001,.03)
def click():
    n=int(.05*SR); return hpf(rng.standard_normal(n),.7)*env(n,.0005,.006)*1.2+pop(1400)[:n]*.5
# chords: Cmaj7 - Am7 - Fmaj7 - G  (bright, friendly)
CH=[[261.6,329.6,392,493.9],[220,261.6,329.6,392],[174.6,220,261.6,329.6],[196,246.9,293.7,392]]
BS=[65.4,55,43.65,49]
ARP=lambda c:[c[0]*2,c[1]*2,c[2]*2,c[3]*2,c[2]*2,c[1]*2]
for bar in range(8):   # 2s bars (4 beats)
    t0=bar*2.0; c=CH[bar%4]
    add(pad(c,2.05),t0,.22)
    if t0>=3.0 or bar>=1:
        for k,f in enumerate(ARP(c)+ARP(c)[:2]):
            add(pluck(f),t0+k*0.25,.13,.35*(-1)**k)
    if t0>=2.0:
        add(bass(BS[bar%4],.9),t0,.35); add(bass(BS[bar%4],.4),t0+1.5,.25)
        for b in range(4):
            add(kick(),t0+b*B,.45)
            add(shaker(),t0+b*B+.25,.18,.3)
            add(shaker(),t0+b*B+.125,.08,-.3); add(shaker(),t0+b*B+.375,.08,-.3)
            if b%2==1: add(snap(),t0+b*B,.35)
# --- v2 cue sheet ---
def key():
    n=int(.035*SR); return hpf(rng.standard_normal(n),.6)*env(n,.0005,.006)*.9+pop(2200)[:n]*.25
for c in (3.2, 7.0, 11.6): add(whoosh(.55),c-.5,.28)
for i in range(9): add(key(),1.7+i*.075,.45,(-1)**i*.2)          # search bar typing
seg=(3.8-.3)/5
for i in range(5): add(whoosh(.35),3.2+i*seg-.1,.14,(-1)**i*.4); add(pop(760+i*110),3.2+i*seg+.35,.25,(-1)**i*.3)
add(pop(1050),7.05,.35)                                          # centre disc
for i in range(5): add(pop(900+i*90),7.0+.2+i*.12+.25,.18,(-1)**i*.4)
for i in range(19): add(key(),7.0+2.24+i*.06,.35,(-1)**i*.2)     # highlight typing
for i in range(19): add(key(),11.6+1.45+i*.05,.35,(-1)**i*.2)    # URL typing
add(click(),11.6+2.85,.7)
add(pad([523.2,659.3,784],1.0),14.0,.15)
x=out/np.max(np.abs(out))*.95; x=np.tanh(x*1.2)/np.tanh(1.2)
f=np.ones(N); fn=int(.5*SR); f[-fn:]=np.linspace(1,0,fn); fi=int(.05*SR); f[:fi]=np.linspace(0,1,fi); x*=f[:,None]
x=(x*.89*32767).astype(np.int16)
w=wave.open('music_v2.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes()); w.close(); print('ok')
