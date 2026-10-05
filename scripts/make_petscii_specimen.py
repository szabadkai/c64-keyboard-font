"""Render the reconstructed front legends by physical key, with PETSCII bytes."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
entries=json.loads((ROOT/'glyphs/petscii-map.json').read_text())['symbols']
keys=list('QWERTYUIOPASDFGHJKLZXCVBNM')+list('+-£@*↑')
im=Image.new('RGB',(1520,1180),'#e9e5da');d=ImageDraw.Draw(im)
ui=lambda size:ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',size)
font=lambda size:ImageFont.truetype(str(ROOT/'fonts/C64Keyboard-Regular.ttf'),size)
d.text((42,32),'C64 / PETSCII KEY-FRONT LEGENDS',font=ui(28),fill='#25333c')
d.text((42,77),'Left: Commodore + key     Right: Shift + key     Codes below are PETSCII hexadecimal bytes.',font=ui(20),fill='#66706e')
for i,key in enumerate(keys):
 x=40+(i%8)*180;y=132+(i//8)*240
 d.rounded_rectangle((x,y,x+164,y+215),radius=10,fill='#25333c')
 d.text((x+82,y+12),key,font=font(52),fill='#eee9d8',anchor='mt')
 for side,xx in [('left',x+8),('right',x+87)]:
  e=next((e for e in entries if e['key']==key and e['position']==side),None)
  if not e:continue
  ch=chr(int(e['font_codepoint'][2:],16))
  d.text((xx,y+149),ch,font=font(84),fill='#eee9d8',anchor='ls')
  d.text((xx+35,y+173),e['petscii_hex'],font=ui(17),fill='#b6c1b9',anchor='mt')
d.text((42,1117),'63 smooth vector legends. Symbol identities are documented; print weights and proportions are reconstructed.',font=ui(19),fill='#66706e')
d.text((42,1148),'Uppercase / graphics mode. The pi legend also works with Commodore + up-arrow.',font=ui(17),fill='#66706e')
im.save(ROOT/'petscii-specimen.png')
print('Rendered petscii-specimen.png')
