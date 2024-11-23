from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import os
import logging
from typing import Dict

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the Whisper model
try:
    model = whisper.load_model("base")
    logger.info("Whisper model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading Whisper model: {str(e)}")
    raise HTTPException(status_code=500, detail="Failed to load Whisper model")


@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)) -> Dict[str, str]:
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio file provided")

    # Validate file type and extension
    if not audio.content_type or not audio.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")

    allowed_extensions = ['.wav', '.mp3', '.flac', '.ogg']
    file_extension = os.path.splitext(audio.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid audio file extension")

    temp_file_path = None

    try:
        # Write the uploaded audio file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_file_path = temp_audio.name

        # Log the transcription attempt
        logger.info(f"Attempting to transcribe file: {audio.filename}")

        # Transcribe the audio file using Whisper
        result = model.transcribe(temp_file_path, fp16=False)

        # Remove the temporary file after processing
        os.unlink(temp_file_path)

        # Check if transcription was successful
        if not result or "text" not in result:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")

        logger.info(f"Transcription successful for file: {audio.filename}")
        return {"transcription": result["text"]}

    except Exception as e:
        # Log the exception and ensure the temporary file is removed
        logger.error(f"Error during transcription: {str(e)}")
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
