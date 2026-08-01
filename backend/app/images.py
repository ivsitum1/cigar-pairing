"""Sigurno ucitavanje slike iz nepouzdanih bajtova.

Oba endpointa (`/ocr`, `/band/*`) primaju datoteku od klijenta. Bez ovoga:
- ne-slika je bacala `UnidentifiedImageError` i vracala **500** umjesto 400;
- "decompression bomb" (mala datoteka, gigabajti piksela) prosla bi do
  `np.array(image)` i pojela memoriju.
"""
from __future__ import annotations

import io

from PIL import Image, UnidentifiedImageError

from .config import MAX_IMAGE_PIXELS

# PIL svoj prag koristi za upozorenje; nas je tvrda granica provjerena rucno
# prije `convert()`, koji je taj koji stvarno alocira piksele.
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


class InvalidImage(ValueError):
    """Klijentova greska (400), ne serverska."""


def load_rgb(data: bytes) -> Image.Image:
    """Dekodiraj bajtove u RGB sliku ili baci `InvalidImage`."""
    if not data:
        raise InvalidImage("empty file")
    try:
        img = Image.open(io.BytesIO(data))
        # `open` je lijen — dimenzije zna prije nego alocira piksele
        w, h = img.size
        if w * h > MAX_IMAGE_PIXELS:
            raise InvalidImage(
                f"image too large: {w}x{h} px (limit {MAX_IMAGE_PIXELS})"
            )
        return img.convert("RGB")
    except InvalidImage:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as e:
        raise InvalidImage(f"unreadable image: {e}") from e
