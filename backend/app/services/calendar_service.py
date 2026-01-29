from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.models.user import User
from app.core.config import settings
from datetime import datetime, timedelta

class CalendarService:
    def build_service(self, user: User):
        creds = Credentials(
            token=user.google_access_token,
            refresh_token=user.google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
        return build('calendar', 'v3', credentials=creds)

    def create_event(self, user: User, title: str, start_time: str, end_time: str = None, description: str = None):
        """
        Creates an event in the user's primary calendar.
        start_time and end_time should be ISO format strings.
        """
        service = self.build_service(user)
        
        # Default end time to 1 hour after start if not provided
        if not end_time:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = start_dt + timedelta(hours=1)
            end_time = end_dt.isoformat()

        event_body = {
            'summary': title,
            'description': description or "Created by Logit Mail AI",
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Kolkata', # MVP: Hardcoded to IST as requested by user context, ideally dynamic
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Kolkata',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60}, # 1 day before
                    {'method': 'popup', 'minutes': 60},      # 1 hour before
                ],
            },
        }

        try:
            event = service.events().insert(calendarId='primary', body=event_body).execute()
            print(f"Event created: {event.get('htmlLink')}")
            return event
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            raise e

calendar_service = CalendarService()
