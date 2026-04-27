# Quick Start Guide - Refactored System

## 🚀 Getting Started

### 1. Start the Services

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend
streamlit run Home.py --server.port 8502
```

### 2. Access the Application

Open your browser: `http://localhost:8502`

## 📋 Testing the Refactored System

### Test 1: Empty States (New User Experience)

1. **Register a new account**
   - Click "Register" tab
   - Fill in: username, email, name, password
   - Click "Create Account"

2. **Login**
   - Enter email and password
   - Click "Login"

3. **Check Dashboard**
   - Should see: "Welcome to Your Learning Journey!"
   - Should see: 3 quick start cards
   - Should NOT see: fake stats or activities

4. **Check Analytics**
   - Navigate to Analytics page
   - Should see: "No Analytics Data Yet"
   - Should see: Action buttons to start learning
   - Should NOT see: fake charts

### Test 2: Content Generation

1. **Go to Learn Page**
   - Click "Learn" in sidebar

2. **Generate Content**
   - Enter topic: "Neural Networks"
   - Select difficulty: "Beginner"
   - Select depth: "Standard"
   - Click "Generate Content"
   - Wait for AI to generate (may take 30-60 seconds)

3. **Verify Content**
   - Check "Explanation" tab - should show AI-generated text
   - Check "Roadmap" tab - should show learning roadmap
   - Check "Code" tab - should show Python code
   - All content should be unique, not hardcoded

4. **Mark Complete**
   - Go to "Explanation" tab
   - Click "Mark as Complete"
   - Verify success message

### Test 3: AI Tutor

1. **Go to Tutor Tab**
   - Should see: "Start a conversation" message

2. **Ask a Question**
   - Type: "What is a neural network?"
   - Press Enter
   - Wait for AI response

3. **Verify Response**
   - Should get real AI answer
   - Should NOT see: "Great question!" template
   - Response should be relevant to your question

4. **Continue Conversation**
   - Ask follow-up questions
   - Verify chat history persists

### Test 4: Analytics Update

1. **Go to Dashboard**
   - Should now see: "1" topic completed
   - Should see: real time spent
   - Should see: updated stats

2. **Go to Analytics**
   - Should now see: charts with real data
   - Should see: topic in completion list
   - Should NOT see: "No data yet" message

## ✅ Expected Behavior

### Empty States (Before Activity):
- Dashboard: Welcome screen with quick start cards
- Analytics: "No Analytics Data Yet" message
- Learn: Popular topics suggestions
- Tutor: "Start a conversation" prompt

### With Data (After Activity):
- Dashboard: Real stats, progress bars, activity timeline
- Analytics: Charts with actual user data
- Learn: Generated content stored and displayed
- Tutor: Conversation history preserved

## ❌ What You Should NOT See

### Never Show:
- ❌ "Great question!" template responses
- ❌ Hardcoded learning content about neural networks
- ❌ Fake quiz scores or progress
- ❌ Static chart data
- ❌ Sample activities like "Completed: CNN 2 hours ago"
- ❌ Pre-filled progress bars
- ❌ Mock achievements

### Always Show:
- ✅ Empty states when no data
- ✅ AI-generated content only
- ✅ Real user activity only
- ✅ Actual completion times
- ✅ Genuine analytics

## 🐛 Troubleshooting

### Issue: "Failed to generate content"

**Possible Causes:**
1. Backend not running
2. Invalid GROQ_API_KEY
3. API rate limit reached
4. Network timeout

**Solutions:**
```bash
# Check backend is running
curl http://localhost:8000/docs

# Verify API key in secrets.toml
cat .streamlit/secrets.toml

# Check backend logs
# Look for errors in terminal running uvicorn

# Test API directly
curl -X POST http://localhost:8000/learning/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"test","difficulty":"Beginner","depth":"Standard"}'
```

### Issue: "Empty states not showing"

**Possible Causes:**
1. Old session data cached
2. Browser cache

