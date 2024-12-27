import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class CoverLetterGenerator:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def generate_cover_letter(self, request):
        """
        Generate a cover letter using Gemini AI
        """
        cover_letter_prompt = f"""
Craft a professional cover letter for a .NET developer position, focusing solely on the essential content. Eliminate any placeholder or template-style headers like addresses or contact information. 

Job Posting Context:
{request.job_post}

Candidate Professional Profile:
- Name: {request.user_name}
- Professional Title: {request.user_title}
- Degree: {request.user_degree}
- Professional Experience: {request.user_experience}
- Key Skills: {request.user_skills}

Writing Guidelines:
1. Begin directly with "Dear Hiring Manager,"

2. First Paragraph:
   - Immediately state the position you're applying for without mentioning platform that has the post
   - Briefly introduce professional background
   - Create an immediate connection to the job requirements

3. Second Paragraph (Experience & Skills):
   - Directly address key technical requirements
   - Provide specific examples of relevant achievements
   - Quantify impacts where possible
   - Highlight most relevant technical skills

4. Third Paragraph (Value Proposition):
   - Explain why you're an ideal candidate
   - Demonstrate understanding of the company's technical needs
   - Express enthusiasm for potential contribution

5. Closing Paragraph:
   - Thank the reader for their consideration
   - Express interest in further discussion
   - Create a subtle call to action

Specific Requirements:
- Total length: 250-300 words
- Use a professional, confident tone
- Focus on technical achievements
- Avoid generic statements
- Sign off with "Sincerely, John Doe"

Emphasize:
- Specific technologies re;ated to the job
- Practical experience
- Measurable impacts
- Alignment with job requirements

Generate a concise, impactful cover letter that goes straight to the professional content.
"""

        try:
            response = self.model.generate_content(cover_letter_prompt)
            
            return {
                "cover_letter": response.text,
                "tokens_used": None  # Add token tracking if possible
            }
        except Exception as e:
            raise ValueError(f"Cover letter generation failed: {str(e)}")