"""
AI service for content generation using Groq/OpenAI
"""
import os
import json
from typing import Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class AIService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Updated to current model
    
    def generate_content(self, topic: str, difficulty: str, depth: str) -> Dict[str, Any]:
        """Generate comprehensive learning content"""
        prompt = f"""
        You are an expert ML educator. Generate structured learning content for:
        
        Topic: {topic}
        Level: {difficulty}
        Depth: {depth}
        
        Provide a comprehensive explanation with:
        1. Introduction and overview
        2. Key concepts (bullet points)
        3. Real-world applications
        4. Common mistakes
        5. Summary
        6. Learning objectives
        
        Format as clean markdown.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=4096
        )
        
        return response.choices[0].message.content
    
    def generate_roadmap(self, topic: str, difficulty: str, depth: str) -> Dict[str, Any]:
        """Generate learning roadmap as JSON"""
        prompt = f"""
        Create a 4-6 week learning roadmap for: {topic}
        Level: {difficulty}, Depth: {depth}
        
        Return ONLY valid JSON with this structure:
        {{
          "weeks": [
            {{
              "id": "week1",
              "title": "Week title",
              "summary": "Brief overview",
              "concepts": ["concept1", "concept2"],
              "milestones": ["milestone1", "milestone2"]
            }}
          ]
        }}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2048
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"weeks": []}
    
    def generate_code(self, topic: str, difficulty: str, depth: str) -> str:
        """Generate working Python code example"""
        prompt = f"""
        Generate a working Python code example for: {topic}
        Level: {difficulty}, Depth: {depth}
        
        Requirements:
        - Include imports
        - Add meaningful comments
        - Make it runnable
        - Use modern Python
        
        Return ONLY the code, no markdown.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=2048
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_quiz(self, topic: str, difficulty: str, depth: str) -> Dict[str, Any]:
        """Generate quiz questions as JSON"""
        prompt = f"""
        Create 5-10 quiz questions for: {topic}
        Level: {difficulty}, Depth: {depth}
        
        Return ONLY valid JSON:
        {{
          "questions": [
            {{
              "id": "q1",
              "type": "mcq",
              "question": "Question text",
              "options": ["A", "B", "C", "D"],
              "answer": "Correct answer",
              "explanation": "Why this is correct",
              "difficulty": "easy"
            }}
          ]
        }}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3096
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"questions": []}
    
    def chat_tutor(self, question: str, context: str = "") -> str:
        """AI tutor for conversational Q&A"""
        prompt = f"""
        You are an expert AI tutor. Answer this question clearly and pedagogically:
        
        Context: {context}
        Question: {question}
        
        Provide a clear, educational response.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1024
        )
        
        return response.choices[0].message.content
