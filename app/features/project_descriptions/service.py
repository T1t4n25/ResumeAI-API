"""Project Descriptions Feature - Business Logic Service"""
import logging
from app.features.project_descriptions.models import ProjectDescriptionRequest, ProjectDescriptionResponse
from app.features.project_descriptions.generator import ProjectDescriptionGenerator


logger = logging.getLogger("resume_flow")


class ProjectDescriptionService:
    """Service for project description generation"""
    
    def __init__(self):
        self.generator = ProjectDescriptionGenerator()
    
    def generate_description(self, request: ProjectDescriptionRequest) -> ProjectDescriptionResponse:
        """
        Generate a professional project description using AI.
        
        Args:
            request: Project description generation request
            
        Returns:
            Generated project description response
        """
        logger.info(f"Generating project description for {request.project_name}")
        description = self.generator.generate_description(request)
        return ProjectDescriptionResponse(project_description=description)


# Global service instance
project_description_service = ProjectDescriptionService()
