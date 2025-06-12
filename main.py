from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from gtts import gTTS
from googletrans import Translator
from pydantic import BaseModel
import io

app = FastAPI()

# -------- Modelos Pydantic para validación --------
class TextToAudioRequest(BaseModel):
    text: str
    language: str = "en"  # Valor por defecto

class TranslationRequest(BaseModel):
    text: str
    language: str  # Código de idioma destino (ej: "es")

# -------- Funciones auxiliares --------
def reduce_text_to_150_chars(text: str) -> str:
    return text[:150]

# -------- Endpoints --------
@app.post("/text-to-audio")
async def text_to_audio(request: TextToAudioRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="El texto es obligatorio.")

    reduced_text = reduce_text_to_150_chars(request.text)

    try:
        tts = gTTS(text=reduced_text, lang=request.language, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={"Content-Disposition": 'attachment; filename="audio.mp3"'}
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al convertir texto a audio: {str(e)}"
        )

@app.post("/translate")
async def translate_text(request: TranslationRequest):
    if not request.text or not request.language:
        raise HTTPException(
            status_code=400,
            detail="El texto y el idioma son obligatorios."
        )

    try:
        translator = Translator()
        translated = translator.translate(request.text, dest=request.language)
        
        return JSONResponse({
            "original": request.text,
            "translated": translated.text,
            "source_lang": translated.src,
            "target_lang": translated.dest
        })

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Error al traducir el texto.",
                "details": str(e)
            }
        )









#Pasos para hacer correr fastAPI
#python -m venv venv
#.\venv\Scripts\activate
#pip install fastapi uvicorn(este solo se le da una vez para instalar)
#pip install fastapi uvicorn gtts googletrans==4.0.0-rc1 python-multipart
#uvicorn main:app --reload
