
import os
import logging
import google.generativeai as genai
from app.features.summaries.models import SummaryRequest
from app.shared.utils.text_utils import reduce_tokens
from dotenv import load_dotenv

load_dotenv()

class SummaryGenerator:
    def __init__(self, model_name="gemini-2.5-flash-lite-preview-06-17"):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel(model_name)
        self.logger = logging.getLogger("resume_flow")

    def generate_summary(self, request: SummaryRequest) -> str:
        """
        Generate a professional summary for resume
        """
        prompt = f"""
**Task:**  
Create a concise and impactful resume summary for a CV that showcases professional expertise and achievements.

**Instructions:**  
- Begin with a strong action verb followed by professional identity  
- Emphasize years of experience  
- Highlight measurable achievements using action verbs (improved, reduced, increased, led, developed)  
- Showcase technical expertise and relevant strengths  
- End with a clear value proposition or impact statement  
- Use achievement-focused language (delivered, implemented, spearheaded, orchestrated)  
- Include quantifiable results  
- Be specific and impactful  
- Maintain a professional tone  
- Must include **at least one** measurable achievement  
- Keep the response between **50-75 words**  
- Do not include any explanations or bullet points  
- Don't spell out numbers (use numerals like "5+ years", "40% improvement")  
- Use strong, direct language throughout

**Example:**  
Spearheaded complex software solutions as a Senior Software Engineer with 5+ years of expertise in cloud architecture. 
Successfully led a team of 5 developers, delivering a system optimization that reduced latency by 40%. 
Demonstrated mastery of Python and AWS, consistently driving innovation in microservices architecture and scalable solutions.

**Candidate Information:**  
- Name and Title: {request.current_title}  
- Experience: {request.years_experience}  
- Key Skills: {request.skills}  
- Achievements: {request.achievements if request.achievements else "Not specified"}

**Now, write the summary following the above instructions.**
        """

        try:
            # Reduce tokens in the prompt
            prompt = reduce_tokens(prompt)
            # Generate content using the model
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            raise ValueError(f"Error generating summary: {str(e)}")
