from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance

HERE = Path(__file__).parent
PLATE = (13, 17, 23)
PAD = 0.10
SUBJECT_SCALE = 0.98
CONTRAST = 1.18
SATURATION = 1.15
THRESHOLD = 26
S = 4

def find_source():
    for name in ("groot-source.png", "groot-source.jpg", "groot-source.jpeg", "groot-source.webp"):
        p = HERE / name
        if p.exists():
            return p
    raise SystemExit("No source image found.")

def subject_bbox(img):
    gray = img.convert("L")
    mask = gray.point(lambda v: 255 if v > THRESHOLD else 0)
    box = mask.getbbox()
    if box is None:
        raise SystemExit("Could not find the subject.")
    return box

def square_crop(img):
    left, top, right, bottom = subject_bbox(img)
    w, h = right - left, bottom - top
    side = int(max(w, h) * (1 + PAD * 2))
    cx, cy = left + w / 2, top + h / 2
    x0, y0 = int(cx - side / 2), int(cy - side / 2)
    canvas = Image.new("RGB", (side, side), PLATE)
    src_box = (max(x0, 0), max(y0, 0), min(x0 + side, img.width), min(y0 + side, img.height))
    region = img.crop(src_box)
    canvas.paste(region, (src_box[0] - x0, src_box[1] - y0))
    return canvas

def build(face, size, rounded=True):
    g = size * S
    icon = Image.new("RGBA", (g, g), (0, 0, 0, 0))
    plate = Image.new("RGBA", (g, g), PLATE + (255,))
    if rounded:
        mask = Image.new("L", (g, g), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, g - 1, g - 1], radius=int(g * 0.22), fill=255)
        icon.paste(plate, (0, 0), mask)
    else:
        icon.paste(plate, (0, 0))
    inner = int(g * SUBJECT_SCALE)
    art = face.resize((inner, inner), Image.LANCZOS).convert("RGBA")
    off = (g - inner) // 2
    if rounded:
        art_mask = Image.new("L", (g, g), 0)
        ImageDraw.Draw(art_mask).rounded_rectangle([0, 0, g - 1, g - 1], radius=int(g * 0.22), fill=255)
        layer = Image.new("RGBA", (g, g), (0, 0, 0, 0))
        layer.paste(art, (off, off))
        icon = Image.composite(layer, icon, art_mask.point(lambda v: 255 if v > 128 else 0))
        out = Image.new("RGBA", (g, g), (0, 0, 0, 0))
        out.paste(icon, (0, 0), art_mask)
        icon = out
    else:
        icon.paste(art, (off, off))
    return icon.resize((size, size), Image.LANCZOS)

def main():
    src = find_source()
    print(f"source: {src.name}")
    img = Image.open(src).convert("RGB")
    face = square_crop(img)
    face = ImageEnhance.Contrast(face).enhance(CONTRAST)
    face = ImageEnhance.Color(face).enhance(SATURATION)
    face.save(HERE / "groot-face.png")
    print("wrote groot-face.png — check this first")
    targets = {
        16: "favicon-16.png",
        32: "favicon-32.png",
        180: "apple-touch-icon.png",
        192: "icon-192.png",
        512: "icon-512.png",
    }
    for size, name in targets.items():
        icon = build(face, size, rounded=(size != 180))
        if size == 180:
            flat = Image.new("RGB", (size, size), PLATE)
            flat.paste(icon, (0, 0), icon)
            icon = flat
        icon.save(HERE / name)
        print("wrote", name)
    build(face, 64).save(HERE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print("wrote favicon.ico")
    svg = HERE / "favicon.svg"
    if svg.exists():
        svg.unlink()
        print("removed favicon.svg")

if __name__ == "__main__":
    main()
