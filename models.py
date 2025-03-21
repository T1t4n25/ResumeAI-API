from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
import base64

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
    
class UserInformation(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    address: Optional[str] = Field(None, description="Physical address")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    summary: Optional[str] = Field(None, description="Professional summary")

class Education(BaseModel):
    institution: str = Field(..., description="Name of educational institution")
    degree: str = Field(..., description="Degree obtained")
    field: str = Field(..., description="Field of study")
    start_date: str = Field(..., description="Start date of education")
    end_date: str = Field(..., description="End date or expected completion")
    gpa: Optional[str] = Field(None, description="GPA if applicable")

class Project(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    end_date: Any = Field(..., description="Project completion date")
    technologies: Optional[List[str]] = Field(None, description="Technologies used")
    url: Optional[str] = Field(None, description="Project URL if available")

class Experience(BaseModel):
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    start_date: Any = Field(..., description="Start date of employment")
    end_date: Any = Field(..., description="End date of employment or 'Present'")
    description: str = Field(..., description="Job description and achievements")
    location: Optional[str] = Field(None, description="Job location")

class TechnicalSkills(BaseModel):
    categories: Dict[str, List[str]] = Field(
        ...,
        description="Technical skills organized by categories",
        example={
            "Programming Languages": ["Python", "Java"],
            "Tools": ["Git", "Docker"],
            "Other Skills": ["AWS", "Azure"]
        }
    )

class CreateResumeRequest(BaseModel):
    information: UserInformation
    education: Optional[List[Education]] = Field(
        None,
        description="List of educational qualifications"
    )
    projects: Optional[List[Project]] = Field(
        None,
        description="List of projects"
    )
    experience: Optional[List[Experience]] = Field(
        None,
        description="List of work experiences"
    )
    technical_skills: Optional[TechnicalSkills] = Field(
        None,
        description="Technical skills with custom categories"
    )
    soft_skills: Optional[List[str]] = Field(
        None,
        description="List of soft skills",
        example=["Communication", "Problem Solving"]
    )
    output_format: str = Field(
        ...,
        description="Desired output format",
        example="pdf",
        pattern="^(pdf|tex|both)$"
    )

class CreateResumeResponse(BaseModel):
    pdf_file: Optional[str] = Field(
        None,
        description="Base64 encoded PDF file content"
    )
    tex_file: Optional[str] = Field(
        None,
        description="LaTeX source code as string"
    )

    class Config:
        json_encoders = {
            bytes: lambda v: base64.b64encode(v).decode('utf-8')
        }