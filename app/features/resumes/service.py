"""Resumes Feature - Business Logic Service"""
import logging
import json
from fastapi import HTTPException
import uuid
from app.features.resumes.models import CreateResumeRequest, CreateResumeResponse
from app.features.resumes.generator import ResumeTexGenerator


logger = logging.getLogger("resume_flow")


class ResumeService:
    """Service for resume generation"""
    
    def create_resume_latex(self, request: CreateResumeRequest, username: str = "user") -> CreateResumeResponse:
        """
        Create a complete resume using LaTeX.
        
        Args:
            request: Resume creation request
            username: Username for logging purposes
            
        Returns:
            Generated resume response (LaTeX)
            
        Raises:
            HTTPException: If LaTeX compilation fails
        """
        logger.info(f"Resume creation requested by {username} for output format: {request.output_format}")
        
        request_dict = json.loads(request.model_dump_json())
        logger.debug(f"Request information dump: {request_dict}")
        
        resume_generator = ResumeTexGenerator(request=request_dict)
        
        try:
            tex_content = resume_generator.generate_tex()
            return CreateResumeResponse(
                id=str(uuid.uuid7()),
                tex_file=tex_content,
                output_format="tex"
            )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating resume for user {username}: {str(e)}")
            raise
                

# Global service instance
resume_service = ResumeService()
