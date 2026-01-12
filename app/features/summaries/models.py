"""Summaries Feature - Pydantic Models"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class SummaryCreate(BaseModel):
    """Request model for summary creation"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "current_title": "Senior Software Engineer",
            "years_experience": "5+ years",
            "skills": "Python, React, AWS, Microservices",
            "achievements": "Led team of 5, Reduced system latency by 40%"
        }
    })
    
    current_title: str = Field(..., description="Your current job title")
    years_experience: str = Field(..., description="Years of professional experience")
    skills: str = Field(..., description="Key skills and technologies")
    achievements: Optional[str] = Field(None, description="Notable achievements or impacts (optional)")


# Keep old name for backward compatibility
SummaryRequest = SummaryCreate


class SummaryResponse(BaseModel):
    """Response model for summary"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "summary": "Experienced Senior Software Engineer with 5+ years...",
            "current_title": "Senior Software Engineer",
            "years_experience": "5+ years",
            "skills": "Python, React, AWS, Microservices",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    })
    
    id: str = Field(..., description="Unique identifier for the summary")
    summary: str = Field(..., description="Generated professional summary for resume")
    current_title: str = Field(..., description="Job title used in generation")
    years_experience: str = Field(..., description="Years of experience")
    skills: str = Field(..., description="Skills used in generation")
    achievements: Optional[str] = Field(None, description="Achievements used in generation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class SummaryListResponse(BaseModel):
    """Response model for listing summaries"""
    data: list[SummaryResponse]
    total: int
    limit: int = 10
    offset: int = 0
