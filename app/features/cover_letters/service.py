"""Cover Letters Feature - Business Logic Service"""
import logging
from app.features.cover_letters.models import CoverLetterCreate, CoverLetterResponse
from app.features.cover_letters.generator import CoverLetterGenerator


logger = logging.getLogger("resume_flow")


class CoverLetterService:
    """Service for cover letter generation"""
    
    def __init__(self):
        self.generator = CoverLetterGenerator()
    
    def generate_cover_letter(self, request: CoverLetterCreate) -> CoverLetterResponse:
        """
        Generate a personalized cover letter using AI.
        
        Args:
            request: Cover letter generation request
            
        Returns:
            Generated cover letter response
        """
        logger.info(f"Generating cover letter for {request.user_name}")
        result = self.generator.generate_cover_letter(request)
        return CoverLetterResponse(**result)


# Global service instance
cover_letter_service = CoverLetterService()
