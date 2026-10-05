#!/usr/bin/env python3
"""Generate the Blueprint Drills app icon and splash source images."""
import math
from PIL import Image, ImageDraw

def lerp(a, b, t):
    return a + (b - a) * t

def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

ACCENT = hex_rgb('#8B5CF6')   # violet
ACCENT2 = hex_rgb('#EC4899')  # pink
BG = hex_rgb('#FBF7FF')
BLOB1 = hex_rgb('#F6D9FF')
BLOB2 = hex_rgb('#D6ECFF')
BLOB3 = hex_rgb('#FFEAD6')

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

def star_points(cx, cy, r_outer, r_inner, points=5, rotation=-90):
    pts = []
    for i in range(points * 2):
        r = r_outer if i % 2 == 0 else r_inner
        angle = math.radians(rotation + i * (360 / (points * 2)))
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts

def make_icon(path, size=1024, rounded=True, pad_ratio=0.0):
    grad = diagonal_gradient((size, size), ACCENT, ACCENT2)
    if rounded:
        mask = rounded_mask((size, size), 0.225)
        out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        out.paste(grad, (0, 0), mask)
    else:
        out = grad.convert('RGBA')

    draw = ImageDraw.Draw(out)
    cx = cy = size / 2
    r_outer = size * 0.30
    r_inner = r_outer * 0.46
    pts = star_points(cx, cy, r_outer, r_inner)
    draw.polygon(pts, fill=(255, 255, 255, 255))
    out.save(path)
    print('wrote', path, out.size)

def make_adaptive_foreground(path, size=1024):
    # Transparent background, star centered within the ~66% safe zone used for adaptive icons
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(out)
    cx = cy = size / 2
    r_outer = size * 0.22
    r_inner = r_outer * 0.46
    pts = star_points(cx, cy, r_outer, r_inner)
    draw.polygon(pts, fill=(255, 255, 255, 255))
    out.save(path)
    print('wrote', path, out.size)

def make_adaptive_background(path, size=1024):
    grad = diagonal_gradient((size, size), ACCENT, ACCENT2).convert('RGBA')
    grad.save(path)
    print('wrote', path, grad.size)

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

    # centered icon card
    icon_size = int(w * 0.34)
    icon = make_icon_inmemory(icon_size)
    img = img.convert('RGBA')
    img.alpha_composite(icon, (int(w / 2 - icon_size / 2), int(h / 2 - icon_size / 2)))
    img.convert('RGB').save(path)
    print('wrote', path, img.size)

def make_icon_inmemory(size):
    grad = diagonal_gradient((size, size), ACCENT, ACCENT2)
    mask = rounded_mask((size, size), 0.225)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(grad, (0, 0), mask)
    draw = ImageDraw.Draw(out)
    cx = cy = size / 2
    r_outer = size * 0.30
    r_inner = r_outer * 0.46
    pts = star_points(cx, cy, r_outer, r_inner)
    draw.polygon(pts, fill=(255, 255, 255, 255))
    return out

if __name__ == '__main__':
    make_icon('icon.png', 1024, rounded=True)
    make_adaptive_foreground('icon-foreground.png', 1024)
    make_adaptive_background('icon-background.png', 1024)
    make_splash('splash.png', (2732, 2732))
