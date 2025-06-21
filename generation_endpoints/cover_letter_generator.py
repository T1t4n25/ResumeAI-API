import os
import google.generativeai as genai
from dotenv import load_dotenv
from utility_func import reduce_tokens

load_dotenv()

class CoverLetterGenerator:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")

    def generate_cover_letter(self, request):
        """
        Generate a cover letter using Gemini AI
        """
        prompt = f"""
**Task:**  
Craft a professional cover letter using the provided job posting and candidate data. Focus solely on the essential content, eliminating any placeholder or template-style headers like addresses or contact information.

**Job Posting Context:**  
{request.job_post}

**Candidate Professional Profile:**  
- Name: {request.user_name}  
- Professional Title: {request.user_title}  
- Degree: {request.user_degree}  
- Professional Experience: {request.user_experience}  
- Key Skills: {request.user_skills}

**Writing Guidelines:**  
1. Begin directly with "Dear Hiring Manager,"

2. **First Paragraph:**  
   - Immediately state the position you're applying for without mentioning platform that has the post  
   - Briefly introduce professional background  
   - Create an immediate connection to the job requirements

3. **Second Paragraph (Experience & Skills):**  
   - Directly address key technical requirements  
   - Provide specific examples of relevant achievements  
   - Quantify impacts where possible  
   - Highlight most relevant technical skills

4. **Third Paragraph (Value Proposition):**  
   - Explain why you're an ideal candidate  
   - Demonstrate understanding of the company's technical needs  
   - Express enthusiasm for potential contribution

5. **Closing Paragraph:**  
   - Thank the reader for their consideration  
   - Express interest in further discussion  
   - Create a subtle call to action

**Specific Requirements:**  
- Total length: 250-300 words  
- Use a professional, confident tone  
- Focus on technical achievements  
- Avoid generic statements  
- Sign off with "Sincerely," followed by the provided name  
- Use numerals for all numbers (e.g., "5 years", "40% improvement") - never spell out numbers

**Emphasize:**  
- Specific technologies from the job posting  
- Practical experience  
- Measurable impacts (always in numeral form)  
- Alignment with job requirements

**Now, write the cover letter following the above instructions.**"""

        try:
            # Reduce tokens in the prompt
            prompt = reduce_tokens(prompt)
            # Generate content using the model
            response = self.model.generate_content(prompt)
            
            return {
                "cover_letter": response.text,
                "tokens_used": response.usage_metadata.total_token_count  # Add token tracking if possible
            }
        except Exception as e:
            raise ValueError(f"Cover letter generation failed: {str(e)}")