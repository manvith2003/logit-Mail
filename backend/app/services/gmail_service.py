from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import base64
from app.models.user import User
from app.models.email import Email
from app.core.config import settings
from app.services import rag_service

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
        
        while fetched_count < max_results:
            try:
                # Calculate how many more to fetch in this batch
                batch_size = min(max_results - fetched_count + skipped_count, 100) # Request slightly more to account for skips
                if batch_size < 10: batch_size = 10 

                results = service.users().messages().list(
                    userId='me', 
                    maxResults=batch_size, 
                    labelIds=[label_id],
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
                    existing_email = await db.execute(select(Email).filter(Email.message_id == msg['id']))
                    if existing_email.scalars().first():
                        skipped_count += 1
                        continue

                    try:
                        # Fetch full message details
                        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                        
                        payload = msg_detail.get('payload', {})
                        headers = payload.get('headers', [])
                        
                        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
                        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
                        recipient = next((h['value'] for h in headers if h['name'] == 'To'), "Unknown")
                        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), None)
                        
                        # Simple body extraction (can be improved for HTML/Multipart)
                        body_text = msg_detail.get('snippet', '')
                        # Try to get full body if available in parts
                        parts = payload.get('parts', [])
                        for part in parts:
                            if part.get('mimeType') == 'text/plain':
                                 data = part.get('body', {}).get('data')
                                 if data:
                                     body_text = base64.urlsafe_b64decode(data).decode('utf-8')
                                     break
            
                        from email.utils import parsedate_to_datetime
            
                        # Parse date using email.utils
                        received_at = datetime.utcnow() # Default fallback
                        if date_str:
                            try:
                                received_at = parsedate_to_datetime(date_str)
                            except Exception as e:
                                print(f"Error parsing date {date_str}: {e}")
                        
                        # AI Processing (RAG & Extraction) - DISABLED FOR SPEED
                        extracted_data = None
                        # try:
                        #     # 1. Extract features (Events, Deadlines)
                        #     extracted_data = await rag_service.process_email_content(body_text)
                            
                        #     # 2. Embed for Search
                        #     rag_service.embed_email(msg['id'], body_text, str(user.id))
                        # except Exception as e:
                        #     print(f"AI Processing failed for {msg['id']}: {e}")
            
                        event_title = None
                        event_date = None
                        deadline = None
                        
                        # AI fields parsing skipped...
            
                        new_email = Email(
                            user_id=user.id,
                            message_id=msg['id'],
                            thread_id=msg['threadId'],
                            subject=subject,
                            sender=sender,
                            recipient=recipient,
                            body_text=body_text,
                            snippet=msg_detail.get('snippet'),
                            received_at=received_at,
                            folder=folder.upper(),
                            label_ids=",".join(msg_detail.get('labelIds', [])), # Save labels
                            # AI Fields
                            is_processed=False, # Mark as not processed
                            event_title=event_title,
                            event_date=event_date,
                            deadline=deadline,
                            action_required=False
                        )
                        db.add(new_email)
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
        
        print(f"DEBUG: Fetched {fetched_count}, Skipped {skipped_count}")
        return fetched_count

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
            print(f"DEBUG: Gmail returned labelIds: {new_label_ids}")

            # Update specific email
            email_query = await db.execute(select(Email).filter(Email.message_id == message_id))
            email_obj = email_query.scalars().first()
            
            if email_obj:
                print(f"DEBUG: Found local email {email_obj.id}, updating labels from '{email_obj.label_ids}' to '{','.join(new_label_ids)}'")
                email_obj.label_ids = ",".join(new_label_ids)
                await db.commit()
                print(f"DEBUG: Updated local DB for message {message_id}")
            else:
                print(f"DEBUG: WARNING - Could not find local email for message_id {message_id}")
            
            return updated_message
        except Exception as e:
            print(f"Error modifying message: {e}")
            raise e

gmail_service = GmailService()
