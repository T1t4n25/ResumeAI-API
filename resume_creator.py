from TexSoup import TexSoup
from TexSoup.data import TexCmd, BraceGroup, Token
import json
import logging
from models import CreateResumeRequest, CreateResumeResponse


class ResumeTexGenerator:
    
    def __init__(self, request, user_id: str):
        logger = logging.getLogger("uvicorn")
        self.user_id = user_id
        self.payload = request
        logger.info("payload inside:",self.payload)
        self.name= self.payload["information"]['name']
        self.phone=self.payload["information"]["phone"]
        self.email=self.payload["information"]["email"]
        self.linkedin=self.payload["information"]["linkedin"]
        self.github=self.payload["information"]["github"]
        
    def fill_info(self, soup:TexSoup):
        # Create complete personal info section in one go
        info = soup.find_all('infoPlaceholder')[1]
        personal_info = [
            r'{{}',TexCmd('Huge', [TexCmd('scshape', [BraceGroup(self.name)])]),r'{}}',
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
        with open('latex_templates/1.tex') as f:
            soup = TexSoup(f, tolerance=1)
            
            # Fill all data
            if len(self.payload["information"]) >= 6:
                self.fill_info(soup)
            
            if self.payload["information"].get("summary"):
                self.fill_summary(soup)
            
            if self.payload.get("experience"):
                self.fill_experience(soup)
            
            if self.payload.get("projects"):
                self.fill_projects(soup)
            
            if self.payload.get("technical_skills"):
                self.fill_tech_skills(soup)
            
            if self.payload.get("soft_skills"):
                self.fill_soft_skills(soup)
            
            # Save changes
            with open(f'generated_resumes/{self.user_id}.tex', 'w') as f:
                cleaned_output = str(soup).replace('section{}', 'section')
                # cleaned_output = (cleaned_output).replace(r'{{}\Huge', r'{\Huge')
                # cleaned_output = (cleaned_output).replace(r'Doe}{}}', r'Doe}}')
                # cleaned_output = (cleaned_output).replace(r'{ \\ }\vspace', r' \\ \vspace')
                f.write(cleaned_output)
                return cleaned_output
            