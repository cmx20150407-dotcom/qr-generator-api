from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
import qrcode
from io import BytesIO
import base64

app = FastAPI(
    title="QR Code Generator API",
    description="Generate QR code PNG or base64 from any text/URL",
    version="1.0.0"
)

# ---------- 健康检查端点（解决Render ping问题）----------
@app.get("/health")
@app.get("/ping")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "message": "QR Code Generator API",
        "endpoints": {
            "/generate?text=...": "Generate QR code",
            "/health": "Health check"
        }
    }

@app.get("/generate")
def generate_qr(
    text: str = Query(..., min_length=1, max_length=1000, description="Content to encode"),
    format: str = Query("png", regex="^(png|base64)$", description="Output format: png (image) or base64")
):
    """
    Generate a QR code from any text or URL.
    - format=png: returns PNG image directly
    - format=base64: returns JSON with base64 string
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        if format == "png":
            return Response(content=buffer.getvalue(), media_type="image/png")
        else:
            b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return {"text": text, "base64": b64, "format": "png"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))