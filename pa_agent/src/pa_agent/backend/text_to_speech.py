import edge_tts
import asyncio
import pygame
from constants import DATA_PATH, OUTPUT_DIR
from pathlib import Path
from data_models import TTSConfig

# "sv-SE-SofieNeural" (Kvinna) eller "sv-SE-MattiasNeural" (Man)
VOICE = "sv-SE-SofieNeural"

async def create_audio_file(text, filename, voice):
    """Skapar ljudfil från text."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)
    
def speak_text(config: TTSConfig):   
    """Läser in text från fil, skapar och spelar mp3-fil"""
    # Läs text, gör till egen funktion om vi vill läsa flera filtyper?
    content = config.input_file.read_text(encoding="utf-8")
    
    # Hämta namnet utan .txt 
    story_name = config.input_file.stem

    # Skapa output-sökväg, vet inte om vi behöver det?
    if config.output_file:
        final_output = config.output_file
    else:
        final_output = Path(OUTPUT_DIR) / f"{story_name}.mp3"

    # Spela upp med pygame - kan använda modulen "playsound" men då kör den igenom hela filen utan att kunna avbryta 
    try:
        asyncio.run(create_audio_file(content, str(final_output), config.voice))
        
        print("Spelar upp...")
        pygame.mixer.init()
        pygame.mixer.music.load(final_output)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.quit()
        print("Klar!")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    # skickar med file_path och testar att byta röst
    test_config = TTSConfig(input_file=DATA_PATH / "mannen_med_klovarna.txt", voice="sv-SE-MattiasNeural")
    speak_text(test_config)