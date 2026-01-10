"""Summaries Feature - Business Logic Service"""
import logging
from app.features.summaries.models import SummaryRequest, SummaryResponse
from app.features.summaries.generator import SummaryGenerator


logger = logging.getLogger("resume_flow")


class SummaryService:
    """Service for professional summary generation"""
    
    def __init__(self):
        self.generator = SummaryGenerator()
    
    def generate_summary(self, request: SummaryRequest) -> SummaryResponse:
        """
        Generate a professional summary for resume using AI.
        
        Args:
            request: Summary generation request
            
        Returns:
            Generated summary response
        """
        logger.info(f"Generating summary for {request.current_title}")
        summary = self.generator.generate_summary(request)
        return SummaryResponse(summary=summary)


# Global service instance
summary_service = SummaryService()
