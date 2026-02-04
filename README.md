![dAgent](./assets/dagent.png)

# Projektplan: AI Voice Assistant ("Personal_Agent")

Detta dokument beskriver arkitekturen och genomförandeplanen för en röststyrd, lokal-först AI-agent. Systemet designas för att vara modulärt, utbyggbart och typ-säkert.

## Tech Stack & Arkitektur

| Komponent | Teknologi | Syfte |
| --- | --- | --- |
| **Språk** | Python 3.11+ | Kärnlogik |
| **Orchestration** | Python + MCP | Hanterar flödet mellan verktyg och modeller |
| **Validering** | **Pydantic** | Tvingar strukturerad output (JSON) från LLM |
| **LLM (Cloud)** | **OpenAI** | Komplex analys, kodning, multimodal input |
| **Databas / RAG** | **LanceDB** | Vektordatabas för dokument och minne |
| **Audio Input** | `faster-whisper` | Använder WhisperModel för lokal Speech-to-Text (STT) |
| **Audio Output** | `edge-tts` | Text-to-Speech (TTS) |
| **Scraping** | BeautifulSoup4, FireCrawl | Hämta nyheter |
| **Docker** | Containarize | Easy peasy för alla |
| **FastAPI** | Api-lager | Mellanlager mellan backend och frontend |
| **Streamlit** | Frontend | Dashboard |

## Kom igång GUIDE

- 1. Klona repot
- 2. Skapa en `.env`-fil i roten med nödvändiga nycklar (t.ex. `BACKEND_URL`, `OPENAI_API_KEY`). Annan nyckel - byt modell

- 3. If docker: 
- Vad ändra i docker-compose???
- docker-compose up --build, sedan http://localhost:8501 i webbläsaren

- 3. Elif Lokal utveckling:
- Kör uv sync för att hämta dependencies
- Terminal 1: uv run uvicorn api:app --reload, 
- Terminal 2: uv run streamlit run app.py

---

## Sprints (Kanban)

### Sprint 1 - MVP (tillsammans)
- [x] Sätt upp API-server
- [x] Sätt upp LanceDB-databas
- [x] Skapa tables och ingesta data
- [x] Sätt upp pydantic-modeller
- [x] Skapa RAG-agent (Diary)
- [x] Koppla ihop samtliga till en enkel Streamlit
- [x] Personlig dagbok (Berätta hur dagen har varit) STT, sparas i .csv, just nu sparas WAV - hur göra?
- [x] Personlig dagbok (ställ frågor till den) STT
- [x] Skapa Docker volumes/container så att det funkar för alla
- [x] Få till Speech-to-text (transkribering)
- [x] Få till Text-to-speech


### Sprint 2 - TOOLS/MCP
- [x] Ingesta V-db med WorldHealthReport25 och hämta ut grejer
- [x] Scrapa nyhetssite och - sammanfatta - läs upp
- [x] Visa KPI:er för nyheter
- [x] Plotta korrelationen mellan mående och dag/aktivitet
- [ ] Plotta fördelningen mellan nyhetskategorier


### Sprint 3 - Finlir
- [ ] Fixa snygg README.md
- [ ] Slides


### Övrigt (Om man vill och hinner):
- [ ] Läs upp mail, schema för dagen/veckan
- [ ] Sammanfatta youtube-klipp till .md-fil och/eller .mp3-fil
- [ ] Koppla nyhetesläget till börsen
- [ ] Spotify - byta låt, hitta genre/vart hör den hemma, vilken lista borde låten vara i
- [ ] Spelningar i stad?
- [ ] Allmän google-sökning med googlesearch-biblioteket


### Framtida möjligheter
- Koppla dagbok till spotify för att se vilken musik du lyssnar på negativa dagar, samma med filmer
- Koppla sömn-data till dagboken för att se korrelation
- Koppla skärmtid (scrollande osv) till upplevt känsla dagen eller dagen efter
- Koppla mot nyheter