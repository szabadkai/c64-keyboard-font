from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
FONT=ROOT/'fonts/C64Keyboard-Regular.ttf'
def make():
    im=Image.new('RGB',(1800,1540),'#e9e5da');d=ImageDraw.Draw(im)
    ui='/System/Library/Fonts/Helvetica.ttc'
    def f(s):return ImageFont.truetype(str(FONT),s)
    def label(p,t,s=22,col='#59615f'):d.text(p,t,font=ImageFont.truetype(ui,s),fill=col)
    label((100,65),'C64  /  KEYBOARD LETTERING',24)
    label((1430,65),'REGULAR  —  1.109',21)
    d.line((100,113,1700,113),fill='#bcbcaf',width=2)
    d.text((90,153),'PRESS PLAY ON TAPE',font=f(147),fill='#25333c')
    label((100,338),'A geometrically normalized reconstruction of the keycap legends.',28)
    for i,c in enumerate(['#bd5350','#c38249','#cfb258','#709a76','#609ea7']):d.rectangle((100+i*82,400,179+i*82,413),fill=c)
    for row,chars in enumerate(['ABCDEFGHIJKLM','NOPQRSTUVWXYZ','0123456789']):
        for col,c in enumerate(chars):
            x=100+col*123;y=484+row*158
            d.rounded_rectangle((x,y,x+105,y+117),13,fill='#c1bdaf')
            d.rounded_rectangle((x,y,x+105,y+109),13,fill='#f7f4e9')
            d.text((x+52,y+15),c,font=f(85),fill='#25333c',anchor='mt')
    d.text((100,990),'! " # $ % & \' ( ) * + - / : ; < = > ? @ £',font=f(62),fill='#25333c')
    d.text((100,1110),'← ↑ → ↓   \ue010 \ue011 \ue012 \ue013 \ue014 \ue015 \ue016 \ue017 \ue018 \ue019 \ue01a \ue01b',font=f(63),fill='#25333c')
    d.line((100,1260,1700,1260),fill='#bcbcaf',width=2)
    label((100,1305),'NORMALIZED FROM THE PHOTOGRAPHS',20)
    label((100,1355),'Narrow capitals · Slashed zero · Hooked Q · Plain I',25,col='#25333c')
    label((100,1400),'Lowercase input uses uppercase key legends. Accent and utility extensions included.',23)
    im.save(ROOT/'specimen.png')
if __name__=='__main__':make()
