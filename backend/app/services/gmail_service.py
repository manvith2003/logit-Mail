from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import base64
from app.models.user import User
from app.models.email import Email
from app.core.config import settings
from app.services.agent_service import agent_service
from app.core.database import SessionLocal # For background tasks

class GmailService:
    def build_service(self, user: User):
        """
        Reconstructs the Gmail API service using stored tokens.
        """
        creds = Credentials(
            token=user.google_access_token,
            refresh_token=user.google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
        return build('gmail', 'v1', credentials=creds)

    async def fetch_emails(self, db: AsyncSession, user: User, max_results: int = 50, folder: str = "INBOX"):
        """
        Fetches emails from Gmail and saves them to the database.
        Returns tuple: (fetched_count, list_of_new_email_ids)
        """
        service = self.build_service(user)
        
        # Map folder to Gmail Label ID
        label_id = 'INBOX'
        if folder.lower() == 'sent':
            label_id = 'SENT'
        elif folder.lower() == 'drafts':
            label_id = 'DRAFT'
        elif folder.lower() == 'starred':
            label_id = 'STARRED'
        
        # List messages (handle pagination)
        print(f"Fetching {folder} emails for user {user.email} with limit {max_results}...")
        
        fetched_count = 0
        skipped_count = 0
        page_token = None
        new_email_ids = []
        consecutive_existing = 0
        stop_sync = False
        
        while fetched_count < max_results:
            if stop_sync:
                break
            try:
                # Calculate how many more to fetch in this batch
                batch_size = min(max_results - fetched_count + skipped_count, 100)
                if batch_size < 10: batch_size = 10 

                # Optimization: Use 'after:TIMESTAMP' to fetch only new emails
                q_filter = ""
                if user.last_synced_at:
                    # Convert to timestamp (seconds)
                    ts = int(user.last_synced_at.timestamp())
                    q_filter = f"after:{ts}"
                    print(f"DEBUG: Using Sync Cursor -> {q_filter}")

                results = service.users().messages().list(
                    userId='me', 
                    maxResults=batch_size, 
                    labelIds=[label_id],
                    q=q_filter,
                    pageToken=page_token
                ).execute()
                
                messages = results.get('messages', [])
                page_token = results.get('nextPageToken')
                
                print(f"DEBUG: Gmail list returned {len(messages)} messages (batch)")
                
                if not messages:
                    break
                    
                for msg in messages:
                    if fetched_count >= max_results:
                        break
                        
                    # Check if email already exists
                    result = await db.execute(select(Email).filter(Email.message_id == msg['id']))
                    existing_email = result.scalars().first()
                    
                    if existing_email and existing_email.body_html:
                        skipped_count += 1
                        
                        # Optimization: If we hit 15 existing emails in a row, assume we are fully synced.
                        # This prevents scanning the entire history looking for "new" count.
                        consecutive_existing += 1
                        if consecutive_existing >= 15:
                            print(f"DEBUG: Found 15 existing emails in a row. Stopping sync at {msg['id']}.")
                            stop_sync = True
                            break
                        continue
                    
                    # Reset counter if we found a new one
                    consecutive_existing = 0

                    try:
                        # Fetch full message details
                        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                        
                        payload = msg_detail.get('payload', {})
                        headers = payload.get('headers', [])
                        
                        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "") or "(No Subject)"
                        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
                        recipient = next((h['value'] for h in headers if h['name'] == 'To'), "Unknown")
                        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), None)
                        
                        # Body extraction
                        body_text = msg_detail.get('snippet', '')
                        parts = payload.get('parts', [])
                        body_html = None
                        
                        # Helper to extract PDF text
                        def extract_pdf_from_attachment(msg_id, attachment_id):
                            try:
                                att = service.users().messages().attachments().get(userId='me', messageId=msg_id, id=attachment_id).execute()
                                data = att.get('data')
                                if data:
                                    file_data = base64.urlsafe_b64decode(data)
                                    import io
                                    from pypdf import PdfReader
                                    reader = PdfReader(io.BytesIO(file_data))
                                    text = ""
                                    for page in reader.pages:
                                        text += page.extract_text() + "\n"
                                    return f"\n\n[Attachment PDF Content]:\n{text}"
                            except Exception as e:
                                print(f"Error parsing PDF attachment: {e}")
                                return ""
                            return ""

                        def get_parts(parts_list):
                            text = ""
                            html = None
                            for part in parts_list:
                                if part.get('mimeType') == 'text/plain':
                                    data = part.get('body', {}).get('data')
                                    if data:
                                        text += base64.urlsafe_b64decode(data).decode('utf-8')
                                elif part.get('mimeType') == 'text/html':
                                    data = part.get('body', {}).get('data')
                                    if data:
                                        html = base64.urlsafe_b64decode(data).decode('utf-8')
                                elif part.get('mimeType') == 'application/pdf':
                                    # PDF Attachment Found
                                    att_id = part.get('body', {}).get('attachmentId')
                                    if att_id:
                                        # Optimization: Only fetch PDF if the body hints at it (prevent waste)
                                        # Check the *snippet* or valid body text found so far
                                        current_context = (body_text + text).lower()
                                        keywords = ["attach", "schedule", "timetable", "exam", "syllabus", "pdf", "file", "find enclosed", "shared"]
                                        
                                        if any(k in current_context for k in keywords):
                                            print(f"DEBUG: Context implies useful PDF ('{next((k for k in keywords if k in current_context), '')}'). Downloading...")
                                            pdf_text = extract_pdf_from_attachment(msg['id'], att_id)
                                            text += pdf_text
                                        else:
                                            print(f"DEBUG: Skipping PDF (No context keywords found in body).")
                                elif part.get('parts'):
                                    nested_text, nested_html = get_parts(part.get('parts'))
                                    if nested_text: text += nested_text # Append, don't replace
                                    if nested_html and not html: html = nested_html
                            return text, html

                        if parts:
                            extracted_text, extracted_html = get_parts(parts)
                            if extracted_text:
                                body_text = extracted_text
                            if extracted_html:
                                body_html = extracted_html
                        else:
                            data = payload.get('body', {}).get('data')
                            if data:
                                decoded = base64.urlsafe_b64decode(data).decode('utf-8')
                                if payload.get('mimeType') == 'text/html':
                                    body_html = decoded
                                else:
                                    body_text = decoded
            
                        from email.utils import parsedate_to_datetime
            
                        # Parse date using email.utils
                        received_at = datetime.utcnow() # Default fallback
                        if date_str:
                            try:
                                received_at = parsedate_to_datetime(date_str)
                            except Exception as e:
                                print(f"Error parsing date {date_str}: {e}")
                        
                        # NO AI PROCESSING HERE - Speed only!

                        if existing_email:
                            existing_email.body_html = body_html
                            existing_email.body_text = body_text 
                            # We will re-process with AI in background if needed, but for now just update content
                            if not existing_email.is_processed:
                                new_email_ids.append(existing_email.id)
                        else:
                            new_email = Email(
                                user_id=user.id,
                                message_id=msg['id'],
                                thread_id=msg['threadId'],
                                subject=subject,
                                sender=sender,
                                recipient=recipient,
                                body_text=body_text,
                                body_html=body_html,
                                snippet=msg_detail.get('snippet'),
                                received_at=received_at,
                                folder=folder.upper(),
                                label_ids=",".join(msg_detail.get('labelIds', [])),
                                is_processed=False
                            )
                            db.add(new_email)
                            await db.flush() # Get the ID
                            new_email_ids.append(new_email.id)
                            fetched_count += 1
                        
                    except Exception as e:
                        print(f"Error processing details for {msg['id']}: {e}")
                        continue
                
                await db.commit() # Commit batch
                
                if not page_token:
                    break

            except Exception as e:
                print(f"Error fetching messages: {e}")
                break
        
        print(f"DEBUG: Fetched {fetched_count} emails. New/Updated for AI: {len(new_email_ids)}")
        if fetched_count > 0:
            # Logic: If this was the FIRST sync (we just set the stamp), 
            # we should NOT return these IDs for AI processing (per optimization request).
            # The user wants "agents will start acting not on the old mails".
            if not user.last_synced_at:
                 print("DEBUG: FIRST SYNC DETECTED. Setting Stamp but Skipping AI for these historical emails.")
                 user.last_synced_at = datetime.utcnow()
                 db.add(user)
                 await db.commit()
                 return fetched_count, []
            
            # Normal case: Update stamp
            user.last_synced_at = datetime.utcnow()
            db.add(user)
            await db.commit()
            print(f"DEBUG: Updated last_synced_at to {user.last_synced_at}")

        return fetched_count, new_email_ids

    async def process_emails_background(self, email_ids: list[str], user_id: str):
        """
        Background task to process emails with AI Agent.
        """
        if not email_ids:
            return

        print(f"Background Task: Agent analyzing {len(email_ids)} emails...")
        
        async with SessionLocal() as db:
            for email_id in email_ids:
                try:
                    result = await db.execute(select(Email).filter(Email.id == email_id))
                    email = result.scalars().first()
                    
                    if not email or email.is_processed:
                        continue
                        
                    # Call the AI Agent
                    # THROTTLE: Sleep 4s to stay under Gemini Free Tier limits (15 RPM)
                    import time
                    time.sleep(4) 
                    
                    analysis = await agent_service.analyze_email(
                        email_content=email.body_text or email.snippet or "", 
                        received_at=email.received_at,
                        email_id=str(email.id),
                        db=db,
                        user_id=user_id,
                        sender=email.sender
                    )
                    
                    if analysis and analysis.get("status") == "processed":
                        # Map JSON fields to DB columns
                        email.is_processed = True
                        
                        # Event Info
                        if analysis.get("event_type"):
                             email.category = analysis.get("event_type") # exam, deadline, meeting
                        
                        payload = analysis.get("calendar_event_payload")
                        if payload:
                            email.event_title = payload.get("summary")
                            
                            start = payload.get("start", {}).get("dateTime")
                            if start:
                                try:
                                    email.event_date = datetime.fromisoformat(start)
                                    email.deadline = datetime.fromisoformat(start) # Logic: event date is the deadline
                                except ValueError:
                                    pass

                        # Priority/Action logic derived from confidence or type
                        if analysis.get("action") == "auto_add":
                             email.priority = "high"
                             email.action_required = True
                        elif analysis.get("action") == "needs_confirmation":
                             email.priority = "medium"
                             email.action_required = True
                        else:
                             email.priority = "low"
                             email.action_required = False

                        await db.commit()
                        print(f"Agent Processed {email.id}: Detected {email.category}")
                    else:
                        # Mark processed even if nothing found to avoid loops
                        email.is_processed = True
                        await db.commit()
                        
                except Exception as e:
                    print(f"Error in Agent background task for email {email_id}: {e}")

    async def send_email(self, user: User, to: list[str], subject: str, body: str, cc: list[str] = None, bcc: list[str] = None):
        """
        Sends an email using the Gmail API.
        """
        service = self.build_service(user)
        
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        message = MIMEMultipart()
        message['to'] = ", ".join(to)
        message['subject'] = subject
        
        if cc:
            message['cc'] = ", ".join(cc)
        if bcc:
            message['bcc'] = ", ".join(bcc)
            
        msg = MIMEText(body)
        message.attach(msg)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        try:
            print(f"Sending email to {to}...")
            sent_message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            print(f"Email sent! Id: {sent_message['id']}")
            return sent_message
        except Exception as e:
            print(f"Error sending email: {e}")
            message = f"Error sending email: {e}" # Fallback
            raise e
            
    async def modify_message(self, db: AsyncSession, user: User, message_id: str, add_labels: list[str] = [], remove_labels: list[str] = []):
        """
        Modifies the labels of a message and syncs to local DB.
        """
        service = self.build_service(user)
        try:
            body = {'addLabelIds': add_labels, 'removeLabelIds': remove_labels}
            updated_message = service.users().messages().modify(userId='me', id=message_id, body=body).execute()
            print(f"DEBUG: Modified message {message_id}: Added {add_labels}, Removed {remove_labels}")
            
            # Sync to local DB
            new_label_ids = updated_message.get('labelIds', [])
            
            # Update specific email
            email_query = await db.execute(select(Email).filter(Email.message_id == message_id))
            email_obj = email_query.scalars().first()
            
            if email_obj:
                email_obj.label_ids = ",".join(new_label_ids)
                await db.commit()
            
            return updated_message
        except Exception as e:
            print(f"Error modifying message: {e}")
            raise e

gmail_service = GmailService()
