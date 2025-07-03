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
    # Enhanced debugging - log everything
    headers = dict(request.headers)
    client_ip = request.client.host
    
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook body: {e}")
        return {"status": "error", "message": "Invalid JSON"}
    
    # Log complete webhook payload for debugging
    print("=" * 80)
    print(f"🔵 VAPI WEBHOOK RECEIVED")
    print(f"Client IP: {client_ip}")
    print(f"Headers: {headers}")
    print(f"Full Body: {body}")
    print("=" * 80)
    
    event_type = body.get("type")
    logger.info(f"📥 Event Type: {event_type}")
    
    # Check for VAPI's actual format
    message = body.get("message", {})
    message_type = message.get("type")
    print(f"📥 Message Type: {message_type}")
    
    # TODO: Validate webhook signature for security
    
    if event_type == "function-call" or message_type == "tool-calls":
        print("🚀 FUNCTION CALL DETECTED!")
        
        # Extract function call data - handle both formats
        tool_call_id = None
        if message_type == "tool-calls":
            # VAPI's actual format
            tool_calls = message.get("toolCalls", [])
            if tool_calls:
                first_tool = tool_calls[0]
                tool_call_id = first_tool.get("id")  # Critical: extract tool call ID
                function_data = first_tool.get("function", {})
                function_name = function_data.get("name")
                parameters = function_data.get("arguments", {})
                print("🔄 Using VAPI tool-calls format")
                print(f"🆔 Tool Call ID: {tool_call_id}")
            else:
                function_name = None
                parameters = {}
        else:
            # Our test format
            function_call_data = body.get("functionCall", {})
            function_name = function_call_data.get("name")
            parameters = function_call_data.get("parameters", {})
            print("🔄 Using test function-call format")
        
        print(f"🎯 Function Name: {function_name}")
        print(f"📋 Parameters: {parameters}")
        
        # Critical debug: Check if function_name is valid
        print(f"🔍 DEBUG: function_name type: {type(function_name)}")
        print(f"🔍 DEBUG: function_name value: '{function_name}'")
        print(f"🔍 DEBUG: function_name is None: {function_name is None}")
        print(f"🔍 DEBUG: function_name is empty: {function_name == ''}")
        
        if not function_name:
            print("❌ CRITICAL: function_name is empty or None!")
            return {"result": {"error": "No function name provided"}}
        
        try:
            # Route to appropriate calendar function with enhanced logging
            print(f"⚡ ABOUT TO ROUTE TO: {function_name}")
            logger.info(f"⚡ Routing to handler for: {function_name}")
            
            if function_name == "get_calendar_events":
                logger.info("📅 Executing get_calendar_events")
                result = await handle_get_calendar_events(parameters)
            elif function_name == "create_calendar_event":
                logger.info("➕ Executing create_calendar_event")
                result = await handle_create_calendar_event(parameters)
            elif function_name == "update_calendar_event":
                logger.info("✏️ Executing update_calendar_event")
                result = await handle_update_calendar_event(parameters)
            elif function_name == "delete_calendar_event":
                logger.info("🗑️ Executing delete_calendar_event")
                result = await handle_delete_calendar_event(parameters)
            else:
                logger.error(f"❌ Unknown function: {function_name}")
                result = {"error": f"Unknown function: {function_name}"}
            
            logger.info(f"✅ Function result: {result}")
            
            # VAPI expects specific format with toolCallId
            if tool_call_id:
                # Correct VAPI format
                response = {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": result.get("message", str(result))  # Use message for voice response
                        }
                    ]
                }
            else:
                # Fallback for test format
                response = {"result": result}
            
            logger.info(f"📤 Returning response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"💥 Error executing {function_name}: {e}")
            logger.error(f"💥 Exception type: {type(e)}")
            import traceback
            logger.error(f"💥 Traceback: {traceback.format_exc()}")
            
            # Format error response for VAPI
            if tool_call_id:
                error_response = {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": f"Sorry, there was an error accessing your calendar: {str(e)}"
                        }
                    ]
                }
            else:
                error_response = {"result": {"error": str(e)}}
            
            logger.info(f"📤 Returning error response: {error_response}")
            return error_response
    
    # Log all other events with details
    logger.info(f"ℹ️ Non-function event received: {event_type}")
    logger.info(f"ℹ️ Event details: {body}")
    
    response = {"status": "ok"}
    logger.info(f"📤 Returning standard response: {response}")
    return response


@router.get("/test")
async def test_webhook():
    """Test endpoint to verify VAPI webhook connectivity"""
    logger.info("🧪 Test endpoint called")
    return {
        "status": "ok", 
        "message": "VAPI webhook is reachable",
        "timestamp": datetime.now().isoformat()
    }


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
    logger.info("🔍 === GET CALENDAR EVENTS HANDLER ===")
    logger.info(f"📥 Input parameters: {parameters}")
    
    start_date = parameters.get("start_date", "today")
    end_date = parameters.get("end_date")
    
    logger.info(f"📅 Parsed dates - start: {start_date}, end: {end_date}")
    
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
    logger.info("➕ === CREATE CALENDAR EVENT HANDLER ===")
    logger.info(f"📥 Input parameters: {parameters}")
    
    title = parameters.get("title")
    start_time = parameters.get("start_time") 
    end_time = parameters.get("end_time")
    description = parameters.get("description")
    
    logger.info(f"📝 Event details - title: '{title}', start: '{start_time}', end: '{end_time}', desc: '{description}'")
    
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