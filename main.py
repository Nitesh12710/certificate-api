from fastapi import FastAPI, Response, HTTPException
from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont
import io
import os
import traceback

app = FastAPI()

# Path to font and PSD
FONT_PATH = "./fonts/DejaVuSerif-Bold.ttf"
TEMPLATE_PATH = "./oro dance certificate (1)[1].psd"  # make sure exact filename

def generate_certificate(name: str):
    try:
        if not os.path.exists(TEMPLATE_PATH):
            raise FileNotFoundError(f"PSD template not found at {TEMPLATE_PATH}")
        if not os.path.exists(FONT_PATH):
            raise FileNotFoundError(f"Font file not found at {FONT_PATH}")

        # Open PSD template
        psd = PSDImage.open(TEMPLATE_PATH)
        img = psd.composite().convert("RGB")

        draw = ImageDraw.Draw(img)
        W, H = img.size

        font_size = int(49.4 * 1.333)
        font = ImageFont.truetype(FONT_PATH, font_size)

        # Calculate centered text
        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        x = (W - text_width) // 2
        y = int(H * 0.375)

        color = (182, 152, 105)
        draw.text((x, y), name, fill=color, font=font)

        buffer = io.BytesIO()
        img.save(buffer, "PDF", resolution=100.0)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    except Exception as e:
        print("Error generating certificate:", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating certificate: {str(e)}")

@app.get("/certificate")
def certificate(name: str):
    pdf_bytes = generate_certificate(name)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{name}.pdf\""}
    )

@app.get("/")
def root():
    return {"message": "Certificate API is running. Use /certificate?name=NAME to generate PDF."}
