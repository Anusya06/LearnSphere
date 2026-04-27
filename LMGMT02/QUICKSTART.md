# ⚡ Quick Start Guide - LearnSphere Pro

Get up and running in 5 minutes!

## 🎯 Prerequisites

- Python 3.11 or higher
- Git
- (Optional) Docker & Docker Compose

## 🚀 Option 1: Quick Setup (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/learnsphere-pro.git
cd learnsphere-pro
```

### 2. Run Setup Script
```bash
# On Linux/Mac
chmod +x setup.sh
./setup.sh

# On Windows
python setup.py
```

### 3. Configure Environment
```bash
# Edit .env file with your API keys
nano .env  # or use your favorite editor
```

Add your Groq API key:
```env
GROQ_API_KEY=your-groq-api-key-here
SECRET_KEY=your-secret-key-here
```

**Get Groq API Key (Free):**
1. Visit https://console.groq.com
2. Sign up for free
3. Create an API key
4. Copy and paste into .env

### 4. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
source venv/bin/activate  # On Windows: venv\Scripts\activate
streamlit run Home.py
```

### 5. Access the Application
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 6. Login
Use demo credentials:
- Email: `demo@learnsphere.com`
- Password: `demo123`

## 🐳 Option 2: Docker (Even Easier!)

### 1. Clone and Configure
```bash
git clone https://github.com/yourusername/learnsphere-pro.git
cd learnsphere-pro
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start with Docker Compose
```bash
docker-compose up -d
```

### 3. Access
- Frontend: http://localhost:8501
- Backend: http://localhost:8000

That's it! 🎉

## 📱 First Steps

### 1. Explore the Dashboard
- View your learning statistics
- Check your progress
- See recent activity

### 2. Start Learning
1. Go to **📚 Learn** page
2. Enter a topic (e.g., "Neural Networks")
3. Select difficulty and depth
4. Click **Generate Content**
5. Explore AI-generated materials

### 3. Take a Quiz
1. Navigate to **📝 Quiz** page
2. Select a quiz
3. Answer questions
4. View detailed feedback

### 4. Check Analytics
1. Visit **📊 Analytics** page
2. View comprehensive insights
3. Track your progress

## 🎓 Example Topics to Try

- Convolutional Neural Networks
- Transformers and Attention Mechanisms
- Natural Language Processing
- Deep Reinforcement Learning
- Computer Vision Fundamentals
- Graph Neural Networks
- Generative Adversarial Networks
- Transfer Learning
- Neural Network Optimization
- Recurrent Neural Networks

## 🛠️ Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Reinstall dependencies
cd backend
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Check if port 8501 is in use
lsof -ti:8501 | xargs kill  # Mac/Linux

# Reinstall dependencies
cd frontend
pip install -r requirements.txt
```

### Database errors
```bash
# Reset database (development only)
rm backend/learnsphere.db
# Restart backend to recreate
```

### API Key errors
- Verify GROQ_API_KEY is set in .env
- Check for extra spaces or quotes
- Ensure API key is valid at https://console.groq.com

## 📚 Next Steps

1. **Read the full documentation**: [README.md](README.md)
2. **Explore all features**: [FEATURES.md](FEATURES.md)
3. **Deploy to production**: [DEPLOYMENT.md](DEPLOYMENT.md)
4. **Customize the platform**: Edit components and styles
5. **Add your own content**: Use the AI generation features

## 💡 Tips

- **Save your progress**: The system automatically tracks your learning
- **Use bookmarks**: Save topics you want to revisit
- **Take notes**: Use the built-in note-taking feature
- **Maintain streaks**: Learn daily to build habits
- **Explore analytics**: Identify your strengths and weaknesses

## 🆘 Need Help?

- **Documentation**: Check README.md and other docs
- **Issues**: Open an issue on GitHub
- **Community**: Join our Discord (link in README)
- **Email**: support@learnsphere.pro

## 🎉 You're Ready!

Start your AI-powered learning journey now! 🚀

---

**Pro Tip**: Try generating content for different difficulty levels to see how the AI adapts the explanations to your skill level.
