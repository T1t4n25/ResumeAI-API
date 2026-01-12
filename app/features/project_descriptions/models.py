"""Project Descriptions Feature - Pydantic Models"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ProjectDescriptionCreate(BaseModel):
    """Request model for project description creation"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "project_name": "E-commerce Website",
            "skills": "React, Firebase, Stripe, REST APIs",
            "project_description": "Built a website for an online store..."
        }
    })
    
    project_name: str = Field(..., description="Name of the project")
    skills: str = Field(..., description="Technologies and skills used in the project")
    project_description: Optional[str] = Field(None, description="Additional description of the project (optional)")


# Keep old name for backward compatibility
ProjectDescriptionRequest = ProjectDescriptionCreate


class ProjectDescriptionResponse(BaseModel):
    """Response model for project description"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "project_description": "Developed a full-stack e-commerce platform...",
            "project_name": "E-commerce Website",
            "skills": "React, Firebase, Stripe, REST APIs",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    })
    
    id: str = Field(..., description="Unique identifier for the project description")
    project_description: str = Field(..., description="Generated professional project description for CV")
    project_name: str = Field(..., description="Name of the project")
    skills: str = Field(..., description="Technologies and skills used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class ProjectDescriptionListResponse(BaseModel):
    """Response model for listing project descriptions"""
    data: list[ProjectDescriptionResponse]
    total: int
    limit: int = 10
    offset: int = 0
