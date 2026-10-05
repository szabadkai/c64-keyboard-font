"""Render reproducible before/after comparisons from saved SVG sources."""
from pathlib import Path
from io import BytesIO
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
from fontTools.fontBuilder import FontBuilder
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
ROOT=Path(__file__).resolve().parents[1]
ROWS=['HNEFMOWQ','01234589','AVXYZCGS']
def preview_font(directory,size):
    fb=FontBuilder(1000,isTTF=True);chars=sorted(set(''.join(ROWS)));names={c:f'uni{ord(c):04X}' for c in chars}
    fb.setupGlyphOrder(['.notdef']+list(names.values()));fb.setupCharacterMap({ord(c):n for c,n in names.items()});glyphs={'.notdef':TTGlyphPen(None).glyph()};metrics={'.notdef':(900,0)}
    for c,name in names.items():
        root=ET.parse(directory/f'{ord(c):04X}.svg').getroot();r=RecordingPen();parse_path(root.find('{http://www.w3.org/2000/svg}path').attrib['d'],r)
        bp=BoundsPen(None);r.replay(bp);x0,_,x1,_=bp.bounds;left=(900-(x1-x0))/2
        pen=TTGlyphPen(None);r.replay(TransformPen(Cu2QuPen(pen,.5,reverse_direction=True),(1,0,0,1,left-x0,0)));glyphs[name]=pen.glyph();metrics[name]=(900,round(left))
    fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(metrics);fb.setupHorizontalHeader(ascent=900,descent=-200);fb.setupNameTable({'familyName':'Outline comparison','styleName':'Regular'});fb.setupOS2();fb.setupPost();fb.setupMaxp();buf=BytesIO();fb.save(buf);buf.seek(0)
    return ImageFont.truetype(buf,size)
def main():
    old=preview_font(ROOT/'glyphs/traced',170);new=preview_font(ROOT/'glyphs',170)
    im=Image.new('RGB',(1800,1510),'#e9e5da');d=ImageDraw.Draw(im)
    ui='/System/Library/Fonts/Helvetica.ttc'
    def label(x,y,text,size=23,color='#25333c'):d.text((x,y),text,font=ImageFont.truetype(ui,size),fill=color)
    label(80,55,'C64 KEYBOARD / GEOMETRIC NORMALIZATION',28)
    label(80,105,'The original photographic traces and the corrected outlines, at the same cap height.',24,'#66706e')
    for row,chars in enumerate(ROWS):
        top=210+row*385
        for k,(font,title,color) in enumerate([(old,'PHOTO TRACE','#8f756a'),(new,'NORMALIZED','#25333c')]):
            baseline=top+125+k*175
            label(80,baseline-100,title,17,color)
            for col,c in enumerate(chars):
                x=305+col*177
                d.line((x-70,baseline,x+70,baseline),fill='#b9bdb4')
                d.line((x-70,baseline-119,x+70,baseline-119),fill='#c9cdc3')
                d.text((x,baseline),c,font=font,fill=color,anchor='ms')
        d.line((80,top+325,1720,top+325),fill='#c1c2b7')
    label(80,1380,'700-unit cap height  /  88-unit vertical stems  /  80-unit horizontal bars',25)
    label(80,1430,'Parallel stems, level bars, regularized bowls, paired symbols, and preserved distinctive details.',22,'#66706e')
    im.save(ROOT/'normalization-comparison.png')
if __name__=='__main__':main()
