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
        Create a concise and impactful resume summary for a CV that showcases professional expertise and achievements.

        Use this information:
        - Name and Title: {request.current_title}
        - Experience: {request.years_experience}
        - Key Skills: {request.skills}
        - Achievements: {request.achievements if request.achievements else "Not specified"}

        Requirements:
        1. Length: 50-75 words
        2. Structure:
           - Start with a strong action verb followed by professional identity
           - Emphasize years of experience
           - Highlight measurable achievements using action verbs (improved, reduced, increased, led, developed)
           - Showcase technical expertise
           - End with value proposition
        3. Style:
           - Use achievement-focused language (delivered, implemented, spearheaded, orchestrated)
           - Include quantifiable results
           - Be specific and impactful
           - Maintain professional tone
           - Must include at least one measurable achievement

        Example Format:
        "Spearheaded complex software solutions as a Senior Software Engineer with 5+ years of expertise in cloud architecture. Successfully led a team of 5 developers, delivering a system optimization that reduced latency by 40%. Demonstrated mastery of Python and AWS, consistently driving innovation in microservices architecture and scalable solutions."

        Generate a powerful summary that emphasizes achievements and expertise.
        IMPORTANT: 
        - Include at least one achievement with metrics
        - Use strong action verbs (developed, implemented, led, improved, reduced, increased)
        - Response MUST be between 50-75 words
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise ValueError(f"Error generating summary: {str(e)}")