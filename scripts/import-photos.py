"""Copy the photos each post used on the old Squarespace site from your own
photo library (e.g. a TrueNAS share) into the website, resized for the web.

It reads scripts/squarespace-photos.json (every post's photos, in gallery
order), finds each file by name anywhere under the folder you give it, and
writes a 2560 px high-quality JPEG to src/photos/<section>/<post>/.

Photos Squarespace renamed to "Photo Jul 06 2024, 7 16 58 PM.jpg" are found
by the time they were taken (from the photo's EXIF data) instead.

Usage, from the project folder:

    pip install pillow            # once  (optional: pip install rawpy  for RAW-only matches)
    python3 scripts/import-photos.py "/Volumes/photos" --check    # just report what it can find
    python3 scripts/import-photos.py "/Volumes/photos"            # copy + resize

On Windows the folder looks like  "\\\\truenas\\photos"  or  "Z:\\Photos".
Already-imported photos are skipped, so it is safe to run again.
"""
import argparse, json, os, re, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, 'scripts', 'squarespace-photos.json')
REPORT = os.path.join(ROOT, 'scripts', 'photo-import-report.txt')

IMG_EXT = {'.jpg', '.jpeg', '.tif', '.tiff', '.png'}
RAW_EXT = {'.arw', '.dng', '.cr2', '.cr3', '.nef', '.raf', '.orf', '.rw2'}
SKIP_DIRS = {'.zfs', '@eaDir', '.Trash', '$RECYCLE.BIN', 'node_modules', '.git'}
DATE_NAME = re.compile(r'^Photo (\w{3} \d{1,2} \d{4}), (\d{1,2}) (\d\d) (\d\d) ([AP]M)$', re.I)


def norm(stem):
    return stem.strip().lower()


def variants(stem):
    """Exact name first, then without copy suffixes like ' 2', ' (1)', '-2'."""
    s = norm(stem)
    out = [s]
    for pat in (r'\s*\(\d+\)$', r'\s+\d+$', r'-\d+$'):
        t = re.sub(pat, '', s)
        if t and t not in out:
            out.append(t)
    return out


def index_library(sources):
    by_name, images = {}, []
    for src in sources:
        for dirpath, dirnames, filenames in os.walk(src):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
            for f in filenames:
                stem, ext = os.path.splitext(f)
                ext = ext.lower()
                if ext in IMG_EXT or ext in RAW_EXT:
                    path = os.path.join(dirpath, f)
                    by_name.setdefault(norm(stem), []).append(path)
                    if ext in IMG_EXT:
                        images.append(path)
    return by_name, images


def best(paths):
    """Prefer finished images over RAW files, then the largest (highest-resolution) file."""
    def key(p):
        ext = os.path.splitext(p)[1].lower()
        try:
            size = os.path.getsize(p)
        except OSError:
            size = 0
        return (ext in IMG_EXT, size)
    return max(paths, key=key)


def taken_at(path):
    try:
        with Image.open(path) as im:
            exif = im.getexif()
            value = exif.get_ifd(0x8769).get(36867) or exif.get(306)  # DateTimeOriginal, DateTime
            return value.strip() if value else None
    except Exception:
        return None


def target_time(stem):
    m = DATE_NAME.match(stem)
    if not m:
        return None
    day, h, mi, s, ampm = m.groups()
    dt = datetime.strptime(f'{day} {h}:{mi}:{s} {ampm.upper()}', '%b %d %Y %I:%M:%S %p')
    return dt.strftime('%Y:%m:%d %H:%M:%S')


def open_image(path):
    if os.path.splitext(path)[1].lower() in RAW_EXT:
        import rawpy  # only needed when a photo exists only as a RAW file
        with rawpy.imread(path) as raw:
            return Image.fromarray(raw.postprocess(use_camera_wb=True, output_bps=8))
    return Image.open(path)


