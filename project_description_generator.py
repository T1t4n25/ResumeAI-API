# project_description_generator.py
import google.generativeai as genai
from models import ProjectDescriptionRequest

class ProjectDescriptionGenerator:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def generate_description(self, request: ProjectDescriptionRequest) -> str:
        """
        Generate a professional project description for a CV/resume.
        """
        # Create base context from required fields
        context = f"""
        Project Name: {request.project_name}
        Technologies and Skills Used: {request.skills}
        """

        # Add additional context if provided
        if request.project_description:
            context += f"\nAdditional Details: {request.project_description}"

        prompt = f"""
        **Task:**
        Create a professional and impactful sentence for a CV/resume based on the following information.

        **Project Details:**
        {context}

        **Instructions:**
        - Begin with a strong action verb.
        - Emphasize the technologies and skills listed.
        - **Include specific metrics or quantifiable results when possible** (e.g., percentages, numbers, time saved).
        - Keep the sentence concise (around 30-50 words).
        - Focus on your contributions and achievements.
        - Highlight the project's complexity and scope.
        - Incorporate relevant details from the additional context if provided.
        - Do not start the sentence with bullet points, numbers, or symbols.

        **Example:**
        Developed a full-stack e-commerce platform using React and Firebase, integrated secure payment processing with Stripe, **increasing user transaction rates by 25%** and **improving page load times by 40%**.

        **Now, write the sentence following the above instructions.**
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise ValueError(f"Error generating project description: {str(e)}")