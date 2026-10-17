#!/usr/bin/env python3
"""Generate the Play Store feature graphic (1024x500) for Coffee Agent,
using the real brand-kit logo mark and the new palette/typography."""
import sys
sys.path.insert(0, '.')
from make_icons import MARK, diagonal_gradient, hex_rgb
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 500
BG = hex_rgb('#F4EFE3')      # Warm Parchment
BG2 = hex_rgb('#DCE8DF')     # Evidence Sage
INK = hex_rgb('#252B28')     # Archive Charcoal
ACCENT2 = hex_rgb('#B28A4A') # Antique Brass

# Background: diagonal gradient, parchment to sage tint
bg = diagonal_gradient((W, H), BG, BG2).convert('RGBA')
img = bg

# Logo mark on the left
mark_h = 260
mw, mh = MARK.size
mark_w = int(mark_h * mw / mh)
mark_resized = MARK.resize((mark_w, mark_h), Image.LANCZOS)
mark_x = 72
mark_y = (H - mark_h) // 2
img.alpha_composite(mark_resized, (mark_x, mark_y))

# Thin brass accent rule under the mark
draw = ImageDraw.Draw(img)
rule_y = mark_y + mark_h + 22
draw.rectangle([mark_x, rule_y, mark_x + mark_w - 1, rule_y + 4], fill=ACCENT2)

# Title + tagline to the right of the mark
text_x = mark_x + mark_w + 56
title_font = ImageFont.truetype('/tmp/fredoka-700.ttf', 92)
tagline_font = ImageFont.truetype('/tmp/funnel-display-500.ttf', 34)

title = "Coffee Agent"
tagline = "PPCE exam practice, fueled by coffee"

# Vertically center the title+tagline block
title_bbox = draw.textbbox((0, 0), title, font=title_font)
tagline_bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
title_h = title_bbox[3] - title_bbox[1]
tagline_h = tagline_bbox[3] - tagline_bbox[1]
gap = 22
block_h = title_h + gap + tagline_h
block_y = (H - block_h) // 2 - title_bbox[1]

draw.text((text_x, block_y), title, font=title_font, fill=INK)
tagline_y = block_y + title_h + gap - title_bbox[1] + tagline_bbox[1] * 0 - tagline_bbox[1]
draw.text((text_x, block_y + title_h + gap), tagline, font=tagline_font, fill=INK)

img.convert('RGB').save('feature_graphic.png')
print('wrote feature_graphic.png', img.size)
