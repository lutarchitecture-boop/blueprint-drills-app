#!/usr/bin/env python3
"""Generate the Coffee Agent app icon and splash source images, built from
the real brand-kit logo mark (extracted from Main Logo.png) on the new
Deep Forest / Antique Brass / Warm Parchment palette."""
import math
import numpy as np
from PIL import Image, ImageDraw

def lerp(a, b, t):
    return a + (b - a) * t

def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

ACCENT = hex_rgb('#173D32')   # Deep Forest
ACCENT2 = hex_rgb('#B28A4A')  # Antique Brass
BG = hex_rgb('#F4EFE3')       # Warm Parchment
BLOB1 = hex_rgb('#DCE8DF')    # Evidence Sage
BLOB2 = hex_rgb('#F3E0C2')    # light brass tint
BLOB3 = hex_rgb('#E3D9C8')    # warm neutral
MARK_COLOR = hex_rgb('#252B28')  # Archive Charcoal

LOGO_SRC = '/mnt/user-data/uploads/Coffe Agent Brand ID-20261016T234231Z-1-001/Coffe Agent Brand ID/6. Main Logo.png'

def extract_mark():
    """Pull just the icon mark (not the wordmark) from the brand-kit logo,
    as a tightly-cropped transparent-background RGBA image recolored to
    Archive Charcoal."""
    img = Image.open(LOGO_SRC).convert('RGB')
    arr = np.array(img)
    lum = arr[:, :, :3].mean(axis=2)
    dark = lum < 120
    dark[:, 440:] = False
    ys, xs = np.where(dark)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pad = 10
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(img.width, x1 + pad), min(img.height, y1 + pad)
    crop = img.crop((x0, y0, x1, y1))
    carr = np.array(crop)
    clum = carr[:, :, :3].mean(axis=2)
    alpha = np.clip((120 - clum) * 4, 0, 255).astype('uint8')
    out = np.zeros((carr.shape[0], carr.shape[1], 4), dtype='uint8')
    out[:, :, 0] = MARK_COLOR[0]
    out[:, :, 1] = MARK_COLOR[1]
    out[:, :, 2] = MARK_COLOR[2]
    out[:, :, 3] = alpha
    return Image.fromarray(out, 'RGBA')

MARK = extract_mark()

def diagonal_gradient(size, c1, c2):
    w, h = size
    img = Image.new('RGB', size)
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = (x / w + y / h) / 2
            r = int(lerp(c1[0], c2[0], t))
            g = int(lerp(c1[1], c2[1], t))
            b = int(lerp(c1[2], c2[2], t))
            px[x, y] = (r, g, b)
    return img

def rounded_mask(size, radius_ratio):
    w, h = size
    mask = Image.new('L', size, 0)
    d = ImageDraw.Draw(mask)
    r = int(min(w, h) * radius_ratio)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return mask

def paste_mark(canvas, box_size, scale=0.52):
    """Paste the brand mark, centered, scaled to `scale` of box_size, preserving aspect ratio."""
    mw, mh = MARK.size
    target_w = int(box_size * scale)
    target_h = int(target_w * mh / mw)
    if target_h > box_size * scale:
        target_h = int(box_size * scale)
        target_w = int(target_h * mw / mh)
    resized = MARK.resize((target_w, target_h), Image.LANCZOS)
    x = (canvas.width - target_w) // 2
    y = (canvas.height - target_h) // 2
    canvas.alpha_composite(resized, (x, y))

def make_icon(path, size=1024, rounded=True):
    grad = diagonal_gradient((size, size), BG, BLOB2)
    if rounded:
        mask = rounded_mask((size, size), 0.225)
        out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        out.paste(grad, (0, 0), mask)
    else:
        out = grad.convert('RGBA')
    paste_mark(out, size, scale=0.56)
    out.save(path)
    print('wrote', path, out.size)

def make_adaptive_foreground(path, size=1024):
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    paste_mark(out, size, scale=0.40)
    out.save(path)
    print('wrote', path, out.size)

def make_adaptive_background(path, size=1024):
    grad = diagonal_gradient((size, size), BG, BLOB2).convert('RGBA')
    grad.save(path)
    print('wrote', path, grad.size)

def make_icon_inmemory(size):
    grad = diagonal_gradient((size, size), BG, BLOB2)
    mask = rounded_mask((size, size), 0.225)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(grad, (0, 0), mask)
    paste_mark(out, size, scale=0.56)
    return out

def make_splash(path, size=(2732, 2732)):
    w, h = size
    img = Image.new('RGB', size, BG)

    def blend_radial(img, cx, cy, radius, color, strength=0.55):
        px = img.load()
        x0 = max(0, int(cx - radius))
        x1 = min(w, int(cx + radius))
        y0 = max(0, int(cy - radius))
        y1 = min(h, int(cy + radius))
        for y in range(y0, y1):
            for x in range(x0, x1, 2):
                d = math.hypot(x - cx, y - cy) / radius
                if d >= 1:
                    continue
                t = (1 - d) * strength
                r, g, b = px[x, y]
                nr = int(lerp(r, color[0], t))
                ng = int(lerp(g, color[1], t))
                nb = int(lerp(b, color[2], t))
                px[x, y] = (nr, ng, nb)
                if x + 1 < x1:
                    px[x + 1, y] = (nr, ng, nb)
        return img

    img = blend_radial(img, w * 0.12, h * 0.08, w * 0.34, BLOB1)
    img = blend_radial(img, w * 0.92, h * 0.18, w * 0.30, BLOB2)
    img = blend_radial(img, w * 0.85, h * 0.92, w * 0.36, BLOB3)

    icon_size = int(w * 0.34)
    icon = make_icon_inmemory(icon_size)
    img = img.convert('RGBA')
    img.alpha_composite(icon, (int(w / 2 - icon_size / 2), int(h / 2 - icon_size / 2)))
    img.convert('RGB').save(path)
    print('wrote', path, img.size)

if __name__ == '__main__':
    make_icon('icon.png', 1024, rounded=True)
    make_adaptive_foreground('icon-foreground.png', 1024)
    make_adaptive_background('icon-background.png', 1024)
    make_splash('splash.png', (2732, 2732))
