from pydantic_ai import Agent
from backend.data_models import RagResponse
from backend.constants import VECTOR_DATABASE_PATH
import lancedb

vector_db = lancedb.connect(uri=VECTOR_DATABASE_PATH)

rag_agent = Agent(
    model="google-gla:gemini-2.5-flash", 
    retries=2,
    system_prompt=(
        "You are an expert behavioral data analyst. Your task is to analyze retrieved diary logs "
        "to identify causal correlations between activities, external factors, and emotional states.\n\n"
        
        "**OPERATIONAL RULES:**\n"
        "1. **Data-Driven Only:** Base all conclusions STRICTLY on the retrieved context. Do not hallucinate traits not present in the logs.\n"
        "2. **Pattern Recognition:** Look for recurring triggers (e.g., 'coding late leads to stress', 'gym leads to focus').\n"
        
    ),
    output_type=RagResponse,
)

@rag_agent.tool_plain
def search_vector_db(query: str) -> str:
    table = vector_db.open_table("diary")
    response = table.search(query).to_list()
    
    return response

