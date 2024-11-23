from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import os
import logging
import subprocess
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


# Function to extract audio from video files (.mp4, .mov)
def extract_audio_from_video(video_path: str, audio_path: str):
    try:
        # Using ffmpeg to extract audio
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", audio_path],
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail="Failed to extract audio from video")


@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)) -> Dict[str, str]:
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio file provided")

    # Validate file type and extension
    if not audio.content_type or (not audio.content_type.startswith('audio/') and not audio.content_type.startswith('video/')):
        raise HTTPException(status_code=400, detail="File must be an audio or video file")

    # Add new allowed file extensions here
    allowed_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.mp4', '.mov']
    file_extension = os.path.splitext(audio.filename)[1].lower()

    # Validate file extension
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid audio or video file extension")

    temp_file_path = None
    temp_audio_path = None

    try:
        # Write the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Log the transcription attempt
        logger.info(f"Attempting to transcribe file: {audio.filename}")

        # If the file is a video, extract the audio
        if file_extension in ['.mp4', '.mov']:
            temp_audio_path = temp_file_path + ".wav"  # Temporary audio file path
            extract_audio_from_video(temp_file_path, temp_audio_path)
            file_to_transcribe = temp_audio_path
        else:
            file_to_transcribe = temp_file_path

        # Transcribe the audio (or extracted audio) file using Whisper
        result = model.transcribe(file_to_transcribe, fp16=False)

        # Remove the temporary files after processing
        os.unlink(temp_file_path)
        if temp_audio_path:
            os.unlink(temp_audio_path)

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
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        raise HTTPException(status_code=500, detail=str(e))
