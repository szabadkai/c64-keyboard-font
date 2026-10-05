"""Render local photo/current-font comparisons from the additional references.

Requires the privately held JPEGs in source/better. Output stays in build/;
neither original photos nor photographic crops are packaged for publication.
"""
from pathlib import Path
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]

def main():
    review = json.loads((ROOT/'glyphs/reference-review.json').read_text())
    rows = review['observations']
    out = ROOT/'build/better'
    out.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGB', (1500, 1170), '#e9e5da')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(ROOT/'fonts/C64Keyboard-Regular.ttf'), 250)
    ui = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 22)
    draw.text((25, 20), 'SHARPER REFERENCES / C64 KEYBOARD 1.105', font=ui, fill='#25333c')
    draw.text((25, 55), 'Photo above, font below. Equal ink height; photographic perspective remains.', font=ui, fill='#66706e')
    for i, item in enumerate(rows):
        ch = item['character']
        with Image.open(ROOT/review['source_directory']/item['photo']) as original:
            sx = original.width/review['crop_coordinate_size'][0]
            sy = original.height/review['crop_coordinate_size'][1]
            box = tuple(round(v * (sx if k % 2 == 0 else sy)) for k, v in enumerate(item['crop']))
            photo = original.crop(box).rotate(item['rotation'], expand=True)
        # Isolate the largest connected ink component only to find the crop.
        # Keep original photo pixels: thresholding never becomes font geometry.
        mask = (np.array(photo.convert('L')) < 80).astype('uint8') * 255
        count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
        if count <= 1:
            raise ValueError(f'No ink found for {ch!r}')
        component = 1 + stats[1:, cv2.CC_STAT_AREA].argmax()
        x, y, w, h = stats[component, :4]
        photo = photo.crop((x, y, x+w, y+h)).resize((round(w*175/h), 175))
        x0, y0 = i % 5 * 300 + 25, i // 5 * 510 + 115
        draw.text((x0, y0), ch if ch != '\ue001' else 'Function f', font=ui, fill='#25333c')
        sheet.paste(photo, (x0, y0+45))
        draw.text((x0-16, y0+410), ch, font=font, fill='#25333c', anchor='ls')
        draw.text((x0, y0+435), item['photo'], font=ui, fill='#66706e')
        draw.text((x0, y0+463), item['action'], font=ui, fill='#66706e')
    sheet.save(out/'reference-review.png')
    print(out/'reference-review.png')

if __name__ == '__main__':
    main()
