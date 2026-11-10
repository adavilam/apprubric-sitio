"""Genera la marca de AppRubric: SVG maestros, PNG y favicon.ico.

Concepto: una rúbrica de 3 criterios x 4 niveles (AI, AF, AS, AA). Cuatro celdas marcadas
forman un visto bueno (✓) que también es una línea de progreso que sube hasta el dorado (AA).
Uso, desde la carpeta prospecto-web: python -I marca/generar_marca.py .
(los archivos _ampliado_*.png que deja son solo para revisar los píxeles; no se publican)
"""
import os
import sys

from PIL import Image, ImageDraw

OUT = sys.argv[1]
os.makedirs(os.path.join(OUT, "marca"), exist_ok=True)

NAVY = (20, 40, 66)
DIM = (255, 255, 255, 26)
WHITE = (233, 237, 240)
TEAL = (89, 176, 160)
GOLD = (220, 176, 85)

# Celdas marcadas (col, fila) y su color: el trazo del visto bueno.
PATH = [((0, 1), WHITE), ((1, 2), TEAL), ((2, 1), TEAL), ((3, 0), GOLD)]


def hexc(c):
    return "#%02X%02X%02X" % c[:3]


# ---------- SVG maestro (lienzo 200) ----------
def isotipo_svg(with_bg=True):
    cell, gap, x0, y0 = 30, 8, 28, 47
    marked = {p for p, _ in PATH}
    parts = []
    if with_bg:
        parts.append('<rect width="200" height="200" rx="44" fill="#142842"/>')
    dim = []
    for r in range(3):
        for c in range(4):
            if (c, r) not in marked:
                dim.append(f'<rect x="{x0 + c * (cell + gap)}" y="{y0 + r * (cell + gap)}" width="{cell}" height="{cell}" rx="7"/>')
    parts.append('<g fill="#FFFFFF" fill-opacity="0.1">' + "".join(dim) + "</g>")
    pts = " ".join(f"{x0 + c * (cell + gap) + cell / 2:g},{y0 + r * (cell + gap) + cell / 2:g}" for (c, r), _ in PATH)
    parts.append(
        '<defs><linearGradient id="ar-trazo" x1="43" y1="0" x2="157" y2="0" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#E9EDF0"/><stop offset=".45" stop-color="#59B0A0"/>'
        '<stop offset="1" stop-color="#DCB055"/></linearGradient></defs>'
    )
    parts.append(f'<polyline points="{pts}" fill="none" stroke="url(#ar-trazo)" stroke-width="9" '
                 'stroke-linecap="round" stroke-linejoin="round"/>')
    for (c, r), color in PATH:
        parts.append(f'<rect x="{x0 + c * (cell + gap)}" y="{y0 + r * (cell + gap)}" width="{cell}" height="{cell}" rx="7" fill="{hexc(color)}"/>')
    return "".join(parts)


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


ISO = isotipo_svg()
write("marca/isotipo.svg",
      f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" role="img" aria-label="AppRubric">{ISO}</svg>\n')
write("favicon.svg",
      f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">{ISO}</svg>\n')

WORD_FONT = "'Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua',Georgia,serif"
SANS = "'Segoe UI',-apple-system,Roboto,Arial,sans-serif"


def lockup(ink, soft, tagline=True):
    tag = (f'<text x="234" y="176" font-family="{SANS}" font-size="23" letter-spacing="4" fill="{soft}">'
           'GESTIÓN EVALUATIVA · MINED</text>') if tagline else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 200" role="img" aria-label="AppRubric">'
            f'<g>{ISO}</g>'
            f'<text x="226" y="114" font-family="{WORD_FONT}" font-size="104" fill="{ink}" letter-spacing="-1">'
            f'App<tspan font-weight="700">Rubric</tspan></text>{tag}</svg>\n')


write("marca/logo-horizontal.svg", lockup("#142842", "#4C5F7A"))
write("marca/logo-horizontal-blanco.svg", lockup("#FFFFFF", "#AEBBC9"))


# ---------- PNG con píxeles ajustados ----------
def raster(size, cell, gap, x0, y0, bg_r, cell_r, line_w, dim_alpha=26):
    s = 8  # supermuestreo
    # Se dibuja sobre un fondo RGB opaco (así las celdas translúcidas se mezclan con el azul)
    # y al final se recortan las esquinas con una máscara.
    img = Image.new("RGB", (size * s, size * s), NAVY)
    d = ImageDraw.Draw(img, "RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size * s - 1, size * s - 1], radius=bg_r * s, fill=255)
    marked = {p for p, _ in PATH}

    def box(c, r):
        x = (x0 + c * (cell + gap)) * s
        y = (y0 + r * (cell + gap)) * s
        return [x, y, x + cell * s - 1, y + cell * s - 1]

    for r in range(3):
        for c in range(4):
            if (c, r) not in marked:
                d.rounded_rectangle(box(c, r), radius=cell_r * s, fill=(255, 255, 255, dim_alpha))
    if line_w:
        centers = [((x0 + c * (cell + gap) + cell / 2) * s, (y0 + r * (cell + gap) + cell / 2) * s) for (c, r), _ in PATH]
        stops = [WHITE, TEAL, TEAL, GOLD]
        steps = 60
        for i in range(len(centers) - 1):
            (ax, ay), (bx, by) = centers[i], centers[i + 1]
            for k in range(steps):
                t0, t1 = k / steps, (k + 1) / steps
                t = (t0 + t1) / 2
                col = tuple(int(stops[i][j] + (stops[i + 1][j] - stops[i][j]) * t) for j in range(3))
                d.line([(ax + (bx - ax) * t0, ay + (by - ay) * t0), (ax + (bx - ax) * t1, ay + (by - ay) * t1)],
                       fill=col + (255,), width=int(line_w * s))
            d.ellipse([ax - line_w * s / 2, ay - line_w * s / 2, ax + line_w * s / 2, ay + line_w * s / 2], fill=stops[i] + (255,))
    for (c, r), color in PATH:
        d.rounded_rectangle(box(c, r), radius=cell_r * s, fill=color + (255,))
    img = img.convert("RGBA")
    img.putalpha(mask)
    return img.resize((size, size), Image.LANCZOS)


def master(size):
    k = size / 200
    return raster(size, 30 * k, 8 * k, 28 * k, 47 * k, 44 * k, 7 * k, 9 * k)


# Tamaños chicos: rejilla ajustada al píxel, sin trazo en 16 (no se lee).
ico16 = raster(16, 2, 2, 1, 3, 3, 0.5, 0, dim_alpha=40)
ico32 = raster(32, 5, 2, 3, 6, 7, 1, 2, dim_alpha=32)
ico48 = raster(48, 8, 3, 3.5, 9.5, 10, 1.5, 2.5)

ico48.save(os.path.join(OUT, "favicon.ico"), format="ICO", sizes=[(16, 16), (32, 32), (48, 48)],
           bitmap_format="png", append_images=[ico16, ico32])
frames = {16: ico16, 32: ico32, 48: ico48}

master(180).convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"))
master(512).save(os.path.join(OUT, "marca", "isotipo-512.png"))
master(1024).save(os.path.join(OUT, "marca", "isotipo-1024.png"))
for n, im in frames.items():
    im.resize((n * 8, n * 8), Image.NEAREST).save(os.path.join(OUT, f"_ampliado_{n}.png"))
print("ok")
