"""VAPI webhook endpoints for voice interactions."""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import os
from datetime import datetime

from app.services.google_calendar import calendar_service
from app.routers.auth import user_tokens
from app.utils.datetime_parser import parse_natural_datetime, format_date_for_query

logger = logging.getLogger(__name__)
router = APIRouter()


# Request models for calendar functions
class GetCalendarEventsRequest(BaseModel):
    start_date: str
    end_date: Optional[str] = None


class CreateCalendarEventRequest(BaseModel):
    title: str
    start_time: str
    end_time: str
    description: Optional[str] = None


class UpdateCalendarEventRequest(BaseModel):
    event_id: str
    title: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class DeleteCalendarEventRequest(BaseModel):
    event_id: str


@router.post("/webhook")
async def vapi_webhook(request: Request) -> Dict[str, Any]:
    """Handle VAPI webhook events.
    
    VAPI sends events here when:
    - User speaks (transcript events)
    - Assistant needs to call a function
    - Call starts/ends
    """
    body = await request.json()
    
    event_type = body.get("type")
    
    # TODO: Validate webhook signature for security
    
    if event_type == "function-call":
        # Handle function calls from VAPI
        function_name = body.get("functionCall", {}).get("name")
        parameters = body.get("functionCall", {}).get("parameters", {})
        
        logger.info(f"VAPI function call: {function_name} with params: {parameters}")
        
        try:
            # Route to appropriate calendar function
            if function_name == "get_calendar_events":
                result = await handle_get_calendar_events(parameters)
            elif function_name == "create_calendar_event":
                result = await handle_create_calendar_event(parameters)
            elif function_name == "update_calendar_event":
                result = await handle_update_calendar_event(parameters)
            elif function_name == "delete_calendar_event":
                result = await handle_delete_calendar_event(parameters)
            else:
                result = {"error": f"Unknown function: {function_name}"}
            
            return {"result": result}
            
        except Exception as e:
            logger.error(f"Error executing {function_name}: {e}")
            return {"result": {"error": str(e)}}
    
    # Log other events
    print(f"Received VAPI event: {event_type}")
    
    return {"status": "ok"}


@router.post("/session/create")
async def create_voice_session() -> Dict[str, str]:
    """Create a new voice session for the frontend."""
    # TODO: Verify user authentication
    # TODO: Create session in Redis
    # TODO: Return session token for frontend
    
    assistant_id = os.getenv("VAPI_ASSISTANT_ID")
    
    return {
        "session_id": "temp_session_id",
        "assistant_id": assistant_id
    }


# Calendar function handlers
async def handle_get_calendar_events(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get calendar events function call"""
    start_date = parameters.get("start_date", "today")
    end_date = parameters.get("end_date")
    
    logger.info(f"Getting calendar events from {start_date} to {end_date}")
    
    # Check if user has authorized Google Calendar
    user_id = "demo_user"  # In production, get from JWT
    if user_id not in user_tokens:
        return {
            "success": False,
            "error": "Please authorize Google Calendar access first. Visit /api/v1/auth/google/login",
            "auth_required": True
        }
    
    try:
        # Parse natural language dates
        parsed_start = format_date_for_query(start_date)
        parsed_end = format_date_for_query(end_date) if end_date else parsed_start
        
        logger.info(f"Parsed dates: {parsed_start} to {parsed_end}")
        
        # Get events from Google Calendar
        events = await calendar_service.get_events(
            user_tokens[user_id], 
            parsed_start, 
            parsed_end
        )
        
        if events:
            event_list = []
            for event in events:
                # Format events for voice response
                start_time = event.get('start', '')
                if 'T' in start_time:
                    # Parse time for natural speech
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    time_str = dt.strftime("%I:%M %p").lstrip('0')
                else:
                    time_str = "all day"
                
                event_list.append(f"{event.get('title', 'Untitled')} at {time_str}")
            
            return {
                "success": True,
                "events": events,
                "message": f"You have {len(events)} events: " + ", ".join(event_list)
            }
        else:
            return {
                "success": True,
                "events": [],
                "message": f"You have no events scheduled for {parsed_start}"
            }
        
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        return {
            "success": False,
            "error": f"Failed to get calendar events: {str(e)}"
        }


async def handle_create_calendar_event(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle create calendar event function call"""
    title = parameters.get("title")
    start_time = parameters.get("start_time") 
    end_time = parameters.get("end_time")
    description = parameters.get("description")
    
    logger.info(f"Creating calendar event: {title}, start: {start_time}, end: {end_time}")
    
    # Check if user has authorized Google Calendar
    user_id = "demo_user"  # In production, get from JWT
    if user_id not in user_tokens:
        return {
            "success": False,
            "error": "Please authorize Google Calendar access first",
            "auth_required": True
        }
    
    try:
        # Parse natural language datetime if needed
        if start_time and not start_time.endswith('Z') and 'T' not in start_time:
            # Looks like natural language, try to parse it
            parsed_start, parsed_end = parse_natural_datetime(f"{start_time}")
            if parsed_start:
                start_time = parsed_start
                if not end_time:  # If no end time specified, use parsed end
                    end_time = parsed_end
        
        if end_time and not end_time.endswith('Z') and 'T' not in end_time:
            # Parse end time as natural language
            parsed_start, parsed_end = parse_natural_datetime(f"{end_time}")
            if parsed_end:
                end_time = parsed_end
        
        # Ensure we have both start and end times
        if not start_time or not end_time:
            return {
                "success": False,
                "error": "Please specify both start and end times for the event"
            }
        
        logger.info(f"Parsed times - start: {start_time}, end: {end_time}")
        
        # Create event in Google Calendar
        event = await calendar_service.create_event(
            user_tokens[user_id],
            title,
            start_time,
            end_time,
            description
        )
        
        return {
            "success": True,
            "event": event,
            "message": f"Successfully created '{title}' on your calendar"
        }
        
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        return {
            "success": False,
            "error": f"Failed to create calendar event: {str(e)}"
        }


async def handle_update_calendar_event(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle update calendar event function call"""
    event_id = parameters.get("event_id")
    title = parameters.get("title")
    start_time = parameters.get("start_time")
    end_time = parameters.get("end_time")
    
    logger.info(f"Updating calendar event: {event_id}")
    
    # TODO: Implement actual Google Calendar integration
    updated_event = {
        "id": event_id,
        "title": title or "Updated Event",
        "start": start_time or "2025-07-04T10:00:00",
        "end": end_time or "2025-07-04T11:00:00"
    }
    
    return {
        "success": True,
        "event": updated_event,
        "message": f"Successfully updated event {event_id}"
    }


async def handle_delete_calendar_event(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle delete calendar event function call"""
    event_id = parameters.get("event_id")
    
    logger.info(f"Deleting calendar event: {event_id}")
    
    # TODO: Implement actual Google Calendar integration
    return {
        "success": True,
        "message": f"Successfully deleted event {event_id}"
    }