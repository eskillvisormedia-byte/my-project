# Photo-real drawing hand: cut out from a photo on white, with its soft contact shadow kept and the
# forearm extended past the photo's edge so it always runs off the bottom-right of the frame.
import os
import cv2
import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
SCALE = 1.1
PAD = 300            # the marker tip sits at (PAD, PAD) in the output image
ARM_DIR = np.array([0.44, 0.90])   # forearm direction in the photo (towards bottom-right)


def build():
    bgr = cv2.imread(os.path.join(HERE, 'hand_photo.png')).astype(np.float32)
    obj = cv2.imread(os.path.join(HERE, 'hand_alpha.png'), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    h, w = obj.shape
    # tip = the hand pixel furthest along the marker towards the upper-left
    ys, xs = np.nonzero(obj > 0.5)
    d = np.array([0.78, 0.63])
    i = np.argmin(xs * d[0] + ys * d[1])
    tip = np.array([xs[i], ys[i]], np.float32)
    # contact shadow from the photo: darkness of the background outside the hand
    lum = bgr.mean(axis=2)
    shadow = np.clip((250 - lum) / 250 * 1.4, 0, 0.35) * (1 - obj)
    rgb = bgr[..., ::-1] * obj[..., None]          # black under the shadow, photo under the hand
    alpha = obj + shadow
    # extend the forearm: pixels beyond the right/bottom edge sample back along the arm direction
    W = H = int(PAD + max(w, h) * 2.2)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sx = (xx - PAD) + tip[0]
    sy = (yy - PAD) + tip[1]
    lim = w - 12.0
    t = np.maximum(np.maximum((sx - lim) / ARM_DIR[0], (sy - lim) / ARM_DIR[1]), 0)
    # mirror-repeat the last stretch of forearm so the skin texture continues without smearing
    L = 160.0
    m = np.mod(t, 2 * L)
    m = np.where(m > L, 2 * L - m, m)
    m = np.where(t > 0, m, 0)
    sx -= t * ARM_DIR[0] + m * ARM_DIR[0]
    sy -= t * ARM_DIR[1] + m * ARM_DIR[1]
    valid = (sx >= 0) & (sy >= 0)
    big = np.dstack([rgb, alpha * 255]).astype(np.float32)
    out = cv2.remap(big, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    out[~valid] = 0
    out = cv2.resize(out, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_AREA)
    # (PAD scaled) -> crop so the tip lands at PAD again
    off = int(round(PAD * SCALE)) - PAD
    out = out[off:, off:]
    a = out[..., 3:4] / 255
    premul = np.dstack([out[..., :3] * 1.0, out[..., 3]]).clip(0, 255).astype(np.uint8)
    img = skia.Image.fromarray(np.ascontiguousarray(premul), colorType=skia.kRGBA_8888_ColorType,
                               alphaType=skia.kPremul_AlphaType)
    return img


if __name__ == '__main__':
    im = build()
    s = skia.Surface(1080, 1920); c = s.getCanvas(); c.clear(0xFFF0EFEB)
    c.drawImage(im, 300 - PAD, 400 - PAD)
    c.drawCircle(300, 400, 4, skia.Paint(Color=0xFFFF0000))
    s.makeImageSnapshot().save(os.path.join(HERE, 'realhand_prev.png'))
