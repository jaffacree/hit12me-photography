"""Download the original photos used on the old Squarespace site into src/photos/.

Each photo is resized to 2560 px on its long edge (high-quality JPEG) so the
repository stays a manageable size. Photos already downloaded are skipped.

Usage (from the project folder):  python3 scripts/fetch-squarespace-photos.py
Needs: pip install pillow
"""
import io, json, os, sys, time, urllib.request
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, 'scripts', 'squarespace-photos.json')
LONG_EDGE, QUALITY = 2560, 88

def fetch(url, tries=4):
    for n in range(tries):
        try:
            with urllib.request.urlopen(url + '?format=original', timeout=60) as r:
                return r.read()
        except Exception as e:
            if n == tries - 1: raise
            time.sleep(2 ** n)

def main(only=None):
    manifest = json.load(open(MANIFEST))
    done = failed = 0
    for folder, urls in manifest.items():
        if only and only not in folder: continue
        out = os.path.join(ROOT, 'src', 'photos', folder)
        os.makedirs(out, exist_ok=True)
        for i, url in enumerate(urls):
            name = urllib.request.unquote(url.rsplit('/', 1)[-1])
            stem = os.path.splitext(name)[0]
            # Prefix keeps the Squarespace gallery order.
            dest = os.path.join(out, f'{i + 1:03d}-{stem}.jpg')
            if os.path.exists(dest): continue
            try:
                im = ImageOps.exif_transpose(Image.open(io.BytesIO(fetch(url))))
                im = im.convert('RGB')
                im.thumbnail((LONG_EDGE, LONG_EDGE), Image.LANCZOS)
                im.save(dest, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
                done += 1
                print(f'ok   {folder}/{os.path.basename(dest)} {im.size[0]}x{im.size[1]}')
            except Exception as e:
                failed += 1
                print(f'FAIL {folder}/{name}: {e}', file=sys.stderr)
    print(f'\n{done} downloaded, {failed} failed')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
