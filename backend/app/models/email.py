from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, UUID, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    message_id = Column(String, unique=True, index=True, nullable=False) # Gmail Message ID
    thread_id = Column(String, index=True)
    label_ids = Column(String, nullable=True) # Stored as comma-separated string for SQLite simplicity, or JSON for PG
    
    subject = Column(String, nullable=True)
    sender = Column(String, nullable=True) # From header
    recipient = Column(String, nullable=True) # To header
    
    body_text = Column(Text, nullable=True)
    snippet = Column(String, nullable=True)
    
    received_at = Column(DateTime(timezone=True), nullable=True)
    is_processed = Column(Boolean, default=False) # For AI processing status
    folder = Column(String, default="INBOX", index=True) # INBOX, SENT, drafts, etc.

    # Extracted Features (RAG/AI)
    event_title = Column(String, nullable=True)
    event_date = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    action_required = Column(Boolean, default=False)

    # FTS
    from sqlalchemy.dialects.postgresql import TSVECTOR
    search_vector = Column(TSVECTOR)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="emails")
    
    # Validation / Indexes
    __table_args__ = (
        Index('ix_emails_search_vector', search_vector, postgresql_using='gin'),
    )
