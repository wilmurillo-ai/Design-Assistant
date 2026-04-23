# Print Production Reference

Use this reference for: print-ready files, CMYK considerations, bleed/trim/safe zones, paper stock,
spot colors, die cuts, foil stamping, embossing, large format, production specifications, and any
design that will be physically printed.

---

## TABLE OF CONTENTS
1. Print Fundamentals
2. File Setup & Specifications
3. Color for Print
4. Paper & Substrates
5. Special Print Techniques
6. Common Print Formats
7. Pre-Flight Checklist
8. PDF Generation (Python)

---

## 1. PRINT FUNDAMENTALS

### Resolution
- **Print standard**: 300 DPI (dots per inch) minimum
- **Large format** (billboards, banners): 72-150 DPI (viewed from distance)
- **Screen printing**: 200-300 DPI
- **Newspaper**: 170-200 DPI

### Bleed, Trim, and Safe Zone

```
┌─── BLEED AREA (3mm / 0.125" beyond trim) ───┐
│  ┌─── TRIM LINE (final cut size) ──────────┐ │
│  │  ┌─── SAFE ZONE (5mm / 0.25" inside) ─┐ │ │
│  │  │                                      │ │ │
│  │  │    ALL IMPORTANT CONTENT             │ │ │
│  │  │    STAYS IN THIS ZONE                │ │ │
│  │  │                                      │ │ │
│  │  └──────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘

Bleed: Background colors/images extend PAST the trim line
Trim: Where the paper is physically cut
Safe: All text and critical elements stay INSIDE this boundary
```

### Units
- **Print design**: Points (pt), millimeters (mm), inches (in)
- **1 inch** = 72 points = 25.4mm
- **1 point** = 1/72 inch ≈ 0.353mm
- **Body text**: Typically 9-12pt for print (vs 16px for screen)

---

## 2. FILE SETUP & SPECIFICATIONS

### Standard Document Sizes

| Format | Dimensions (mm) | Dimensions (inches) |
|--------|-----------------|-------------------|
| A5 | 148 × 210 | 5.83 × 8.27 |
| A4 | 210 × 297 | 8.27 × 11.69 |
| A3 | 297 × 420 | 11.69 × 16.54 |
| A2 | 420 × 594 | 16.54 × 23.39 |
| US Letter | 216 × 279 | 8.5 × 11 |
| US Legal | 216 × 356 | 8.5 × 14 |
| Tabloid | 279 × 432 | 11 × 17 |
| Business Card (US) | 89 × 51 | 3.5 × 2 |
| Business Card (EU) | 85 × 55 | 3.35 × 2.17 |
| DL Envelope | 110 × 220 | 4.33 × 8.66 |
| #10 Envelope | 105 × 241 | 4.125 × 9.5 |

### File Format Requirements
- **PDF/X-1a**: Standard for print-ready files. CMYK only, fonts embedded, no transparency.
- **PDF/X-4**: Modern standard. Supports transparency, ICC profiles, layers.
- **TIFF**: For high-quality raster images. Uncompressed or LZW compression.
- **EPS**: Legacy vector format. Still accepted by some printers.
- **SVG**: NOT standard for print — convert to PDF before sending.

---

## 3. COLOR FOR PRINT

### CMYK vs RGB
- **Screen design**: RGB (additive color — light-based)
- **Print design**: CMYK (subtractive color — ink-based)
- **Key difference**: CMYK has a smaller color gamut. Vibrant blues, greens, and oranges
  in RGB cannot be exactly reproduced in CMYK. Always design in CMYK for print.

### CMYK Gotchas
- Pure black text: Use K=100 only (not C=0, M=0, Y=0, K=100 mixed with other channels)
- Rich black (for large black areas): C=40, M=30, Y=30, K=100
- Maximum ink coverage: Usually 300% total (C+M+Y+K ≤ 300). Some printers allow 320%.
- Registration marks: Use C=100, M=100, Y=100, K=100 (registration color)

### Spot Colors (Pantone)
- Used when exact color matching is critical (brand colors, metallic, neon)
- Printed with a dedicated ink, not CMYK mix
- Pantone Matching System (PMS) is the industry standard
- Specify as "PMS [number] C" (coated paper) or "PMS [number] U" (uncoated paper)
- Common special inks: Metallic gold/silver, fluorescent/neon, white (for dark substrates)

### Color Considerations
- **Paper affects color**: White paper vs cream paper vs colored stock changes how inks appear
- **Coated vs uncoated**: Coated paper = more vivid colors, uncoated = softer/muted
- **Proofing**: Always request a physical proof before a large print run
- **Color management**: Embed ICC profiles. US standard: SWOP for web offset, GRACoL for sheetfed.

---

## 4. PAPER & SUBSTRATES

### Paper Weight Systems
- **GSM (grams per square meter)**: International standard
  - 80gsm: Standard copy paper
  - 120gsm: Premium letterhead
  - 170-200gsm: Flyers, brochures
  - 250-350gsm: Business cards, postcards
  - 400gsm+: Rigid packaging, luxury cards

- **US weight system**: Confusingly based on the ream weight of a specific parent sheet size
  - 20lb bond = ~75gsm (copy paper)
  - 80lb text = ~120gsm (brochures)
  - 100lb cover = ~270gsm (cards)

### Paper Finishes
| Finish | Character | Best For |
|--------|-----------|----------|
| Matte | Non-reflective, easy to read | Text-heavy documents, fine art prints |
| Gloss | Shiny, vibrant colors | Photos, magazines, marketing materials |
| Satin/Silk | Between matte and gloss | Premium brochures, lookbooks |
| Uncoated | Natural texture, absorbent | Letterheads, books, eco-friendly brands |
| Linen | Textured, cross-hatch pattern | Certificates, luxury stationery |
| Kraft | Brown, recycled feel | Eco brands, packaging, rustic aesthetic |

