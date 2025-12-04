from fastapi import FastAPI, Response
from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = FastAPI()

# Path to local font (your .ttf file in fonts/)
FONT_PATH = "./fonts/DejaVuSerif-Bold.ttf"  # replace with actual filename

# Path to PSD template
TEMPLATE_PATH = "./oro_template.psd"

def generate_certificate(name: str):
    # Open PSD template and convert to RGB
    psd = PSDImage.open(TEMPLATE_PATH)
    img = psd.composite().convert("RGB")

    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Font size
    font_size = int(49.4 * 1.333)

    # Load font
    if os.path.exists(FONT_PATH):
        font = ImageFont.truetype(FONT_PATH, font_size)
    else:
        font = ImageFont.load_default()

    # Calculate centered position
    bbox = draw.textbbox((0, 0), name, font=font)
    text_width = bbox[2] - bbox[0]
    x = (W - text_width) // 2
    y = int(H * 0.375)

    # Text color #b69869
    color = (182, 152, 105)

    # Draw name on image
    draw.text((x, y), name, fill=color, font=font)

    # Save image to PDF in memory
    buffer = io.BytesIO()
    img.save(buffer, "PDF", resolution=100.0)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes

@app.get("/certificate")
def certificate(name: str):
    pdf_bytes = generate_certificate(name)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{name}.pdf\""}
    )

# Optional root to avoid 404
@app.get("/")
def root():
    return {"message": "Certificate API is running. Use /certificate?name=NAME to generate PDF."}
