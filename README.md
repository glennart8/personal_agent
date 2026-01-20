# Projektplan: AI Voice Assistant ("The Architect")

Detta dokument beskriver arkitekturen och genomförandeplanen för en röststyrd, lokal-först AI-agent. Systemet designas för att vara modulärt, utbyggbart och typ-säkert.

## Tech Stack & Arkitektur

| Komponent | Teknologi | Syfte |
| :--- | :--- | :--- |
| **Språk** | Python 3.11+ | Kärnlogik |
| **Orchestration** | Python + MCP | Hanterar flödet mellan verktyg och modeller |
| **Validering** | **Pydantic** | Tvingar strukturerad output (JSON) från LLM |
| **LLM (Lokal)** | **Ollama** (Llama 3 / Mistral) | Snabba kommandon, routing, integritet |
| **LLM (Cloud)** | **Google Gemini** | Komplex analys, kodning, multimodal input |
| **Databas / RAG** | **LanceDB** | Vektordatabas för dokument och minne |
| **Audio Input** | `faster-whisper` | Lokal Speech-to-Text (STT) |
| **Audio Output** | `edge-tts` | Text-to-Speech (TTS) |
| **Web / Scraping** | BeautifulSoup4, `googlesearch-python` | Hämta nyheter och events |

---

## Sprints (Kanban Setup)

Projektet delas upp i logiska faser. Varje punkt nedan kan vara en egen "Issue" i GitHub.

### Sprint 1: "The Body" (Input/Output Loop)
*Mål: Agenten ska kunna höra och prata. Inget "tänkande" än.*

- [ ] **Repo Setup:** Initiera git, skapa `venv`, och `requirements.txt`.
- [ ] **STT Modul:** Implementera `faster-whisper` för att transkribera mikrofonljud i realtid.
- [ ] **TTS Modul:** Implementera `edge-tts` för att spela upp text som ljud.
- [ ] **Wake Word (Optional):** Enkel detektion för att börja lyssna (t.ex. Porcupine eller volym-threshold).
- [ ] **The Loop:** Sy ihop allt: *Mic -> Text -> (Dummy Print) -> Audio*.

### Sprint 2: "The Brain" (Routing & Pydantic)
*Mål: Agenten förstår intention och väljer modell.*

- [ ] **Pydantic Models:** Definiera `UserIntent`-klasser (t.ex. `PlayMusic`, `SummarizeNews`, `GeneralChat`).
- [ ] **LLM Client Wrapper:** Skapa en abstraktion som kan anropa antingen Ollama eller Gemini.
- [ ] **Router Logic:** Bygg logiken som tar user input -> klassificerar intent via Ollama -> returnerar strukturerat Pydantic-objekt.
- [ ] **Context Manager:** En enkel lista som håller de senaste 5-10 meddelandena i minnet.

### Sprint 3: "The Toolsmith" (Spotify & Google Integrations)
*Mål: Agenten kan påverka omvärlden via API:er.*

- [ ] **Spotify Auth:** Sätt upp Spotify Developer App och skapa auth-flow (Spotipy).
- [ ] **Google Auth:** Sätt upp GCP-projekt för Calendar & Gmail API.
- [ ] **MCP Implementation:** Strukturera verktygen enligt Model Context Protocol (eller liknande interface-mönster).
    - `tools/spotify.py` (play, pause, next)
    - `tools/calendar.py` (list_events, add_event)
    - `tools/gmail.py` (send_email)
- [ ] **Action Execution:** Koppla Pydantic-objekten från Sprint 2 till dessa funktioner.

### Sprint 4: "The Librarian" (RAG & LanceDB)
*Mål: Agenten kan läsa och minnas dokument.*

- [ ] **Ingestion Pipeline:** Skript för att läsa PDF/TXT och chunka texten.
- [ ] **Embedding:** Använd en lokal modell (via Ollama eller `sentence-transformers`) för att skapa vektorer.
- [ ] **LanceDB Setup:** Spara vektorer och metadata i LanceDB.
- [ ] **Retrieval:** Implementera sökfunktionen som hämtar relevant kontext innan frågan skickas till LLM.

### Sprint 5: "The Explorer" (Web & News)
*Mål: Agenten kan hämta information från internet.*

- [ ] **News Scraper:** Bygg en modul med `BeautifulSoup` för att hämta rubriker från SVT/Omni/BBC.
- [ ] **Event Finder:** Logik för att söka efter "Konserter i [Stad]" och parsa datum/platser.
- [ ] **Summarizer:** Använd Gemini för att sammanfatta långa webbsidor till korta röst-notiser.

---

## Utvecklingsregler (Guidelines)

### 1. Pydantic First
All interaktion med LLM som ska leda till en handling **måste** valideras genom en Pydantic Model.
```python
class MusicIntent(BaseModel):
    song: str
    artist: str | None
    device: str = "living_room"

### Filstruktur
/src 
    /agent 
    /brain.py # LLM logic & Router memory.py # LanceDB interactions 
/io 
    ears.py # Whisper STT mouth.py # Edge TTS 
/mcp-tools 
    spotify.py 
    calendar.py 
    gmail.py 
# MCP / Tool definitions spotify_tool.py google_tool.py web_tool.py 
main.py # Entry point 