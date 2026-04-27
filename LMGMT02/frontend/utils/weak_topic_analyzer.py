"""
Weak Topic Analyzer
Identifies topics where user needs more practice based on quiz performance
"""
from datetime import datetime, timedelta


class WeakTopicAnalyzer:
    """Analyze quiz performance to identify weak topics"""
    
    def __init__(self):
        self.WEAK_THRESHOLD = 70  # Below 70% is considered weak
        self.NEEDS_PRACTICE_THRESHOLD = 80  # Below 80% needs practice
    
    def analyze_weak_topics(self, user_id, learning_db):
        """
        Analyze quiz scores to identify weak topics
        
        Returns:
            dict: {
                'weak_topics': list of topics scoring < 70%,
                'needs_practice': list of topics scoring 70-80%,
                'strong_topics': list of topics scoring > 80%,
                'recommendations': list of actionable recommendations
            }
        """
        try:
            # Get all quiz scores
            quiz_scores = learning_db.get_all_quiz_scores(user_id)
            
            if not quiz_scores:
                return {
                    'weak_topics': [],
                    'needs_practice': [],
                    'strong_topics': [],
                    'recommendations': []
                }
            
            # Categorize topics by performance
            weak_topics = []
            needs_practice = []
            strong_topics = []
            
            # Group by topic and calculate average score
            topic_scores = {}
            for score in quiz_scores:
                topic = score['topic']
                percentage = (score['score'] / score['max_score'] * 100) if score['max_score'] > 0 else 0
                
                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(percentage)
            
            # Calculate averages and categorize
            for topic, scores in topic_scores.items():
                avg_score = sum(scores) / len(scores)
                attempts = len(scores)
                
                topic_data = {
                    'topic': topic,
                    'avg_score': round(avg_score, 1),
                    'attempts': attempts,
                    'latest_score': scores[-1]
                }
                
                if avg_score < self.WEAK_THRESHOLD:
                    weak_topics.append(topic_data)
                elif avg_score < self.NEEDS_PRACTICE_THRESHOLD:
                    needs_practice.append(topic_data)
                else:
                    strong_topics.append(topic_data)
            
            # Sort by score (lowest first for weak topics)
            weak_topics.sort(key=lambda x: x['avg_score'])
            needs_practice.sort(key=lambda x: x['avg_score'])
            strong_topics.sort(key=lambda x: x['avg_score'], reverse=True)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(weak_topics, needs_practice)
            
            return {
                'weak_topics': weak_topics,
                'needs_practice': needs_practice,
                'strong_topics': strong_topics,
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"Error analyzing weak topics: {e}")
            return {
                'weak_topics': [],
                'needs_practice': [],
                'strong_topics': [],
                'recommendations': []
            }
    
    def _generate_recommendations(self, weak_topics, needs_practice):
        """Generate actionable recommendations"""
        recommendations = []
        
        if weak_topics:
            for topic_data in weak_topics[:3]:  # Top 3 weak topics
                recommendations.append({
                    'type': 'urgent',
                    'topic': topic_data['topic'],
                    'message': f"Review {topic_data['topic']} - Current score: {topic_data['avg_score']:.0f}%",
                    'action': 'Retake lesson and quiz',
                    'priority': 'high'
                })
        
        if needs_practice:
            for topic_data in needs_practice[:2]:  # Top 2 practice topics
                recommendations.append({
                    'type': 'practice',
                    'topic': topic_data['topic'],
                    'message': f"Practice {topic_data['topic']} - Current score: {topic_data['avg_score']:.0f}%",
                    'action': 'Take additional quizzes',
                    'priority': 'medium'
                })
        
        if not recommendations:
            recommendations.append({
                'type': 'success',
                'topic': None,
                'message': "Great job! All topics are performing well.",
                'action': 'Continue learning new topics',
                'priority': 'low'
            })
        
        return recommendations
    
    def get_improvement_suggestions(self, topic, current_score):
        """Get specific improvement suggestions for a topic"""
        suggestions = []
        
        if current_score < 50:
            suggestions.append("📚 Review the lesson content thoroughly")
            suggestions.append("🎧 Listen to the audio version for better retention")
            suggestions.append("💬 Ask the AI tutor for clarification")
            suggestions.append("🎴 Use flashcards to memorize key concepts")
        elif current_score < 70:
            suggestions.append("📝 Take detailed study notes")
            suggestions.append("💻 Practice with code examples")
            suggestions.append("🗺️ Follow the learning roadmap step by step")
            suggestions.append("🔄 Retake the quiz after reviewing")
        else:
            suggestions.append("🎯 Take more challenging quizzes")
            suggestions.append("🚀 Move to advanced topics")
            suggestions.append("💡 Apply concepts in real projects")
        
        return suggestions
    
    def calculate_improvement_rate(self, user_id, topic, learning_db):
        """Calculate improvement rate for a specific topic"""
        try:
            quiz_scores = learning_db.get_topic_quiz_history(user_id, topic)
            
            if len(quiz_scores) < 2:
                return None
            
            # Compare first and last scores
            first_score = (quiz_scores[0]['score'] / quiz_scores[0]['max_score'] * 100)
            last_score = (quiz_scores[-1]['score'] / quiz_scores[-1]['max_score'] * 100)
            
            improvement = last_score - first_score
            
            return {
                'first_score': round(first_score, 1),
                'last_score': round(last_score, 1),
                'improvement': round(improvement, 1),
                'attempts': len(quiz_scores),
                'trend': 'improving' if improvement > 0 else 'declining' if improvement < 0 else 'stable'
            }
            
        except Exception as e:
            print(f"Error calculating improvement rate: {e}")
            return None
    
    def get_focus_areas(self, weak_topics, limit=5):
        """Get top focus areas for improvement"""
        if not weak_topics:
            return []
        
        focus_areas = []
        for topic_data in weak_topics[:limit]:
            focus_areas.append({
                'topic': topic_data['topic'],
                'score': topic_data['avg_score'],
                'urgency': 'High' if topic_data['avg_score'] < 50 else 'Medium',
                'estimated_time': '2-3 hours'
            })
        
        return focus_areas


def get_weak_topic_analyzer():
    """Get weak topic analyzer instance"""
    return WeakTopicAnalyzer()
