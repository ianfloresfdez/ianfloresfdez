"""Convierte foto-original.jpg en arte ASCII (una versión para tema oscuro y otra para claro).

Se ejecuta a mano solo cuando cambia la foto: python ascii.py
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

COLS, ROWS = 90, 66  # con letra de 8 px; menos resolución y los ojos se pierden
CROP = (220, 180, 940, 1257)  # cabeza y hombros (x0, y0, x1, y1) sobre la foto original
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"


def person_mask(im):
    """Fondo = zona azulada (B > R) conectada al borde superior; el resto es la persona."""
    blur = im.filter(ImageFilter.GaussianBlur(4))
    r, _, b = blur.split()
    px_r, px_b = r.load(), b.load()
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    m = mask.load()
    for y in range(h):
        for x in range(w):
            if px_b[x, y] - px_r[x, y] >= 5:
                m[x, y] = 128
    for seed in [(x, 2) for x in range(0, w, 40)] + [(2, y) for y in range(0, 700, 40)] + [(w - 3, y) for y in range(0, 900, 40)]:
        if mask.getpixel(seed) == 128:
            ImageDraw.floodfill(mask, seed, 255)
    bg = mask.point(lambda v: 255 if v == 255 else 0)
    bg = bg.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(9))  # suaviza bordes
    return ImageOps.invert(bg)


def to_ascii(gray, mask, invert):
    out = []
    g, mk = gray.load(), mask.load()
    for y in range(ROWS):
        row = ""
        for x in range(COLS):
            if mk[x, y] < 128:
                row += " "
                continue
            v = g[x, y] / 255
            if invert:
                v = 1 - v
            v = 0.08 + 0.92 * v  # mínimo de densidad para que la silueta se vea
            row += RAMP[min(len(RAMP) - 1, int(v * (len(RAMP) - 1)))]
        out.append(row.rstrip())
    return "\n".join(out) + "\n"


def main():
    im = Image.open("foto-original.jpg").convert("RGB")
    mask = person_mask(im).crop(CROP).resize((COLS, ROWS), Image.BILINEAR)
    gray = ImageOps.grayscale(im.crop(CROP))
    # normaliza la luz localmente: la mitad derecha de la cara está en sombra y el ojo se perdía
    a = np.asarray(gray, float)
    local = a / (np.asarray(gray.filter(ImageFilter.GaussianBlur(45)), float) + 20)
    a = 0.5 * local / np.percentile(local, 99) + 0.5 * a / 255
    gray = Image.fromarray(np.clip(a * 255, 0, 255).astype("uint8"))
    gray = ImageOps.autocontrast(gray, cutoff=1).point(lambda v: int(255 * (v / 255) ** 1.4))
    gray = gray.filter(ImageFilter.UnsharpMask(3, 160, 0)).resize((COLS, ROWS), Image.LANCZOS)
    with open("ascii_dark.txt", "w", encoding="utf-8") as f:
        f.write(to_ascii(gray, mask, invert=False))
    with open("ascii_light.txt", "w", encoding="utf-8") as f:
        f.write(to_ascii(gray, mask, invert=True))


if __name__ == "__main__":
    main()
