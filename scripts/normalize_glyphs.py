"""Reconstruct ideal key legends with explicit geometric constraints.

The photo traces are observations, not master geometry. Shared dimensions,
parallel stems, horizontal bars and symmetric bowls remove projective distortion
and print wear together. This is a constrained reconstruction, not a recovered
camera calibration: a single curved keycap photograph cannot determine that.
"""
from pathlib import Path
import json
import shutil
import xml.etree.ElementTree as ET
import pathops
from fontTools.svgLib.path import parse_path
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
ROOT=Path(__file__).resolve().parents[1]
V=88; H=80; CAP=700
SHAPES={};NOTES={}
def path(d):
    p=pathops.Path();parse_path(d,p.getPen());return p

def rect(x,y,w,h):return path(f'M{x} {y}h{w}v{h}h{-w}Z')
def union(*items):
    out=pathops.Path()
    for p in items:out=pathops.op(out,p,pathops.PathOp.UNION)
    return out

def subtract(a,b):return pathops.op(a,b,pathops.PathOp.DIFFERENCE)
def transform(p,t):
    out=pathops.Path();p.draw(TransformPen(out.getPen(),t));return out

def stroke(d,width=V):
    p=path(d);p.stroke(width,pathops.LineCap.BUTT_CAP,pathops.LineJoin.ROUND_JOIN,4)
    p.convertConicsToQuads(.08)
    return pathops.simplify(p)

def ellipse(x,y,rx,ry):
    k=.5522847498307936
    return path(f'M{x+rx} {y}C{x+rx} {y+k*ry} {x+k*rx} {y+ry} {x} {y+ry}C{x-k*rx} {y+ry} {x-rx} {y+k*ry} {x-rx} {y}C{x-rx} {y-k*ry} {x-k*rx} {y-ry} {x} {y-ry}C{x+k*rx} {y-ry} {x+rx} {y-k*ry} {x+rx} {y}Z')
def ring(x,y,rx,ry,sx=V,sy=H):return subtract(ellipse(x,y,rx,ry),ellipse(x,y,rx-sx,ry-sy))
def put(c,p,note):SHAPES[c]=path(p) if isinstance(p,str) else p;NOTES[c]=note

