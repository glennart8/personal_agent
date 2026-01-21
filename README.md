# Projektplan: AI Voice Assistant ("Personal_Agent")

Detta dokument beskriver arkitekturen och genomförandeplanen för en röststyrd, lokal-först AI-agent. Systemet designas för att vara modulärt, utbyggbart och typ-säkert.

## Tech Stack & Arkitektur

| Komponent | Teknologi | Syfte |
| --- | --- | --- |
| **Språk** | Python 3.11+ | Kärnlogik |
| **Orchestration** | Python + MCP | Hanterar flödet mellan verktyg och modeller |
| **Validering** | **Pydantic** | Tvingar strukturerad output (JSON) från LLM |
| **LLM (Lokal)** | **Ollama** (Llama 3 / Mistral) | Snabba kommandon, routing, integritet |
| **LLM (Cloud)** | **Google Gemini** | Komplex analys, kodning, multimodal input |
| **Databas / RAG** | **LanceDB** | Vektordatabas för dokument och minne |
| **Audio Input** | `faster-whisper` | Använder WhisperModel för lokal Speech-to-Text (STT) |
| **Audio Output** | `edge-tts` | Text-to-Speech (TTS) |
| **Web / Scraping** | BeautifulSoup4, `googlesearch-python` | Hämta nyheter och events |
| **Docker** | Containarize | Containarize every fucking thing - easy peasy för alla |
| **FastAPI** | Api-lager | Mellanlager mellan backend och frontend |
| **Streamlit** | Frontend | Dashboard |

---

## Sprints (Kanban)

### Sprint 1 - MVP (tillsammans)
- [x] Sätt upp API-server
- [x] Sätt upp LanceDB-databas
- [x] Skapa tables och ingesta data
- [x] Sätt upp pydantic-modeller
- [x] Skapa RAG-agent (Diary)
- [x] Koppla ihop samtliga till en enkel Streamlit
- [x] Personlig dagbok (Berätta hur dagen har varit) STT, sparas i .csv
- [ ] Personlig dagbok (ställ frågor till den) STT
- [x] Skapa Docker volumes/container så att det funkar för alla
- [x] Få till Speech-to-text (transkribering)
- [ ] Få till Text-to-speech



### Sprint 2 - TOOLS/MCP
- [ ] Scrapa nyhetssite och - sammanfatta - läs upp
- [ ] Läs upp mail, schema för dagen/veckan
- [ ] Plotta fördelningen mellan nyhetskategorier
- [ ] Plotta korrelationen mellan mående och dag/aktivitet

### Sprint 3 - Finlir
- [ ] Fixa snygg README.md
- [ ] Slides ()


### Övrigt (Om man vill och hinner):
- [ ] Sammanfatta youtube-klipp till .md-fil och/eller .mp3-fil
- [ ] Koppla nyhetesläget till börsen
- [ ] Spotify - byta låt, hitta genre/vart hör den hemma, vilken lista borde låten vara i
- [ ] Spelningar i stad?
- [ ] Allmän google-sökning med googlesearch-biblioteket

### Funderingar
- Behövs en "vanlig" databas för strukturerad output osv?
