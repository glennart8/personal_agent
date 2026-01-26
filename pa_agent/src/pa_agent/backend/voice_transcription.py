from faster_whisper import WhisperModel
import edge_tts
import io

model = WhisperModel("base", device="cpu", compute_type="int8")


async def transcribe_audio(audio_bytes) -> str:
    audio_file = io.BytesIO(audio_bytes)
    segments, _ = model.transcribe(audio_file, language="sv")
    # Slå ihop alla segment till en sträng
    text = " ".join([segment.text for segment in segments])
    
    return text.strip()


async def transcribe_text(text):
    communicate = edge_tts.Communicate(text, "sv-SE-SofieNeural")
    audio_output = io.BytesIO()
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_output.write(chunk["data"])
    
    audio_output.seek(0)
    
    return audio_output.getvalue()