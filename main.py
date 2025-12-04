# main.py
from fastapi import FastAPI, Response
from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = FastAPI()

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

TEMPLATE_PATH = "oro dance certificate (1)[1].psd"

def generate_certificate(name: str):
    psd = PSDImage.open(TEMPLATE_PATH)
    img = psd.composite().convert("RGB")

    draw = ImageDraw.Draw(img)
    W, H = img.size
    font_size = int(49.4 * 1.333)

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

    bbox = draw.textbbox((0,0), name, font=font)
    text_width = bbox[2] - bbox[0]
    x = (W - text_width) // 2
    y = int(H * 0.375)
    color = (182,152,105)
    draw.text((x, y), name, fill=color, font=font)

    buffer = io.BytesIO()
    img.save(buffer, "PDF", resolution=100.0)
    return buffer.getvalue()

@app.get("/certificate")
def certificate(name: str):
    pdf_bytes = generate_certificate(name)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{name}.pdf\""}
    )
