"""Resumes Feature - Business Logic Service"""
import logging
import json
import subprocess
from pathlib import Path
from fastapi import HTTPException

from app.features.resumes.models import CreateResumeRequest, CreateResumeResponse
from app.features.resumes.generator import ResumeTexGenerator


logger = logging.getLogger("resume_flow")


class ResumeService:
    """Service for resume generation"""
    
    def create_resume(self, request: CreateResumeRequest, username: str = "user") -> CreateResumeResponse:
        """
        Create a complete resume using LaTeX.
        
        Args:
            request: Resume creation request
            username: Username for logging purposes
            
        Returns:
            Generated resume response (PDF and/or LaTeX)
            
        Raises:
            HTTPException: If LaTeX compilation fails
        """
        logger.info(f"Resume creation requested by {username} for output format: {request.output_format}")
        
        request_dict = json.loads(request.model_dump_json())
        logger.debug(f"Request information dump: {request_dict}")
        
        resume_generator = ResumeTexGenerator(request=request_dict)
        output_format = request_dict['output_format']
        
        try:
            if output_format == "tex":
                tex_content = resume_generator.generate_tex()
                logger.info(f"Tex generated successfully for user {username}")
                return CreateResumeResponse(pdf_file=None, tex_file=tex_content)
            
            elif output_format == "pdf":
                try:
                    pdf_path = resume_generator.generate_pdf()
                    pdf_content = pdf_path.read_bytes()
                    resume_generator.cleanup()  # Clean up temporary files
                    
                    logger.info(f"PDF generated successfully for user {username}")
                    return CreateResumeResponse(pdf_file=pdf_content, tex_file=None)
                
                except subprocess.CalledProcessError as e:
                    logger.error(f"LaTeX compilation failed for user {username}: {e.stderr.decode()}")
                    raise HTTPException(
                        status_code=500,
                        detail="PDF compilation failed"
                    )
            
            elif output_format == "both":
                tex_content = resume_generator.generate_tex()
                
                # Compile PDF
                try:
                    pdf_path = resume_generator.generate_pdf()
                    pdf_content = pdf_path.read_bytes()
                    resume_generator.cleanup()  # Clean up temporary files
                    logger.info(f"PDF & Tex generated successfully for user {username}")
                    return CreateResumeResponse(pdf_file=pdf_content, tex_file=tex_content)
                
                except subprocess.CalledProcessError as e:
                    logger.error(f"LaTeX compilation failed for user {username}: {e.stderr.decode()}")
                    raise HTTPException(
                        status_code=500,
                        detail="PDF compilation failed"
                    )
            
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid output format specified"
                )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating resume for user {username}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error generating resume\nPlease report this issue to the developers."
            )


# Global service instance
resume_service = ResumeService()
