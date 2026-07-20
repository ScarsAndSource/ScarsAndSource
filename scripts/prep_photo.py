"""
prep_photo.py — run once per source photo.

    python scripts/prep_photo.py source-photo.jpg

Pipeline:
  1. Remove background (rembg) so only the subject remains.
  2. CLAHE contrast boost (OpenCV) so flat lighting gets real highlights/shadows.
  3. Composite onto pure white so background maps to the blank end of the
     ASCII ramp (white -> space character).
Output: scripts/prepped/source-prepped.png (grayscale, ready for make_ascii_svg.py)
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUT_DIR = Path(__file__).parent / "prepped"
OUT_DIR.mkdir(exist_ok=True)


def remove_background(src_path: Path) -> Image.Image:
    with open(src_path, "rb") as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes)
    return Image.open(__import__("io").BytesIO(output_bytes)).convert("RGBA")


def boost_contrast_clahe(img_rgba: Image.Image) -> np.ndarray:
    rgb = np.array(img_rgba.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    return clahe.apply(gray)


def composite_on_white(img_rgba: Image.Image, gray_clahe: np.ndarray) -> Image.Image:
    alpha = np.array(img_rgba)[:, :, 3]
    white_bg = np.full_like(gray_clahe, 255)
    # where alpha is 0 (removed background) -> pure white
    # where alpha is 255 (subject) -> CLAHE-boosted grayscale
    alpha_f = alpha.astype(float) / 255.0
    merged = (gray_clahe * alpha_f + white_bg * (1 - alpha_f)).astype(np.uint8)
    return Image.fromarray(merged, mode="L")


def main():
    if len(sys.argv) != 2:
        print("usage: python prep_photo.py <source-photo.jpg>")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    if not src_path.exists():
        print(f"file not found: {src_path}")
        sys.exit(1)

    print("removing background...")
    no_bg = remove_background(src_path)

    print("boosting local contrast (CLAHE)...")
    clahe_gray = boost_contrast_clahe(no_bg)

    print("compositing onto white...")
    final = composite_on_white(no_bg, clahe_gray)

    out_path = OUT_DIR / "source-prepped.png"
    final.save(out_path)
    print(f"done -> {out_path}")


if __name__ == "__main__":
    main()
