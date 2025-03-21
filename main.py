import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import requests
import datetime
from contextlib import asynccontextmanager
from time import strftime
import subprocess
from pathlib import Path

# Local imports
from models import (
    CoverLetterRequest, 
    CoverLetterResponse, 
    ProjectDescriptionRequest, 
    ProjectDescriptionResponse,
    SummaryRequest,
    SummaryResponse,
    CreateResumeRequest,
    CreateResumeResponse
)
from api_key_manager import APIKeyManager
from cover_letter_generator import CoverLetterGenerator
from project_description_generator import ProjectDescriptionGenerator
from summary_generator import SummaryGenerator
from resume_creator import ResumeTexGenerator

# Load environment variables
load_dotenv()

# Configure logging
LOG_FILENAME = datetime.datetime.now().strftime('logs/logfile_%Y_%m_%d.log')
logging.basicConfig(level=logging.INFO, filename=LOG_FILENAME)
logger = logging.getLogger("uvicorn")

handler_file = logging.FileHandler(LOG_FILENAME)
handler_file.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler_file)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize logging for the lifespan of the application
    """

    # Update IP address for dynamic DNS
    try:
        response = requests.get(f"http://api-ipv4.dynu.com/nic/update?hostname=resumeai.webredirect.org&password={os.getenv('DYNU_PASS')}")
        logger.info(f"IP address updated: {response.text}")
    except Exception as e:
        logger.error(f"Error updating IP address: {str(e)}")
            
    yield
    try:
        logoff_ip = requests.get(f"http://api.dynu.com/nic/update?hostname=resumeai.webredirect.org&password={os.getenv('DYNU_PASS')}&offline=yes")
        logger.info(f"IP address logged off: {logoff_ip.text}")
    except Exception as e:
        logger.error(f"Error logging off IP address: {str(e)}")
        
    logger.info("Shutting down...")
    logger.removeHandler(handler_file)
    handler_file.close()
    
# create log folder if not existed
if not os.path.exists('logs'):
    os.makedirs('logs')

api_key_manager = APIKeyManager(logger=logger)
cover_letter_generator = CoverLetterGenerator()
project_description_generator = ProjectDescriptionGenerator()
summary_generator = SummaryGenerator()
summary_generator = SummaryGenerator()


# Create FastAPI app
app = FastAPI(
    title="Resume Flow API",
    description="""
    AI-powered generator for:
    - Professional Cover Letters
    - Summary and Project Descriptions for CV
    - Create Resume using LaTeX
    
    Built with FastAPI and Google's Gemini AI.
    """,
    version="3.0.0",
    lifespan=lifespan
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

@app.post("/create-resume", 
         response_model=CreateResumeResponse,
         dependencies=[Depends(api_key_manager.validate_api_key)])
async def create_resume(request: CreateResumeRequest):
    """
    Generate a complete resume using LaTeX
    """
    logger.info(f"Received resume creation request for output format: {request.output_format}")
    try:
        # Fix: Access Pydantic model attributes using dot notation
        user_id = f"{request.information.name}-" + strftime("%Y%m%d-%H%M%S")
        output_dir = Path("generated_resumes")
        output_dir.mkdir(exist_ok=True)
        
        if request.output_format == "tex":
            resume_generator = ResumeTexGenerator(request=request, user_id=user_id)
            tex_file = resume_generator.generate_tex()
            return CreateResumeResponse(pdf_file=None, tex_file=tex_file)
            
        elif request.output_format == "pdf":
            # Save TEX file first
            resume_generator = ResumeTexGenerator(request=request, user_id=user_id)
            tex_content = resume_generator.generate_tex()
            tex_path = output_dir / f"{user_id}.tex"
            tex_path.write_text(tex_content)
            
            # Compile PDF using subprocess
            try:
                subprocess.run([
                    'latexmk',
                    '-pdf',
                    f'-jobname={user_id}',
                    tex_path
                ], cwd=output_dir, check=True, capture_output=True)
                
                pdf_path = output_dir / f"{user_id}.pdf"
                if pdf_path.exists():
                    pdf_content = pdf_path.read_bytes()
                    # Clean up temporary files
                    subprocess.run(['latexmk', '-c'], cwd=output_dir)
                    return CreateResumeResponse(pdf_file=pdf_content, tex_file=None)
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="PDF file was not generated"
                    )
                    
            except subprocess.CalledProcessError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"LaTeX compilation failed: {e.stderr.decode()}"
                )
        elif request.output_format == "both":
            # Save TEX file
            resume_generator = ResumeTexGenerator(request=request, user_id=user_id)
            tex_content = resume_generator.create_resume(request)
            tex_path = output_dir / f"{user_id}.tex"
            tex_path.write_text(tex_content)

            # Compile PDF
            try:
                subprocess.run([
                    'latexmk',
                    '-pdf',
                    f'-jobname={user_id}',
                    tex_path
                ], cwd=output_dir, check=True, capture_output=True)
                
                pdf_path = output_dir / f"{user_id}.pdf"
                if pdf_path.exists():
                    pdf_content = pdf_path.read_bytes()
                    # Clean up temporary files
                    subprocess.run(['latexmk', '-c'], cwd=output_dir)
                    return CreateResumeResponse(pdf_file=pdf_content, tex_file=tex_content)
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="PDF file was not generated"
                    )
                    
            except subprocess.CalledProcessError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"LaTeX compilation failed: {e.stderr.decode()}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid output format specified"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating resume: {str(e)}"
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
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")