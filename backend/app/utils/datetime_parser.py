"""
Utility functions for parsing natural language dates and times
"""
import re
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def parse_natural_datetime(text: str, default_duration_hours: int = 1) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse natural language datetime expressions into ISO format
    
    Examples:
    - "tomorrow at 4pm" -> ("2025-07-04T16:00:00Z", "2025-07-04T17:00:00Z")
    - "today at 2:30pm" -> ("2025-07-03T14:30:00Z", "2025-07-03T15:30:00Z")
    - "Monday at 9am" -> ("2025-07-07T09:00:00Z", "2025-07-07T10:00:00Z")
    """
    try:
        text = text.lower().strip()
        now = datetime.now(timezone.utc)
        
        # Default to today
        target_date = now.date()
        
        # Parse day references
        if "tomorrow" in text:
            target_date = (now + timedelta(days=1)).date()
        elif "today" in text:
            target_date = now.date()
        elif "monday" in text:
            days_ahead = 0 - now.weekday()  # Monday is 0
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            target_date = (now + timedelta(days=days_ahead)).date()
        elif "tuesday" in text:
            days_ahead = 1 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            target_date = (now + timedelta(days=days_ahead)).date()
        elif "wednesday" in text:
            days_ahead = 2 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            target_date = (now + timedelta(days=days_ahead)).date()
        elif "thursday" in text:
            days_ahead = 3 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            target_date = (now + timedelta(days=days_ahead)).date()
        elif "friday" in text:
            days_ahead = 4 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            target_date = (now + timedelta(days=days_ahead)).date()
        elif "saturday" in text:
            days_ahead = 5 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            target_date = (now + timedelta(days=days_ahead)).date()
        elif "sunday" in text:
            days_ahead = 6 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            target_date = (now + timedelta(days=days_ahead)).date()
        
        # Parse time references
        hour = 12  # default noon
        minute = 0
        
        # Look for time patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',  # 2:30pm, 11:45am
            r'(\d{1,2})\s*(am|pm)',         # 2pm, 11am
            r'(\d{1,2}):(\d{2})',           # 14:30, 09:15 (24hr)
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 3:  # has am/pm
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if match.group(2) else 0
                    period = match.group(3)
                    
                    if period == 'pm' and hour != 12:
                        hour += 12
                    elif period == 'am' and hour == 12:
                        hour = 0
                elif len(match.groups()) == 2 and match.group(3):  # just hour with am/pm
                    hour = int(match.group(1))
                    minute = 0
                    period = match.group(2)
                    
                    if period == 'pm' and hour != 12:
                        hour += 12
                    elif period == 'am' and hour == 12:
                        hour = 0
                else:  # 24-hour format
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if match.group(2) else 0
                break
        
        # Create start datetime
        start_dt = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
        start_dt = start_dt.replace(tzinfo=timezone.utc)
        
        # Create end datetime (default 1 hour later)
        end_dt = start_dt + timedelta(hours=default_duration_hours)
        
        # Format as ISO strings
        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat()
        
        logger.info(f"Parsed '{text}' -> start: {start_iso}, end: {end_iso}")
        
        return start_iso, end_iso
        
    except Exception as e:
        logger.error(f"Error parsing datetime '{text}': {e}")
        return None, None


def format_date_for_query(text: str) -> Optional[str]:
    """
    Parse natural language date for calendar queries
    
    Examples:
    - "today" -> "2025-07-03"
    - "tomorrow" -> "2025-07-04"
    - "Monday" -> "2025-07-07"
    """
    try:
        text = text.lower().strip()
        now = datetime.now(timezone.utc)
        
        if "today" in text:
            return now.strftime("%Y-%m-%d")
        elif "tomorrow" in text:
            return (now + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "yesterday" in text:
            return (now - timedelta(days=1)).strftime("%Y-%m-%d")
        elif "monday" in text:
            days_ahead = 0 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            target = now + timedelta(days=days_ahead)
            return target.strftime("%Y-%m-%d")
        elif "tuesday" in text:
            days_ahead = 1 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            target = now + timedelta(days=days_ahead)
            return target.strftime("%Y-%m-%d")
        # Add more days as needed...
        
        # Try to parse as YYYY-MM-DD if already in that format
        if re.match(r'\d{4}-\d{2}-\d{2}', text):
            return text
            
        # Default to today if can't parse
        return now.strftime("%Y-%m-%d")
        
    except Exception as e:
        logger.error(f"Error parsing date '{text}': {e}")
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")