from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="Ancient Script OCR API")

# CORS (allow everything for now)
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

# Optional: small transliteration placeholder for demo
def transliterate_text(text: str):
    # For now just return text in Latin-range form if possible.
    # Replace with a real transliterator or DB mapping later.
    return text

# POST /detect (kept, warns)
@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    return JSONResponse({"error": "File upload is not used in the new flow. Send OCR text to /detect-text."})

# NEW: accepts JSON { "text": "...", "target_lang": "en" }
@app.post("/detect-text")
async def detect_text(payload: dict):
    text = payload.get("text", "") or ""
    target_lang = payload.get("target_lang", "en")
    if not text:
        return JSONResponse({"error": "No text provided"}, status_code=400)

    script = detect_script(text)
    transliteration = transliterate_text(text)

    # Translate using LibreTranslate (no API key required on libretranslate.com; if blocked, replace with preferred translator)
    translation = None
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
                j = resp.json()
                translation = j.get("translatedText", "")
            else:
                translation = ""
    except Exception as e:
        translation = ""

    # pronunciation placeholder: we return transliteration for now.
    pronunciation = transliteration

    return JSONResponse({
        "script": script,
        "raw_text": text,
        "transliteration": transliteration,
        "pronunciation": pronunciation,
        "meaning": "",        # placeholder (you can extend lexicon lookups here)
        "translation": translation
    })

@app.get("/")
async def root():
    return {"message": "Ancient OCR Backend Running!"}
