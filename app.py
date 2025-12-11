from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import pytesseract
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
def detect_script(text):
    if any("𑀀" <= ch <= "𑁍" for ch in text):
        return "Brahmi"
    if any("ꯀ" <= ch <= "꯽" for ch in text):
        return "Meetei Mayek"
    return "Unknown Ancient Script"


# ----- OCR Endpoint -----
@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    content = await file.read()
    image = Image.open(io.BytesIO(content))

    extracted_text = pytesseract.image_to_string(image)

    script = detect_script(extracted_text)

    return JSONResponse({
        "script": script,
        "raw_text": extracted_text,
        "transliteration": "",
        "pronunciation": "",
        "meaning": "",
        "translation": ""
    })


@app.get("/")
async def root():
    return {"message": "Ancient OCR Backend Running!"}

