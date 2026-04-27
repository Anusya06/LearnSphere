# Advanced Features - Quick Start Guide

## Overview

This guide helps you implement the 15 advanced features step-by-step.

---

## ✅ Step 1: Database Setup (COMPLETE)

The database foundation is ready!

**File Created**: `frontend/utils/advanced_features_db.py`

**Test Database**:
```python
from frontend.utils.advanced_features_db import get_advanced_db

# Initialize database
db = get_advanced_db()
print("✅ Database initialized successfully!")
```

---

## Quick Implementation Guide

### Feature 1: Learning Streak (Easiest to Start)

**Where**: Dashboard.py

**Add to Dashboard**:
```python
from utils.advanced_features_db import get_advanced_db

# Get streak
db = get_advanced_db()
streak = db.get_streak(user_id)

# Display
st.markdown(f"""
    <div style="background:#f59e0b22;padding:20px;border-radius:12px;text-align:center">
        <h2 style="color:#f59e0b">🔥 {streak} Day Streak</h2>
        <p>Keep learning to maintain your streak!</p>
    </div>
""", unsafe_allow_html=True)
```

**Update Streak** (add to Learn.py when topic generated):
```python
db = get_advanced_db()
new_streak = db.update_streak(user_id)
```

---

### Feature 2: Bookmark Button (Simple Addition)

**Where**: Learn.py

**Add Button**:
```python
if st.button("⭐ Bookmark This Topic", use_container_width=True):
    db = get_advanced_db()
    if db.save_bookmark(user_id, current_topic, generated_content):
        st.success("✅ Topic bookmarked!")
```

**Display Bookmarks in Dashboard**:
```python
db = get_advanced_db()
bookmarks = db.get_bookmarks(user_id)

st.markdown("### ⭐ Saved Topics")
for bookmark in bookmarks:
    st.markdown(f"- {bookmark['topic']}")
```

---

### Feature 3: AI Flashcards

**Where**: Learn.py - New Tab

**Generate Flashcards**:
```python
def generate_flashcards(topic: str) -> list:
    prompt = f"""Generate 10 flashcards for the topic: {topic}
    
    Return ONLY a JSON array in this format:
    [
        {{"question": "What is X?", "answer": "X is..."}},
        {{"question": "Why Y?", "answer": "Because..."}}
    ]
    """
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a flashcard generator. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    content = response.choices[0].message.content.strip()
    # Clean markdown if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    
    return json.loads(content)
```

**Display Flashcards**:
```python
if 'flashcard_index' not in st.session_state:
    st.session_state.flashcard_index = 0
    st.session_state.show_answer = False

flashcards = st.session_state.get('flashcards', [])

if flashcards:
    current = flashcards[st.session_state.flashcard_index]
    
    # Flashcard display
    if not st.session_state.show_answer:
        st.markdown(f"""
            <div style="background:#667eea;padding:40px;border-radius:20px;text-align:center;min-height:200px">
                <h3 style="color:white">Question</h3>
                <p style="color:white;font-size:1.2em">{current['question']}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="background:#10b981;padding:40px;border-radius:20px;text-align:center;min-height:200px">
                <h3 style="color:white">Answer</h3>
                <p style="color:white;font-size:1.2em">{current['answer']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬅️ Previous"):
            st.session_state.flashcard_index = max(0, st.session_state.flashcard_index - 1)
            st.session_state.show_answer = False
            st.rerun()
    
    with col2:
        if st.button("🔄 Flip"):
            st.session_state.show_answer = not st.session_state.show_answer
            st.rerun()
    
    with col3:
        if st.button("➡️ Next"):
            st.session_state.flashcard_index = min(len(flashcards) - 1, st.session_state.flashcard_index + 1)
            st.session_state.show_answer = False
            st.rerun()
```

---

### Feature 4: Badge System

**Where**: Profile.py

**Check and Award Badges**:
```python
def check_and_award_badges(user_id: int):
    db = get_advanced_db()
    learning_db = get_learning_db()
    
    # Get statistics
    stats = learning_db.get_profile_statistics(user_id)
    streak = db.get_streak(user_id)
    
    # First Topic Badge
    if stats['topics_learned'] >= 1 and not db.has_badge(user_id, "First Topic"):
        db.award_badge(user_id, "First Topic", "Generated your first learning topic")
    
    # Quiz Master Badge
    if stats['average_score'] >= 80 and not db.has_badge(user_id, "Quiz Master"):
        db.award_badge(user_id, "Quiz Master", "Achieved 80%+ average quiz score")
    
    # Explorer Badge
    if stats['topics_learned'] >= 10 and not db.has_badge(user_id, "Explorer"):
        db.award_badge(user_id, "Explorer", "Learned 10 different topics")
    
    # Consistent Learner Badge
    if streak >= 7 and not db.has_badge(user_id, "Consistent Learner"):
        db.award_badge(user_id, "Consistent Learner", "Maintained a 7-day learning streak")
```