def build_shapes():
    bowl=path('M190 700C64 700 0 632 0 515V185C0 68 64 0 190 0C316 0 380 68 380 185V515C380 632 316 700 190 700Z')
    counter=path('M190 620C117 620 88 579 88 505V195C88 121 117 80 190 80C263 80 292 121 292 195V505C292 579 263 620 190 620Z')
    o=subtract(bowl,counter)
    put('O',o,'380 × 700; parallel 88-unit stems; symmetric bowls; 80-unit caps')
    # LSZ04731 supplies the actual C key, previously inferred from CTRL.
    c_outer=path('M180 700C60 700 0 632 0 515V185C0 68 60 0 180 0C300 0 360 68 360 185V515C360 632 300 700 180 700Z')
    c_inner=path('M180 620C112 620 88 579 88 505V195C88 121 112 80 180 80C248 80 272 121 272 195V505C272 579 248 620 180 620Z')
    put('C',subtract(subtract(c_outer,c_inner),rect(220,230,160,260)),'LSZ04731 C key: 360-unit bowl, shorter 260-unit opening, level terminals and shared 88/80-unit strokes')
    put('G',union(subtract(o,rect(240,380,160,125)),rect(180,300,200,80)),'LSZ04731: crossbar raised to 300–380, longer inward reach; O-family bowl and shared stroke weights')
    put('Q',union(o,stroke('M190 170L264 40H440',72)),'O-family bowl; preserved low diagonal and horizontal tail')
    put('D',subtract(path('M0 0V700H182C317 700 380 636 380 510V190C380 64 317 0 182 0Z'),path('M88 80H178C263 80 292 117 292 195V505C292 583 263 620 178 620H88Z')),'Parallel stems and matching D/O bowl dimensions')
    p=subtract(path('M0 0V700H184C319 700 380 639 380 530V480C380 370 319 310 184 310H88V0Z'),path('M88 390H180C262 390 292 420 292 485V525C292 590 262 620 180 620H88Z'))
    put('P',p,'88-unit stem; horizontal bowl boundaries; upright right shoulder')
    put('R',union(p,path('M181 344H276L410 0H315Z')),'P-family bowl with straight diagonal leg')
    put('B',subtract(path('M0 0V700H180C305 700 366 642 366 528C366 447 338 398 282 367C348 341 380 284 380 195C380 68 313 0 180 0Z'),union(path('M88 408H174C250 408 278 445 278 521C278 589 250 620 174 620H88Z'),path('M88 80H179C259 80 292 116 292 197C292 286 259 328 179 328H88Z'))),'Shared upright stem; level waist; optically larger lower bowl')
    for c,arms in [('E',[(0,620,340,80),(0,320,300,80),(0,0,340,80)]),('F',[(0,620,340,80),(0,320,300,80)]),('L',[(0,0,340,80)])]:
        put(c,union(rect(0,0,V,CAP),*(rect(*r) for r in arms)),'E/F/L family: one stem width, level 80-unit bars')
    put('H',union(rect(0,0,V,CAP),rect(312,0,V,CAP),rect(0,310,400,H)),'Exactly parallel equal stems; centered horizontal crossbar')
    put('I',rect(0,0,V,CAP),'Plain rectangle; constant stem width')
    put('T',union(rect(156,0,V,CAP),rect(0,620,400,H)),'Centered stem; horizontal cap bar')
    put('U','M0 700H88V190C88 115 117 80 190 80C263 80 292 115 292 190V700H380V185C380 63 316 0 190 0C64 0 0 63 0 185Z','O-family lower bowl; equal parallel stems')
    put('J','M272 700H360V180C360 62 302 0 180 0C58 0 0 62 0 180V245H88V185C88 112 112 80 180 80C248 80 272 112 272 185Z','Parallel upright stem; level top; matched lower bowl weight')
    put('N',union(rect(0,0,V,CAP),rect(332,0,V,CAP),path('M0 700H94L420 0H326Z')),'420 × 700 rectangle; parallel stems and straight diagonal')
    put('K',union(rect(0,0,V,CAP),path('M70 334L310 700H414L176 343L420 0H311L119 270L88 222Z')),'Upright stem; straight diagonal arms; aligned cap and baseline')
    put('A','M0 0L188 700H272L460 0H370L329 155H131L90 0Z M153 235H307L230 525Z','Symmetric diagonal stems; level crossbar; centered apex')
    put('V','M0 700H90L220 160L350 700H440L262 0H178Z','Symmetric V; parallel sides within each diagonal stroke')
    put('X','M0 0L168 350L0 700H96L220 442L344 700H440L272 350L440 0H344L220 258L96 0Z','Mirrored straight diagonals; centered crossing')
    put('Y','M0 700H96L210 422L324 700H420L254 330V0H166V330Z','Symmetric fork; vertical centered 88-unit stem')
    put('M','M0 0V700H100L290 225L480 700H580V0H492V487L333 105H247L88 487V0Z','Parallel outer stems; mirrored diagonals; centered inner vertex')
    put('W','M0 700H92L166 150L282 700H378L494 150L568 700H660L548 0H448L330 540L212 0H112Z','660-unit broad W; paired mirrored diagonals')
    put('Z','M0 700H380V620L103 80H380V0H0V80L277 620H0Z','Equal level bars; parallel diagonal edges')
    # The keycap S is not a rotated copy of itself: its upper bowl is about
    # 30 units narrower, the upper terminal ends lower and the lower terminal
    # higher (LSZ04731, IMG_0322). A point-symmetric S reads as upside down.
    s=stroke('M334 480C334 600 280 656 195 656C105 656 56 605 56 530C56 450 110 405 195 365C290 320 348 270 348 180C348 90 290 44 196 44C100 44 44 95 44 225')
    put('S',s,'Photo-fitted: 366-unit upper bowl over a 392-unit lower bowl; upper terminal at 480, lower at 225; consistent stroke')
    put('0',pathops.op(union(o,stroke('M50 0L330 700',65)),rect(0,0,380,700),pathops.PathOp.INTERSECTION),'O-family oval with preserved slash, clipped to its bounding rectangle')
    put('1','M110 0V588L15 533L0 618L123 700H198V0Z','Vertical stem; preserved flag; no added baseline serif')
    # Match the base's upper-left bevel to the *outer edge* of the diagonal.
    # A full rectangle here projected left of the stroke, leaving a small spur.
    diagonal_dx,diagonal_dy=263-44,352-44
    diagonal_length=(diagonal_dx**2+diagonal_dy**2)**.5
    edge_x=44-(V/2)*diagonal_dy/diagonal_length
    edge_y=44+(V/2)*diagonal_dx/diagonal_length
    left_join_y=edge_y-edge_x*diagonal_dy/diagonal_dx
    top_join_x=(H-left_join_y)*diagonal_dx/diagonal_dy
    two_base=path(f'M0 0H380V{H}H{top_join_x}L0 {left_join_y}Z')
    put('2',union(stroke('M44 530C44 615 95 656 190 656C285 656 336 615 336 530C336 466 303 412 263 352L44 44'),two_base),'Level baseline and symmetric upper bowl; straight diagonal continues into a flush, spur-free base junction')
    # Fit the unequal bowls directly: 3 has a narrower upper bowl and a
    # taller lower opening. Stroked matching arcs lost those proportions.
    three=path('M10 530V548C10 646 75 700 187 700C299 700 360 646 360 540V505C360 443 340 410 288 380C354 348 380 292 380 213V181C380 61 310 0 190 0C66 0 0 69 0 160V184H88V164C88 106 119 80 190 80C261 80 292 118 292 184V222C292 304 252 336 180 336H140V416H178C243 416 272 452 272 514V539C272 591 248 620 187 620C126 620 98 592 98 545V530Z')
    put('3',three,'Photo-fitted unequal bowls: 360-unit upper width, 380-unit lower width; level terminals and short central bar')
    put('4','M270 700H358V240H430V160H358V0H270V160H0V240Z M270 537L105 240H270Z','Parallel right stem; horizontal bar; triangular counter')
    five=path('M24 700H356V620H112V426C141 452 169 464 208 464C321 464 380 394 380 285V190C380 65 315 0 190 0C66 0 0 64 0 164V184H88V168C88 108 119 80 190 80C261 80 292 117 292 190V280C292 354 265 384 207 384C157 384 132 359 112 310H24Z')
    put('5',five,'Photo-fitted raised shoulder and tall lower bowl; inset parallel upper stem; horizontal top and clean open terminal')
    six_outer=path('M190 700C316 700 380 637 380 532V493H292V532C292 590 258 620 190 620C121 620 88 585 88 520V419C120 447 158 461 201 461C316 461 380 389 380 281V185C380 63 316 0 190 0C64 0 0 63 0 185V514C0 630 64 700 190 700Z')
    six_counter=path('M190 381C120 381 88 336 88 268V195C88 121 117 80 190 80C263 80 292 121 292 195V268C292 336 260 381 190 381Z')
    six=subtract(six_outer,six_counter)
    put('6',six,'Photo-fitted tall lower counter (301 units), parallel bowl sides, 80-unit shoulder, upright backbone, and short upper hook')
    # LSZ04735 resolves the straight sides and taller counter that the old
    # elliptical model lost. Fit 9 independently: its counter remains shorter
    # than 6's, rather than assuming the two are exact rotations.
    nine_outer=path('M190 700C64 700 0 637 0 515V419C0 311 64 255 179 255C222 255 260 269 292 297V180C292 115 259 80 190 80C122 80 88 110 88 168V207H0V168C0 63 64 0 190 0C316 0 380 70 380 186V515C380 637 316 700 190 700Z')
    nine_counter=path('M190 620C117 620 88 579 88 505V432C88 364 120 335 190 335C260 335 292 364 292 432V505C292 579 263 620 190 620Z')
    put('9',subtract(nine_outer,nine_counter),'LSZ04735: 285-unit tall upper counter, parallel bowl sides, 80-unit shoulder and upright backbone; independent of 6')
    put('7','M0 700H380V620L137 0H40L283 620H0Z','Horizontal top bar; straight constant-width diagonal')
    # The photo's lower counter is taller than the upper one. Two similar
    # ellipses made the previous waist 158 units thick instead of about 80.
    # Keep the upright symmetry while fitting these observed proportions.
    eight=path('M190 700C72 700 13 642 13 542V518C13 456 40 414 85 389Q101 380 85 371C26 335 0 286 0 218V182C0 63 64 0 190 0C316 0 380 63 380 182V218C380 286 354 335 295 371Q279 380 295 389C340 414 367 456 367 518V542C367 642 308 700 190 700Z')
    upper_eight=path('M190 620C129 620 101 588 101 536V507C101 450 129 420 190 420C251 420 279 450 279 507V536C279 588 251 620 190 620Z')
    lower_eight=path('M190 340C118 340 88 296 88 230V190C88 112 118 80 190 80C262 80 292 112 292 190V230C292 296 262 340 190 340Z')
    put('8',subtract(eight,union(upper_eight,lower_eight)),'Narrower upper bowl; taller lower counter (260 vs 200 units); 80-unit waist; bilateral symmetry')
    # Small legends have their own optical weight, independent of the main caps.
    put('.',ellipse(50,50,50,50),'Circular dot on baseline')
    put(':',union(ellipse(50,50,50,50),ellipse(50,430,50,50)),'Equal circular dots on one vertical axis; upper dot raised for cap-height text')
    comma=path('M100 50C100 14 78 -26 34 -70H0L28 8C-10 35 -5 100 50 100C79 100 100 78 100 50Z')
    put(',',comma,'Circular head with clean tapered tail')
    put(';',union(comma,ellipse(50,430,50,50)),'Colon-family dot and comma-family tail')
    # Text punctuation sits on the baseline at full weight. On the keycap, !
    # is a small shifted legend raised above the 1, which looked broken in text.
    put('!',union(path('M0 700H104L90 220H14Z'),ellipse(52,50,50,50)),'Tapered stem at stem weight; baseline dot matching the full stop')
    put('"',union(rect(0,460,80,240),rect(150,460,80,240)),'Equal rectangular strokes with parallel edges')
    put("'",path('M72 700H150L68 480H0Z'),'Straight slanted stroke')
    put('-',rect(0,310,460,80),'Level 80-unit horizontal stroke')
    put('=',union(rect(0,200,460,80),rect(0,420,460,80)),'Equal parallel bars and equal bearings')
    put('+',union(rect(0,310,500,80),rect(210,100,80,500)),'Perpendicular bars with equal thickness and centered crossing')
    put('/',path('M0 0H96L456 700H360Z'),'Straight parallel diagonal edges')
    left=stroke('M270 515L40 350L270 185',62)
    put('<',left,'Symmetric angled arms around math axis')
    put('>',transform(left,(-1,0,0,1,310,0)),'Exact reflected counterpart of less-than')
    bracket=stroke('M310 660L40 515V185L310 40',80)
    put('[',bracket,'Original angular bracket; vertical spine and mirrored arms')
    put(']',transform(bracket,(-1,0,0,1,350,0)),'Exact reflected angular bracket')
    paren=stroke('M188 700C-4 471 -4 229 188 0',76)
    put('(',paren,'Smooth symmetric parenthesis around mid-height')
    put(')',transform(paren,(-1,0,0,1,220,0)),'Exact reflected parenthesis')
    put('*',union(*(stroke(d,78) for d in ['M0 350H620','M150 73L470 627','M150 627L470 73'])),'Three equal straight strokes intersecting at one center')
    # # and % are small shifted legends on the keycaps; text needs cap height.
    put('#',union(rect(100,0,76,CAP),rect(300,0,76,CAP),stroke('M0 205L476 275',76),stroke('M0 425L476 495',76)),'Cap-height upright strokes and matching intentionally sloped crossbars')
    put('?',union(stroke('M44 535C44 615 96 656 190 656C284 656 336 610 336 530C336 456 294 409 241 371C206 344 184 316 184 264V224'),ellipse(184,50,50,50)),'Smooth bowl; centered stem and circular dot')
    put('←',union(rect(135,315,625,70),path('M0 350L170 450V250Z')),'Horizontal shaft and centered symmetric triangular head')
    put('↑',union(rect(55,0,70,565),path('M90 700L0 530H180Z')),'Vertical shaft and centered symmetric triangular head')
    # The keycap $ is a small shifted legend; in text it needs the full S at
    # the shared stroke weight, with the stem extending past cap and baseline.
    put('$',union(s,rect(165,-90,66,880)),'Full-size S crossed by one vertical stem extending 90 units beyond cap height and baseline')
    percent=union(ring(115,555,115,145,76,72),ring(425,145,115,145,76,72),stroke('M95 -40L445 740',76))
    put('%',pathops.op(percent,rect(-100,0,800,CAP),pathops.PathOp.INTERSECTION),'Cap-height oval counters and straight diagonal; paired sizes')
    # Fitted to a close-up of the & key print: small teardrop loop, broad lower
    # bowl, and a forked tail where the leg meets the baseline beside a short
    # spur. The print's tiny prong under the spur is smoothed into one curve.
    amp_body=stroke('M262 654C340 654 406 610 406 540C406 472 362 424 302 388C190 330 48 300 48 180C48 92 125 48 222 48C298 48 350 72 392 112',92)
    amp_leg=stroke('M262 654C190 654 129 610 129 540C122 482 130 446 183 404L406 70C425 40 445 15 455 -40')
    amp_tail=path('M360 195L430 232L518 236L546 212Q490 160 476 118Q468 80 500 30Q510 10 500 0L430 0L380 100Z')
    amp_notch=path('M335 -10L345 0Q362 32 390 60Q404 26 422 0L432 -10Z')
    amp=subtract(union(amp_body,amp_leg,amp_tail),amp_notch)
    put('&',pathops.op(amp,rect(-100,0,1000,CAP),pathops.PathOp.INTERSECTION),'Photo-fitted to the & key print at cap height: teardrop loop, broad bowl, spur and baseline foot')
    put('£','M0 0V80H35C110 80 132 140 132 230V340H72V420H132V505C132 635 211 700 360 700C509 700 600 630 600 490H500C500 577 452 620 360 620C268 620 232 580 232 505V420H410V340H232V230C232 163 218 112 184 80H420C472 80 500 123 500 210H600C600 70 528 0 420 0Z','LSZ04734: wider 600-unit silhouette, raised crossbar, square left foot and rising right terminal; 100-unit symbol stem')
    # IMG_0307/LSZ04734: a heavy spiral whose tail ends level at the bottom,
    # wrapped around a small, right-leaning a with a narrow counter.
    a_bowl=subtract(ellipse(0,0,128,132),ellipse(4,0,46,80))
    at=union(stroke('M462 44H310C150 44 44 160 44 330C44 510 172 612 328 612C496 612 610 505 610 345C610 262 576 212 522 212C470 212 440 236 424 268'),
             stroke('M396 212L446 470',84),transform(a_bowl,(1,0,.22,1,312,338)))
    put('@',at,'Photo-fitted: 88-unit spiral with a level bottom tail; leaning a with a narrow counter')
    put('\ue001','M120 0V350H0V446H120V520C120 642 174 700 284 700H360V604H284C240 604 220 575 220 520V446H360V350H220V0Z','LSZ04733 function f: 100-unit stem, 96-unit bar, flat-ended hook aligned with crossbar, and shared 700-unit height')

