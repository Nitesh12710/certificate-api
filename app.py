from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = FastAPI()

# CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

TEMPLATE_PATH = "oro_template.psd"   # Upload your PSD here

def generate_certificate(name: str):
    # Load PSD
    psd = PSDImage.open(TEMPLATE_PATH)
    img = psd.composite().convert("RGB")

    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Font size
    font_size = int(49.4 * 1.333)  # ≈ 66px

    font = None
    for p in FONT_PATHS:
        if os.path.exists(p):
            try:
                font = ImageFont.truetype(p, font_size)
                break
            except:
                continue
    if font is None:
        font = ImageFont.load_default()

    # Center text
    bbox = draw.textbbox((0, 0), name, font=font)
    text_width = bbox[2] - bbox[0]
    x = int((W - text_width) / 2)
    y = int(H * 0.375)

    # Color #b69869
    color = (182, 152, 105)
    draw.text((x, y), name, fill=color, font=font)

    # Convert to PDF (in-memory)
    buffer = io.BytesIO()
    img.save(buffer, "PDF", resolution=100.0)
    buffer.seek(0)
    return buffer


@app.get("/certificate")
def create_certificate(name: str):
    pdf_bytes = generate_certificate(name)
    return Response(
        content=pdf_bytes.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{name}.pdf\""}
    )
