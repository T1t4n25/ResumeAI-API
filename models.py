from pydantic import ConfigDict, BaseModel, Field, field_serializer
from typing import Optional
import base64

class CoverLetterRequest(BaseModel):
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
    cover_letter: str
    tokens_used: Optional[int] = None

class ProjectDescriptionRequest(BaseModel):
    project_name: str = Field(
        ..., 
        description="Name of the project",
        examples=["E-commerce Website"]
    )
    skills: str = Field(
        ...,
        description="Technologies and skills used in the project",
        examples=["React, Firebase, Stripe, REST APIs"]
    )
    project_description: Optional[str] = Field(
        None,
        description="Additional description of the project (optional)",
        examples=["Built a website for an online store. Users can browse products, add to cart, and checkout."]
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
    summary: str = Field(
        ...,
        description="Generated professional summary for resume"
    )
    
class CreateResumeRequest(BaseModel):
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
    
class RegisterUserRequest(BaseModel):
    username: str = Field(
        ...,
        description="Username for the account",
        examples=["johndoe"]
    )
    password: str = Field(
        ...,
        description="Password for the account",
        examples=["securepassword123"]
    )

class RegisterUserResponse(BaseModel):
    message: str = Field(
        ...,
        description="Confirmation message for successful registration",
        examples=["User registered successfully"]
    )
    api_key: str = Field(
        ...,
        description="API key for accessing the service",
        examples=["your_generated_api_key"]
    )

class GenerateAPIKeyRequest(BaseModel):
    username: str = Field(
        ...,
        description="Username for which to generate the API key",
        examples=["johndoe"]
    )
    password: str = Field(
        ...,
        description="Password for the account",
        examples=["securepassword123"]
    )

class GenerateAPIKeyResponse(BaseModel):
    message: str = Field(
        ...,
        description="Confirmation message for successful API key generation",
        examples=["API key generated successfully"]
    )
    api_key: str = Field(
        ...,
        description="Generated API key for accessing the service",
        examples=["your_generated_api_key"]
    )

class GetAPIKeysRequest(BaseModel):
    api_key: str = Field(
        ...,
        description="API key for authentication",
        examples=["your_generated_api_key"]
    )
    
class GetAPIKeysResponse(BaseModel):
    username: str = Field(
        ...,
        description="Username associated with the API key",
        examples=["johndoe"]
    )
    api_keys: list[dict[str, str]] = Field(
        ...,
        description="List of API keys associated with the user",
        examples=[[{
            "id": "1",
            "api_key": "1BCDEFG8...",
            "created_at": "2023-10-01T12:00:00Z"
        }]]
    )

