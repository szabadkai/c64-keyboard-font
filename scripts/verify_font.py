"""Validate coverage, outline bounds, and desktop rendering of the delivered fonts."""
from pathlib import Path
from io import BytesIO
import json
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
reports=[]
for ext in ['ttf','otf','woff2']:
    path=ROOT/'fonts'/f'C64Keyboard-Regular.{ext}'
    font=TTFont(path,checkChecksums=2);cmap=font.getBestCmap()
    assert font['OS/2'].fsType==0,(ext,'embedding flag conflicts with CC0')
    assert 'CC0 1.0 Universal' in font['name'].getDebugName(13),(ext,'license metadata missing')
    assert font['name'].getDebugName(14)=='https://creativecommons.org/publicdomain/zero/1.0/',(ext,'license URL missing')
    assert 0xE000 not in cmap,(ext,'removed logo glyph is still mapped')
    assert 'uniE000' not in font.getGlyphOrder(),(ext,'removed logo glyph is still present')
    assert set(range(32,127))<=set(cmap),'Printable ASCII coverage incomplete'
    for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':assert cmap[ord(c)]==cmap[ord(c.lower())]
    widths={font['hmtx'][cmap[ord(c)]][0] for c in '0123456789'};assert len(widths)==1
    glyphs=font.getGlyphSet();empty=[];contours=0
    for name in font.getGlyphOrder():
        pen=BoundsPen(glyphs);glyphs[name].draw(pen)
        if pen.bounds is None:empty.append(name);continue
        x0,y0,x1,y1=pen.bounds
        assert y0>=-220 and y1<=1000,(ext,name,pen.bounds)
        assert x0>=-1 and x1<=font['hmtx'][name][0]+1,(ext,name,pen.bounds)
    assert empty==['space'],(ext,empty)
    # Every function-key label is one mapped glyph at the same optical size.
    function_codes=list(range(0xE010,0xE01C))
    assert all(cp in cmap for cp in function_codes)
    assert len({cmap[cp] for cp in function_codes})==12
    petscii=json.loads((ROOT/'glyphs/petscii-map.json').read_text())['symbols']
    assert len(petscii)==63
    assert {e['screen_code'] for e in petscii}==set(range(64,128))-{96}
    for entry in petscii:
        cp=int(entry['font_codepoint'][2:],16)
        assert cp in cmap,(ext,entry['keyboard'])
        assert font['hmtx'][cmap[cp]][0]==830
        pen=BoundsPen(glyphs);glyphs[cmap[cp]].draw(pen)
        if entry['framed']:assert pen.bounds==(65,0,765,700),(ext,entry,pen.bounds)
    for cp in function_codes:
        pen=BoundsPen(glyphs);glyphs[cmap[cp]].draw(pen)
        assert abs(pen.bounds[1])<1 and abs(pen.bounds[3]-455)<1,(ext,cp,pen.bounds)
    widest_single=max(font['hmtx'][cmap[cp]][0] for cp in range(0xE010,0xE019))
    assert all(font['hmtx'][cmap[cp]][0]>widest_single for cp in range(0xE019,0xE01C))
    assert font['OS/2'].version>=4
    # Round-trip every table, including WOFF2 decompression.
    stream=BytesIO();font.flavor=None;font.save(stream);stream.seek(0);TTFont(stream)
    reports.append(dict(format=ext,glyphs=len(font.getGlyphOrder()),mapped_characters=len(cmap),bytes=path.stat().st_size))
for ext in ['ttf','otf']:
    f=ImageFont.truetype(str(ROOT/'fonts'/f'C64Keyboard-Regular.{ext}'),64)
    for text in ['ABCDEFGHIJKLMNOPQRSTUVWXYZ','0123456789','LOAD "*",8,1','ÁÉÍÓÖŐÚÜŰ','\ue010\ue021','\ue018\ue019\ue01a\ue01b']:
        assert f.getmask(text).getbbox(),(ext,text)
# Render all unique mappings at useful viewing size for a final visual review.
font=TTFont(ROOT/'fonts/C64Keyboard-Regular.ttf');cmap=font.getBestCmap()
chars=[];seen=set()
for cp,name in sorted(cmap.items()):
    if name in seen or cp==32:continue
    seen.add(name);chars.append(chr(cp))
im=Image.new('RGB',(1440,((len(chars)+9)//10)*142),'#f6f3e9');d=ImageDraw.Draw(im)
f=ImageFont.truetype(str(ROOT/'fonts/C64Keyboard-Regular.ttf'),72)
ui=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',13)
for i,ch in enumerate(chars):
    x=i%10*144;y=i//10*142
    d.text((x+72,y+10),ch,font=f,fill='#25333c',anchor='mt')
    d.text((x+72,y+115),f'U+{ord(ch):04X}',font=ui,fill='#66706e',anchor='mt')
(ROOT/'build').mkdir(exist_ok=True);im.save(ROOT/'build/all-glyphs.png')
(ROOT/'build/validation.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
