#!/usr/bin/env python3
"""Apply the miniature / tilt-shift grade to a Blender render."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / max(edge1 - edge0, 1e-6), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def vertical_tilt_mask(width, height, focus_y=0.52, band=0.20, feather=0.27):
    yy = np.arange(height, dtype=np.float32) / max(height - 1, 1)
    distance = np.abs(yy - focus_y)
    weight = smoothstep(band, band + feather, distance)
    return np.repeat(weight[:, None], width, axis=1)


def process(src, dst):
    image = Image.open(src).convert("RGB")
    width, height = image.size

    # Warm, saturated miniature grade.
    image = ImageEnhance.Color(image).enhance(1.38)
    image = ImageEnhance.Contrast(image).enhance(1.12)
    image = ImageEnhance.Brightness(image).enhance(1.02)
    arr = np.asarray(image).astype(np.float32) / 255.0
    arr[..., 0] *= 1.035
    arr[..., 2] *= 0.955
    arr = np.clip(arr, 0.0, 1.0)
    image = Image.fromarray((arr * 255.0 + 0.5).astype(np.uint8))

    # Tilt-shift blur: sharp band across the middle, progressive blur above/below.
    blur_soft = image.filter(ImageFilter.GaussianBlur(radius=max(1.2, height * 0.0032)))
    blur_strong = image.filter(ImageFilter.GaussianBlur(radius=max(3.0, height * 0.0075)))
    weight = vertical_tilt_mask(width, height)
    mask_soft = Image.fromarray((np.clip(weight * 1.15, 0, 1) * 255).astype(np.uint8), mode="L")
    mask_strong = Image.fromarray((smoothstep(0.40, 1.0, weight) * 255).astype(np.uint8), mode="L")
    image = Image.composite(blur_soft, image, mask_soft)
    image = Image.composite(blur_strong, image, mask_strong)

    # Soft bloom.
    arr = np.asarray(image).astype(np.float32) / 255.0
    bloom = np.asarray(image.filter(ImageFilter.GaussianBlur(radius=max(4.0, height * 0.012)))).astype(np.float32) / 255.0
    arr = np.clip(arr + bloom * 0.05, 0.0, 1.0)

    # Vignette.
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    cx, cy = width / 2.0, height * 0.52
    r = np.sqrt(((xx - cx) / (width * 0.66)) ** 2 + ((yy - cy) / (height * 0.66)) ** 2)
    vignette = np.clip(1.0 - 0.13 * smoothstep(0.52, 1.0, r), 0.0, 1.0)
    arr *= vignette[..., None]

    # Fine grain.
    rng = np.random.default_rng(20261106)
    grain = rng.normal(0.0, 0.0045, size=(height, width, 1)).astype(np.float32)
    arr = np.clip(arr + grain, 0.0, 1.0)

    result = Image.fromarray((arr * 255.0 + 0.5).astype(np.uint8))
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    result.save(dst, format="PNG", optimize=True)
    if dst.suffix.lower() == ".png":
        result.save(dst.with_suffix(".jpg"), format="JPEG", quality=93, subsampling=1)
    print("WROTE", dst)


if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "renders" / "mini-city-raw.png")
    target = sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "renders" / "mini-city-still.png")
    process(source, target)