**Display Badges**:
```python
db = get_advanced_db()
badges = db.get_badges(user_id)

st.markdown("### 🏆 Your Badges")

badge_icons = {
    "First Topic": "🥇",
    "Quiz Master": "🎯",
    "Explorer": "🗺️",
    "Consistent Learner": "🔥"
}

cols = st.columns(4)
for i, badge in enumerate(badges):
    with cols[i % 4]:
        icon = badge_icons.get(badge['badge_name'], "🏅")
        st.markdown(f"""
            <div style="background:#667eea22;padding:20px;border-radius:12px;text-align:center">
                <div style="font-size:3em">{icon}</div>
                <h4>{badge['badge_name']}</h4>
                <p style="font-size:0.8em">{badge['badge_description']}</p>
            </div>
        """, unsafe_allow_html=True)
```

---

### Feature 5: AI Recommendations

**Where**: Dashboard.py

**Generate Recommendations**:
```python
def generate_recommendations(user_id: int):
    learning_db = get_learning_db()
    topics = learning_db.get_learning_topics(user_id, limit=10)
    
    if not topics:
        return []
    
    topics_list = [t['topic_name'] for t in topics]
    topics_str = ", ".join(topics_list)
    
    prompt = f"""Based on these learned topics: {topics_str}
    
    Recommend 5 next topics to learn. Consider difficulty progression.
    Return as JSON array:
    [
        {{"topic": "Topic Name", "reason": "Why learn this"}},
        ...
    ]
    """
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a learning advisor. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    content = response.choices[0].message.content.strip()
    # Clean and parse
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    
    recommendations = json.loads(content)
    
    # Save to database
    db = get_advanced_db()
    db.save_recommendations(user_id, recommendations)
    
    return recommendations
```

**Display Recommendations**:
```python
st.markdown("### 📚 Recommended for You")

db = get_advanced_db()
recommendations = db.get_recommendations(user_id)

if not recommendations:
    if st.button("🔄 Generate Recommendations"):
        recommendations = generate_recommendations(user_id)
        st.rerun()

for rec in recommendations:
    st.markdown(f"""
        <div style="background:#1e1e1e;padding:15px;border-radius:10px;margin:10px 0">
            <h4 style="color:#667eea">{rec['recommended_topic']}</h4>
            <p style="color:#b0b0b0">{rec.get('reason', '')}</p>
        </div>
    """, unsafe_allow_html=True)
```

---

## Implementation Order

### Week 1: Foundation
1. ✅ Database setup
2. Learning streak system
3. Bookmark feature
4. Badge system basics

### Week 2: AI Features
5. AI Flashcards
6. AI Recommendations
7. Study Notes Generator

### Week 3: Advanced
8. Mind Map Generator
9. Code Debugger
10. Coding Challenges

### Week 4: Analytics & Polish
11. Skill Growth Chart
12. Weekly Report
13. Study Timer
14. Learning Path
15. UI Polish

---

## Testing Each Feature

### Test Streak:
```python
db = get_advanced_db()
streak = db.update_streak(1)  # user_id = 1
print(f"Current streak: {streak}")
```

### Test Bookmarks:
```python
db = get_advanced_db()
db.save_bookmark(1, "Python Basics", "Content here")
bookmarks = db.get_bookmarks(1)
print(bookmarks)
```

### Test Badges:
```python
db = get_advanced_db()
db.award_badge(1, "First Topic", "Generated first topic")
badges = db.get_badges(1)
print(badges)
```

---

## Common Issues

### Issue: Database not found
**Solution**: Make sure `frontend_users.db` exists in the frontend directory

### Issue: JSON parsing error
**Solution**: Clean AI response before parsing:
```python
content = content.strip()
if content.startswith("```"):
    content = content.split("```")[1]
    if content.startswith("json"):
        content = content[4:]
    content = content.strip()
```

### Issue: Streak not updating
**Solution**: Call `update_streak()` after every learning activity

---

## Next Steps

1. Start with Learning Streak (easiest)
2. Add Bookmark button
3. Implement Badge system
4. Add AI Flashcards
5. Continue with other features

---

## Status

- ✅ Database: READY
- ✅ Code Examples: PROVIDED
- ⏳ Integration: YOUR TURN
- ⏳ Testing: AFTER INTEGRATION

**You now have everything needed to implement all 15 advanced features!** 🚀
