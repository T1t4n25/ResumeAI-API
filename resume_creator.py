from TexSoup import TexSoup
from TexSoup.data import TexCmd, BraceGroup
import logging
import os
import subprocess
from pathlib import Path
from time import strftime

class ResumeTexGenerator:
    
    def __init__(self, request):
        logger = logging.getLogger("uvicorn")
        self.payload = request
        logger.info("payload inside:",self.payload)
        self.name= self.payload["information"]['name']
        self.phone=self.payload["information"]["phone"]
        self.email=self.payload["information"]["email"]
        self.linkedin=self.payload["information"]["linkedin"]
        self.github=self.payload["information"]["github"]
        self.user_id = self.payload["information"]["name"].replace(" ", '') + "-" + strftime("%Y%m%d-%H%M%S")
        
        self.tex_template = Path('latex_templates') / '1.tex'
        self.output_dir = Path('generated_resumes')
        self.filled_tex_file = Path(self.output_dir) / f"{self.user_id}.tex"
        self.compiled_pdf_file = Path(self.output_dir) / f"{self.user_id}.pdf"
        
        self.tex_filled = False # Flag to check if the tex file is filled
        with open(self.tex_template) as f:
            self.soup = TexSoup(f, tolerance=1)
        
    def fill_info(self, soup:TexSoup):
        """
        Fills the personal information section of the resume template.
        """
        # Create complete personal info section in one go
        info = soup.find_all('infoPlaceholder')[1]
        personal_info = [
            BraceGroup(TexCmd('Huge', [TexCmd('scshape', [BraceGroup(self.name)])])),
            BraceGroup(r' \\ '),
            TexCmd('vspace', [BraceGroup('1pt')]),
            TexCmd('small', [
                TexCmd('raisebox', [BraceGroup(r'-0.1\height'), 
                TexCmd('faPhone', [f'\\ {self.phone} ~ '])]),
                TexCmd('href', [BraceGroup(r'mailto:'+self.email)]),
                BraceGroup(r'\raisebox{-0.2\height}\faEnvelope\  \underline{'+self.email+r'}')
                ,
                ' ~ ',
                TexCmd('href', [BraceGroup(f'{self.linkedin}')]),
                BraceGroup(r'\raisebox{-0.2\height}\faLinkedin\  \underline{'+self.linkedin+r'}')
                ,
                ' ~ ',
                TexCmd('href', [BraceGroup(f'{{{self.github}}}')]),
                BraceGroup(r'\raisebox{-0.2\height}\faGithub\  \underline{'+self.github+'}')
            ]),
            TexCmd('vspace', [BraceGroup('-8pt')])
        ]
        
        info.args.clear()
        # for n in personal_info:
        #     info.args.append(n)
        info.args.extend(personal_info)
        # Create Education Section
        edu = soup.find_all('eduPlaceholder')[1]
        edu.args.clear()
        for edu_item in self.payload["education"]:
            new_edu = TexCmd('resumeEduSubheading', [
            BraceGroup(f'{edu_item["school"]}'),
            BraceGroup(f'{str(edu_item["start_date"]) + " - " + str(edu_item["end_date"])}'),
            BraceGroup(f'{edu_item["degree"]}'),
            BraceGroup('')
            ])
            edu.args.append(new_edu)
        
    def fill_summary(self, soup: TexSoup):
        """
        Fills the summary section of the resume template.
        """
        summary = soup.find_all('summaryPlaceholder')[1]
        sum_body = self.payload["information"]["summary"]
        summary.args[0].string = sum_body

    def fill_experience(self, soup: TexSoup):
        experience = soup.find_all('expPlaceholder')[1]
        experience.args.clear()
        for exp_item in self.payload["experience"]:
            new_exp = TexCmd('resumeSubheading', [
                BraceGroup(exp_item['title']),
                BraceGroup(str(exp_item['start_date']) + " - " + str(exp_item['end_date'])),
                BraceGroup(exp_item['company']),
                BraceGroup('')
            ])
            achievements = [TexCmd('resumeItem', [BraceGroup(achievement + '.')]) 
                            for achievement in exp_item['description'].split('. ')]
            full_exp_entry = [new_exp, TexCmd('resumeItemListStart')]
            achievements.append(TexCmd('resumeItemListEnd'))
            full_exp_entry.extend(achievements)
            experience.args.extend(full_exp_entry)

    def fill_projects(self, soup: TexSoup):
        """
        Fills the projects section of the resume template.
        """
        projects = soup.find_all('projectsPlaceholder')[1]
        projects.args.clear()
        for proj_item in self.payload["projects"]:
            new_proj = TexCmd('resumeProjectHeading', [
                BraceGroup(f'\\textbf{{{proj_item["name"]}}} $|$ \\emph{{{proj_item["skills"]}}}'),
                BraceGroup(str(proj_item["end_date"]))
            ])
            achievements = [TexCmd('resumeItem', [BraceGroup(achievement + '.')]) 
                            for achievement in proj_item['description'].split('. ') if achievement.strip()]
            full_proj_entry = [new_proj, TexCmd('resumeItemListStart')]
            achievements.append(TexCmd('resumeItemListEnd'))
            full_proj_entry.extend(achievements)
            projects.args.extend(full_proj_entry)

    def fill_tech_skills(self, soup: TexSoup):
        """
        Fills the technical skills section of the resume template.
        """
        tech_skills = soup.find_all('techSkillsPlaceholder')[1]
        tech_skills.args.clear()
        skills_content = []
        for key, value in self.payload["technical_skills"].items():
            skills_content.append(TexCmd('textbf', [BraceGroup(key)]))  
            skills_content.append(BraceGroup(': ' + ', '.join(value)))
            skills_content.append(BraceGroup(r' \\ '))
        
        tech_skills.args.extend(skills_content)

    def fill_soft_skills(self, soup: TexSoup):
        soft_skills = soup.find_all('softSkillsPlaceholder')[1]
        soft_skills.args.clear()
        soft_skills_content = TexCmd('emph', '{'+', '.join(self.payload['soft_skills']) + '}')
        soft_skills.args.append(soft_skills_content)

    def generate_tex(self):
        """
        This method fills in all sections of the resume template based on the provided payload.
        The generated LaTeX code is saved to soup and can be compiled to PDF later.
        
        """
        with open(self.tex_template) as f:
            self.soup = TexSoup(f, tolerance=1)
            
            # Fill all data
            if len(self.payload["information"]) >= 6:
                self.fill_info(self.soup)
            
            if self.payload["information"].get("summary"):
                self.fill_summary(self.soup)
            
            if self.payload.get("experience"):
                self.fill_experience(self.soup)
            
            if self.payload.get("projects"):
                self.fill_projects(self.soup)
            
            if self.payload.get("technical_skills"):
                self.fill_tech_skills(self.soup)
            
            if self.payload.get("soft_skills"):
                self.fill_soft_skills(self.soup)
                
            self.tex_filled = True
            return str(self.soup)
            
    def generate_pdf(self):
        # Save tex file for compilation
        if not self.tex_filled:
            self.generate_tex()
            
            
        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.filled_tex_file, 'w') as f:
            cleaned_output = str(self.soup).replace('section{}', 'section')
            f.write(cleaned_output)
        
        # Convert Path object to string for subprocess
        working_dir = str(self.output_dir.absolute())
        
        subprocess.run([
            'latexmk',
            '-pdf',
            '-f',
            f'-jobname={self.user_id}',
            f"{self.user_id}.tex"
        ], cwd=working_dir, check=True, capture_output=True, timeout=5)
        
        #print(f"PDF generated at: {self.compiled_pdf_file}")
        return self.compiled_pdf_file
    
    def cleanup(self):
        """
        Cleans up generated files after compilation.
        """
        # Cleaning up auxiliary files
        subprocess.run(['latexmk', '-C'], cwd=self.output_dir, check=True)
        os.remove(self.filled_tex_file)
        
