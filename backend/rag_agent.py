from pydantic_ai import Agent
from backend.data_models import RagResponse
from backend.constants import VECTOR_DATABASE_PATH
import lancedb

vector_db = lancedb.connect(uri=VECTOR_DATABASE_PATH)

diary_agent = Agent(
    model="google-gla:gemini-2.5-flash", 
    retries=2,
    system_prompt=(
        "You are an expert behavioral data analyst.\n"
        "**CRITICAL INSTRUCTION:** You typically do not have the user's data in memory. "
        "You MUST ALWAYS use the `search_vector_db` tool to retrieve diary logs relevant to the user's query before answering.\n\n"
        
        "**OPERATIONAL RULES:**\n"
        "1. **Data-Driven Only:** Base all conclusions STRICTLY on the retrieved context from the tool.\n"
        "2. **Pattern Recognition:** Look for recurring triggers.\n"
        "3. **If no data found:** State clearly that no relevant entries were found in the database."
    ),
    output_type=RagResponse
)


@diary_agent.tool_plain
def search_vector_db(query: str) -> str:
    """
    Search the vector database for diary entries. 
    Use this tool whenever the user asks about their history, mood, or activities.
    """
    table = vector_db.open_table("diary")
    response = table.search(query).to_list()
    
    return response

