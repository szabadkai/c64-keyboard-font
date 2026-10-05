"""Decode original HEIC files with macOS sips; retain upright pixel order."""
from pathlib import Path
import concurrent.futures
import subprocess
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
def convert(p):
    out=ROOT/'build/full'/f'{p.stem}.png'
    if not out.exists():
        subprocess.run(['sips','-s','format','png',str(p),'--out',str(out)],capture_output=True,check=True)
        im=Image.open(out)
        # sips has already oriented the pixels. Remove the stale orientation tag.
        im.save(out,exif=b'')
    return out
if __name__=='__main__':
    (ROOT/'build/full').mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        paths=list(pool.map(convert,sorted((ROOT/'source').glob('*.HEIC'))))
    print(f'Decoded {len(paths)} photographs')
