from TexSoup import TexSoup
from TexSoup.data import TexCmd, BraceGroup, Token
import json
from models import CreateResumeRequest, CreateResumeResponse
# Example usage
payload = json.load(open('example_cv.json'))


class ResumeTexGenerator:
    
    def __init__(self, request: CreateResumeRequest, user_id: str):
        self.user_id = user_id
        self.payload = request
        self.name= payload["information"]['name']
        self.phone=payload["information"]["phone"]
        self.email=payload["information"]["email"]
        self.linkedin=payload["information"]["linkedin"]
        self.github=payload["information"]["github"]
        
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
        for edu_item in payload["education"]:
            new_edu = TexCmd('resumeEduSubheading', [
            BraceGroup(f'{edu_item["school"]}'),
            BraceGroup(f'{str(edu_item["start_date"]) + " - " + str(edu_item["end_date"])}'),
            BraceGroup(f'{edu_item["degree"]}'),
            BraceGroup(f'{edu_item["location"]}')
            ])
            edu.args.append(new_edu)
        
    def fill_summary(self, soup: TexSoup):
        summary = soup.find_all('summaryPlaceholder')[1]
        sum_body = payload["information"]["summary"]
        summary.args[0].string = sum_body

    def fill_experience(soup: TexSoup):
        experience = soup.find_all('expPlaceholder')[1]
        experience.args.clear()
        for exp_item in payload["experience"]:
            new_exp = TexCmd('resumeSubheading', [
                BraceGroup(exp_item['title']),
                BraceGroup(str(exp_item['start_date']) + " - " + str(exp_item['end_date'])),
                BraceGroup(exp_item['company']),
                BraceGroup(exp_item['location'])
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
        for proj_item in payload["projects"]:
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
        skills_content = [
            TexCmd('textbf', [BraceGroup('Languages')]),
            BraceGroup(': ' + ', '.join(payload['technical_skills']['languages'])),
            BraceGroup(' \\\\'),
            TexCmd('textbf', [BraceGroup('Developer Tools')]),
            BraceGroup(': ' + ', '.join(payload['technical_skills']['developer_tools'])),
            BraceGroup(' \\\\'),
            TexCmd('textbf', [BraceGroup('Technologies/Frameworks')]),
            BraceGroup(': ' + ', '.join(payload['technical_skills']['frameworks'])),
            BraceGroup(' \\\\')
        ]
        tech_skills.args.extend(skills_content)

    def fill_soft_skills(self, soup: TexSoup):
        soft_skills = soup.find_all('softSkillsPlaceholder')[1]
        soft_skills.args.clear()
        soft_skills_content = TexCmd('emph', '{'+', '.join(payload['soft_skills']) + '}')
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
                cleaned_output = (cleaned_output).replace(r'{{}\Huge', r'{\Huge')
                cleaned_output = (cleaned_output).replace(r'Doe}{}}', r'Doe}}')
                cleaned_output = (cleaned_output).replace(r'{ \\ }\vspace', r' \\ \vspace')
                f.write(cleaned_output)
            
            # Return response with tex content
            with open(f'generated_resumes/{self.user_id}.tex', 'r') as f:
                tex_content = f.read()
            return CreateResumeResponse(tex_file=tex_content)