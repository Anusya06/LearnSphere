# 📡 LearnSphere Pro - API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://api.learnsphere.pro
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## 🔐 Authentication Endpoints

### Register User
Create a new user account.

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=johndoe",
  "total_time_spent": 0.0,
  "streak_count": 0,
  "theme": "light",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `400`: Email or username already exists
- `422`: Validation error

---

### Login
Authenticate and receive JWT token.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401`: Invalid credentials

---

### Get Current User
Get authenticated user's profile.

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `token` (required): JWT token

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=johndoe",
  "total_time_spent": 45.5,
  "streak_count": 15,
  "theme": "light",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `401`: Invalid or expired token
- `404`: User not found

---

## 📚 Learning Endpoints

### Create Topic with AI Content
Generate a new learning topic with AI-generated content.

**Endpoint:** `POST /learning/topics`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "Convolutional Neural Networks",
  "difficulty": "Intermediate",
  "depth": "Standard"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Convolutional Neural Networks",
  "difficulty": "Intermediate",
  "depth": "Standard",
  "text_content": "# Convolutional Neural Networks\n\n...",
  "roadmap_json": {
    "weeks": [...]
  },
  "code_example": "import numpy as np\n...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `401`: Unauthorized
- `422`: Validation error
- `500`: AI generation failed

---

### Get All Topics
Retrieve list of all topics.

**Endpoint:** `GET /learning/topics`

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 20)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Convolutional Neural Networks",
    "difficulty": "Intermediate",
    "depth": "Standard",
    "text_content": "...",
    "roadmap_json": {...},
    "code_example": "...",
    "created_at": "2024-01-15T10:30:00Z"
  },
  ...
]
```

---

### Get Topic by ID
Retrieve a specific topic.

**Endpoint:** `GET /learning/topics/{topic_id}`

**Path Parameters:**
- `topic_id` (required): Topic ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Convolutional Neural Networks",
  "difficulty": "Intermediate",
  "depth": "Standard",
  "text_content": "...",
  "roadmap_json": {...},
  "code_example": "...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `404`: Topic not found

---

### Update Progress
Update user's learning progress for a topic.

**Endpoint:** `POST /learning/progress`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `user_id` (required): User ID

**Request Body:**
```json
{
  "topic_id": 1,
  "completion_percentage": 75.0,
  "time_spent": 30.0,
  "is_completed": false,
  "milestones_completed": ["week1", "week2"]
}
```

**Response:** `200 OK`
```json
{
  "message": "Progress updated successfully"
}
```

**Errors:**
- `401`: Unauthorized
- `404`: Topic not found

---

### Add Bookmark
Bookmark a topic.

