"""Cover Letters Feature - Pydantic Models"""
from pydantic import BaseModel, Field
from typing import Optional


class CoverLetterRequest(BaseModel):
    """Request model for cover letter generation"""
    job_post: str = Field(
        ..., 
        description="Full job posting text",
        examples=["Senior .NET Developer at TechInnovate Solutions. We are seeking an experienced .NET professional with strong skills in C#, .NET Core, and cloud technologies."]
    )
    user_name: str = Field(
        ..., 
        description="Full name of the job applicant",
        examples=["John Doe"]
    )
    user_degree: str = Field(
        description="Highest educational degree",
        examples=["Bachelor of Science in Computer Science"]
    )
    user_title: str = Field(
        description="Current professional title",
        examples=["Software Engineer"]
    )
    user_experience: str = Field(
        description="Professional experience summary",
        examples=["5 years of professional .NET development experience"]
    )
    user_skills: str = Field(
        description="Relevant professional skills",
        examples=["C#, .NET Core, Azure, SQL Server, RESTful APIs"]
    )


class CoverLetterResponse(BaseModel):
    """Response model for cover letter generation"""
    cover_letter: str
    tokens_used: Optional[int] = None
