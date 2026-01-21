from pydantic_ai import Agent
from backend.data_models import DiaryExtraction

# Agent för extraktion (STT), borde testa att köra med OLLAMA
stt_agent = Agent(
    model="google-gla:gemini-2.5-flash",
    output_type=DiaryExtraction,
    system_prompt="""Du är en assistent som extraherar dagboksdata ur talspråk. 
                Var koncis och använd gärna användarens egna ord
                """
)