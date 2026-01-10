"""Project Descriptions Feature - Pydantic Models"""
from pydantic import BaseModel, Field
from typing import Optional


class ProjectDescriptionRequest(BaseModel):
    """Request model for project description generation"""
    project_name: str = Field(
        ..., 
        description="Name of the project",
        examples=["E-commerce Website"]
    )
    skills: str = Field(
        ...,
        description="Technologies and skills used in the project",
        examples=["React, Firebase, Stripe, REST APIs"]
    )
    project_description: Optional[str] = Field(
        None,
        description="Additional description of the project (optional)",
        examples=["Built a website for an online store. Users can browse products, add to cart, and checkout."]
    )


class ProjectDescriptionResponse(BaseModel):
    """Response model for project description generation"""
    project_description: str = Field(
        ...,
        description="Generated professional project description for CV"
    )