def main():
    build_shapes()
    manifest=json.loads((ROOT/'glyphs/source-map.json').read_text())
    new_references={e['character']:e for e in json.loads((ROOT/'glyphs/high-resolution-map.json').read_text())}
    review=json.loads((ROOT/'glyphs/reference-review.json').read_text())
    refinements={e['character']:e['photo'] for e in review['observations'] if e['action']=='refined'}
    assert set(SHAPES)=={e['character'] for e in manifest}
    raw=ROOT/'glyphs/traced';raw.mkdir(exist_ok=True)
    report=[]
    for e in manifest:
        ch=e['character'];name=f'{ord(ch):04X}.svg';dest=ROOT/'glyphs'/name
        if not (raw/name).exists():shutil.copy2(dest,raw/name)
        p=pathops.simplify(SHAPES[ch]);b=BoundsPen(None);p.draw(b);x0,y0,x1,y1=b.bounds
        p=transform(p,(1,0,0,1,-x0,0));pen=SVGPathPen(None,ntos=lambda v:format(v,'.4f').rstrip('0').rstrip('.') if v else '0');p.draw(pen)
        width=x1-x0;outline=pen.getCommands()
        dest.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -820 {width+40:.3f} 1040"><path transform="scale(1,-1)" d="{outline}"/></svg>\n')
        reference=new_references[ch]
        report.append(dict(character=ch,codepoint=e['codepoint'],source_photo=refinements.get(ch,e['photo']),original_source_photo=e['photo'],additional_reference=reference['photo'],revised_from_new_reference=ch in refinements,method='constrained geometric reconstruction',assumptions=NOTES[ch],original_width=e['width'],new_reference_width=reference['width'],width=round(width,3),bounds=[round(v,3) for v in (0,y0,width,y1)]))
    (ROOT/'glyphs/normalization.json').write_text(json.dumps(dict(version='1.112',cap_height=CAP,vertical_stem=V,horizontal_bar=H,note='Inferred design geometry; no claim of unique camera calibration. Original observations are retained in traced/; newer camera observations in high-resolution/. See reference-review.json for refinements.',glyphs=report),ensure_ascii=False,indent=2)+'\n')
    print(f'Normalized all {len(report)} core glyphs; photo traces retained separately')
if __name__=='__main__':main()
