from pydantic import BaseModel, Field
from typing import Optional

class CoverLetterRequest(BaseModel):
    job_post: str = Field(
        ..., 
        description="Full job posting text",
        example="Senior .NET Developer at TechInnovate Solutions. We are seeking an experienced .NET professional with strong skills in C#, .NET Core, and cloud technologies."
    )
    user_name: str = Field(
        ..., 
        description="Full name of the job applicant",
        example="John Doe"
    )
    user_degree: str = Field(
        description="Highest educational degree",
        example="Bachelor of Science in Computer Science"
    )
    user_title: str = Field(
        description="Current professional title",
        example="Software Engineer"
    )
    user_experience: str = Field(
        description="Professional experience summary",
        example="5 years of professional .NET development experience"
    )
    user_skills: str = Field(
        description="Relevant professional skills",
        example="C#, .NET Core, Azure, SQL Server, RESTful APIs"
    )

class CoverLetterResponse(BaseModel):
    cover_letter: str
    tokens_used: Optional[int] = None

class ProjectDescriptionRequest(BaseModel):
    project_name: str = Field(
        ..., 
        description="Name of the project",
        example="E-commerce Website"
    )
    skills: str = Field(
        ...,
        description="Technologies and skills used in the project",
        example="React, Firebase, Stripe, REST APIs"
    )
    project_description: Optional[str] = Field(
        None,
        description="Additional description of the project (optional)",
        example="Built a website for an online store. Users can browse products, add to cart, and checkout."
    )

class ProjectDescriptionResponse(BaseModel):
    project_description: str = Field(
        ...,
        description="Generated professional project description for CV"
    )
    
class SummaryRequest(BaseModel):
    current_title: str = Field(
        ..., 
        description="Your current job title",
        example="Senior Software Engineer"
    )
    years_experience: str = Field(
        ...,
        description="Years of professional experience",
        example="5+ years"
    )
    skills: str = Field(
        ...,
        description="Key skills and technologies",
        example="Python, React, AWS, Microservices"
    )
    achievements: Optional[str] = Field(
        None,
        description="Notable achievements or impacts (optional)",
        example="Led team of 5, Reduced system latency by 40%"
    )

class SummaryResponse(BaseModel):
    summary: str = Field(
        ...,
        description="Generated professional summary for resume"
    )