import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

# Local imports
from models import (
    CoverLetterRequest, 
    CoverLetterResponse, 
    ProjectDescriptionRequest, 
    ProjectDescriptionResponse,
    SummaryRequest,
    SummaryResponse
)
from api_key_manager import APIKeyManager
from cover_letter_generator import CoverLetterGenerator
from project_description_generator import ProjectDescriptionGenerator
from summary_generator import SummaryGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize managers
api_key_manager = APIKeyManager()
cover_letter_generator = CoverLetterGenerator()
project_description_generator = ProjectDescriptionGenerator()
summary_generator = SummaryGenerator()


# Create FastAPI app
app = FastAPI(
    title="Resume Flow API",
    description="""
    AI-powered generator for:
    - Professional Cover Letters
    - Project Descriptions for CV
    
    Built with FastAPI and Google's Gemini AI.
    """,
    version="2.0.0"
)

# Create API Key Header dependency
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    API Key validation dependency
    """
    if not api_key:
        raise HTTPException(
            status_code=403, 
            detail="Could not validate credentials"
        )
    
    # Use the API key manager to validate
    try:
        if api_key not in api_key_manager.valid_api_keys:
            raise HTTPException(
                status_code=403, 
                detail="Invalid API key"
            )
        return api_key
    except Exception:
        raise HTTPException(
            status_code=403, 
            detail="Could not validate credentials"
        )


@app.post("/generate-cover-letter", 
          response_model=CoverLetterResponse)
async def generate_cover_letter(
    request: CoverLetterRequest,
    api_key: str = Depends(api_key_manager.validate_api_key)
):
    """
    Generate a personalized cover letter
    """
    try:
        result = cover_letter_generator.generate_cover_letter(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating cover letter: {str(e)}"
        )

@app.post("/generate-project-description", 
          response_model=ProjectDescriptionResponse)
async def generate_project_description(
    request: ProjectDescriptionRequest,
    api_key: str = Depends(api_key_manager.validate_api_key)
):
    """
    Generate a professional project description for CV
    """
    try:
        description = project_description_generator.generate_description(request)
        return {"project_description": description}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating project description: {str(e)}"
        )

@app.post("/generate-summary", 
          response_model=SummaryResponse,
          dependencies=[Depends(api_key_manager.validate_api_key)])
async def generate_summary(request: SummaryRequest):
    """
    Generate a professional summary for resume
    """
    try:
        summary = summary_generator.generate_summary(request)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )

        
@app.get("/generate-api-key")
def create_api_key():
    """
    Generate a new API key
    In production, add authentication/authorization
    """
    new_key = api_key_manager.generate_new_api_key()
    return {"api_key": new_key}

@app.get("/health")
def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)