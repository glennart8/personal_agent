# import sys
# import os
# from datetime import datetime, timedelta

# # Lägg till backend-mappen i sys.path för att kunna importera moduler därifrån
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

# from google_calendar import fetch_next_week, add_event

# def run_tests():
#     test_fetch_calender()
#     test_insert_to_calender()


# def test_fetch_calender():
#     print("Startar anslutningstest mot Google Calendar...")
#     try:
#         events = fetch_next_week()
#         print(f"✅ Funkar! Hittade {len(events)} händelser.")         
#     except Exception as e:
#         print(f"❌ Testet misslyckades!")


# def test_insert_to_calender():
#     print("Testar att skapa en händelse i kalendern...")
    
#     start = datetime.now().isoformat() + "+01:00"
#     end = (datetime.now() + timedelta(hours=1)).isoformat() + "+01:00"
    
#     try:
#         event = add_event(
#             summary="TEST: Automatiserat test",
#             location="Python Script",
#             description="Om du ser detta fungerar add_event-funktionen!",
#             start_time=start,
#             end_time=end
#         )
        
#         # Verifiera att vi fick ett ID från Google
#         if 'id' in event:
#             print(f"✅ Funkar! Event skapat med ID: {event['id']}")
#             print(f"🔗 Länk: {event.get('htmlLink')}")
#         else:
#             print("⚠️ Något gick fel, fick inget ID från Google.")
            
#     except Exception as e:
#         print(f"❌ Fel vid insättning: {e}")

# if __name__ == "__main__":
#     run_tests()