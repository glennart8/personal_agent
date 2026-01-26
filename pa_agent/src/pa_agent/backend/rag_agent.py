from pydantic_ai import Agent
from data_models import RagResponse
from constants import VECTOR_DATABASE_PATH
import lancedb

vector_db = lancedb.connect(uri=VECTOR_DATABASE_PATH)


def search_vector_db(query: str, table: str) -> str:
    """
    Search the vector database for entries from the specified table.
    
    Args:
        query: The search query
        table: The table name ('diary' or 'science')
    """
    db_table = vector_db.open_table(table)
    response = db_table.search(query).to_list()
    return response


diary_agent = Agent(
    model="google-gla:gemini-2.5-flash", 
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
    model="google-gla:gemini-2.5-flash", 
    retries=2,
    system_prompt=(
        "You are an expert in science topic of behavioral and mental health.\n"
        "You MUST ALWAYS use the `search_vector_db` tool with table='science' to retrieve science articles relevant to the user's query before answering.\n\n"
        
        "**OPERATIONAL RULES:**\n"
        "1. **Data-Driven Only:** Base all conclusions STRICTLY on the retrieved context from the tool.\n"
        #"2. **Look for correlations between science and users behavior**\n"
        "3. **If no data found:** State clearly that no relevant entries were found in the database."
    ),
    output_type=RagResponse,
    tools=[search_vector_db]
)