**Endpoint:** `POST /learning/bookmarks/{topic_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `topic_id` (required): Topic ID

**Query Parameters:**
- `user_id` (required): User ID

**Response:** `200 OK`
```json
{
  "message": "Bookmark added"
}
```

---

### Remove Bookmark
Remove a bookmark.

**Endpoint:** `DELETE /learning/bookmarks/{topic_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `topic_id` (required): Topic ID

**Query Parameters:**
- `user_id` (required): User ID

**Response:** `200 OK`
```json
{
  "message": "Bookmark removed"
}
```

---

### Chat with AI Tutor
Ask questions to the AI tutor.

**Endpoint:** `POST /learning/chat`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "question": "What is backpropagation?",
  "context": "Neural Networks"
}
```

**Response:** `200 OK`
```json
{
  "response": "Backpropagation is an algorithm used to train neural networks..."
}
```

---

## 📝 Quiz Endpoints

### Create Quiz
Create a new quiz manually.

**Endpoint:** `POST /quiz/create`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "topic_id": 1,
  "title": "CNN Quiz",
  "difficulty": "Intermediate",
  "time_limit": 600,
  "questions_json": {
    "questions": [...]
  }
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "topic_id": 1,
  "title": "CNN Quiz",
  "difficulty": "Intermediate",
  "time_limit": 600,
  "questions_json": {...},
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Generate Quiz with AI
Generate a quiz using AI.

**Endpoint:** `POST /quiz/generate/{topic_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `topic_id` (required): Topic ID

**Query Parameters:**
- `difficulty` (required): Quiz difficulty

**Response:** `200 OK`
```json
{
  "id": 1,
  "topic_id": 1,
  "title": "Convolutional Neural Networks Quiz",
  "difficulty": "Intermediate",
  "time_limit": 600,
  "questions_json": {
    "questions": [
      {
        "id": "q1",
        "type": "mcq",
        "question": "What is a convolution operation?",
        "options": ["A", "B", "C", "D"],
        "answer": "A",
        "explanation": "...",
        "difficulty": "medium"
      }
    ]
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `404`: Topic not found
- `500`: AI generation failed

---

### Get Quiz
Retrieve a specific quiz.

**Endpoint:** `GET /quiz/quiz/{quiz_id}`

**Path Parameters:**
- `quiz_id` (required): Quiz ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "topic_id": 1,
  "title": "CNN Quiz",
  "difficulty": "Intermediate",
  "time_limit": 600,
  "questions_json": {...},
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `404`: Quiz not found

---

### Submit Quiz
Submit quiz answers and get results.

**Endpoint:** `POST /quiz/submit`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `user_id` (required): User ID

**Request Body:**
```json
{
  "quiz_id": 1,
  "answers_json": {
    "q1": "A",
    "q2": "True",
    "q3": "Answer text"
  },
  "time_taken": 450
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "score": 8.5,
  "max_score": 10.0,
  "percentage": 85.0,
  "time_taken": 450,
  "feedback_json": {
    "feedback": [
      {
        "id": "q1",
        "question": "...",
        "correct": true,
        "user_answer": "A",
        "correct_answer": "A",
        "explanation": "..."
      }
    ]
  },
  "completed_at": "2024-01-15T11:00:00Z"
}
```

---

### Get User Quiz Attempts
Retrieve all quiz attempts for a user.

**Endpoint:** `GET /quiz/attempts/{user_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `user_id` (required): User ID

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "score": 8.5,
    "max_score": 10.0,
    "percentage": 85.0,
    "time_taken": 450,
    "feedback_json": {...},
    "completed_at": "2024-01-15T11:00:00Z"
  },
  ...
]
```

---

## 📊 Analytics Endpoints

### Get Analytics Dashboard
Get comprehensive analytics for a user.

**Endpoint:** `GET /analytics/dashboard/{user_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `user_id` (required): User ID

**Response:** `200 OK`
```json
{
  "total_topics": 24,
  "completed_topics": 18,
  "total_time_spent": 156.5,
  "quiz_average": 87.3,
  "streak_count": 15,
  "weekly_activity": [
    {
      "date": "2024-01-15",
      "time_spent": 3.5
    },
    ...
  ],
  "topic_performance": [
    {
      "topic_id": 1,
      "completion": 100.0,
      "time_spent": 5.5
    },
    ...
  ]
}
```

---

### Get Quiz History
Get quiz performance history.

**Endpoint:** `GET /analytics/quiz-history/{user_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `user_id` (required): User ID

**Response:** `200 OK`
```json
{
  "attempts": [
    {
      "quiz_id": 1,
      "score": 8.5,
      "percentage": 85.0,
      "time_taken": 450,
      "completed_at": "2024-01-15T11:00:00Z"
    },
    ...
  ]
}
```

---

## 🔍 Error Responses

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## 📝 Rate Limiting

- **Rate Limit**: 100 requests per minute per IP
- **Headers**:
  - `X-RateLimit-Limit`: Maximum requests
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

---

## 🔒 Security Best Practices

1. **Always use HTTPS** in production
2. **Store JWT tokens securely** (httpOnly cookies recommended)
3. **Rotate API keys** regularly
4. **Validate all inputs** on client side
5. **Handle errors gracefully** without exposing sensitive info
6. **Use environment variables** for secrets
7. **Enable CORS** only for trusted domains

---

## 📚 Interactive API Documentation

Visit these URLs when the backend is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API testing and detailed schema documentation.

---

## 🧪 Example Usage (Python)

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepass123",
    "full_name": "John Doe"
})
print(response.json())

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "user@example.com",
    "password": "securepass123"
})
token = response.json()["access_token"]

# Create topic
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/learning/topics", 
    headers=headers,
    json={
        "title": "Neural Networks",
        "difficulty": "Beginner",
        "depth": "Overview"
    }
)
topic = response.json()
print(topic)
```

---

## 📞 Support

For API support:
- Email: api@learnsphere.pro
- Documentation: https://docs.learnsphere.pro
- GitHub Issues: https://github.com/yourusername/learnsphere-pro/issues
