# Building C64 Keyboard

Run commands from the repository root. The checked-in SVG outlines and mapping files are sufficient to rebuild the fonts; original photographs are not required.

## Environment

The current build is verified with Python 3.14 on macOS.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The font builder uses FontTools. Outline construction also uses skia-pathops. Specimen and validation scripts use Pillow and currently reference macOS Helvetica at `/System/Library/Fonts/Helvetica.ttc`; on another platform, change those UI-font paths to an installed font. The font build itself does not depend on Helvetica.

## Build from saved outlines

```sh
.venv/bin/python scripts/build_font.py
.venv/bin/python scripts/verify_font.py
.venv/bin/python scripts/verify_geometry.py
.venv/bin/python scripts/make_specimen.py
.venv/bin/python scripts/make_petscii_specimen.py
.venv/bin/python scripts/make_comparison.py
.venv/bin/python scripts/make_reference_comparison.py
.venv/bin/python scripts/package_font.py
```

The outputs are TTF, OTF, and WOFF2 fonts in `fonts/`, a character map, specimen and comparison PNGs, and `C64-Keyboard.zip`. Validation also writes `build/validation.json` and `build/all-glyphs.png` for inspection. Open `preview.html` to check the webfont and insertion buttons.

Version 1.109 has 202 glyphs and 262 mapped characters. Validation checks printable ASCII, uppercase/lowercase aliases, numeral widths, function-key labels, all 63 PETSCII legends, outline bounds, and font-table round trips. The geometry check covers the original letters, numbers, and paired punctuation.

## Regenerate geometric outlines

Only run these when changing construction parameters or intentionally regenerating outlines; they overwrite the corresponding editable SVGs.

```sh
.venv/bin/python scripts/normalize_glyphs.py
.venv/bin/python scripts/build_petscii.py
```

Then run the build and validation sequence above. `normalize_glyphs.py` reconstructs the 64 core shapes using the saved reference metadata. `build_petscii.py` reconstructs the 63 graphics and their thin cell frames; pi remains unframed.

## Sources and mappings

| Path | Purpose |
| --- | --- |
| `glyphs/*.svg` | Editable core lettering outlines |
| `glyphs/traced/` | Saved traces from the original photographs |
| `glyphs/high-resolution/` | Saved traces from the newer camera references |
| `glyphs/source-map.json` | Original crops and source metadata |
| `glyphs/high-resolution-map.json` | Newer crops and source metadata |
| `glyphs/reference-review.json` | Photo-review decisions and refinements |
| `glyphs/normalization.json` | Core geometry assumptions and provenance |
| `glyphs/petscii/` | Editable PETSCII front-legend outlines |
| `glyphs/petscii-map.json` | Key assignments and code mappings |
| `fonts/character-map.json` | Built glyph coverage and provenance |

The photo-review record retains version 1.106, when that review was made. The core normalization record is at 1.109, when S, @, and the text punctuation were revised. Version 1.107 added PETSCII; version 1.108 removed the former U+E000 symbol.

## Optional photo extraction

This workflow requires the original private photographs, which are excluded from Git and the download package. It also requires the `potrace` executable; HEIC conversion uses macOS `sips`.

- `prepare_references.py` converts the original HEIC photographs from `source/` into `build/full/`.
- `extract_glyphs.py` saves original traces in `glyphs/traced/`.
- `extract_new_references.py` uses LSZ camera JPEGs in `source/better/` (or `source/`) and saves separate traces in `glyphs/high-resolution/`.
- `review_references.py` renders the private photograph comparisons into `build/better/`.

Photo traces retain perspective and print wear. Geometric construction is an interpretation of the intended printed design, not a camera calibration or an exact recovery of manufacturing artwork.

## Packaging

`package_font.py` includes documentation, fonts, editable outlines, mapping files, Python scripts, the HTML preview, and public specimen/comparison images. It excludes `.venv/`, `build/`, and `source/`. The ZIP has one `C64-Keyboard/` root directory; extract it before opening the preview.
