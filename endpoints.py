import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import exc
from database import get_db
from models import Document, DocumentCreate, DocumentRead

router = APIRouter()

@router.post("/create", response_model=DocumentRead, status_code=201)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    """
    Endpoint to add a new document to the database.
    Handles duplicate URL conflicts.
    """
    db_document = Document(
        document_title=document.document_title,
        document_type=document.document_type,
        year=document.year,
        quarter=document.quarter,
        pdf_url=document.pdf_url,
    )
    
    try:
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    except exc.IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, 
            detail=f"Document with URL '{document.pdf_url}' already exists."
        )

@router.get("/read", response_model=List[DocumentRead])
def read_documents(
    document_type: Optional[str] = Query(None, description="Filter by document type."),
    year: Optional[int] = Query(None, description="Filter by year."),
    quarter: Optional[int] = Query(None, description="Filter by quarter."),
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Endpoint to retrieve documents with optional filtering.
    """
    query = db.query(Document)
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
        
    if year:
        query = query.filter(Document.year == year)
        
    if quarter:
        query = query.filter(Document.quarter == quarter)
        
    documents = query.limit(limit).all()
    
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found matching the criteria.")
        
    return documents