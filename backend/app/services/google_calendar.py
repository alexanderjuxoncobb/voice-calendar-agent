"""
Google Calendar service for managing calendar events
"""
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Service for interacting with Google Calendar API"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
        
        # Check credentials when needed, not during init
        self._credentials_checked = False
    
    def _check_credentials(self):
        """Check if credentials are available"""
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Missing Google OAuth credentials in environment variables")
    
    def get_auth_url(self) -> str:
        """Get OAuth authorization URL for user consent"""
        self._check_credentials()
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return auth_url
    
    def exchange_code_for_tokens(self, auth_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access/refresh tokens"""
        self._check_credentials()
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        
        flow.fetch_token(code=auth_code)
        
        credentials = flow.credentials
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
    
    def build_service(self, token_data: Dict[str, Any]):
        """Build Google Calendar service with user credentials"""
        credentials = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )
        
        # Refresh if needed
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        
        return build('calendar', 'v3', credentials=credentials)
    
    async def get_events(self, token_data: Dict[str, Any], start_date: str, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get calendar events for date range"""
        try:
            service = self.build_service(token_data)
            
            # Convert dates to RFC3339 format
            start_datetime = f"{start_date}T00:00:00Z"
            end_datetime = f"{end_date or start_date}T23:59:59Z"
            
            logger.info(f"Fetching events from {start_datetime} to {end_datetime}")
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_datetime,
                timeMax=end_datetime,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format events for response
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'No Title'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', ''),
                    'location': event.get('location', '')
                })
            
            return formatted_events
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise
        except Exception as error:
            logger.error(f"Error fetching calendar events: {error}")
            raise
    
    async def create_event(self, token_data: Dict[str, Any], title: str, start_time: str, end_time: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new calendar event"""
        try:
            service = self.build_service(token_data)
            
            event_body = {
                'summary': title,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            if description:
                event_body['description'] = description
            
            logger.info(f"Creating event: {title}")
            
            event = service.events().insert(
                calendarId='primary',
                body=event_body
            ).execute()
            
            return {
                'id': event['id'],
                'title': event.get('summary'),
                'start': event['start'].get('dateTime'),
                'end': event['end'].get('dateTime'),
                'description': event.get('description', ''),
                'html_link': event.get('htmlLink')
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise
        except Exception as error:
            logger.error(f"Error creating calendar event: {error}")
            raise
    
    async def update_event(self, token_data: Dict[str, Any], event_id: str, title: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing calendar event"""
        try:
            service = self.build_service(token_data)
            
            # Get existing event
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Update fields
            if title:
                event['summary'] = title
            if start_time:
                event['start']['dateTime'] = start_time
            if end_time:
                event['end']['dateTime'] = end_time
            
            logger.info(f"Updating event: {event_id}")
            
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                'id': updated_event['id'],
                'title': updated_event.get('summary'),
                'start': updated_event['start'].get('dateTime'),
                'end': updated_event['end'].get('dateTime'),
                'description': updated_event.get('description', '')
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise
        except Exception as error:
            logger.error(f"Error updating calendar event: {error}")
            raise
    
    async def delete_event(self, token_data: Dict[str, Any], event_id: str) -> bool:
        """Delete a calendar event"""
        try:
            service = self.build_service(token_data)
            
            logger.info(f"Deleting event: {event_id}")
            
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise
        except Exception as error:
            logger.error(f"Error deleting calendar event: {error}")
            raise


# Global instance
calendar_service = GoogleCalendarService()