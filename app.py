from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="Ancient Script OCR API")

# CORS (Allow Lovable & Flutter to access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Script Detection Logic -----
def detect_script(text: str):
    # Brahmi Unicode Range
    if any("𑀀" <= ch <= "𑁍" for ch in text):
        return "Brahmi"

    # Meetei Mayek Unicode Range
    if any("ꯀ" <= ch <= "꯽" for ch in text):
        return "Meetei Mayek"

    return "Unknown Ancient Script"


# ----- Placeholder Transliteration -----
def transliterate_text(text: str):
    # Simple placeholder — returns same text
    # Later we can add actual transliteration rules
    return text


# ----- OLD ENDPOINT (No longer used) -----
@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    return JSONResponse({
        "error": "File upload OCR removed. Use /detect-text endpoint."
    })


# ----- NEW ENDPOINT (Frontend sends OCR text) -----
@app.post("/detect-text")
async def detect_text(payload: dict):
    text = payload.get("text", "") or ""
    target_lang = payload.get("target_lang", "en")

    script = detect_script(text)
    transliteration = transliterate_text(text)
    pronunciation = transliteration  # placeholder

    # ----- Translation using LibreTranslate -----
    translation = ""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://libretranslate.com/translate",
                json={
                    "q": text,
                    "source": "auto",
                    "target": target_lang,
                    "format": "text"
                },
                headers={"accept": "application/json"}
            )
            if resp.status_code == 200:
                translation = resp.json().get("translatedText", "")
    except Exception:
        translation = ""

    return JSONResponse({
        "script": script,
        "raw_text": text,
        "transliteration": transliteration,
        "pronunciation": pronunciation,
        "meaning": "",  # future feature
        "translation": translation
    })


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Ancient OCR Backend Running!"}
