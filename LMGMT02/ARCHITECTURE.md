# 🏗️ LearnSphere Pro - System Architecture

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Desktop    │  │    Tablet    │  │    Mobile    │      │
│  │   Browser    │  │   Browser    │  │   Browser    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Streamlit Application                      │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│  │  │Dashboard │ │  Learn   │ │   Quiz   │ │Analytics │ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │         UI Components & Custom CSS               │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND LAYER                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                 FastAPI Application                     │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│  │  │   Auth   │ │ Learning │ │   Quiz   │ │Analytics │ │ │
│  │  │   API    │ │   API    │ │   API    │ │   API    │ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │              Business Logic Layer                 │ │ │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐ │ │ │
│  │  │  │ AI Service │  │Auth Service│  │   Others   │ │ │ │
│  │  │  └────────────┘  └────────────┘  └────────────┘ │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│     DATABASE LAYER       │  │    EXTERNAL SERVICES     │
│  ┌────────────────────┐  │  │  ┌────────────────────┐ │
│  │   PostgreSQL       │  │  │  │    Groq API        │ │
│  │   ┌──────────┐     │  │  │  │  (AI Generation)   │ │
│  │   │  Users   │     │  │  │  └────────────────────┘ │
│  │   │  Topics  │     │  │  │  ┌────────────────────┐ │
│  │   │  Quizzes │     │  │  │  │   OpenAI API       │ │
│  │   │ Progress │     │  │  │  │   (Optional)       │ │
│  │   └──────────┘     │  │  │  └────────────────────┘ │
│  └────────────────────┘  │  │  ┌────────────────────┐ │
│  ┌────────────────────┐  │  │  │   Redis Cache      │ │
│  │   Redis (Cache)    │  │  │  │   (Optional)       │ │
│  └────────────────────┘  │  │  └────────────────────┘ │
└──────────────────────────┘  └──────────────────────────┘
```

## 🔄 Request Flow

### 1. User Authentication Flow
```
User → Frontend → POST /auth/login → Backend
                                    ↓
                              Verify Password
                                    ↓
                              Generate JWT
                                    ↓
Frontend ← Return Token ← Backend
    ↓
Store Token
    ↓
Include in Headers
```

### 2. Content Generation Flow
```
User Input → Frontend → POST /learning/topics → Backend
                                               ↓
                                         AI Service
                                               ↓
                                         Groq API
                                               ↓
                                    Generate Content
                                               ↓
                                      Save to Database
                                               ↓
Frontend ← Return Content ← Backend
    ↓
Display to User
```

### 3. Quiz Taking Flow
```
User → Select Quiz → GET /quiz/{id} → Backend
                                     ↓
                              Fetch Questions
                                     ↓
Frontend ← Return Quiz ← Backend
    ↓
User Answers
    ↓
Submit → POST /quiz/submit → Backend
                            ↓
                       Score Quiz
                            ↓
                    Save Attempt
                            ↓
Frontend ← Return Results ← Backend
```

## 🗄️ Database Schema

### Users Table
```sql
users
├── id (PK)
├── email (UNIQUE)
├── username (UNIQUE)
├── hashed_password
├── full_name
├── avatar_url
├── total_time_spent
├── streak_count
├── last_active
├── theme
└── created_at
```

### Topics Table
```sql
topics
├── id (PK)
├── title
├── difficulty
├── depth
├── text_content
├── roadmap_json
├── code_example
├── audio_url
├── visual_prompt
├── created_at
└── updated_at
```

### Topic Progress Table
```sql
topic_progress
├── id (PK)
├── user_id (FK → users)
├── topic_id (FK → topics)
├── is_completed
├── completion_percentage
├── time_spent
├── last_accessed
└── milestones_completed
```

### Quizzes Table
```sql
quizzes
├── id (PK)
├── topic_id (FK → topics)
├── title
├── difficulty
├── time_limit
├── questions_json
└── created_at
```

### Quiz Attempts Table
```sql
quiz_attempts
├── id (PK)
├── user_id (FK → users)
├── quiz_id (FK → quizzes)
├── answers_json
├── score
├── max_score
├── percentage
├── time_taken
├── feedback_json
├── started_at
└── completed_at
```

### Bookmarks Table
```sql
bookmarks
├── id (PK)
├── user_id (FK → users)
├── topic_id (FK → topics)
└── created_at
```

### Notes Table
```sql
notes
├── id (PK)
├── user_id (FK → users)
├── topic_id (FK → topics)
├── content
├── created_at
└── updated_at
```

## 🔐 Security Architecture

### Authentication Flow
```
1. User Registration
   ↓
   Hash Password (bcrypt)
   ↓
   Store in Database
   ↓
   Return Success

