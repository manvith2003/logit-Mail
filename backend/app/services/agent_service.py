import json
import logging
from datetime import datetime, timedelta
import dateparser
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class EventDetectionAgent:
    def __init__(self):
        # Initialize Gemini LLM
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-flash-latest",
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.1,
                convert_system_message_to_human=True 
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Agent: {e}")
            self.llm = None

    async def analyze_email(self, email_content: str, received_at: datetime, email_id: str, db=None, user_id: str=None, sender: str=None) -> dict:
        """
        Analyzes email content using strict rules + dateparser for resolution.
        """
        if not self.llm:
            return None

        prompt = f"""
You are an AI automation agent.
OBJECTIVE: Detect deadlines/exams/meetings.

STEP 1: INTENT DETECTION
Detect: deadline, exam, submission, meeting, assignment, homework, project.
NOTE: The email may contain "[Attachment PDF Content]: ...". Treat this as critical high-priority text.
If NONE: Return {{ "status": "ignored" }}

STEP 2: EXTRACTION
Extract:
- event_title: Short summary (e.g. "Math Exam").
- date_text: The EXACT text snippet describing the date.
- event_type: exam | deadline | meeting

SPECIAL RULE FOR LISTS/TIMETABLES (e.g. from PDFs):
1. If text contains multiple events on DIFFERENT dates, extract ONLY the *FIRST* upcoming one.
2. If multiple events occur on the *SAME DATE* (e.g. "10am Math" and "2pm Physics"), YOU MUST COMBINE them into one event.
   - Title: "2 Exams: Math & Physics" (or "Math & Physics Exams")
   - Date: The shared date.
   - Do NOT create separate JSON objects. Return ONE object representing the combined schedule for that day.

STEP 3: OUTPUT JSON
{{
  "email_id": "{email_id}",
  "status": "processed",
  "event_type": "exam | deadline | meeting",
  "event_title": "...",
  "date_text": "...", 
  "confidence": 0.0 to 1.0,
  "action": "auto_add | needs_confirmation"
}}

EMAIL CONTENT:
{email_content}
"""
        try:
            # Call LLM
            response = await self.llm.ainvoke(prompt)
            print(f"DEBUG: LLM Response Content Type: {type(response.content)}")
            print(f"DEBUG: LLM Response Content: {response.content}")
            
            if isinstance(response.content, list):
                # Handle list of dicts (e.g. [{'type': 'text', 'text': ...}])
                pieces = []
                for part in response.content:
                    if isinstance(part, dict) and 'text' in part:
                        pieces.append(part['text'])
                    else:
                        pieces.append(str(part))
                content = "".join(pieces).strip()
            else:
                content = response.content.strip()
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(content)
            
            if result.get("status") == "ignored":
                return result

            # --- Python Logic Layer (The "Brain") ---
            
            # 1. Resolve Date using dateparser
            date_text = result.get("date_text")
            
            # Defensive: ensure date_text is a string
            if isinstance(date_text, list):
                date_text = " ".join(date_text)
                
            resolved_date = None
            
            if date_text:
                prefixes = ["", "before ", "by ", "on ", "due ", "due date ", "until "]
                lower_text = date_text.lower()
                
                for prefix in prefixes:
                    if resolved_date:
                        break
                        
                    # 1. Clean prefix
                    if prefix and prefix not in lower_text:
                        continue
                        
                    clean_text = lower_text.replace(prefix, "").strip()
                    if not clean_text:
                        continue
                    
                    # 2. Try Direct Parse
                    parsed = dateparser.parse(
                        clean_text,
                        settings={'RELATIVE_BASE': received_at, 'PREFER_DATES_FROM': 'future'}
                    )
                    if parsed:
                        resolved_date = parsed
                        break
                        
                    # 3. Manual Fallbacks on CLEANED text
                    
                    # "next week [day]" -> [day] + 7 days
                    if "next week" in clean_text:
                         super_clean = clean_text.replace("next week", "").strip()
                         base_day = dateparser.parse(super_clean, settings={'RELATIVE_BASE': received_at, 'PREFER_DATES_FROM': 'future'})
                         if base_day:
                             resolved_date = base_day + timedelta(days=7)
                             break

                    # "end of this month"
                    if "end of this month" in clean_text:
                        import calendar
                        last_day = calendar.monthrange(received_at.year, received_at.month)[1]
                        resolved_date = received_at.replace(day=last_day)
                        break

                    # "end of next month"
                    if "end of next month" in clean_text:
                        import calendar
                        if received_at.month == 12:
                            nm_year = received_at.year + 1
                            nm_month = 1
                        else:
                            nm_year = received_at.year
                            nm_month = received_at.month + 1
                        last_day = calendar.monthrange(nm_year, nm_month)[1]
                        resolved_date = received_at.replace(year=nm_year, month=nm_month, day=last_day)
                        break

                    # "end of weekend"
                    if "end of weekend" in clean_text:
                        days_ahead = 6 - received_at.weekday()
                        if days_ahead <= 0: days_ahead += 7
                        resolved_date = received_at + timedelta(days=days_ahead)
                        break
                    
                    # Manual Fix for "weekend" -> Upcoming Friday
                    if "weekend" in clean_text:
                        # Find next Friday (weekday 4)
                        # Current weekday: Mon=0, Sun=6
                        days_ahead = 4 - received_at.weekday()
                        if days_ahead <= 0: # If today is Friday, Saturday, Sunday -> Next Friday
                             days_ahead += 7
                        
                        resolved_date = received_at + timedelta(days=days_ahead)
                        # Set to end of day (23:59:59) roughly implies "night"
                        resolved_date = resolved_date.replace(hour=23, minute=59, second=59)
                        break

                    # "next [day]" fallback (must be last manual check to avoid clashing with next week)
                    if "next " in clean_text:
                         super_clean = clean_text.replace("next ", "").strip()
                         base_day = dateparser.parse(super_clean, settings={'RELATIVE_BASE': received_at, 'PREFER_DATES_FROM': 'future'})
                         if base_day:
                             resolved_date = base_day + timedelta(days=7)
                             break

            # --- CONTEXT LOOKUP (The "Memory" Feature) ---
            # If no date found, but text implies a reference like "before the meeting"
            if not resolved_date and db and user_id and sender:
                 # Check for specific keywords
                 context_keywords = ["meeting", "exam", "submission", "deadline"]
                 found_keyword = next((k for k in context_keywords if k in (date_text or "").lower()), None)
                 
                 if found_keyword:
                     # Query DB for the *next* event of this type
                     try:
                         # normalize keyword to category if needed
                         cat = found_keyword
                         if cat == "submission": cat = "deadline"
                         
                         from app.models.email import Email
                         from sqlalchemy import select
                         
                         # OPTIMIZATION: 
                         # 1. Match Sender (Context usually implies same source)
                         # 2. Limit to 10 Days (Don't link to something months away)
                         limit_date = received_at + timedelta(days=10)
                         
                         query = select(Email).filter(
                             Email.user_id == user_id,
                             Email.sender == sender,
                             Email.category.ilike(f"%{cat}%"),
                             Email.event_date > received_at,
                             Email.event_date <= limit_date
                         ).order_by(Email.event_date.asc()).limit(1)
                         
                         res = await db.execute(query)
                         context_email = res.scalars().first()
                         
                         if context_email:
                             resolved_date = context_email.event_date
                             result["reason"] = f"Resolved via context: Linked to '{context_email.subject}'"
                             print(f"DEBUG: Context found! Linked to {context_email.id}")
                     except Exception as ex:
                         print(f"DEBUG: Context lookup failed: {ex}")

            if not resolved_date:
                # Fallback: if LLM failed to give text but gave nothing, or dateparser failed
                result["action"] = "needs_confirmation"
                result["reason"] = result.get("reason", "Could not resolve date")
                return result

            # 2. Apply Notification Rules
            event_type = result.get("event_type", "meeting");
            reminders = []
            
            if event_type == "exam":
                # Notify 2 days before + 1 hour before
                reminders = [
                    {"method": "email", "minutes": 2 * 24 * 60}, 
                    {"method": "popup", "minutes": 60}
                ]
            elif event_type == "deadline":
                # Notify 1 day before + 1 hour before
                reminders = [
                     {"method": "email", "minutes": 24 * 60},
                     {"method": "popup", "minutes": 60}
                ]
            else:
                # Default (Meeting)
                reminders = [{"method": "popup", "minutes": 10}]

            # 3. Construct Calendar Payload
            start_iso = resolved_date.isoformat()
            end_iso = (resolved_date + timedelta(hours=1)).isoformat()
            
            result["resolved_date"] = start_iso
            # Ensure action is set so UI shows notification
            if "action" not in result or result["action"] == "ignored":
                 result["action"] = "needs_confirmation"
            result["calendar_event_payload"] = {
                "summary": result.get("event_title", "Event"),
                "description": f"Detected from email. Original text: '{date_text}'",
                "start": {"dateTime": start_iso},
                "end": {"dateTime": end_iso},
                "reminders": {
                    "useDefault": False,
                    "overrides": reminders
                }
            }
            
            return result
            
        except Exception as e:
            print(f"Error during AI analysis: {e}")
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                # CRITICAL: Do not silence Rate Limits! Raise so we don't mark as processed.
                raise e
            return None

agent_service = EventDetectionAgent()