def main():
    # Example usage
    request = {
    "information": {
        "address": "123 Example Street",
        "email": "example@gmail.com",
        "github": "github.com/example",
        "linkedin": "linkedin.com/in/example",
        "name": "John Doe",
        "phone": "01123456789",
        "summary": "Software engineer with 5 years experience"
    },
    "education": [
        {
        "degree": "BSc Computer Science",
        "end_date": "2020",
        "gpa": "3.5",
        "location": "Tanta, Egypt",
        "school": "Example University",
        "start_date": "2016"
        }
    ],
    "projects": [
        {
        "description": "Project description",
        "end_date": "2022",
        "name": "Project Name",
        "skills": "Python, FastAPI, Google Gemini AI, PyTest, Pydantic"
        }
    ],
    "experience": [
        {
        "company": "Example Company",
        "description": "Job description",
        "end_date": "Present",
        "start_date": "2020",
        "title": "Software Engineer"
        }
    ],
    "technical_skills": {
        "Other Skills": [
        "AWS",
        "Azure"
        ],
        "Programming Languages": [
        "Python",
        "Java"
        ],
        "Tools": [
        "Git",
        "Docker"
        ]
    },
    "soft_skills": [
        "Communication",
        "Problem Solving"
    ],
    "output_format": "pdf"
    }
    
    generator = ResumeTexGenerator(request)
    print("Generated LaTeX content!")
    print()
    pdf_file = generator.generate_pdf()
    print(f"PDF generated at: {pdf_file}")
    
    
if __name__ == "__main__":
    main()