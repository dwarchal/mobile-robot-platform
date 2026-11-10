#!/usr/bin/env python3
"""Prepare photos for this public repo: resize and strip all metadata.

Usage:
    prepare_photos.py SRC... -o docs/photos     # process files/dirs into the output dir
    prepare_photos.py --check docs/photos       # verify: no metadata, long side <= limit

What it does:
  * applies the EXIF orientation to the pixels (so the photo is not rotated after stripping),
  * scales the long side down to --max-px (default 1600); smaller photos are not upscaled,
  * writes a new file from pixels only: no EXIF (incl. GPS, camera serial, date), no XMP,
    no IPTC, no comments, no embedded thumbnails,
  * JPEG/HEIC -> .jpg (quality 85), PNG -> .png.

Requires Pillow (HEIC input additionally needs pillow-heif).
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}


def iter_images(paths):
    for p in map(Path, paths):
        if p.is_dir():
            yield from sorted(f for f in p.rglob("*") if f.suffix.lower() in EXTS)
        elif p.suffix.lower() in EXTS:
            yield p


def process(src: Path, out_dir: Path, max_px: int) -> Path:
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        im.thumbnail((max_px, max_px), Image.LANCZOS)
        is_png = src.suffix.lower() == ".png"
        mode = "RGBA" if is_png and im.mode in ("RGBA", "LA", "P") else "RGB"
        # Copy pixels only into a fresh image -> nothing from the original info survives.
        clean = Image.new(mode, im.size)
        clean.paste(im.convert(mode))
    dst = out_dir / (src.stem.lower().replace(" ", "-") + (".png" if is_png else ".jpg"))
    if is_png:
        clean.save(dst, "PNG", optimize=True)
    else:
        clean.save(dst, "JPEG", quality=85, optimize=True, progressive=True)
    return dst


def problems(path: Path, max_px: int):
    found = []
    with Image.open(path) as im:
        if max(im.size) > max_px:
            found.append(f"size {im.size[0]}x{im.size[1]} > {max_px}")
        if len(im.getexif()):
            found.append("EXIF present")
        keys = set(im.info) - {"jfif", "jfif_version", "jfif_unit", "jfif_density",
                               "dpi", "progressive", "progression", "adobe",
                               "adobe_transform", "gamma"}
        if keys:
            found.append("metadata: " + ", ".join(sorted(keys)))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("-o", "--out", type=Path, help="output directory")
    ap.add_argument("--max-px", type=int, default=1600)
    ap.add_argument("--check", action="store_true", help="only verify files, change nothing")
    args = ap.parse_args()

    try:
        import pillow_heif  # noqa: F401
        pillow_heif.register_heif_opener()
    except ImportError:
        pass

    files = list(iter_images(args.paths))
    if args.check:
        bad = 0
        for f in files:
            if found := problems(f, args.max_px):
                bad += 1
                print(f"FAIL {f}: {'; '.join(found)}")
        print(f"{len(files) - bad}/{len(files)} OK")
        return 1 if bad else 0

    if not args.out:
        ap.error("-o/--out is required unless --check is used")
    args.out.mkdir(parents=True, exist_ok=True)
    for f in files:
        dst = process(f, args.out, args.max_px)
        with Image.open(dst) as im:
            print(f"{f} -> {dst} ({im.size[0]}x{im.size[1]}, {dst.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
