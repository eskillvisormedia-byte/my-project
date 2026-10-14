# Walmart categories: 15s SaaS motion video

- 1080x1920 (9:16), 30 fps, 15 s
- Colours: orange `#FF6A00`, orange tint `#FFF1E7`, text `#111111`, white `#FFFFFF`
- Fonts: Inter 700 / 900
- Built with Higgsfield's `higgsedit` motion-graphics CLI (`edit.jsx`)
- Music: original synthesized bed (`music.py`), muxed with ffmpeg

## Timeline
| Time | Scene |
|---|---|
| 0.0–3.0 | Hook: WALMART ISN'T JUST ABOUT GROCERIES |
| 3.0–6.5 | Category cards slide in (Electronics, Beauty, Home, Fashion, Health & Wellness) |
| 6.5–11.6 | Cards glide into a hub around a centre circle (cart icon, which is where the logo goes), plus body copy |
| 11.6–15.0 | CTA: SEE WHERE YOUR PRODUCT COULD FIT, button www.eskillvisor.com, cursor click |

## Rebuild
```bash
higgsedit fonts add . "Inter:700" && higgsedit fonts add . "Inter:900"
python3 music.py
RENDER=1 higgsedit build edit.jsx            # LOGO=path/to/logo.png to put a logo in the hub
ffmpeg -i renders/wm.mp4 -i music.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest final.mp4
```
