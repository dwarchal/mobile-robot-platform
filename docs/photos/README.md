# Photos

Parts and assembly photos. Every photo in this directory is resized to max. 1600 px on the long
side and has all metadata removed (EXIF incl. GPS, XMP, IPTC, thumbnails).

Before committing new photos:

```sh
python3 scripts/prepare_photos.py ~/raw-photos -o docs/photos
python3 scripts/prepare_photos.py --check docs/photos
```

Never commit original camera files. The `--check` also runs in CI on every push.

Naming: `YYYY-MM-DD-short-description.jpg`, e.g. `2026-11-14-romi-chassis-kit.jpg`.
