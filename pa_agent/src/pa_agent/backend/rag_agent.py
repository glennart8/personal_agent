from pydantic_ai import Agent
from data_models import RagResponse, DiaryExtraction, RoutingDescision, NewsExtraction
from constants import VECTOR_DATABASE_PATH
import lancedb

from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
import os

# from pydantic_ai.models.openai import OpenAIChatModel
# from pydantic_ai.providers.openai import OpenAIProvider

# ollama_provider = OpenAIProvider(
#     base_url='http://localhost:11434/v1',
#     api_key='ollama',  # Krävs ofta av klienten men ignoreras av Ollama
# )

# model = OpenAIChatModel(
#     model_name="llama3.2",
#     provider=ollama_provider
# )

load_dotenv()

model = OpenAIModel(
    model_name="gpt-4o-mini",
)


vector_db = lancedb.connect(uri=VECTOR_DATABASE_PATH)

# def search_vector_db(query: str, table: str) -> str:
#     """
#     Search the vector database for entries from the specified table.
    
#     Args:
#         query: The search query
#         table: The table name ('diary' or 'science')
#     """
#     db_table = vector_db.open_table(table)
#     response = db_table.search(query).to_list()
#     return response

def search_vector_db(query: str, table: str) -> str:
    """
    Search the vector database for entries from the specified table.
    """
    db_table = vector_db.open_table(table)
    
    # begränsa till 5 träffar
    results = db_table.search(query).limit(5).to_list()
    
    # rensa bort vektordata för att spara tokens - från 280 000 till ca 1 000 :S
    # behöver inte returnera vektorerna då vi inte ska göra något med dem
    clean_results = []
    for item in results:
        # Ta bort fältet som innehåller vektorn
        item.pop('embedding', None) 
                
        clean_results.append(item)

    # returnera som sträng
    return str(clean_results)

diary_agent = Agent(
    #model="google-gla:gemini-2.5-flash", 
    model=model,
    retries=2,
    system_prompt=(
        "You are an expert behavioral data analyst.\n"
        "**CRITICAL INSTRUCTION:** You typically do not have the user's data in memory. "
        "You MUST ALWAYS use the `search_vector_db` tool with table='diary' to retrieve diary logs relevant to the user's query before answering.\n\n"
        
        "**OPERATIONAL RULES:**\n"
        "1. **Data-Driven Only:** Base all conclusions STRICTLY on the retrieved context from the tool.\n"
        "2. **Pattern Recognition:** Look for recurring triggers.\n"
        "3. **If no data found:** State clearly that no relevant entries were found in the database."
        "4. **Always answer in Swedish.**"
    ),
    output_type=RagResponse,
    tools=[search_vector_db]
)

science_agent = Agent(
    #model="google-gla:gemini-2.5-flash", 
    model=model,
    retries=2,
    system_prompt=(
        "You are an expert in science topic of behavioral and mental health.\n"
        "You MUST ALWAYS use the `search_vector_db` tool with table='science' to retrieve science articles relevant to the user's query before answering.\n\n"
        
        "**OPERATIONAL RULES:**\n"
        "1. **Data-Driven Only:** Base all conclusions STRICTLY on the retrieved context from the tool.\n"
        "2. **Look for correlations between science and users behavior**\n"
        "3. **If no data found:** State clearly that no relevant entries were found in the database."
        "4. **Try to give sources to the information given**"
        "5. **Always answer in Swedish.**"
    ),
    output_type=RagResponse,
    tools=[search_vector_db]
)

# Agent för extraktion (STT), borde testa att köra med OLLAMA
stt_agent = Agent(
    #model="google-gla:gemini-2.5-flash",
    model=model,
    retries=2,
    output_type=DiaryExtraction,
    system_prompt="""
        Du är en assistent som extraherar dagboksdata ur talspråk. 
        
        1. Var mycket kort och koncis.
        2. Använd användarens egna ord för aktiviteten.
        3. För 'mood' - använd ENDAST 'positivt' eller 'negativt.'
        4. För 'keywords' - välj generella substantiv som gör det lätt att gruppera statistiken senare.
    """
)

news_agent = Agent(
    model="google-gla:gemini-2.5-flash",
    retries=2,
    output_type=NewsExtraction,
    system_prompt="""
        Du är en assistent som extraherar nyheter. 
        
        1. Var mycket kort och koncis.
        2. För 'mood' - använd ENDAST 'positivt' eller 'negativt.'
        3. För 'keywords' - välj generella substantiv som gör det lätt att gruppera statistiken senare.
    """
)


route_agent = Agent(
    #model="google-gla:gemini-2.5-flash",
    model=model,
    retries=2,
    output_type=RoutingDescision,
    system_prompt="""
        Du är en router-agent. Din uppgift är att kategorisera användarens input.
        
        Välj en av följande kategorier:
        - ENTRY: Om användaren berättar om sin dag, sina känslor eller vad de har gjort (t.ex. "Idag känner jag mig glad och jag har tränat").
        - QUERY: Om användaren ställer en fråga om sitt förflutna eller sin dagbok (t.ex. "Hur mådde jag förra veckan?").
        
        Svara endast med ordet ENTRY eller QUERY.
    """
)


# EN NEWS_AGENT