"""Build desktop and web fonts from the editable SVG outlines in glyphs/."""
from pathlib import Path
import json, math, xml.etree.ElementTree as ET
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.svgLib.path import parse_path
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'fonts'
SHAPES={};META={}
def rec(path):
    pen=RecordingPen();parse_path(path,pen);return pen

def transformed(p,t):
    pen=RecordingPen();p.replay(TransformPen(pen,t));return pen

def bounds(p):
    pen=BoundsPen(None);p.replay(pen);return pen.bounds

def put(char,p,note='Constructed extension'):
    SHAPES[char]=rec(p) if isinstance(p,str) else p;META[char]=note

def reflect(src,char,horizontal=False,vertical=False):
    p=SHAPES[src];x0,y0,x1,y1=bounds(p)
    put(char,transformed(p,(-1 if horizontal else 1,0,0,-1 if vertical else 1,x1+x0 if horizontal else 0,y1+y0 if vertical else 0)))

def combine(items):
    out=RecordingPen()
    for p,t in items:p.replay(TransformPen(out,t))
    return out

def build():
    OUT.mkdir(exist_ok=True)
    for entry in json.loads((ROOT/'glyphs/source-map.json').read_text()):
        ch=entry['character'];root=ET.parse(ROOT/'glyphs'/f'{ord(ch):04X}.svg').getroot()
        put(ch,root.find('{http://www.w3.org/2000/svg}path').attrib['d'],f"Geometrically normalized from {entry['photo']}")
    reflect('/','\\',horizontal=True);reflect('←','→',horizontal=True);reflect('↑','↓',vertical=True)
    reflect("'",'`',horizontal=True)
    put('|','M0 -80H88V780H0Z')
    put('_','M0 -90H460V-10H0Z')
    put('^','M0 480L170 700H250L420 480H322L210 624L98 480Z')
    put('~','M0 315C70 460 142 440 228 373C300 318 325 330 375 408L445 364C371 233 302 241 221 296C146 348 115 373 70 277Z')
    put('{','M280 710H200C115 710 100 655 100 575V450C100 395 75 390 20 390V310C75 310 100 305 100 250V125C100 45 115 -10 200 -10H280V65H225C188 65 180 85 180 135V255C180 307 164 335 132 350C164 365 180 393 180 445V565C180 615 188 635 225 635H280Z')
    reflect('{','}',horizontal=True)
    # Curly quotes, typographic dashes, and mathematical operators.
    put('‘',transformed(SHAPES[','],(-1,0,0,-1,bounds(SHAPES[','])[2],700+bounds(SHAPES[','])[1])))
    put('’',transformed(SHAPES[','],(1,0,0,1,0,600)))
    for ch,src in [('“','‘'),('”','’')]:
        w=bounds(SHAPES[src])[2];put(ch,combine([(SHAPES[src],(1,0,0,1,0,0)),(SHAPES[src],(1,0,0,1,w+65,0))]))
    for ch,w in [('–',500),('—',800),('−',460)]: put(ch,f'M0 310H{w}V390H0Z')
    put('×','M0 150L155 350L0 550L70 605L210 420L350 605L420 550L265 350L420 150L350 95L210 280L70 95Z')
    put('…',combine([(SHAPES['.'],(1,0,0,1,i*210,0)) for i in range(3)]))
    # Function-key f is kept as a separate private-use glyph; lowercase f stays F.
    for i in range(1,9):
        put(chr(0xE00F+i),combine([(SHAPES['\ue001'],(.65,0,0,.65,0,0)),(SHAPES[str(i)],(.65,0,0,.65,420,0))]),f'Composed f{i} legend')
    # Compose key labels without turning common words into automatic ligatures.
    labels=['CTRL','RUN\nSTOP','SHIFT\nLOCK','SHIFT','RETURN','RESTORE','CLR\nHOME','INST\nDEL','CRSR']
    for index,label in enumerate(labels):
        lines=label.split('\n');items=[];scale=.42
        lengths=[sum(bounds(SHAPES[c])[2]+130 for c in line)-130 for line in lines];maxlen=max(lengths)
        for row,(line,length) in enumerate(zip(lines,lengths)):
            x=(maxlen-length)/2
            for c in line:
                items.append((SHAPES[c],(scale,0,0,scale,x*scale,(len(lines)-row-1)*400)))
                x+=bounds(SHAPES[c])[2]+130
        put(chr(0xE020+index),combine(items),f'Composed {label.replace(chr(10)," / ")} legend')
    # Latin accents are composed from the uppercase key lettering for practical typing.
    accents={
      'acute':rec('M55 760L180 910H290L135 760Z'),
      'grave':rec('M200 760L65 910H-45L120 760Z'),
      'circumflex':rec('M-30 760L85 910H165L280 760H184L125 839L66 760Z'),
      'dieresis':rec('M-10 780H70V870H-10Z M180 780H260V870H180Z'),
      'tilde':rec('M-35 792C10 901 77 890 131 847C175 815 196 826 220 874L282 838C230 748 171 755 119 794C74 825 52 843 25 770Z'),
      'doubleacute':rec('M-45 760L50 910H140L35 760Z M145 760L240 910H330L225 760Z'),
      'ring':rec('M125 960C15 960 15 740 125 740C235 740 235 960 125 960Z M125 903C168 903 168 797 125 797C82 797 82 903 125 903Z'),
    }
    groups={'acute':'ÁÉÍÓÚÝĆŃŚŹ','grave':'ÀÈÌÒÙ','circumflex':'ÂÊÎÔÛ','dieresis':'ÄËÏÖÜŸ','tilde':'ÃÑÕ','doubleacute':'ŐŰ','ring':'Å'}
    import unicodedata
    for kind,chars in groups.items():
        for ch in chars:
            base=unicodedata.normalize('NFD',ch)[0];w=bounds(SHAPES[base])[2]
            put(ch,combine([(SHAPES[base],(1,0,0,1,0,0)),(accents[kind],(1,0,0,1,(w-250)/2,0))]),'Composed accent extension')
    put('Ç',combine([(SHAPES['C'],(1,0,0,1,0,0)),(rec('M180 20H245L209 -52C300 -58 290 -170 190 -170H120V-115H186C229 -115 229 -90 177 -92H145Z'),(1,0,0,1,0,0))]))
    # Font metrics. Numerals share one advance; letter spacing follows actual width.
    names={c:f'uni{ord(c):04X}' for c in SHAPES};order=['.notdef','space']+list(names.values())
    cmap={32:'space',160:'space',**{ord(c):n for c,n in names.items()}}
    for c,n in names.items():
        if c.isupper() and len(c.lower())==1:cmap[ord(c.lower())]=n
    gl={'.notdef':rec('M50 0H470V700H50Z M125 75V625H395V75Z'),'space':RecordingPen()}
    metrics={'.notdef':(520,50),'space':(310,0)}
    for c,p in SHAPES.items():
        x0,y0,x1,y1=bounds(p);w=x1-x0;bearing=65
        if c.isdigit() and c.isascii():advance=560;bearing=(560-w)/2
        else:advance=round(w+130)
        # Narrow I remains deliberately plain, with a little more breathing room.
        if c=='I':advance=290;bearing=(290-w)/2
        if c in '.:,;':advance=max(270,advance);bearing=(advance-w)/2
        gl[names[c]]=transformed(p,(1,0,0,1,bearing-x0,0));metrics[names[c]]=(advance,round(bearing))
    common={'familyName':'C64 Keyboard','styleName':'Regular','uniqueFontIdentifier':'C64Keyboard-Regular-1.103','fullName':'C64 Keyboard Regular','psName':'C64Keyboard-Regular','version':'Version 1.103','description':'Geometrically normalized reconstruction of the keycap legends in the supplied C64 photographs. Lowercase maps to uppercase. Unofficial reconstruction.','manufacturer':'Independent reconstruction','designer':'Reconstructed from user-supplied photographs'}
    kern='feature kern {\n'+ '\n'.join(f'pos {names[a]} {names[b]} {value};' for a,b,value in [('A','V',-45),('A','W',-30),('A','Y',-40),('V','A',-45),('W','A',-30),('Y','A',-40),('T','A',-35),('L','T',-30),('L','V',-30),('L','Y',-40),('T','O',-15),('T','.',-45)])+'\n} kern;'
    for ttf in [True,False]:
        fb=FontBuilder(1000,isTTF=ttf);fb.setupGlyphOrder(order);fb.setupCharacterMap(cmap)
        fb.setupHorizontalMetrics(metrics);fb.setupHorizontalHeader(ascent=1000,descent=-220,lineGap=0)
        fb.setupNameTable(common);fb.setupOS2(version=4,sTypoAscender=1000,sTypoDescender=-220,sTypoLineGap=0,usWinAscent=1000,usWinDescent=220,sxHeight=700,sCapHeight=700,usWeightClass=400,usWidthClass=3,fsSelection=0xC0)
        fb.setupPost()
        if ttf:
            glyphs={}
            for name,p in gl.items():
                pen=TTGlyphPen(None);p.replay(Cu2QuPen(pen,max_err=.65,reverse_direction=True));glyphs[name]=pen.glyph()
            fb.setupGlyf(glyphs);fb.setupMaxp()
        else:
            chars={}
            for name,p in gl.items():
                pen=T2CharStringPen(metrics[name][0],None);p.replay(pen);chars[name]=pen.getCharString()
            fb.setupCFF('C64Keyboard-Regular',{'FullName':'C64 Keyboard Regular','FamilyName':'C64 Keyboard','Weight':'Regular'},chars,{})
        addOpenTypeFeaturesFromString(fb.font,kern)
        fb.font['head'].fontRevision=1.103
        fb.font['head'].created=fb.font['head'].modified=3874003200
        ext='ttf' if ttf else 'otf';fb.save(OUT/f'C64Keyboard-Regular.{ext}')
        if ttf:fb.font.flavor='woff2';fb.save(OUT/'C64Keyboard-Regular.woff2')
    coverage=[{'character':c,'codepoint':f'U+{ord(c):04X}','source':META[c]} for c in SHAPES]
    (OUT/'character-map.json').write_text(json.dumps(coverage,indent=2,ensure_ascii=False)+'\n')
    print(f'Built {len(order)} glyphs / {len(cmap)} mapped characters in TTF, OTF and WOFF2')
if __name__=='__main__':build()
