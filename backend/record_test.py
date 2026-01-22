import asyncio
from speech_to_text import process_voice_entry, record_audio, ask_db_with_voice
from constants import DATA_PATH


def input_to_diary():
    audio_file = f"{DATA_PATH}/audio/test_diary.wav"

    record_audio(audio_file, duration=10) 

    # Transkribera, LLM tar ut variablerna, sparar i .csv 
    asyncio.run(process_voice_entry(audio_file))


if __name__ == "__main__":
    
    input_to_diary()
    
    # answer = asyncio.run(ask_db_with_voice())
    # print(f"\n Svar från agent: \n\n {answer}")
    