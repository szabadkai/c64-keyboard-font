"""Extract key legends, suppress surface texture, and trace editable SVG outlines."""
from pathlib import Path
import json, subprocess, xml.etree.ElementTree as ET
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
ROOT=Path(__file__).resolve().parents[1]
SPECS={}
def add(char,num,crop=(300,240,650,620),height=700,bottom=0,multi=False):
    SPECS[char]=dict(photo=f'IMG_{num:04}.HEIC',crop=list(crop),height=height,bottom=bottom,multi=multi)
for char,num in zip('POIUYTREWQ',range(308,318)): add(char,num)
for char,num in zip('ASDFGHJKL',range(321,330)): add(char,num)
for char,num in [('M',340),('N',341),('B',342),('V',343),('X',345),('Z',346)]:add(char,num)
add('C',318,(185,340,295,490))
for char,num in zip('1234567890',[288,289,290,292,293,294,295,296,297,298]):
    add(char,num,(290,{'1':480,'2':380,'3':380,'4':370,'5':370,'6':345,'7':345,'8':380,'9':365,'0':320}[char],650,690))
# Shift legends above the numerals; height is relative to the main cap height.
for char,num,crop,height,bottom,multi in [
 ('!',288,(430,280,540,480),500,200,True),
 ('"',289,(420,255,550,390),240,460,True),
 ('#',290,(310,230,490,390),500,150,False),
 ('$',292,(330,210,515,380),610,70,False),
 ('%',293,(310,175,580,385),520,90,True),
 ('&',294,(350,155,560,360),540,0,False),
 ("'",295,(370,175,520,310),220,480,False),
 ('(',296,(345,185,500,370),720,-10,False),
 (')',297,(390,175,550,360),720,-10,False),
 ('+',299,(340,255,620,560),500,100,False),
 ('-',300,(300,300,630,475),82,309,False),
 ('£',301,(330,200,685,600),700,0,False),
 ('*',306,(300,260,640,585),620,40,False),
 ('@',307,(330,270,660,610),650,0,False),
 (':',330,(395,415,530,640),340,0,True),
 (';',331,(380,405,510,580),430,-90,True),
 ('[',330,(400,225,555,405),700,0,False),
 (']',331,(380,225,530,395),700,0,False),
 ('=',332,(310,235,635,500),300,200,True),
 ('?',337,(335,240,485,370),700,0,True),
 ('/',337,(335,390,535,640),700,0,False),
 ('>',338,(370,245,580,400),370,165,False),
 ('.',338,(380,480,585,590),110,0,False),
 ('<',339,(370,255,570,460),370,165,False),
 (',',339,(380,490,570,660),170,-60,False),
 ('←',287,(270,300,650,495),200,250,False),
 ('↑',305,(340,220,510,620),700,0,False),
 ('\ue000',348,(370,395,600,600),580,60,True),
 ('\ue001',349,(355,300,445,500),700,0,False),
 ]:add(char,num,crop,height,bottom,multi)

def extract(spec):
    path=ROOT/'build/full'/spec['photo'].replace('.HEIC','.png')
    im=np.array(Image.open(path).convert('RGB'))
    h,w=im.shape[:2];x0,y0,x1,y1=spec['crop'];sc=w/1000
    im=im[round(y0*sc):round(y1*sc),round(x0*sc):round(x1*sc)]
    gray=cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)
    gray=cv2.GaussianBlur(gray,(0,0),1.3)
    _,binary=cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    n,lab,stats,cent=cv2.connectedComponentsWithStats(binary)
    # Keycap edges and neighboring legends touch the ROI border; discard them.
    for i in range(1,n):
        x,y,w,h,area=stats[i]
        if x==0 or y==0 or x+w==binary.shape[1] or y+h==binary.shape[0]:
            stats[i,cv2.CC_STAT_AREA]=0
    areas=stats[1:,cv2.CC_STAT_AREA];largest=areas.max()
    if largest==0: raise ValueError(f'Crop cuts off glyph: {spec}')
    chosen=[i for i in range(1,n) if stats[i,cv2.CC_STAT_AREA]>=largest*(.055 if spec['multi'] else .8)]
    if not spec['multi']:chosen=[int(np.argmax(areas))+1]
    mask=np.where(np.isin(lab,chosen),255,0).astype('uint8')
    # Fill only tiny print defects, keeping the letter's actual counters.
    inv=255-mask;n,lab,stats,_=cv2.connectedComponentsWithStats(inv)
    for i in range(1,n):
        if stats[i,cv2.CC_STAT_AREA]<largest*.02: mask[lab==i]=255
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    mask=cv2.GaussianBlur(mask,(0,0),1.8)
    mask=np.where(mask>127,255,0).astype('uint8')
    y,x=np.where(mask>0);bb=(x.min(),y.min(),x.max()+1,y.max()+1)
    return im,mask[bb[1]:bb[3],bb[0]:bb[2]]

