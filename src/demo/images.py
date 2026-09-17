"""
Préparation des images avant envoi au modèle.

Objectifs : limiter le coût (une image plus grande coûte plus de tokens sans
gagner en lisibilité de légende), et retirer les métadonnées EXIF, qui peuvent
contenir les coordonnées GPS de l'appareil ayant pris la photo.
"""

import io

from PIL import Image, ImageOps

COTE_MAX = 1024
QUALITE_JPEG = 85


def preparer_image(donnees, cote_max=COTE_MAX, qualite=QUALITE_JPEG):
    """Redimensionne, réoriente et réencode une image en JPEG sans EXIF.

    Args:
        donnees: bytes de l'image téléversée.

    Returns:
        (jpeg_bytes, (largeur, hauteur)) après redimensionnement.

    Raises:
        ValueError: si le fichier n'est pas une image lisible.
    """
    try:
        image = Image.open(io.BytesIO(donnees))
        image.load()
    except Exception as exc:
        raise ValueError("Fichier illisible : envoyez une image JPEG ou PNG.") from exc

    # Applique l'orientation EXIF puis abandonne toutes les métadonnées.
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    image.thumbnail((cote_max, cote_max), Image.LANCZOS)

    # Reconstruire l'image à partir des seuls pixels : rien d'autre ne suit.
    propre = Image.frombytes(image.mode, image.size, image.tobytes())

    tampon = io.BytesIO()
    propre.save(tampon, format="JPEG", quality=qualite, optimize=True)
    return tampon.getvalue(), propre.size
