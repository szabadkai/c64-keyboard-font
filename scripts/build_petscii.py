"""Construct smooth C64 key-front graphics; positions follow PETSCII's 8x8 cell.

These are geometric interpretations of printed legends, not bitmap ROM traces.
Mapping facts: https://www.pagetable.com/c64ref/charset/ (C64 upper/graphics).
"""
from pathlib import Path
import json
import pathops
from fontTools.pens.svgPathPen import SVGPathPen
from normalize_glyphs import path, rect, union, subtract, transform, stroke, ellipse, ring
ROOT=Path(__file__).resolve().parents[1]
CELL=700
UNIT=CELL/8


def shapes():
    s={}
    def r(x,y,w,h):return rect(x*UNIT,y*UNIT,w*UNIT,h*UNIT)
    # Screen-code order. Each band retains its position within the cell.
    s[0x40]=r(0,3.5,8,1)
    heart=path('M350 65C280 145 85 295 85 458C85 625 270 668 350 535C430 668 615 625 615 458C615 295 420 145 350 65Z')
    spade=union(transform(heart,(1,0,0,-1,0,700)),path('M310 270H390C384 172 402 111 470 65H230C298 111 316 172 310 270Z'))
    s[0x41]=spade
    for code,x in [(0x42,3.5),(0x47,2.5),(0x48,4.5),(0x54,1.5),(0x59,5.5)]:s[code]=r(x,0,1,8)
    for code,y in [(0x43,3.5),(0x44,4.5),(0x45,5.5),(0x46,2.5),(0x52,1.5)]:s[code]=r(0,y,8,1)
    # Rounded corners have the same center junction as the straight line pieces.
    arc=stroke('M0 350H175C272 350 350 272 350 175V0',UNIT)
    s[0x49]=arc
    s[0x4a]=transform(arc,(-1,0,0,-1,700,700))
    s[0x4b]=transform(arc,(1,0,0,-1,0,700))
    s[0x55]=transform(arc,(-1,0,0,1,700,0))
    s[0x4c]=union(r(0,0,1,8),r(0,0,8,1))
    s[0x4f]=union(r(0,0,1,8),r(0,7,8,1))
    s[0x50]=union(r(7,0,1,8),r(0,7,8,1))
    s[0x7a]=union(r(7,0,1,8),r(0,0,8,1))
    def clipped(d):return pathops.op(stroke(d,UNIT),r(0,0,8,8),pathops.PathOp.INTERSECTION)
    s[0x4d]=clipped('M0 700L700 0')
    s[0x4e]=clipped('M0 0L700 700')
    s[0x56]=union(s[0x4d],s[0x4e])
    s[0x51]=ellipse(350,350,245,245)
    s[0x53]=heart
    s[0x57]=ring(350,350,245,245,UNIT,UNIT)
    s[0x58]=union(ellipse(350,492,143,143),ellipse(205,300,143,143),ellipse(495,300,143,143),path('M310 350H390C383 191 403 111 470 65H230C297 111 317 191 310 350Z'))
    s[0x5a]=path('M350 660L610 350L350 40L90 350Z')
    # Line junctions, centered independently of the offset one-eighth bands.
    def junction(d):return stroke(d,UNIT)
    for code,d in {
        0x5b:'M0 350H700M350 0V700',0x5d:'M350 0V700',
        0x6b:'M350 0V700M350 350H700',0x6d:'M350 700V350H700',
        0x6e:'M0 350H350V0',0x70:'M350 0V350H700',
        0x71:'M0 350H700M350 350V700',0x72:'M0 350H700M350 350V0',
        0x73:'M350 0V700M350 350H0',0x7d:'M0 350H350V700'
    }.items():s[code]=junction(d)
    def shade(w,h):
        return union(*(r(x,y,1,1) for y in range(h) for x in range(w) if (x+y)%2==0))
    s[0x5c]=shade(4,8);s[0x66]=shade(8,8);s[0x68]=shade(8,4)
    s[0x5e]=union(rect(75,520,550,85),rect(183,90,85,430),path('M440 520H525V195C525 135 547 125 597 148V66C494 28 440 72 440 180Z'))
    s[0x5f]=path('M0 700H700V0Z');s[0x69]=path('M0 0V700H700Z')
    for code,coords in {
        0x61:(0,0,4,8),0x62:(0,0,8,4),0x63:(0,7,8,1),0x64:(0,0,8,1),
        0x65:(0,0,1,8),0x67:(7,0,1,8),0x6a:(6,0,2,8),0x6c:(4,0,4,4),
        0x6f:(0,0,8,2),0x74:(0,0,2,8),0x75:(0,0,3,8),0x76:(5,0,3,8),
        0x77:(0,6,8,2),0x78:(0,5,8,3),0x79:(0,0,8,3),0x7b:(0,0,4,4),
        0x7c:(4,4,4,4),0x7e:(0,4,4,4)
    }.items():s[code]=r(*coords)
    s[0x7f]=union(r(0,4,4,4),r(4,0,4,4))
    assert set(s)==set(range(0x40,0x80))-{0x60}
    return s


def write_svg(p,dest):
    pen=SVGPathPen(None);p.draw(pen)
    dest.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-35 -735 770 770"><path transform="scale(1,-1)" d="'+pen.getCommands()+'"/></svg>\n')


def main():
    manifest=json.loads((ROOT/'glyphs/petscii-map.json').read_text())
    folder=ROOT/'glyphs/petscii';folder.mkdir(exist_ok=True)
    frame=subtract(rect(0,0,700,700),rect(24,24,652,652))
    geometry=shapes()
    for e in manifest['symbols']:
        symbol=geometry[e['screen_code']]
        # The pi on the up-arrow key is printed without a reference frame.
        p=symbol if e['screen_code']==0x5e else union(frame,symbol)
        write_svg(p,folder/f"{e['font_codepoint'][2:]}.svg")
    print(f"Constructed {len(manifest['symbols'])} key-front graphics")

if __name__=='__main__':main()
