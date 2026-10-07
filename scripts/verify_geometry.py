"""Check the delivered SVG geometry, not just the construction parameters."""
from pathlib import Path
import xml.etree.ElementTree as ET
import pathops
from fontTools.svgLib.path import parse_path
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
ROOT=Path(__file__).resolve().parents[1]
def load(c):
    e=ET.parse(ROOT/'glyphs'/f'{ord(c):04X}.svg').getroot();p=pathops.Path();parse_path(e.find('{http://www.w3.org/2000/svg}path').attrib['d'],p.getPen());return p

def bounds(p):
    pen=BoundsPen(None);p.draw(pen);return pen.bounds

def scan(p,y):
    # Half-unit sampling checks equal thickness across multiple heights.
    intervals=[];start=None
    for i in range(-2,1602):
        x=i/2;inside=p.contains((x+.25,y))
        if inside and start is None:start=x
        if not inside and start is not None:intervals.append((start,x));start=None
    return intervals

def assert_pair(a,b,t):
    p=pathops.Path();load(a).draw(TransformPen(p.getPen(),t));q=load(b)
    # Each exported glyph is translated to x=0 after its construction.
    x0=bounds(p)[0];aligned=pathops.Path();p.draw(TransformPen(aligned.getPen(),(1,0,0,1,-x0,0)))
    error=pathops.op(aligned,q,pathops.PathOp.XOR).area
    assert error<.15,(a,b,error)

for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
    x0,y0,x1,y1=bounds(load(c));assert abs(y0)<.1 and abs(y1-700)<.1,(c,(x0,y0,x1,y1))
for y in [100,200,450,550,600]:
    assert scan(load('H'),y)==[(0,88),(312,400)],('H',y,scan(load('H'),y))
for c in ['O','D']:
    for y in [250,350,450]:assert scan(load(c),y)==[(0,88),(292,380)],(c,y,scan(load(c),y))
for c in ['E','F','L','P','R']:
    for y in [100,200]:assert scan(load(c),y)[0]==(0,88),(c,y,scan(load(c),y))
for c,x,expected in [('E',200,[(0,80),(320,400),(620,700)]),('F',200,[(320,400),(620,700)]),('L',200,[(0,80)]),('T',100,[(620,700)]),('H',200,[(310,390)])]:
    transposed=pathops.Path();load(c).draw(TransformPen(transposed.getPen(),(0,1,1,0,0,0)))
    assert scan(transposed,x)==expected,(c,scan(transposed,x))
for c in ['A','H','I','M','O','T','U','V','W','X','Y','8']:
    p=load(c);x0,_,x1,_=bounds(p);mirrored=pathops.Path();p.draw(TransformPen(mirrored.getPen(),(-1,0,0,1,x0+x1,0)))
    assert pathops.op(p,mirrored,pathops.PathOp.XOR).area<.15,c
assert_pair('(',')',(-1,0,0,1,220,0))
assert_pair('[',']',(-1,0,0,1,350,0))
assert_pair('<','>',(-1,0,0,1,310,0))
# Same number of counters survives simplification.
for c,count in [('A',2),('B',3),('O',2),('Q',2),('0',3),('8',3),('N',1),('H',1),('3',1),('5',1),('6',2),('9',2)]:
    assert len(list(load(c).contours))==count,(c,len(list(load(c).contours)))
# Regression: an 8 must retain the photographed taller lower opening and
# an 80-unit waist, rather than two small, widely separated round holes.
eight=load('8');vertical=pathops.Path();eight.draw(TransformPen(vertical.getPen(),(0,1,1,0,0,0)))
assert scan(vertical,190)==[(0,80),(340,420),(620,700)],scan(vertical,190)
assert scan(eight,210)==[(0,88),(292,380)],scan(eight,210)
assert scan(eight,525)==[(13,101),(279,367)],scan(eight,525)
# Regression: preserve the source-specific numeral proportions rather than
# reusing matching round arcs for 3, 5 and 6.
assert scan(load('3'),535)==[(10,98),(272,360)],scan(load('3'),535)
assert scan(load('5'),530)==[(24,112)],scan(load('5'),530)
assert scan(load('5'),250)==[(292,380)],scan(load('5'),250)
assert scan(load('6'),250)==[(0,88),(292,380)],scan(load('6'),250)
six_vertical=pathops.Path();load('6').draw(TransformPen(six_vertical.getPen(),(0,1,1,0,0,0)))
assert scan(six_vertical,190)==[(0,80),(381,460.5),(620,700)],scan(six_vertical,190)
# Regression: the outer diagonal of 2 continues through the top of its
# baseline bar, without the former rectangular protrusion at the left.
two=load('2')
assert not two.contains((1,79)) and two.contains((20,79))
def left_edge_at(y):
    lo,hi=0.,100.
    for _ in range(30):
        mid=(lo+hi)/2
        if two.contains((mid,y)):hi=mid
        else:lo=mid
    return (lo+hi)/2
edges=[left_edge_at(y) for y in [70,80,90]]
assert abs(edges[0]+edges[2]-2*edges[1])<.01,edges
# Regression (#5): S keeps the keycap's narrower upper bowl instead of
# reading as a rotated copy of itself.
s_upper=scan(load('S'),530);s_lower=scan(load('S'),170)
assert s_upper[-1][1]-s_upper[0][0]<s_lower[-1][1]-s_lower[0][0]-20,(s_upper,s_lower)
print('Geometry verified: 36 cap bounds, parallel stems, shared thickness, symmetry, paired glyphs, and counters')
