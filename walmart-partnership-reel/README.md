# ESkillVisor Walmart partnership reel (sketch style, 1080x1920, 1:35)

Marker-on-paper whiteboard animation with an illustrated drawing hand. Everything is drawn in code with skia-python.

- `build/scenes.py`: the 10 scenes, their time windows (matched to the script) and on-screen text/icons
- `build/engine.py`: text/stroke reveal, pen and hand motion, paper background
- `build/icons.py`: minimal line icons; `build/hand.py`: the hand holding the marker
- `build/music.py`: synthesized soft background music

Render:

    pip install skia-python numpy pillow   # skia needs libegl1 (apt)
    cd build
    python3 render.py stills OUTDIR 12 47 90    # preview frames at given seconds
    python3 render.py video silent.mp4
    python3 music.py music.wav
    ffmpeg -i silent.mp4 -i music.wav -filter:a volume=-5dB -c:v copy -c:a aac -shortest out.mp4

To sync to a recorded voiceover, change the `Scene(t0, t1, ...)` windows in `scenes.py` to the line timings;
drawing speed inside each scene adapts to its window.
Fonts: Patrick Hand / Patrick Hand SC (SIL Open Font License).
