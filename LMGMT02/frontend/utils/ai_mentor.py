"""
AI Mentor Recommendation System
Analyzes user progress and recommends next topics to learn
"""
import streamlit as st
from groq import Groq
from datetime import datetime
import json


class AIMentor:
    """AI Mentor for personalized learning recommendations"""
    
    def __init__(self):
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except KeyError:
            self.client = None
    
    def get_recommendation(self, user_id, db, advanced_db):
        """
        Generate AI mentor recommendation based on user progress
        
        Args:
            user_id: User ID
            db: Learning database instance
            advanced_db: Advanced features database instance
        
        Returns:
            dict: Recommendation with topic, reason, difficulty, estimated_time
        """
        if not self.client:
            return None
        
        try:
            # Gather user data
            completed_topics = db.get_completed_topics_list(user_id)
            quiz_scores = db.get_recent_quiz_scores(user_id, limit=10)
            weak_topics = self._identify_weak_topics(quiz_scores)
            skill_level = self._calculate_skill_level(user_id, db)
            
            # Build context for AI
            context = self._build_context(completed_topics, quiz_scores, weak_topics, skill_level)
            
            # Generate recommendation using AI
            recommendation = self._generate_ai_recommendation(context)
            
            return recommendation
            
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return None
    
    def _identify_weak_topics(self, quiz_scores):
        """Identify topics where user scored below 70%"""
        weak_topics = []
        for score in quiz_scores:
            percentage = (score['score'] / score['max_score'] * 100) if score['max_score'] > 0 else 0
            if percentage < 70:
                weak_topics.append({
                    'topic': score['topic'],
                    'score': percentage
                })
        return weak_topics
    
    def _calculate_skill_level(self, user_id, db):
        """Calculate user's current skill level"""
        topics_count = db.get_completed_topics_count(user_id)
        avg_score = db.get_average_quiz_score(user_id)
        
        if topics_count < 5 or avg_score < 60:
            return "Beginner"
        elif topics_count < 15 or avg_score < 80:
            return "Intermediate"
        else:
            return "Advanced"
    
    def _build_context(self, completed_topics, quiz_scores, weak_topics, skill_level):
        """Build context string for AI"""
        context = f"User Skill Level: {skill_level}\n\n"
        
        if completed_topics:
            context += f"Completed Topics ({len(completed_topics)}):\n"
            for topic in completed_topics[-10:]:  # Last 10 topics
                context += f"- {topic}\n"
            context += "\n"
        
        if weak_topics:
            context += "Weak Areas (needs improvement):\n"
            for weak in weak_topics[:5]:  # Top 5 weak topics
                context += f"- {weak['topic']} (Score: {weak['score']:.0f}%)\n"
            context += "\n"
        
        if quiz_scores:
            recent_topics = [q['topic'] for q in quiz_scores[-5:]]
            context += f"Recent Learning: {', '.join(recent_topics)}\n"
        
        return context
    
    def _generate_ai_recommendation(self, context):
        """Generate recommendation using Groq AI"""
        prompt = f"""You are an AI learning mentor. Based on the user's learning history, recommend the NEXT BEST topic they should learn.

{context}

Provide a recommendation in this EXACT JSON format:
{{
  "topic": "Specific topic name",
  "reason": "Clear explanation why this topic is recommended (2-3 sentences)",
  "difficulty": "Beginner/Intermediate/Advanced",
  "estimated_time": "2-3 hours"
}}

Consider:
- Natural learning progression
- Fill knowledge gaps
- Build on completed topics
- Address weak areas
- Match skill level

Return ONLY the JSON, no markdown."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert AI learning mentor. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean markdown if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            recommendation = json.loads(content)
            return recommendation
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return None
    
    def get_fallback_recommendation(self, skill_level="Intermediate"):
        """Provide fallback recommendation if AI fails"""
        recommendations = {
            "Beginner": {
                "topic": "Introduction to Machine Learning",
                "reason": "Start with ML fundamentals to build a strong foundation. This topic covers essential concepts that will help you understand more advanced topics later.",
                "difficulty": "Beginner",
                "estimated_time": "2-3 hours"
            },
            "Intermediate": {
                "topic": "Neural Networks Fundamentals",
                "reason": "Deepen your understanding of neural networks, a core concept in modern AI. This will prepare you for advanced deep learning topics.",
                "difficulty": "Intermediate",
                "estimated_time": "3-4 hours"
            },
            "Advanced": {
                "topic": "Transformer Architecture",
                "reason": "Explore cutting-edge transformer models that power modern NLP. This advanced topic will enhance your expertise in state-of-the-art AI.",
                "difficulty": "Advanced",
                "estimated_time": "4-5 hours"
            }
        }
        return recommendations.get(skill_level, recommendations["Intermediate"])


def get_ai_mentor():
    """Get AI Mentor instance"""
    return AIMentor()
