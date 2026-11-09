"""Fig. 7 -- six real crops. The image carries pixels only: every label and reading is set as
Word text in the table beneath the figure (see build/assemble.py), so nothing is typeset inside
a bitmap. Each crop is shown at its native pixel grid (nearest-neighbour), centred on a common
3:2 canvas so the six panels align."""
import os
from PIL import Image, ImageDraw
from gallery_cases import CASES

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROPS = os.path.join(REPO, 'data', 'crops')
OUT = os.path.join(REPO, 'figures', 'png')
CW, CH, PAD = 600, 400, 36

for k, (cond, idx, why, lab) in enumerate(CASES):
    im = Image.open(os.path.join(CROPS, f'FE41p2_{cond}_{idx:02d}.png')).convert('RGB')
    s = min((CW - 2 * PAD) / im.width, (CH - 2 * PAD) / im.height)
    s = max(1, int(s))                      # integer scale keeps the native pixel grid
    big = im.resize((im.width * s, im.height * s), Image.NEAREST)
    canvas = Image.new('RGB', (CW, CH), (255, 255, 255))
    canvas.paste(big, ((CW - big.width) // 2, (CH - big.height) // 2))
    ImageDraw.Draw(canvas).rectangle([0, 0, CW - 1, CH - 1], outline=(150, 150, 150), width=2)
    p = os.path.join(OUT, f'fig07_crop_{"abcdef"[k]}.png')
    canvas.save(p)
    print('wrote', p, f'scale {s}')
