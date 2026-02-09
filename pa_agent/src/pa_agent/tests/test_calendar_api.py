import pytest
from datetime import datetime, timedelta
import sys
import os

# Lägg till backend-mappen i sys.path för att kunna importera moduler därifrån
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from google_calendar import fetch_next_week, add_event

from data_ingestion import add_data
from rag_agent import search_vector_db


# GOOGLE CALENDAR
def test_fetch_calendar_connection():
    """Testar att vi kan hämta händelser och att svaret är en lista."""
    events = fetch_next_week()
    
    # Verifiera att vi får tillbaka en lista (även om den är tom)
    assert isinstance(events, list)

# Just nu sparas en händelse i kalendern, behöver ta bort det också
def test_insert_and_verify_event():
    """Testar att skapa en händelse och verifierar att Google returnerar ett ID."""
    start = datetime.now().isoformat() + "+01:00"
    end = (datetime.now() + timedelta(hours=1)).isoformat() + "+01:00"
    
    event = add_event(
        summary="PYTEST: Verifiering",
        location="Pytest Framework",
        description="Detta test körs via pytest",
        start_time=start,
        end_time=end
    )
    
    # Här görs de faktiska testerna - pytest kör ALLA funktioner som börjar eller slutar med test
    assert event is not None, "Event-objektet får inte vara None"
    assert 'id' in event, "Eventet skapades men saknar ett ID från Google"
    assert event['summary'] == "PYTEST: Verifiering", "Titeln på det skapade eventet matchar inte"
    
    
    
    
    
# LANCE DB
def test_insert_and_search_diary():
    pass