def main():
    (ROOT/'build/masks').mkdir(parents=True,exist_ok=True)
    (ROOT/'glyphs').mkdir(exist_ok=True)
    sheet=Image.new('RGB',(1500,((len(SPECS)+7)//8)*230),'#ecebe5');d=ImageDraw.Draw(sheet)
    manifest=[]
    for i,(char,spec) in enumerate(SPECS.items()):
        im,mask=extract(spec);code=f'{ord(char):04X}';height,width=mask.shape
        # Trace at a fixed raster height so the smoothing tolerance has equal effect.
        factor=240/height
        scaled=cv2.resize(mask,None,fx=factor,fy=factor,interpolation=cv2.INTER_AREA)
        scaled=cv2.GaussianBlur(scaled,(0,0),.9)
        scaled=np.where(scaled>127,255,0).astype('uint8')
        # These letters have no counters. Any enclosed white island is wear.
        if char in 'CEFGHIJKLMNSTUVWXYZ12357':
            contours,_=cv2.findContours(scaled,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            scaled[:]=0
            cv2.drawContours(scaled,contours,-1,255,cv2.FILLED)
        scaled=np.pad(scaled,12)
        pbm=ROOT/'build/masks'/f'{code}.pbm'
        Image.fromarray(255-scaled).convert('1').save(pbm)
        svg=ROOT/'build/masks'/f'{code}.svg'
        subprocess.run(['potrace',str(pbm),'-s','--flat','-a','1.05','-O','0.7','-o',str(svg)],check=True)
        root=ET.parse(svg).getroot();path=root.find('.//{http://www.w3.org/2000/svg}path').attrib['d']
        rec=RecordingPen();parse_path(path,rec);bounds=BoundsPen(None);rec.replay(bounds)
        xmin,ymin,xmax,ymax=bounds.bounds;s=spec['height']/(ymax-ymin)
        # Potrace's native path coordinates are Cartesian (its SVG group flips y).
        pen=SVGPathPen(None);rec.replay(TransformPen(pen,(s,0,0,s,-xmin*s,spec['bottom']-ymin*s)))
        outline=pen.getCommands();gw=(xmax-xmin)*s
        (ROOT/'glyphs'/f'{code}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -820 {gw+40:.3f} 1040"><path transform="scale(1,-1)" d="{outline}"/></svg>\n')
        entry=dict(character=char,codepoint=f'U+{code}',**spec,width=round(gw,3),outline=outline)
        manifest.append(entry)
        x=i%8*187;y=i//8*230
        thumb=Image.fromarray(im);thumb.thumbnail((175,112));sheet.paste(thumb,(x+6,y+22))
        thumb=Image.fromarray(255-mask);thumb.thumbnail((130,85));sheet.paste(thumb,(x+20,y+139))
        d.text((x+6,y+3),f'{char if ord(char)<127 else code} / {spec["photo"][4:8]}',fill='black')
    (ROOT/'glyphs/source-map.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    sheet.save(ROOT/'build/extraction-review.png')
    print(f'Extracted {len(manifest)} glyphs')
if __name__=='__main__':main()
