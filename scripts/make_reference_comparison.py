"""Compare saved LSZ photo traces with the current geometric outlines."""
from PIL import Image, ImageDraw, ImageFont
import make_comparison

ROOT=make_comparison.ROOT
CHARS='CG9£\ue000\ue001'

def main():
    make_comparison.ROWS=[CHARS]
    traced=make_comparison.preview_font(ROOT/'glyphs/high-resolution',250)
    normalized=make_comparison.preview_font(ROOT/'glyphs',250)
    image=Image.new('RGB',(1800,730),'#e9e5da')
    draw=ImageDraw.Draw(image)
    def label(x,y,text,size=23,color='#25333c'):
        draw.text((x,y),text,font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',size),fill=color)
    label(65,40,'C64 KEYBOARD / NEW CAMERA REFERENCES',30)
    label(65,91,'Saved photo traces compared with the updated geometric outlines at the same scale.',24,'#66706e')
    for row,(font,title,color) in enumerate([(traced,'NEW TRACE','#8f756a'),(normalized,'UPDATED','#25333c')]):
        baseline=345+row*265
        label(65,baseline-110,title,20,color)
        for i,c in enumerate(CHARS):
            x=370+i*250
            draw.line((x-100,baseline,x+100,baseline),fill='#b9bdb4')
            draw.text((x,baseline),c,font=font,fill=color,anchor='ms')
            if row==0:
                label(x-90,baseline-220,['C','G','9','Pound','Commodore','Function f'][i],22)
    label(65,672,'Photo traces retain print wear and perspective. Geometric outlines use explicit design assumptions.',22,'#66706e')
    image.save(ROOT/'latest-reference-comparison.png')

if __name__=='__main__':main()