def convert(src, dest, long_edge, quality):
    im = open_image(src)
    icc = im.info.get('icc_profile')
    im = ImageOps.exif_transpose(im).convert('RGB')
    im.thumbnail((long_edge, long_edge), Image.LANCZOS)
    tmp = dest + '.part'
    # EXIF (including any GPS location) is intentionally not copied to the web version.
    im.save(tmp, 'JPEG', quality=quality, optimize=True, progressive=True, subsampling=0, icc_profile=icc)
    os.replace(tmp, dest)
    return im.size


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('sources', nargs='+', help='folder(s) to search, e.g. your TrueNAS photo share')
    ap.add_argument('--check', action='store_true', help='only report what can be found; copy nothing')
    ap.add_argument('--only', help='only posts whose folder contains this text')
    ap.add_argument('--size', type=int, default=2560, help='long edge in pixels (default 2560)')
    ap.add_argument('--quality', type=int, default=88, help='JPEG quality (default 88)')
    args = ap.parse_args()

    for s in args.sources:
        if not os.path.isdir(s):
            sys.exit(f'Folder not found: {s}')

    manifest = json.load(open(MANIFEST))
    print('Indexing your photo library (this can take a minute on a network share)...')
    by_name, images = index_library(args.sources)
    print(f'  {sum(len(v) for v in by_name.values())} photo files found\n')

    jobs, missing, raw_only = [], [], []
    time_index = None
    for folder, urls in manifest.items():
        if args.only and args.only not in folder:
            continue
        seen = set()
        for i, url in enumerate(urls):
            name = urllib.parse.unquote_plus(url.rsplit('/', 1)[-1])
            stem = os.path.splitext(name)[0]
            if norm(stem) in seen:  # header photo repeated in the gallery
                continue
            seen.add(norm(stem))
            found = None
            for v in variants(stem):
                if v in by_name:
                    found = best(by_name[v])
                    break
            if not found and (t := target_time(stem)):
                if time_index is None:
                    print('Reading capture times to match renamed "Photo ..." files...')
                    time_index = {}
                    with ThreadPoolExecutor(8) as pool:
                        for p, when in zip(images, pool.map(taken_at, images)):
                            if when:
                                time_index.setdefault(when, []).append(p)
                if t in time_index:
                    found = best(time_index[t])
            dest = os.path.join(ROOT, 'src', 'photos', folder, f'{i + 1:03d}-{stem}.jpg')
            if not found:
                missing.append(f'{folder}/{name}')
                continue
            if os.path.splitext(found)[1].lower() in RAW_EXT:
                raw_only.append(f'{folder}/{name}  <-  {found}')
            jobs.append((found, dest, folder, name))

    total = len(jobs) + len(missing)
    lines = [f'Found {len(jobs)} of {total} photos.', '']
    if missing:
        lines += [f'Not found ({len(missing)}):'] + [f'  {m}' for m in missing] + ['']
    if raw_only:
        lines += [f'Only a RAW file was found ({len(raw_only)}) - these need "pip install rawpy",',
                  'or export them as JPEG from Lightroom into your library and run again:'] + [f'  {r}' for r in raw_only] + ['']
    open(REPORT, 'w').write('\n'.join(lines))
    print('\n'.join(lines[:1]))
    print(f'Full list saved to {os.path.relpath(REPORT, ROOT)}\n')

    if args.check:
        return

    todo = [j for j in jobs if not os.path.exists(j[1])]
    print(f'Importing {len(todo)} photos ({len(jobs) - len(todo)} already done)...')

    def work(job):
        src, dest, folder, name = job
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            w, h = convert(src, dest, args.size, args.quality)
            return f'ok    {folder}/{os.path.basename(dest)}  {w}x{h}'
        except Exception as e:
            return f'FAIL  {folder}/{name}: {e}'

    fails = 0
    with ThreadPoolExecutor(4) as pool:
        for n, msg in enumerate(pool.map(work, todo), 1):
            fails += msg.startswith('FAIL')
            print(f'[{n}/{len(todo)}] {msg}')
    print(f'\nDone. {len(todo) - fails} imported, {fails} failed, {len(missing)} not found.')
    print('Next: commit and push the new files in src/photos to GitHub to publish them.')


if __name__ == '__main__':
    main()
