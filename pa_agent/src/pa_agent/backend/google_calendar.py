from datetime import datetime, timezone, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from constants import CREDENTIALS_PATH, TOKEN_PATH


# Vad api:et ska ha för access
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    
    # hämta credentials
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    # om det inte finns, skapa token utifrån credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Använd str() eftersom biblioteket förväntar sig en sträng-sökväg
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)
        
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def fetch_next_week():
    service = get_calendar_service()

    # tid - en vecka fram
    now = datetime.now(timezone.utc)
    time_min = now.isoformat()
    time_max = (now + timedelta(days=7)).isoformat()

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    #print(f"Raw result: {events_result}")

    return events_result.get('items', [])




# INSERT FÖR ATT LÄGGA IN, Bygg body, skicka med body och calenderId
def add_event(summary, location, description, start_time, end_time):
    service = get_calendar_service()

    event_body = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Europe/Stockholm',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Europe/Stockholm',
        },
    }

    event = service.events().insert(calendarId='primary', body=event_body).execute()
    print(f"Händelse skapad: {event.get('htmlLink')}")
    return event



if __name__ == "__main__":   
    # Skapar ett möte iövermorgon kl 09:00 - 10:00
    # add_event(
    #     summary='Projektmöte API',
    #     location='Götet / Discord',
    #     description='Genomgång av JSON-struktur.',
    #     start_time='2026-02-10T09:00:00+01:00',
    #     end_time='2026-02-10T10:00:00+01:00'
    # )        
    
    # add_event(
    # summary='Gym: Ben & Bål',
    # location='Lokala Gymmet',
    # description='Fokus på knäböj och stabilitet.',
    # start_time='2026-02-12T07:00:00+01:00',
    # end_time='2026-02-12T08:15:00+01:00'
    # )
    
    # add_event(
    #     summary='Lunch: Rekryteringssnack',
    #     location='Restaurang Köket',
    #     description='Diskussion om framtida samarbeten.',
    #     start_time='2026-02-12T12:00:00+01:00',
    #     end_time='2026-02-12T13:00:00+01:00'
    # )

    # add_event(
    #     summary='After Work: Teamet',
    #     location='Brewery Bar',
    #     description='Fira avslutad milstolpe.',
    #     start_time='2026-02-13T17:30:00+01:00',
    #     end_time='2026-02-13T20:00:00+01:00'
    # )    
    
    # add_event(
    # summary='Storhandling',
    # location='ICA Maxi',
    # description='Följ inköpslistan i mobilen.',
    # start_time='2026-02-14T10:00:00+01:00',
    # end_time='2026-02-14T11:30:00+01:00'
    # )
    
    events = fetch_next_week()
       
    print(f"Nästa event: {events[0]['summary']}")
    
    # if not events:
    #     print("Inga händelser hittades för den kommande veckan.")
    # else:
    #     for event in events:
              # summary är titeln man sätter, Ingen titel som fallback
              # använder get() för att uvika krasch om ingen 'summary' finns.
    #         print(f"{event.get('summary', 'Ingen titel')}") 
        
