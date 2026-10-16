#!/usr/bin/env python3
"""Build www/index.html for the native (offline) app: swap Google Fonts CDN
links for locally-bundled @font-face declarations, inject question data,
and wrap in a full standalone HTML document."""
import json

TEMPLATE = 'source/app_template.html'
QUESTIONS = 'source/questions_master.json'
ORAL = 'source/oral_practice.json'
OUT = 'www/index.html'

FONT_FACES = """<style>
  @font-face{ font-family:'Baloo 2'; font-style:normal; font-weight:600; font-display:swap; src:url('fonts/baloo-2-latin-600-normal.woff2') format('woff2'); }
  @font-face{ font-family:'Baloo 2'; font-style:normal; font-weight:700; font-display:swap; src:url('fonts/baloo-2-latin-700-normal.woff2') format('woff2'); }
  @font-face{ font-family:'Baloo 2'; font-style:normal; font-weight:800; font-display:swap; src:url('fonts/baloo-2-latin-800-normal.woff2') format('woff2'); }
  @font-face{ font-family:'Plus Jakarta Sans'; font-style:normal; font-weight:400; font-display:swap; src:url('fonts/plus-jakarta-sans-latin-400-normal.woff2') format('woff2'); }
  @font-face{ font-family:'Plus Jakarta Sans'; font-style:normal; font-weight:500; font-display:swap; src:url('fonts/plus-jakarta-sans-latin-500-normal.woff2') format('woff2'); }
  @font-face{ font-family:'Plus Jakarta Sans'; font-style:normal; font-weight:600; font-display:swap; src:url('fonts/plus-jakarta-sans-latin-600-normal.woff2') format('woff2'); }
  @font-face{ font-family:'Plus Jakarta Sans'; font-style:normal; font-weight:700; font-display:swap; src:url('fonts/plus-jakarta-sans-latin-700-normal.woff2') format('woff2'); }
  @font-face{ font-family:'Space Mono'; font-style:normal; font-weight:400; font-display:swap; src:url('fonts/space-mono-latin-400-normal.woff2') format('woff2'); }
  @font-face{ font-family:'Space Mono'; font-style:normal; font-weight:700; font-display:swap; src:url('fonts/space-mono-latin-700-normal.woff2') format('woff2'); }
</style>
"""

tpl = open(TEMPLATE, encoding='utf-8').read()

# Strip the three Google-Fonts related lines (preconnects + stylesheet link), replace with local @font-face
lines = tpl.split('\n')
kept = []
skipped = 0
for line in lines:
    if 'fonts.googleapis.com' in line or 'fonts.gstatic.com' in line:
        skipped += 1
        continue
    kept.append(line)
assert skipped == 3, f'expected to strip 3 google-fonts lines, stripped {skipped}'
tpl = '\n'.join(kept)
tpl = tpl.replace('<style>', FONT_FACES + '<style>', 1)

data = json.load(open(QUESTIONS))
payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
assert '__QUESTIONS_JSON__' in tpl
tpl = tpl.replace('__QUESTIONS_JSON__', payload)

oral_data = json.load(open(ORAL))
oral_payload = json.dumps(oral_data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
assert '__ORAL_JSON__' in tpl
tpl = tpl.replace('__ORAL_JSON__', oral_payload)

doc = (
    '<!doctype html>\n<html lang="en">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '</head>\n<body>\n' + tpl + '\n</body>\n</html>\n'
)
open(OUT, 'w', encoding='utf-8').write(doc)
print('wrote', OUT, len(doc.encode('utf-8')), 'bytes')
