from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from google.cloud import vision
from google.cloud.vision_v1 import types
import io
import os

app = FastAPI(title="Ancient Script OCR API - Google Vision")

# Allow Flutter / Lovable to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Make sure Google credentials are available
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not GOOGLE_CREDENTIALS:
    print("⚠️ WARNING: GOOGLE_APPLICATION_CREDENTIALS variable missing!")


# ----- Script Detection -----
def detect_script(text):
    if any("𑀀" <= ch <= "𑁍" for ch in text):
        return "Brahmi"
    if any("ꯀ" <= ch <= "꯽" for ch in text):
        return "Meetei Mayek"
    return "Unknown Ancient Script"


# ----- Google Vision OCR -----
@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    try:
        content = await file.read()

        client = vision.ImageAnnotatorClient()
        image = types.Image(content=content)

        response = client.text_detection(image=image)
        annotations = response.text_annotations

        if len(annotations) == 0:
            return JSONResponse({"error": "No text detected"}, status_code=400)

        extracted_text = annotations[0].description
        script = detect_script(extracted_text)

        return JSONResponse({
            "script": script,
            "raw_text": extracted_text,
            "transliteration": "",
            "pronunciation": "",
            "meaning": "",
            "translation": ""
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/")
async def root():
    return {"message": "Google Vision OCR Backend Running!"}
