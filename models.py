from pydantic import BaseModel, Field
from typing import Optional
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
    
class CreateResumeRequest(BaseModel):
    information: dict[str, str] = Field(
        ...,
        description="User Information",
        example={
            "name": "John Doe",
            "email": "example@gmail.com",
            "phone": "01123456789",
            "address": "123 Example Street",
            "linkedin": "linkedin.com/in/example",
            "github": "github.com/example",
            "summary": "Software engineer with 5 years experience"
        }
    )
    education: Optional[list[dict[str, str]]] = Field(
        None,
        description="List of educational qualifications",
        example=[{
            "degree": "BSc Computer Science",
            "school": "Example University",
            "start_date": '2016',
            "end_date": '2020',
            "location": 'Tanta, Egypt',
            "gpa": '3.5'
        }]
    )
    projects: Optional[list[dict[str, str]]] = Field(
        None,
        description="List of projects",
        example=[{
            "name": "Project Name",
            "skills": "Python, FastAPI, Google Gemini AI, PyTest, Pydantic",
            "description": "Project description",
            "end_date": '2022'
        }]
    )
    experience: Optional[list[dict[str, str]]] = Field(
        None,
        description="List of work experiences",
        example=[{
            "title": "Software Engineer",
            "company": "Example Company",
            "start_date": '2020',
            "end_date": "Present",
            "description": "Job description"
        }]
    )
    technical_skills: Optional[dict[str, list[str]]] = Field(
        None,
        description="Technical skills with custom categories",
        example={
            "Programming Languages": ["Python", "Java"],
            "Tools": ["Git", "Docker"],
            "Other Skills": ["AWS", "Azure"]
        }
    )
    soft_skills: Optional[list] = Field(
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
    pdf_file: Optional[bytes] = Field(
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