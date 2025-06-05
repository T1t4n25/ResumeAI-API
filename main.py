import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from dotenv import load_dotenv
import requests
import datetime
from contextlib import asynccontextmanager
from time import strftime
import subprocess
from pathlib import Path
import json
import hashlib
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
from generation_endpoints.cover_letter_generator import CoverLetterGenerator
from generation_endpoints.project_description_generator import ProjectDescriptionGenerator
from generation_endpoints.summary_generator import SummaryGenerator
from resume_creator import ResumeTexGenerator
from Auth_DataBase.auth_database import AuthDatabase

# Load environment variables
load_dotenv()
output_dir = Path("logs")
output_dir.mkdir(exist_ok=True)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

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
        
    # Limiter setup
    
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# Initialize components
api_key_manager = APIKeyManager(logger=logger)
auth_db = AuthDatabase()
cover_letter_generator = CoverLetterGenerator()
project_description_generator = ProjectDescriptionGenerator()
summary_generator = SummaryGenerator()

# Define API Key security scheme
api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="API Key for authentication. Include your API key in the X-API-Key header."
)

# Security dependency function
async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validate API key using Security
    """
    if not api_key_manager.validate_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key

# Create FastAPI app
app = FastAPI(
    title="Resume Flow API",
    description="""
    AI-powered generator for:
    - Professional Cover Letters
    - Summary and Project Descriptions for CV
    - Create Resume using LaTeX
    
    Built with FastAPI, Google's Gemini AI and LaTeX.
    
    ## Authentication
    All protected endpoints require an API key in the `X-API-Key` header.
    
    ## Getting Started
    1. Register a new user account
    2. Use the returned API key for authenticated requests
    3. Include the API key in the `X-API-Key` header for all protected endpoints
    """,
    version="4.0.0",
    lifespan=lifespan,
    root_path="/api/resume-flow"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication endpoints
@app.post("/auth/register", tags=["Authentication"])
async def register_user(username: str, password: str):
    """
    Register a new user and generate their first API key
    """
    try:
        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create user
        user_id = auth_db.create_user(username, password_hash)
        
        # Generate API key for the user
        api_key = api_key_manager.generate_new_api_key(user_id)
        
        logger.info(f"New user registered: {username} with ID: {user_id}")
        
        return {
            "message": "User registered successfully",
            "api_key": api_key
        }
    except Exception as e:
        logger.error(f"Registration failed for {username}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/auth/generate-api-key", tags=["Authentication"])
async def generate_api_key(username: str, password: str):
    """
    Generate a new API key for existing user
    """
    try:
        # Hash the password to check
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Find user by username
        user = auth_db.get_user_by_username(username)
        
        if not user or user['password_hash'] != password_hash:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Generate new API key
        api_key = api_key_manager.generate_new_api_key(user['id'])
        
        logger.info(f"New API key generated for user: {username}")
        
        return {
            "message": "API key generated successfully",
            "api_key": api_key
        }
    except HTTPException:
        raise
    # except Exception as e:
    #     logger.error(f"API key generation failed for {username}: {str(e)}")
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"API key generation failed: {str(e)}"
    #     )

@app.get("/auth/my-api-keys", tags=["Authentication"])
async def get_my_api_keys(api_key: str = Security(get_api_key)):
    """
    Get all API keys for the authenticated user
    """
    try:
        user = api_key_manager.get_user_from_api_key(api_key)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        api_keys = auth_db.get_user_api_keys(user['id'])
        
        return {
            "username": user['username'],
            "api_keys": [
                {
                    "id": str(key['id']),
                    "api_key": key['api_key'][:8] + "...",  # Show only first 8 chars for security
                    "created_at": key['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                }
                for key in api_keys
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting API keys: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving API keys: {str(e)}"
        )

# Protected endpoints
@app.post("/generate-cover-letter", 
          response_model=CoverLetterResponse,
          tags=["Content Generation"])
@limiter.limit("5/minute")
async def generate_cover_letter(
    request: Request,
    user_data: CoverLetterRequest,
    api_key: str = Security(get_api_key)
):
    """
    Generate a personalized cover letter
    
    Requires valid API key in X-API-Key header.
    """
    try:
        # Log API usage
        user = api_key_manager.get_user_from_api_key(api_key)
        logger.info(f"Cover letter generation requested by user: {user['username'] if user else 'Unknown'}")
        
        result = cover_letter_generator.generate_cover_letter(user_data)
        return result
    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating cover letter: {str(e)}"
        )

@app.post("/generate-project-description", 
          response_model=ProjectDescriptionResponse,
          tags=["Content Generation"])
@limiter.limit("5/minute")
async def generate_project_description(
    request: Request,
    user_data: ProjectDescriptionRequest,
    api_key: str = Security(get_api_key)
):
    """
    Generate a professional project description for CV
    
    Requires valid API key in X-API-Key header.
    """
    try:
        # Log API usage
        user = api_key_manager.get_user_from_api_key(api_key)
        logger.info(f"Project description generation requested by user: {user['username'] if user else 'Unknown'}")
        
        description = project_description_generator.generate_description(user_data)
        return {"project_description": description}
    except Exception as e:
        logger.error(f"Error generating project description: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating project description: {str(e)}"
        )

@app.post("/generate-summary", 
          response_model=SummaryResponse,
          tags=["Content Generation"])
@limiter.limit("5/minute")
async def generate_summary(
    request: Request,
    user_data: SummaryRequest,
    api_key: str = Security(get_api_key)
):
    """
    Generate a professional summary for resume
    
    Requires valid API key in X-API-Key header.
    """
    try:
        # Log API usage
        user = api_key_manager.get_user_from_api_key(api_key)
        logger.info(f"Summary generation requested by user: {user['username'] if user else 'Unknown'}")
        
        summary = summary_generator.generate_summary(user_data)
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )

@app.post("/create-resume", 
         response_model=CreateResumeResponse,
         tags=["Content Generation"])
@limiter.limit("5/minute")
async def create_resume(
    request: Request,
    user_data: CreateResumeRequest,
    api_key: str = Security(get_api_key)
):
    """
    Generate a complete resume using LaTeX
    
    Requires valid API key in X-API-Key header.
    """
    try:
        # Log API usage
        user = api_key_manager.get_user_from_api_key(api_key)
        logger.info(f"Resume creation requested by user: {user['username'] if user else 'Unknown'} for output format: {user_data.output_format}")
        
        request_dict = json.loads(user_data.model_dump_json())
        logger.debug(f"Request information dump: {request_dict}")
        user_id = request_dict["information"]["name"].replace(" ", '') + "-" + strftime("%Y%m%d-%H%M%S")

        output_dir = Path("generated_resumes")
        output_dir.mkdir(exist_ok=True)
        
        if request_dict['output_format'] == "tex":
            resume_generator = ResumeTexGenerator(request=request_dict, user_id=user_id)
            tex_content = resume_generator.generate_tex()
            os.remove(f"generated_resumes/{user_id}.tex")
            return CreateResumeResponse(pdf_file=None, tex_file=tex_content)
            
        elif request_dict['output_format'] == "pdf":
            # Save TEX file first
            resume_generator = ResumeTexGenerator(request=request_dict, user_id=user_id)
            tex_content = resume_generator.generate_tex()
            
            # Compile PDF using subprocess
            try:
                # Convert Path object to string for subprocess
                working_dir = str(output_dir.absolute())
                
                subprocess.run([
                    'latexmk',
                    '-pdf',
                    '-f',
                    f'-jobname={user_id}',
                    f"{user_id}.tex"
                ], cwd=working_dir, check=True, capture_output=True, timeout=5)
                
                pdf_path = output_dir / f"{user_id}.pdf"
                if pdf_path.exists():
                    pdf_content = pdf_path.read_bytes()
                    # Clean up temporary files
                    subprocess.run(['latexmk', '-C'], cwd=working_dir, check=True)
                    os.remove(f"generated_resumes/{user_id}.tex")
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
        elif request_dict['output_format'] == "both":
            # Save TEX file
            resume_generator = ResumeTexGenerator(request=request_dict, user_id=user_id)
            tex_content = resume_generator.generate_tex()

            # Compile PDF 
            try:
                subprocess.run([
                    'latexmk',
                    '-pdf',
                    f'-jobname={user_id}',
                    f"{user_id}.tex"
                ], cwd=output_dir, check=True, capture_output=True)
                
                pdf_path = output_dir / f"{user_id}.pdf"
                if pdf_path.exists():
                    pdf_content = pdf_path.read_bytes()
                    # Clean up temporary files
                    subprocess.run(['latexmk', '-C'], cwd=output_dir)
                    os.remove(f"generated_resumes/{user_id}.tex")
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating resume: {str(e)}"
        )

# Public endpoints
@app.get("/health", tags=["Health"])
@limiter.limit("6/minute")
def health_check(request: Request):
    """
    Simple health check endpoint
    """
    return {"status": "healthy"}

@app.get("/", tags=["Info"])
@limiter.limit("6/minute")
def root(request: Request):
    """
    Root endpoint with API information
    """
    return {
        "message": "Resume Flow API",
        "version": "4.0.0",
        "endpoints": {
            "auth": ["/auth/register", "/auth/generate-api-key", "/auth/my-api-keys"],
            "protected": ["/generate-cover-letter", "/generate-project-description", "/generate-summary", "/create-resume"],
            "public": ["/health", "/"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")