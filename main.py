import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("No Gemini API key set. Please set GEMINI_API_KEY environment variable.")

PORT = int(os.getenv('PORT', 8000))

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
class CoverLetterResponse(BaseModel):
    cover_letter: str = Field(
        description="""
        AI-generated cover letter. 
        
        IMPORTANT NOTE: 
        - Each generation is unique
        - Content may vary between requests
        - Focuses on matching job requirements
        - Personalized to input details
        """,
        examples="""Dear Hiring Manager,

I am writing to apply for the Senior .NET Developer position at TechInnovate Solutions.  With five years of experience as a Software Engineer specializing in .NET development, my skills and experience align perfectly with your requirements. My background in building scalable web applications and implementing microservices architectures makes me a strong candidate for this role.

My expertise encompasses C#, .NET Core, and Azure cloud technologies, including extensive experience with SQL Server and the development of RESTful APIs.  In my previous role, I spearheaded the migration of a legacy application to .NET Core, resulting in a 30% performance improvement and a 15% reduction in infrastructure costs. I also designed and implemented a new microservices architecture for a high-traffic e-commerce platform, significantly enhancing scalability and maintainability. This involved leveraging Azure services such as App Service, Azure SQL Database, and Azure Service Bus. My contributions consistently delivered reliable, high-performing solutions.

I am confident I can make a significant contribution to TechInnovate Solutions. My understanding of your company’s focus on innovative cloud-based solutions, coupled with my proven ability to deliver results in a fast-paced environment, makes me an ideal fit.  I am particularly excited by the opportunity to leverage my expertise in microservices architecture to contribute to your ongoing projects.

Thank you for your time and consideration. I am eager to discuss how my skills and experience can benefit TechInnovate Solutions and welcome the opportunity to speak with you further.

Sincerely,
John Doe
"""
    )

app = FastAPI(
    title="Cover Letter Generator API",
    description="""
    ## Cover Letter Generation API

    ### 🤖 AI-Powered Cover Letter Generation

    #### Key Points:
    - Uses Google's Gemini AI
    - Dynamically generates unique cover letters
    - Tailored to specific job postings
    - Personalized to individual profiles

    ### ⚠️ Important Disclaimer
    - Each cover letter generation is unique
    - Content will vary between requests
    - AI aims to capture key professional details
    - Recommended to review and personalize further

    ### 🎯 Generation Approach
    1. Analyze job posting
    2. Incorporate professional profile
    3. Generate contextually relevant content
    4. Maintain professional tone and structure

    ### 🛠 Recommended Workflow
    - Use generated letter as a strong draft
    - Review and customize as needed
    - Highlight personal achievements
    - Align with specific job nuances
    """,
    version="1.0.0",
    contact={
        "name": "Zeyad Hemeda",
        "email": "zeyad.mohammedwork@gmail.com",
    },
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc alternative documentation
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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