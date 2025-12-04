from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont
import io
import os

def handler(request):
    name = request.query.get("name")

    if not name:
        return {
            "status": 400,
            "body": "Missing ?name= parameter"
        }

    TEMPLATE_PATH = "./oro_template.psd"

    psd = PSDImage.open(TEMPLATE_PATH)
    img = psd.composite().convert("RGB")

    draw = ImageDraw.Draw(img)
    W, H = img.size

    font_size = int(49.4 * 1.333)

    FONT_PATHS = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]

    font = None
    for f in FONT_PATHS:
        if os.path.exists(f):
            try:
                font = ImageFont.truetype(f, font_size)
                break
            except:
                pass

    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), name, font=font)
    text_width = bbox[2] - bbox[0]
    x = (W - text_width) // 2
    y = int(H * 0.375)

    color = (182, 152, 105)
    draw.text((x, y), name, fill=color, font=font)

    buffer = io.BytesIO()
    img.save(buffer, "PDF", resolution=100.0)
    pdf_bytes = buffer.getvalue()

    return {
        "status": 200,
        "headers": {
            "Content-Type": "application/pdf",
            "Content-Disposition": f"attachment; filename=\"{name}.pdf\""
        },
        "body": pdf_bytes,
        "encoding": "binary"
    }
