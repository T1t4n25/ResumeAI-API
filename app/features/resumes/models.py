"""Resumes Feature - Pydantic Models"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional
import base64


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


class CreateResumeResponse(BaseModel):
    """Response model for resume creation"""
    pdf_file: Optional[bytes] = Field(
        None,
        description="Base64 encoded PDF file content"
    )
    tex_file: Optional[str] = Field(
        None,
        description="LaTeX source code as string"
    )
    
    @field_serializer('pdf_file')
    def serialize_pdf(self, pdf_file: Optional[bytes]) -> Optional[str]:
        if pdf_file is None:
            return None
        return base64.b64encode(pdf_file).decode('utf-8')
