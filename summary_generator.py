# summary_generator.py
import google.generativeai as genai
from models import SummaryRequest

class SummaryGenerator:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def generate_summary(self, request: SummaryRequest) -> str:
        """
        Generate a professional summary for resume
        """
        prompt = f"""
        Create a concise and impactful resume summary for a CV that showcases professional expertise and value proposition.

        Use this information:
        - Name and Title: {request.current_title}
        - Experience: {request.years_experience}
        - Key Skills: {request.skills}
        - Achievements: {request.achievements if request.achievements else "Not specified"}

        Requirements:
        1. Length: 50-75 words
        2. Structure:
           - Open with professional identity and experience level
           - Highlight core technical expertise and skills
           - Showcase quantifiable achievements
           - End with value proposition
        3. Style:
           - Use confident, professional tone
           - Include action-oriented language
           - Be specific and measurable
           - Avoid clichés and generic statements

        Example Format:
        "Seasoned Software Engineer with 5+ years of expertise in cloud architecture and full-stack development. Demonstrated success in leading high-impact projects, including a system optimization initiative that reduced latency by 40%. Brings deep expertise in Python, AWS, and microservices architecture, with a proven track record of delivering scalable solutions."

        Generate a powerful summary that demonstrates expertise and potential value to employers.
        The response MUST be between 50-75 words and maintain a professional, achievement-focused tone.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise ValueError(f"Error generating summary: {str(e)}")