from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from PIL import Image
import io

app = FastAPI(title="Ancient Script OCR API")

# CORS (Allow Lovable & Flutter to access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Script Detection (Dummy) -----
def detect_script(text: str):
    if any("𑀀" <= ch <= "𑁍" for ch in text):
        return "Brahmi"
    if any("ꯀ" <= ch <= "꯽" for ch in text):
        return "Meetei Mayek"
    return "Unknown Ancient Script"

# ========== OLD FILE UPLOAD ENDPOINT (not used now) ==========
@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    return JSONResponse({
        "error": "File upload is no longer used. Send OCR text to /detect-text instead."
    })

# ========== NEW ENDPOINT FOR TEXT FROM TESSERACT.JS ==========
@app.post("/detect-text")
async def detect_text(payload: dict):
    text = payload.get("text", "")

    script = detect_script(text)

    return JSONResponse({
        "script": script,
        "raw_text": text,
        "transliteration": "",
        "pronunciation": "",
        "meaning": "",
        "translation": ""
    })

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Ancient OCR Backend Running!"}
