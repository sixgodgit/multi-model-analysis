# Infographic Pipeline (HTML → PNG)

When image generation APIs are unavailable, convert HTML infographics to PNG via weasyprint + pdftoppm.

## Pipeline

```
1. write_file → dark-themed HTML (1000px wide, compact layout)
2. weasyprint HTML → PDF
3. pdftoppm PDF → PNG (200 dpi)
4. PIL resize to 900px wide, compress to ~400KB
5. Send via MEDIA: path in response
```

## Key Commands

```bash
# Step 2
python3 -c "from weasyprint import HTML; HTML('/tmp/input.html').write_pdf('/tmp/output.pdf')"

# Step 3
pdftoppm -png -r 200 /tmp/output.pdf /tmp/output

# Step 4
python3 -c "
from PIL import Image
im = Image.open('/tmp/output-1.png')
ratio = 900 / im.width
im_resized = im.resize((900, int(im.height * ratio)), Image.LANCZOS)
im_resized.save('/tmp/final.png', optimize=True, quality=85)
"
```

## HTML Design Rules for WeasyPrint

- Set explicit `width: 1000px` on body (PDF page renders at fixed width)
- Use inline Google Fonts (works with weasyprint)
- Compact layout: smaller fonts (10-14px), tighter spacing (4-8px gaps), simpler decorations
- Single-column for columns, or 3-column grid with `grid-template-columns: 1fr 1fr 1fr`
- Test with weasyprint first: if content overflows to 2+ pages, reduce font sizes or trim content
- Avoid `position: absolute` / `position: fixed` — weasyprint handles them poorly
- Avoid `box-shadow` with large blur radius (renders slowly)
- Use `border-image: linear-gradient(...)` carefully — weasyprint may not support it

## Pitfalls

- weasyprint.online (Google Fonts) can fail if the server has no internet. Fall back to system fonts.
- 3+ pages = too long. One page max (2300px at 200dpi). Reduce content density if needed.
- `pdftoppm -r 200` is the sweet spot: readable text + reasonable file size.
- After resize + compression, stay under 500KB for QQ/Telegram delivery.
- Google Fonts imports block rendering — consider pre-warming via curl.
