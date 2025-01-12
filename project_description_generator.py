# project_description_generator.py
import google.generativeai as genai
from models import ProjectDescriptionRequest

class ProjectDescriptionGenerator:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def generate_description(self, request: ProjectDescriptionRequest) -> str:
        """
        Generate a professional project description for CV
        """
        # Create base context from required fields
        context = f"""
        Project Name: {request.project_name}
        Technologies/Skills: {request.skills}
        """

        # Add description if provided
        if request.project_description:
            context += f"\nAdditional Context: {request.project_description}"

        prompt = f"""
        Create a professional, concise bullet point for a CV/resume based on:

        {context}

        Guidelines:
        - Start with a strong action verb
        - Emphasize the technologies and skills provided
        - Keep it between 30-50 words
        - Make it impactful and professional
        - Format as a single bullet point
        - Focus on technical implementation
        - Highlight the complexity and scope
        - If additional context is provided, incorporate relevant details

        Example Format:
        "Developed a full-stack e-commerce platform utilizing React and Firebase, implementing secure payment processing with Stripe and achieving seamless user experience through responsive design."

        Generate a similar style bullet point emphasizing the provided skills and technologies.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise ValueError(f"Error generating project description: {str(e)}")