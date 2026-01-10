"""Summaries Feature - Pydantic Models"""
from pydantic import BaseModel, Field
from typing import Optional


class SummaryRequest(BaseModel):
    """Request model for summary generation"""
    current_title: str = Field(
        ..., 
        description="Your current job title",
        examples=["Senior Software Engineer"]
    )
    years_experience: str = Field(
        ...,
        description="Years of professional experience",
        examples=["5+ years"]
    )
    skills: str = Field(
        ...,
        description="Key skills and technologies",
        examples=["Python, React, AWS, Microservices"]
    )
    achievements: Optional[str] = Field(
        None,
        description="Notable achievements or impacts (optional)",
        examples=["Led team of 5, Reduced system latency by 40%"]
    )


class SummaryResponse(BaseModel):
    """Response model for summary generation"""
    summary: str = Field(
        ...,
        description="Generated professional summary for resume"
    )
