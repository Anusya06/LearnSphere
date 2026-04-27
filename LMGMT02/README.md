# 🎓 LearnSphere Pro - AI-Powered Learning Management System

A next-generation, production-ready Learning Management System powered by AI, featuring modern UI/UX, comprehensive analytics, and intelligent learning tools.

## ✨ Features

### 🎨 Modern UI/UX
- **Glassmorphism & Gradient Design** - Beautiful, modern interface
- **Responsive Layout** - Works seamlessly on desktop, tablet, and mobile
- **Dark/Light Mode** - Customizable theme preferences
- **Smooth Animations** - Polished transitions and interactions
- **Professional Components** - Reusable, production-ready UI elements

### 🤖 AI-Powered Learning
- **AI Content Generation** - Personalized learning materials using Groq/OpenAI
- **Adaptive Quizzes** - Smart assessments that adjust to your skill level
- **AI Tutor Chat** - Real-time conversational assistance
- **Code Generation** - Working code examples for every topic
- **Audio Narration** - Text-to-speech for accessibility

### 📊 Advanced Analytics
- **Progress Tracking** - Detailed learning progress visualization
- **Performance Insights** - Identify strengths and areas for improvement
- **Study Time Analytics** - Track time spent on each topic
- **Quiz Performance Trends** - Monitor improvement over time
- **Weekly Heatmaps** - Visual representation of learning activity

### 🎯 Learning Tools
- **Interactive Roadmaps** - Week-by-week learning paths
- **Code Editor** - In-browser code execution
- **Flashcards** - Auto-generated study cards
- **Bookmarks** - Save favorite topics
- **Notes** - Markdown-supported note-taking

### 🏆 Gamification
- **Achievement Badges** - Unlock rewards for milestones
- **Learning Streaks** - Maintain daily learning habits
- **Leaderboards** - Compete with other learners
- **Progress Levels** - Level up as you learn

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── api/           # API endpoints
│   │   ├── auth.py    # Authentication
│   │   ├── learning.py # Learning content
│   │   ├── quiz.py    # Quiz management
│   │   └── analytics.py # Analytics
│   ├── models/        # Database models
│   │   ├── user.py
│   │   ├── topic.py
│   │   └── quiz.py
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   │   ├── ai_service.py
│   │   └── auth_service.py
│   ├── database/      # Database config
│   └── main.py        # FastAPI app
└── requirements.txt
```

### Frontend (Streamlit)
```
frontend/
├── pages/             # Multi-page app
│   ├── 1_🏠_Dashboard.py
│   ├── 2_📚_Learn.py
│   ├── 3_📝_Quiz.py
│   ├── 4_📊_Analytics.py
│   └── 5_👤_Profile.py
├── components/        # Reusable components
│   ├── ui_components.py
│   ├── auth_components.py
│   └── charts.py
├── styles/
│   └── custom.css     # Modern styling
├── utils/
└── Home.py            # Entry point
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (or SQLite for development)
- Docker & Docker Compose (optional)

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/learnsphere-pro.git
cd learnsphere-pro
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

1. **Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env
# Edit .env with your configuration

# Run migrations (if using Alembic)
alembic upgrade head

# Start the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Frontend Setup**
```bash
cd frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the frontend
streamlit run Home.py
```

## 🔑 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/learnsphere

# Security
SECRET_KEY=your-secret-key-here

# AI Service
GROQ_API_KEY=your-groq-api-key

# Optional
OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://localhost:6379
```

### Get API Keys

1. **Groq API Key** (Free)
   - Visit: https://console.groq.com
   - Sign up and get your API key
   - Fast, free inference for LLMs

2. **OpenAI API Key** (Optional)
   - Visit: https://platform.openai.com
   - Alternative to Groq

## 📚 Usage

### Demo Credentials
- Email: `demo@learnsphere.com`
- Password: `demo123`

### Creating Content

1. Navigate to **📚 Learn** page
2. Enter a topic (e.g., "Neural Networks")
3. Select difficulty and depth
4. Click **Generate Content**
5. Explore AI-generated materials

### Taking Quizzes

1. Go to **📝 Quiz** page
2. Select a quiz
3. Answer questions
4. Submit and view detailed feedback

### Viewing Analytics

1. Visit **📊 Analytics** page
2. View comprehensive learning insights
3. Track progress over time
4. Identify areas for improvement

## 🛠️ Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
pytest
```

### Database Migrations
```bash
cd backend

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Quality
```bash
# Format code
black .

# Lint
flake8 .
pylint app/

# Type checking
mypy app/
```

## 🚢 Deployment

### Deploy to Render

1. **Backend**
   - Create new Web Service
   - Connect GitHub repo
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Frontend**
   - Create new Web Service
   - Build command: `pip install -r frontend/requirements.txt`
   - Start command: `streamlit run frontend/Home.py --server.port $PORT`

3. **Database**
   - Create PostgreSQL database
   - Copy connection string to `DATABASE_URL`

### Deploy to AWS

See `docs/AWS_DEPLOYMENT.md` for detailed instructions.

### Deploy to GCP

See `docs/GCP_DEPLOYMENT.md` for detailed instructions.

## 📖 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user

#### Learning
- `POST /learning/topics` - Create topic with AI content
- `GET /learning/topics` - List all topics
- `POST /learning/progress` - Update progress
- `POST /learning/chat` - Chat with AI tutor

#### Quiz
- `POST /quiz/generate/{topic_id}` - Generate quiz
- `POST /quiz/submit` - Submit quiz attempt
- `GET /quiz/attempts/{user_id}` - Get quiz history

#### Analytics
- `GET /analytics/dashboard/{user_id}` - Get analytics
- `GET /analytics/quiz-history/{user_id}` - Quiz performance

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** - Fast AI inference
- **Streamlit** - Beautiful web apps
- **FastAPI** - Modern Python web framework
- **Plotly** - Interactive visualizations

## 📧 Contact

- Website: https://learnsphere.pro
- Email: support@learnsphere.pro
- Twitter: @LearnSpherePro

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Video content generation
- [ ] Live coding challenges
- [ ] Peer-to-peer learning
- [ ] Integration with Notion/Obsidian
- [ ] Multi-language support
- [ ] Offline mode
- [ ] AR/VR learning experiences

---

Made with ❤️ by the LearnSphere Team
