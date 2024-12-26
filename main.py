from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import google.generativeai as genai
from API_KEYS import GEMINI_API_KEY

class CoverLetterRequest(BaseModel):
    job_post: str = Field(
        ..., 
        description="Full job posting text",
        example="Senior .NET Developer position at Tech Company, seeking experienced professional..."
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
        example="5 years of .NET development experience"
    )
    user_skills: str = Field(
        description="Relevant professional skills",
        example="C#, .NET Core, Azure, SQL Server"
    )

app = FastAPI(
    title="Cover Letter Generator API",
    description="""
    ## Cover Letter Generation API

    This API uses Google's Gemini AI to generate personalized cover letters based on:
    - Job Posting Details
    - Applicant's Professional Profile

    ### Features:
    - AI-powered cover letter generation
    - Personalization based on user input
    - Professional formatting

    ### Requirements:
    - Provide complete job posting
    - Include applicant's professional details
    """,
    version="1.0.0",
    contact={
        "name": "Zeyad Hemeda",
        "email": "shadodiss@gmail.com",
    },
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc alternative documentation
)

@app.post("/generate-cover-letter", 
          response_model=dict,
          summary="Generate Personalized Cover Letter",
          description="Creates a tailored cover letter using Gemini AI")
async def generate_cover_letter(request: CoverLetterRequest):
    """
    Generate a cover letter with the following steps:
    1. Analyze job posting
    2. Incorporate user's professional details
    3. Create personalized cover letter using Gemini AI
    """
    try:
        # Existing Gemini configuration and generation logic
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        cover_letter_prompt = f"""
Craft a professional cover letter for a .NET developer position, focusing solely on the essential content. Eliminate any placeholder or template-style headers like addresses or contact information. 

Job Posting Context:
{request.job_post}

Candidate Professional Profile:
- Name: {request.user_name}
- Professional Title: {request.user_title}
- Degree: {request.user_degree}
- Professional Experience: {request.user_experience}
- Key Skills: {request.user_skills}

Writing Guidelines:
1. Begin directly with "Dear Hiring Manager,"

2. First Paragraph:
   - Immediately state the position you're applying for
   - Briefly introduce professional background
   - Create an immediate connection to the job requirements

3. Second Paragraph (Experience & Skills):
   - Directly address key technical requirements
   - Provide specific examples of relevant achievements
   - Quantify impacts where possible
   - Highlight most relevant technical skills

4. Third Paragraph (Value Proposition):
   - Explain why you're an ideal candidate
   - Demonstrate understanding of the company's technical needs
   - Express enthusiasm for potential contribution

5. Closing Paragraph:
   - Thank the reader for their consideration
   - Express interest in further discussion
   - Create a subtle call to action

Specific Requirements:
- Total length: 250-300 words
- Use a professional, confident tone
- Focus on technical achievements
- Avoid generic statements
- Sign off with "Sincerely, John Doe"

Emphasize:
- Specific .NET and cloud technologies
- Practical experience
- Measurable impacts
- Alignment with job requirements

Generate a concise, impactful cover letter that goes straight to the professional content.
"""
        response = model.generate_content(cover_letter_prompt)
        
        return {
            "cover_letter": response.text
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating cover letter: {str(e)}"
        )

# Optional: Add error handling middleware
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

# Run with: uvicorn main:app --reload