from fastapi import FastAPI, Response, HTTPException
from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont
import io
import os
import traceback

app = FastAPI()

# Path to PSD template
TEMPLATE_PATH = "oro dance certificate (1)[1].psd"

# Font paths to try (Railway uses Linux, so we need fallbacks)
FONT_PATHS = [
    "fonts/GOUDYB.TTF",                    # Goudy Old Style Bold (local)
    "fonts/DejaVuSerif-Bold.ttf",          # Fallback serif font
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",  # Railway/Linux path
]

def generate_certificate(name: str):
    try:
        if not os.path.exists(TEMPLATE_PATH):
            raise FileNotFoundError(f"Template not found at {TEMPLATE_PATH}")

        # Load and convert PSD to image
        psd = PSDImage.open(TEMPLATE_PATH)
        img = psd.composite().convert('RGB')
        
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        # Font configuration - 160 px
        font_size = 160
        
        # Try to load font
        font = None
        last_error = None
        for font_path in FONT_PATHS:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    print(f"✓ Using font: {font_path}")
                    break
                except Exception as e:
                    last_error = str(e)
                    continue
        
        if font is None:
            error_msg = f"No suitable font found. Last error: {last_error}" if last_error else "No suitable font found. Please add font to ./fonts/ directory"
            raise FileNotFoundError(error_msg)
        
        # Calculate text position (centered horizontally)
        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        
        # Position: Centered horizontally, at 37% from top
        x = int((W - text_width) / 2)
        y = int(H * 0.37)
        
        # Color: #b69869 (golden/tan color)
        color = (0xb6, 0x98, 0x69)
        
        # Draw the name
        draw.text((x, y), name, fill=color, font=font)
        
        # Save as PDF
        buffer = io.BytesIO()
        img.save(buffer, 'PDF', resolution=100.0)
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
