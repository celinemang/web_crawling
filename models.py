from typing import Optional
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

# Base class for ORM models
Base = declarative_base()

class Document(Base):
    """
    SQLAlchemy ORM Model for the 'documents' table.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_title = Column(Text, nullable=False)
    document_type = Column(Text, nullable=False)
    year = Column(Integer, nullable=True)
    quarter = Column(Integer, nullable=True)
    pdf_url = Column(Text, nullable=False, unique=True)
    
    def __repr__(self):
        return f"<Document(title='{self.document_title}', year={self.year})>"

# --- Pydantic Schemas for API ---
class DocumentBase(BaseModel):
    """Base schema for document data."""
    document_title: str
    document_type: str
    year: Optional[int] = None
    quarter: Optional[int] = None
    pdf_url: str

class DocumentCreate(DocumentBase):
    """Schema for POST /create request body."""
    # Inherits all fields from DocumentBase
    pass

class DocumentRead(DocumentBase):
    """Schema for GET /read response."""
    id: int #include id number
    
    class Config:
        # Allows Pydantic to read data from an ORM model
        from_attributes = True