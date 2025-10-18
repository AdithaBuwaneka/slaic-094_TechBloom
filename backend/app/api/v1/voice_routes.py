# app/api/v1/endpoints/voice_routes.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import base64
import asyncio
from io import BytesIO

from google.cloud import speech_v1p1beta1 as speech
from google.api_core import exceptions as google_exceptions
from pydub import AudioSegment

# --- ✅ Add this line ---
# Explicitly set the path to your ffmpeg installation.
# Replace the path with the output from the 'which ffmpeg' command.
AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"

router = APIRouter()

# --- Global, Reusable Speech Client ---
try:
    speech_client = speech.SpeechClient()
    print("✅ Google Cloud Speech client initialized successfully.")
except google_exceptions.DefaultCredentialsError:
    speech_client = None
    print("🔴 FATAL ERROR: Google Cloud credentials not found.")
# ------------------------------------

async def transcribe_audio_file(audio_bytes: bytes) -> str:
    """
    Transcribes a complete audio file with full response logging.
    """
    if not speech_client:
        raise Exception("Speech client is not initialized.")

    # --- Steps 1-4: Audio Conversion (Verified as Working) ---
    print(f"--- Transcribing Audio (Step 1/5): Received {len(audio_bytes)} raw bytes.")
    try:
        audio_segment = AudioSegment.from_file(BytesIO(audio_bytes), format="m4a")
        duration_ms = len(audio_segment)
        print(f"--- Transcribing Audio (Step 2/5): Loaded M4A. Duration: {duration_ms / 1000.0:.2f} seconds.")
        if duration_ms == 0: return ""
    except Exception as e:
        print(f"🔴 --- FAILED (Step 2/5): pydub could not load audio. Error: {e}")
        return ""
    audio_segment = audio_segment.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    print("--- Transcribing Audio (Step 3/5): Converted to 16kHz mono PCM.")
    pcm_data = audio_segment.raw_data
    print(f"--- Transcribing Audio (Step 4/5): Extracted {len(pcm_data)} bytes of PCM data.")
    if not pcm_data: return ""
    # -----------------------------------------------------------

    recognition_audio = speech.RecognitionAudio(content=pcm_data)
    
    # --- ✅ Final, More Robust Configuration ---
    # This config is more explicit and often resolves issues with mobile audio.
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_automatic_punctuation=True,
        # Use a model better suited for short commands
        model="command_and_search", 
    )

    print("--- Transcribing Audio (Step 5/5): Sending data to Google STT API...")
    response = await asyncio.to_thread(speech_client.recognize, config=config, audio=recognition_audio)
    
    # --- ✅ Full Response Logging ---
    # This will print the entire object returned by Google.
    print("--- Full Google API Response ---")
    print(response)
    print("---------------------------------")
    # ---------------------------------
    
    if response.results:
        transcript = response.results[0].alternatives[0].transcript.strip()
        print(f"--- Google API returned transcript: '{transcript}'")
        return transcript
    else:
        print("--- Google API returned a successful but empty result.")
        return ""

@router.websocket("/voice")
async def voice_websocket(websocket: WebSocket, token: str = ""):
    await websocket.accept()
    print("Voice WebSocket connection accepted.")

    try:
        while True:
            message_text = await websocket.receive_text()
            message = json.loads(message_text)
            msg_type = message.get("type")

            if msg_type == "audio_chunk":
                if not message.get("data"):
                    continue
                
                # Decode the Base64 audio data
                audio_bytes = base64.b64decode(message["data"])
                
                print(f"Received audio chunk of {len(audio_bytes)} bytes.")

                # Transcribe the audio
                try:
                    transcript = await transcribe_audio_file(audio_bytes)
                    print(f"Transcription result: '{transcript}'")
                    # Send the final transcript back to the client
                    await websocket.send_text(json.dumps({
                        "type": "final",
                        "text": transcript
                    }))
                except Exception as e:
                    print(f"Error during transcription: {e}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))

    except WebSocketDisconnect:
        print("Voice WebSocket client disconnected.")
    except Exception as e:
        print(f"An error occurred in the voice WebSocket: {e}")