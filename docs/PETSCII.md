# PETSCII front legends

The font includes 63 graphic legends from the fronts of the C64 keys. On the keyboard, the left legend is produced with **Commodore + key**, and the right legend with **Shift + key**, in **uppercase/graphics mode**. Pi is printed alone on the up-arrow key and works with either modifier.

![PETSCII reference sheet](../petscii-specimen.png)

## Insert and copy

Open the extracted package's `preview.html`, scroll to **PETSCII front legends**, and click a symbol. It is inserted at the cursor in the type tester. Copy the resulting text and select **C64 Keyboard** in the destination application. If the destination uses another font, private-use characters may appear as empty boxes or unrelated symbols.

The buttons insert Unicode characters for this font. They do not send C64 key combinations or produce a PETSCII-encoded file.

## Three different codes

- **PETSCII byte:** the character value produced by the C64 keyboard. The picker and reference sheet label these in hexadecimal, with a `$` prefix.
- **Screen code:** the character-cell index used by the C64 display. This differs from the PETSCII byte.
- **Font code point:** the Unicode private-use character used to select the reconstructed legend in this font.

The font code is **U+E100 plus the screen code**: U+E140–U+E17F, excluding U+E160. The omitted screen code `$60` is a blank space with no printed graphic legend. Existing space characters remain available normally.

For example, **Shift + A** produces the spade: PETSCII `$C1` (193), screen code `$41` (65), font character **U+E141**. To insert it programmatically in Python or JavaScript, use the string `"\uE141"` and render it with C64 Keyboard.

The `unicode` field in [petscii-map.json](../glyphs/petscii-map.json) records the corresponding standard Unicode symbol for reference. Those standard code points are not aliases for the framed glyphs. This font does not decode arbitrary PETSCII byte streams or implement C64 control codes, reverse video, or character-set switching.

## Key map

Each cell below gives **PETSCII byte / font code point**. The exact screen code, symbol name, and modifier are also recorded in the [JSON map](../glyphs/petscii-map.json).

| Key | Commodore: left legend | Shift: right legend |
| --- | --- | --- |
| Q | `$AB` / `U+E16B` | `$D1` / `U+E151` |
| W | `$B3` / `U+E173` | `$D7` / `U+E157` |
| E | `$B1` / `U+E171` | `$C5` / `U+E145` |
| R | `$B2` / `U+E172` | `$D2` / `U+E152` |
| T | `$A3` / `U+E163` | `$D4` / `U+E154` |
| Y | `$B7` / `U+E177` | `$D9` / `U+E159` |
| U | `$B8` / `U+E178` | `$D5` / `U+E155` |
| I | `$A2` / `U+E162` | `$C9` / `U+E149` |
| O | `$B9` / `U+E179` | `$CF` / `U+E14F` |
| P | `$AF` / `U+E16F` | `$D0` / `U+E150` |
| A | `$B0` / `U+E170` | `$C1` / `U+E141` |
| S | `$AE` / `U+E16E` | `$D3` / `U+E153` |
| D | `$AC` / `U+E16C` | `$C4` / `U+E144` |
| F | `$BB` / `U+E17B` | `$C6` / `U+E146` |
| G | `$A5` / `U+E165` | `$C7` / `U+E147` |
| H | `$B4` / `U+E174` | `$C8` / `U+E148` |
| J | `$B5` / `U+E175` | `$CA` / `U+E14A` |
| K | `$A1` / `U+E161` | `$CB` / `U+E14B` |
| L | `$B6` / `U+E176` | `$CC` / `U+E14C` |
| Z | `$AD` / `U+E16D` | `$DA` / `U+E15A` |
| X | `$BD` / `U+E17D` | `$D8` / `U+E158` |
| C | `$BC` / `U+E17C` | `$C3` / `U+E143` |
| V | `$BE` / `U+E17E` | `$D6` / `U+E156` |
| B | `$BF` / `U+E17F` | `$C2` / `U+E142` |
| N | `$AA` / `U+E16A` | `$CE` / `U+E14E` |
| M | `$A7` / `U+E167` | `$CD` / `U+E14D` |
| + | `$A6` / `U+E166` | `$DB` / `U+E15B` |
| - | `$DC` / `U+E15C` | `$DD` / `U+E15D` |
| £ | `$A8` / `U+E168` | `$A9` / `U+E169` |
| @ | `$A4` / `U+E164` | `$BA` / `U+E17A` |
| * | `$DF` / `U+E15F` | `$C0` / `U+E140` |
| ↑ | Same pi as Shift | `$DE` / `U+E15E` |

## Reconstruction and sources

Key assignments, PETSCII bytes, screen codes, and Unicode equivalents were checked against Michael Steil and Lisa Brodner's [Ultimate Commodore 64 Reference](https://www.pagetable.com/c64ref/charset/). The [C64 OS keyboard map](https://c64os.com/post/keymap_toscreeneditor) documents modifier behavior.

The supplied keyboard photo establishes the printed legend style and use of thin square cell frames. The outlines are smooth geometric reconstructions, not exact photo traces or the C64 screen bitmap font. Frame thickness, suit curves, rounded corners, and print proportions are inferred. Pi is unframed.

Each legend uses an 830-unit advance around a 700-unit cell, with 65 units of space on each side. This supports consistent placement on keycap artwork; the framed, spaced legends are not intended as seamless screen-art tiles.

Editable SVGs are in [glyphs/petscii/](../glyphs/petscii/). See [BUILDING.md](BUILDING.md) for regeneration and validation.
