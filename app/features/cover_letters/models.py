"""Cover Letters Feature - Pydantic Models"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class CoverLetterCreate(BaseModel):
    """Request model for cover letter creation"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_post": "Senior .NET Developer at TechInnovate Solutions...",
            "user_name": "John Doe",
            "user_degree": "Bachelor of Science in Computer Science",
            "user_title": "Software Engineer",
            "user_experience": "5 years of professional .NET development experience",
            "user_skills": "C#, .NET Core, Azure, SQL Server, RESTful APIs"
        }
    })
    
    job_post: str = Field(..., description="Full job posting text")
    user_name: str = Field(..., description="Full name of the job applicant")
    user_degree: Optional[str] = Field(None, description="Highest educational degree")
    user_title: Optional[str] = Field(None, description="Current professional title")
    user_experience: Optional[str] = Field(None, description="Professional experience summary")
    user_skills: Optional[str] = Field(None, description="Relevant professional skills")


# Keep old name for backward compatibility
CoverLetterRequest = CoverLetterCreate


class CoverLetterResponse(BaseModel):
    """Response model for cover letter"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "cover_letter": "Dear Hiring Manager,\n\n...",
            "tokens_used": 1250,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    })
    
    id: str = Field(..., description="Unique identifier for the cover letter")
    cover_letter: str = Field(..., description="Generated cover letter content")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used in generation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class CoverLetterListResponse(BaseModel):
    """Response model for listing cover letters"""
    data: list[CoverLetterResponse]
    total: int
    limit: int = 10
    offset: int = 0
