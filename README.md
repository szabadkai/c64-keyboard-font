# C64 Keyboard

An installable vector reconstruction of the **printed lettering on classic Commodore 64 keycaps**, traced from close-up photographs of a physical keyboard.

![C64 Keyboard font specimen showing the alphabet, numerals, punctuation, arrows, and function-key legends](specimen.png)

**[Download the font (TTF)](fonts/C64Keyboard-Regular.ttf?raw=true)** · [OTF](fonts/C64Keyboard-Regular.otf?raw=true) · [Webfont (WOFF2)](fonts/C64Keyboard-Regular.woff2?raw=true) · [Complete package](C64-Keyboard.zip?raw=true)

Download or clone this repository and open [preview.html](preview.html) locally to type with the font, change its size and background, and insert special key legends. Keep it beside the `fonts/` folder. The [specimen image](specimen.png) above shows the actual font; GitHub's README does not load custom webfonts.

## Install and use

- [C64Keyboard-Regular.ttf](fonts/C64Keyboard-Regular.ttf?raw=true) — recommended desktop font. On macOS, double-click and choose Install Font.
- [C64Keyboard-Regular.otf](fonts/C64Keyboard-Regular.otf?raw=true) — the same design with PostScript outlines. Install either this or the TTF; they share a family name.
- [C64Keyboard-Regular.woff2](fonts/C64Keyboard-Regular.woff2?raw=true) — webfont. The preview demonstrates a local `@font-face` declaration.

The family appears as **C64 Keyboard**, style **Regular**. No font has been installed automatically.

## Character coverage

136 glyphs with 195 mapped Unicode characters, including all printable ASCII, uppercase Latin letters, digits, punctuation, £, four arrows, and selected accented Latin letters (including Á É Í Ó Ö Ő Ú Ü Ű).

- Lowercase input intentionally maps to the corresponding uppercase outline. There is no separate lowercase alphabet on these photographed keys.
- Numerals use equal advances. Letters use proportional spacing with a few kerning pairs.
- The zero keeps its slash; I is a plain vertical stroke; Q keeps its hooked tail.
- Brackets retain the angled shapes printed above colon and semicolon.
- The original on-screen bitmap font and the full set of graphics on the fronts of the keys are outside this reconstruction.

## Special key legends

Use the buttons in the preview to insert these private-use characters into the type tester. They can then be selected and copied. These glyphs are also available through applications with a Unicode glyph palette.

| Unicode | Legend |
|---|---|
| U+E000 | Photographed Commodore key symbol |
| U+E001 | Function-key lowercase f |
| U+E010–U+E017 | f1 through f8 |
| U+E020 | CTRL |
| U+E021 | RUN / STOP |
| U+E022 | SHIFT / LOCK |
| U+E023 | SHIFT |
| U+E024 | RETURN |
| U+E025 | RESTORE |
| U+E026 | CLR / HOME |
| U+E027 | INST / DEL |
| U+E028 | CRSR |

The multi-letter and function legends are composed from the reconstructed characters. Ordinary words are never replaced automatically by key labels.

## How it was reconstructed

65 core shapes were traced from the supplied close-ups. The process isolates the dark printing, removes small surface defects, fits smooth curves, and normalizes cap height and bearings. The outline shapes retain some of the photographed printing's asymmetry; this is a photo-based reconstruction, not a claim to recover the manufacturer's original master artwork.

C comes from the **CTRL** key in IMG_0318; there is no dedicated C close-up in the supplied sequence. Function f comes from IMG_0349. The Commodore symbol comes from IMG_0348. Original photographs are kept locally and are not included in this public repository. The editable vector outlines and source mapping are included.

The right and down arrows are reflected from the photographed left and up arrows. Missing ASCII utility symbols, typographic punctuation, and accent marks are constructed additions. `fonts/character-map.json` identifies the origin of every distinct mapped outline. `glyphs/source-map.json` records the photograph and crop for each directly traced shape. Crop coordinates refer to upright 1000-pixel-wide previews; the extraction itself uses full-resolution decodes.

This is an independent, unofficial reconstruction. The name and photographed logo identify the source keyboard; they do not imply endorsement.

## Editable sources and rebuilding

`glyphs/*.svg` are the editable core outlines, with filenames corresponding to hexadecimal Unicode values. The SVG uses a flipped display group around Cartesian font coordinates. Edit the path's coordinates and run the font builder to keep edits. Running the extraction script again overwrites those core SVGs.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_font.py
.venv/bin/python scripts/make_specimen.py
.venv/bin/python scripts/verify_font.py
```

To retrace the photographs from scratch on macOS, place the original photographs in the local `source/` directory. This optional step requires those photographs, which are not distributed here, plus `sips` and the `potrace` executable:

```sh
.venv/bin/python scripts/prepare_references.py
.venv/bin/python scripts/extract_glyphs.py
.venv/bin/python scripts/build_font.py
.venv/bin/python scripts/make_specimen.py
```

The font builder works from the saved SVGs without needing HEIC support or Potrace. The specimen renderer uses the macOS system Helvetica font for its captions. `build/` and `.venv/` are disposable working files.
