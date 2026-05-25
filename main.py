from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.exceptions import RequestValidationError
import qrcode
from io import BytesIO
import base64

app = FastAPI(
    title="QR Code Generator API",
    description="Generate QR codes from text or URL. Returns PNG image or base64 string.",
    version="1.1.0"
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "hint": "Check documentation at https://rapidapi.com/user/cmx20150407/api/qr-code-generator"
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": "Invalid parameters",
                "details": exc.errors(),
                "hint": "Provide 'text' parameter (1-1000 chars) and optional 'size' (100-1000)"
            }
        }
    )

@app.get("/health")
@app.get("/ping")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "message": "QR Code Generator API",
        "docs": "/docs",
        "health": "/health",
        "usage": "GET /generate?text=Hello&size=200&format=png"
    }

@app.get("/generate")
async def generate_qr(
    text: str = Query(..., min_length=1, max_length=1000, description="Content to encode"),
    size: int = Query(200, ge=100, le=1000, description="Image size in pixels"),
    format: str = Query("png", regex="^(png|base64)$", description="Output format")
):
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
        
        # 调整尺寸
        if size != 200:
            from PIL import Image
            img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        if format == "png":
            return Response(content=buffer.getvalue(), media_type="image/png")
        else:
            b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return {"text": text, "base64": b64, "size": size, "format": "png"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
