"""Package the distributable files without photographs or build caches."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
files=[ROOT/n for n in ['README.md','CHANGELOG.md','requirements.txt','preview.html','specimen.png','normalization-comparison.png','latest-reference-comparison.png','petscii-specimen.png']]
for folder in ['fonts','glyphs','docs']:
    files+=sorted(p for p in (ROOT/folder).rglob('*') if p.is_file())
files+=sorted((ROOT/'scripts').glob('*.py'))
with ZipFile(ROOT/'C64-Keyboard.zip','w',ZIP_DEFLATED) as z:
    for p in files:z.write(p,Path('C64-Keyboard')/p.relative_to(ROOT))
with ZipFile(ROOT/'C64-Keyboard.zip') as z:
    assert z.testzip() is None
    assert 'C64-Keyboard/glyphs/traced/004E.svg' in z.namelist()
print(f'Packaged {len(files)} files; {(ROOT/"C64-Keyboard.zip").stat().st_size:,} bytes')
