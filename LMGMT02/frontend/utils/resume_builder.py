"""
Resume Skill Builder
Converts learning progress into resume-ready skills
"""
from datetime import datetime
import re


class ResumeSkillBuilder:
    """Build resume skills from learning progress"""
    
    def __init__(self):
        self.skill_categories = {
            "Programming Languages": [
                "python", "javascript", "java", "c++", "cpp", "c#", "csharp",
                "go", "rust", "ruby", "php", "swift", "kotlin", "typescript"
            ],
            "Machine Learning & AI": [
                "machine learning", "deep learning", "neural network", "ai",
                "artificial intelligence", "nlp", "computer vision", "reinforcement learning",
                "supervised learning", "unsupervised learning", "transformer", "lstm", "rnn",
                "cnn", "gan", "bert", "gpt"
            ],
            "Data Science & Analytics": [
                "data analysis", "data science", "statistics", "pandas", "numpy",
                "data visualization", "matplotlib", "seaborn", "plotly", "tableau",
                "sql", "database", "big data", "data mining"
            ],
            "Web Development": [
                "react", "angular", "vue", "html", "css", "frontend", "backend",
                "node.js", "express", "django", "flask", "rest api", "graphql",
                "web development", "responsive design", "ui/ux"
            ],
            "Cloud & DevOps": [
                "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd",
                "devops", "cloud computing", "terraform", "jenkins"
            ],
            "Algorithms & Data Structures": [
                "algorithm", "data structure", "sorting", "searching", "tree",
                "graph", "dynamic programming", "recursion", "linked list",
                "hash table", "binary search", "complexity analysis"
            ],
            "Tools & Frameworks": [
                "git", "github", "tensorflow", "pytorch", "keras", "scikit-learn",
                "opencv", "spacy", "nltk", "jupyter", "vscode"
            ]
        }
    
    def generate_resume_skills(self, user_id, learning_db):
        """
        Generate resume-ready skills from completed topics
        
        Returns:
            dict: Categorized skills with proficiency levels
        """
        try:
            # Get completed topics
            completed_topics = learning_db.get_completed_topics_list(user_id)
            
            if not completed_topics:
                return {}
            
            # Categorize skills
            categorized_skills = {}
            
            for category, keywords in self.skill_categories.items():
                skills_in_category = set()
                
                for topic in completed_topics:
                    topic_lower = topic.lower()
                    
                    for keyword in keywords:
                        if keyword in topic_lower:
                            # Extract skill name
                            skill_name = self._extract_skill_name(topic, keyword)
                            skills_in_category.add(skill_name)
                
                if skills_in_category:
                    categorized_skills[category] = sorted(list(skills_in_category))
            
            return categorized_skills
            
        except Exception as e:
            print(f"Error generating resume skills: {e}")
            return {}
    
    def _extract_skill_name(self, topic, keyword):
        """Extract clean skill name from topic"""
        # Capitalize properly
        if keyword in ["python", "java", "javascript", "typescript", "go", "rust"]:
            return keyword.capitalize()
        elif keyword in ["c++", "cpp"]:
            return "C++"
        elif keyword in ["c#", "csharp"]:
            return "C#"
        elif keyword in ["nlp"]:
            return "Natural Language Processing"
        elif keyword in ["ai"]:
            return "Artificial Intelligence"
        elif keyword in ["ml", "machine learning"]:
            return "Machine Learning"
        elif keyword in ["ui/ux"]:
            return "UI/UX Design"
        elif keyword in ["rest api"]:
            return "REST API Development"
        else:
            # Title case for multi-word skills
            return keyword.title()
    
    def generate_skill_summary(self, categorized_skills):
        """Generate a text summary of skills"""
        if not categorized_skills:
            return "No skills to display yet. Complete more topics to build your skill profile!"
        
        summary = "## Professional Skills Summary\n\n"
        
        for category, skills in categorized_skills.items():
            summary += f"### {category}\n"
            summary += ", ".join(skills)
            summary += "\n\n"
        
        return summary
    
    def generate_skills_text_export(self, categorized_skills, user_name="Your Name"):
        """Generate downloadable text format"""
        if not categorized_skills:
            return "No skills available"
        
        text = f"PROFESSIONAL SKILLS - {user_name}\n"
        text += f"Generated: {datetime.now().strftime('%B %d, %Y')}\n"
        text += "=" * 60 + "\n\n"
        
        for category, skills in categorized_skills.items():
            text += f"{category.upper()}\n"
            text += "-" * 40 + "\n"
            for skill in skills:
                text += f"• {skill}\n"
            text += "\n"
        
        text += "\n" + "=" * 60 + "\n"
        text += "Skills acquired through LearnSphere Pro AI Learning Platform\n"
        
        return text
    
    def get_skill_count(self, categorized_skills):
        """Get total number of unique skills"""
        total = 0
        for skills in categorized_skills.values():
            total += len(skills)
        return total
    
    def get_top_skills(self, categorized_skills, limit=10):
        """Get top N skills across all categories"""
        all_skills = []
        for category, skills in categorized_skills.items():
            for skill in skills:
                all_skills.append((skill, category))
        
        return all_skills[:limit]


def get_resume_builder():
    """Get resume builder instance"""
    return ResumeSkillBuilder()