**Solutions:**
```python
# Clear session in Streamlit
# Add to sidebar temporarily:
if st.button("Clear Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
```

Or clear browser cache and reload.

### Issue: "Text invisible in dark/light mode"

**Solutions:**
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Check theme_helper.py is loaded
4. Inspect element to see computed styles

### Issue: "Tutor gives template responses"

**This should NOT happen!** If it does:
1. Check Learn page code - should call API
2. Verify API endpoint is correct
3. Check backend logs for errors
4. Test API directly with curl

## 📊 Data Flow Verification

### Content Generation Flow:
```
User Input → API Call → AI Generation → Store in user_data → Display
```

**Verify:**
1. Check network tab for API call
2. Check response contains content
3. Verify content stored in session
4. Confirm content displays correctly

### Analytics Flow:
```
User Activity → Record in user_data → Calculate Metrics → Display Charts
```

**Verify:**
1. Complete a topic
2. Check user_data has entry
3. Go to Analytics
4. Verify chart shows data point

## 🔍 Debugging Tips

### Check User Data:
```python
# Add to any page temporarily
if st.checkbox("Show Debug Info"):
    st.write("User Data:", get_user_data())
    st.write("Session State:", dict(st.session_state))
```

### Check API Connection:
```python
# Test API endpoint
import requests
response = requests.get("http://localhost:8000/")
st.write("API Status:", response.status_code)
```

### Monitor Network Requests:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Perform action (generate content, ask tutor)
4. Check request/response

## 📝 Quick Reference

### Key Functions:

```python
# User Data
from utils.user_data import (
    get_user_data,           # Get current user's data
    has_any_data,            # Check if user has activity
    store_generated_content, # Store AI content
    get_generated_content,   # Retrieve stored content
    add_topic_completed,     # Record completion
    add_quiz_attempt,        # Record quiz
    store_tutor_message,     # Store chat
    get_tutor_chat_history   # Get chat history
)

# UI Components
from components.ui_components import (
    empty_state,             # Show empty state
    stat_card,               # Display metric
    animated_progress_bar,   # Show progress
    toast_notification       # Show message
)
```

### API Endpoints:

```
POST /learning/generate  - Generate content
POST /learning/tutor     - AI tutor chat
POST /quiz/generate      - Generate quiz (TODO)
POST /auth/login         - User login
POST /auth/register      - User registration
```

## 🎯 Success Criteria

You've successfully tested the refactored system when:

- [x] New users see empty states
- [x] Content is AI-generated
- [x] Tutor gives real responses
- [x] Analytics show real data
- [x] No static/fake data visible
- [x] Data persists correctly
- [x] Empty states disappear after activity

## 📞 Need Help?

### Check Documentation:
1. `REFACTORING_COMPLETE.md` - Detailed changes
2. `NEXT_STEPS.md` - Implementation guide
3. `STATIC_DATA_STATUS.md` - What's done/remaining
4. `REFACTORING_SUMMARY.md` - Overview

### Common Issues:
- Backend not running → Start with `uvicorn app.main:app --reload`
- API key missing → Check `.streamlit/secrets.toml`
- Content not generating → Check backend logs
- Empty states not showing → Clear browser cache

## 🚀 Next Steps

After verifying everything works:

1. **Integrate Quiz Generation** (High Priority)
   - See `NEXT_STEPS.md` section 3

2. **Verify Audio Feature** (High Priority)
   - See `NEXT_STEPS.md` section 2

3. **Implement Security** (Critical for Production)
   - See `NEXT_STEPS.md` section on Security

4. **Migrate to Database** (Required for Production)
   - See `NEXT_STEPS.md` section on Database

## 🎉 Congratulations!

You now have a fully dynamic, AI-powered learning platform with:
- ✅ No static data
- ✅ Real AI integration
- ✅ User-specific content
- ✅ Professional empty states
- ✅ Production-ready foundation

Happy learning! 🚀