2. User Login
   ↓
   Verify Password
   ↓
   Generate JWT Token
   ↓
   Return Token

3. Protected Requests
   ↓
   Include JWT in Header
   ↓
   Verify Token
   ↓
   Extract User Info
   ↓
   Process Request
```

### Security Layers
```
┌─────────────────────────────────┐
│   Input Validation (Pydantic)   │
├─────────────────────────────────┤
│   Authentication (JWT)          │
├─────────────────────────────────┤
│   Authorization (User Roles)    │
├─────────────────────────────────┤
│   SQL Injection (ORM)           │
├─────────────────────────────────┤
│   XSS Protection (Sanitization) │
├─────────────────────────────────┤
│   CORS Configuration            │
├─────────────────────────────────┤
│   Rate Limiting                 │
└─────────────────────────────────┘
```

## 📊 Data Flow Diagram

```
┌──────────┐
│   User   │
└────┬─────┘
     │
     ▼
┌──────────────────┐
│    Frontend      │
│  (Streamlit)     │
└────┬─────────────┘
     │
     │ HTTP/REST
     ▼
┌──────────────────┐
│   API Gateway    │
│   (FastAPI)      │
└────┬─────────────┘
     │
     ├─────────────────┐
     │                 │
     ▼                 ▼
┌──────────┐    ┌──────────┐
│ Database │    │ AI API   │
│(Postgres)│    │ (Groq)   │
└──────────┘    └──────────┘
```

## 🚀 Deployment Architecture

### Development
```
┌─────────────────────────────────┐
│      Local Machine              │
│  ┌──────────┐  ┌──────────┐    │
│  │ Frontend │  │ Backend  │    │
│  │  :8501   │  │  :8000   │    │
│  └──────────┘  └──────────┘    │
│  ┌──────────────────────────┐  │
│  │   SQLite Database        │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
```

### Production (Docker)
```
┌─────────────────────────────────────────┐
│           Docker Host                    │
│  ┌────────────┐  ┌────────────┐        │
│  │  Frontend  │  │  Backend   │        │
│  │ Container  │  │ Container  │        │
│  │   :8501    │  │   :8000    │        │
│  └────────────┘  └────────────┘        │
│  ┌────────────┐  ┌────────────┐        │
│  │ PostgreSQL │  │   Redis    │        │
│  │ Container  │  │ Container  │        │
│  └────────────┘  └────────────┘        │
│  ┌──────────────────────────────────┐  │
│  │      Docker Network              │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Production (Cloud)
```
┌─────────────────────────────────────────────┐
│              Load Balancer                   │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│  Frontend   │  │  Frontend   │
│  Instance 1 │  │  Instance 2 │
└─────────────┘  └─────────────┘
       │                │
       └───────┬────────┘
               │
               ▼
┌─────────────────────────────┐
│      API Gateway            │
└──────────────┬──────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│  Backend    │  │  Backend    │
│  Instance 1 │  │  Instance 2 │
└─────────────┘  └─────────────┘
       │                │
       └───────┬────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│  Database   │  │    Cache    │
│  (Primary)  │  │   (Redis)   │
└─────────────┘  └─────────────┘
       │
       ▼
┌─────────────┐
│  Database   │
│  (Replica)  │
└─────────────┘
```

## 🔄 Scalability Strategy

### Horizontal Scaling
```
1. Frontend: Multiple Streamlit instances
2. Backend: Multiple FastAPI instances
3. Database: Read replicas
4. Cache: Redis cluster
5. Load Balancer: Distribute traffic
```

### Vertical Scaling
```
1. Increase CPU/RAM per instance
2. Optimize database queries
3. Add indexes
4. Implement caching
5. Use CDN for static assets
```

## 📈 Performance Optimization

### Caching Strategy
```
┌─────────────────────────────────┐
│      Request Flow               │
└─────────────────────────────────┘
         │
         ▼
    Check Cache
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    │         ▼
    │    Query Database
    │         │
    │         ▼
    │    Store in Cache
    │         │
    └────┬────┘
         │
         ▼
    Return Data
```

### Database Optimization
```
1. Indexes on frequently queried columns
2. Connection pooling
3. Query optimization
4. Lazy loading
5. Pagination
6. Read replicas
```

## 🛡️ Disaster Recovery

### Backup Strategy
```
1. Database: Daily automated backups
2. User uploads: S3/Cloud storage
3. Configuration: Version control
4. Logs: Centralized logging
```

### Recovery Plan
```
1. Database restore from backup
2. Redeploy from Docker images
3. Restore configuration
4. Verify data integrity
5. Resume operations
```

---

This architecture is designed for:
- ✅ Scalability
- ✅ Reliability
- ✅ Security
- ✅ Performance
- ✅ Maintainability
