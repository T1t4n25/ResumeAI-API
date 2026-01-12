"""Resumes Feature - Pydantic Models"""
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Optional
from datetime import datetime
import base64
import uuid


class CreateResumeRequest(BaseModel):
    """Request model for resume creation"""
    information: dict[str, str] = Field(
        ...,
        description="User Information",
        examples=[{
            "name": "John Doe",
            "email": "example@gmail.com",
            "phone": "01123456789",
            "address": "123 Example Street",
            "linkedin": "linkedin.com/in/example",
            "github": "github.com/example",
            "summary": "Software engineer with 5 years experience"
        }]
    )
    education: Optional[list[dict[str, str]]] = Field(
        None,
        description="List of educational qualifications",
        examples=[[{
            "degree": "BSc Computer Science",
            "school": "Example University",
            "start_date": '2016',
            "end_date": '2020',
            "location": 'Tanta, Egypt',
            "gpa": '3.5'
        }]]
    )
    projects: Optional[list[dict[str, str]]] = Field(
        None,
        description="List of projects",
        examples=[[{
            "name": "Project Name",
            "skills": "Python, FastAPI, Google Gemini AI, PyTest, Pydantic",
            "description": "Project description",
            "end_date": '2022'
        }]]
    )
    experience: Optional[list[dict[str, str]]] = Field(
        None,
        description="List of work experiences",
        examples=[[{
            "title": "Software Engineer",
            "company": "Example Company",
            "start_date": '2020',
            "end_date": "Present",
            "description": "Job description"
        }]]
    )
    technical_skills: Optional[dict[str, list[str]]] = Field(
        None,
        description="Technical skills with custom categories",
        examples=[{
            "Programming Languages": ["Python", "Java"],
            "Tools": ["Git", "Docker"],
            "Other Skills": ["AWS", "Azure"]
        }]
    )
    soft_skills: Optional[list] = Field(
        None,
        description="List of soft skills",
        examples=[["Communication", "Problem Solving"]]
    )
    output_format: str = Field(
        ...,
        description="Desired output format",
        examples=["pdf"],
        pattern="^(pdf|tex|both)$"
    )


class ResumeResponse(BaseModel):
    """Response model for resume"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "output_format": "pdf",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "pdf_url": "/resumes/550e8400-e29b-41d4-a716-446655440000/pdf",
            "latex_url": "/resumes/550e8400-e29b-41d4-a716-446655440000/latex"
        }
    })
    
    id: str = Field(..., description="Unique identifier for the resume")
    output_format: str = Field(..., description="Output format used (pdf, tex, or both)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    pdf_url: Optional[str] = Field(None, description="URL to download PDF version")
    latex_url: Optional[str] = Field(None, description="URL to download LaTeX source")


class CreateResumeResponse(BaseModel):
    """Response model for resume creation (includes file content)"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "pdf_file": "base64_encoded_pdf_content...",
            "tex_file": "\\documentclass{article}...",
            "output_format": "pdf"
        }
    })
    
    id: str = Field(..., description="Unique identifier for the resume")
    pdf_file: Optional[str] = Field(
        None,
        description="Base64 encoded PDF file content (only if output_format is 'pdf' or 'both')"
    )
    tex_file: Optional[str] = Field(
        None,
        description="LaTeX source code as string (only if output_format is 'tex' or 'both')"
    )
    output_format: str = Field(..., description="Output format used")
    
    @field_serializer('pdf_file')
    def serialize_pdf(self, pdf_file: Optional[str]) -> Optional[str]:
        if pdf_file is None:
            return None
        return pdf_file


class ResumeListResponse(BaseModel):
    """Response model for listing resumes"""
    data: list[ResumeResponse]
    total: int
    limit: int = 10
    offset: int = 0