---

## 5. SPECIAL PRINT TECHNIQUES

### Foil Stamping
- Metallic or colored foil pressed onto paper with a heated die
- Gold, silver, rose gold, holographic, colored foils
- Design consideration: Fine details may not transfer. Keep lines ≥0.5pt.
- Creates luxury, premium feel

### Embossing / Debossing
- **Emboss**: Raised impression from the surface
- **Deboss**: Pressed into the surface
- **Blind emboss**: No ink or foil, just the texture
- Design consideration: Works best on heavier stock (250gsm+). Minimum detail size: 1mm.

### Die Cutting
- Custom-shaped cuts through the paper
- Used for: Unique business card shapes, packaging windows, pop-up elements
- Design consideration: Provide a separate die line layer. Corners should have minimum 2mm radius.

### Spot UV / Spot Varnish
- Glossy varnish applied to specific areas of a matte surface
- Creates contrast between shiny and matte
- Popular for: Logo highlight, photo accents, premium business cards
- Design consideration: Provide on a separate layer. Avoid on very small text.

### Letterpress
- Traditional printing method pressing inked type into paper
- Creates a distinctive debossed/tactile impression
- Best on thick, soft, uncoated stock (300gsm+ cotton paper)
- Limited to 1-2 colors per pass

---

## 6. COMMON PRINT FORMATS

### Folding Patterns
```
BI-FOLD (4 panels):
┌────────┬────────┐
│ Inside │ Inside │
│ Left   │ Right  │
└────────┴────────┘
    ↕ fold ↕

TRI-FOLD (6 panels):
┌────────┬────────┬────────┐
│ Panel  │ Panel  │ Panel  │
│   1    │   2    │   3    │
└────────┴────────┴────────┘
Note: Panel 3 (the flap that folds in) is 1-2mm narrower

Z-FOLD (6 panels):
Same as tri-fold but folds in opposite directions (accordion style)

GATE FOLD (4 panels):
┌───┬────────────┬───┐
│   │            │   │
│ L │   Center   │ R │
│   │            │   │
└───┴────────────┴───┘
Left and right panels fold inward to meet at center
```

### Binding Methods
- **Saddle stitch**: Stapled through the spine. Up to ~64 pages. Most economical.
- **Perfect binding**: Pages glued to a flat spine. Books, thick magazines. 48+ pages.
- **Spiral/Wire-O**: Metal wire binding. Lies flat when open. Notebooks, calendars.
- **Case binding (hardcover)**: Pages sewn and glued into rigid boards. Premium books.
- **Japanese stab binding**: Decorative exposed stitching. Art books, portfolios.

---

## 7. PRE-FLIGHT CHECKLIST

Before sending any file to print, verify:

- [ ] **Resolution**: All images 300 DPI at final print size
- [ ] **Color mode**: CMYK (not RGB)
- [ ] **Bleed**: 3mm (0.125") on all sides where color/images reach the edge
- [ ] **Safe zone**: All text and important elements 5mm (0.25") inside trim
- [ ] **Fonts**: All fonts embedded or converted to outlines
- [ ] **Black text**: Uses K=100 only (not rich black for small text)
- [ ] **Rich black areas**: C=40, M=30, Y=30, K=100 for large black surfaces
- [ ] **Total ink coverage**: Under 300% (C+M+Y+K)
- [ ] **Overprint**: Black text set to overprint (avoids knockout/white halo)
- [ ] **Transparency**: Flattened (for PDF/X-1a) or preserved (for PDF/X-4)
- [ ] **Trim marks**: Included if required by printer
- [ ] **Spelling**: Triple-checked (print is permanent!)
- [ ] **Proof**: Reviewed at actual size on screen or physical proof requested

---

## 8. PDF GENERATION (PYTHON / REPORTLAB)

### Basic Setup
```python
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch, pt
from reportlab.pdfgen import canvas
from reportlab.lib.colors import CMYKColor, HexColor

# Create PDF
c = canvas.Canvas("output.pdf", pagesize=A4)
width, height = A4  # 595.28 × 841.89 points

# CMYK colors
brand_blue = CMYKColor(0.85, 0.5, 0, 0.1)
rich_black = CMYKColor(0.4, 0.3, 0.3, 1.0)
paper_white = CMYKColor(0, 0, 0, 0)

# Add content
c.setFont("Helvetica-Bold", 24)
c.setFillColor(rich_black)
c.drawString(50*mm, height - 40*mm, "Document Title")

# Add bleed (extend document beyond trim)
# Create at trim size + 6mm (3mm bleed each side)
# Adjust all coordinates by +3mm

c.save()
```

### Print-Ready PDF with Bleed
```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

bleed = 3 * mm
trim_w, trim_h = A4
page_w = trim_w + 2 * bleed
page_h = trim_h + 2 * bleed

c = canvas.Canvas("print_ready.pdf", pagesize=(page_w, page_h))

# Background (extends to bleed)
c.setFillColorRGB(0.05, 0.05, 0.15)
c.rect(0, 0, page_w, page_h, fill=1)

# Trim marks
c.setStrokeColorRGB(0, 0, 0)
c.setLineWidth(0.25)
mark_len = 5 * mm
# Top-left
c.line(bleed, page_h - bleed, bleed, page_h - bleed + mark_len)
c.line(bleed, page_h - bleed, bleed - mark_len, page_h - bleed)
# ... repeat for all four corners

# Content (offset by bleed)
c.setFont("Helvetica", 12)
c.setFillColorRGB(1, 1, 1)
c.drawString(bleed + 20*mm, page_h - bleed - 30*mm, "Content starts here")

c.save()
```
