# 🚀 Deployment Guide - LearnSphere Pro

## Quick Deployment Options

### 1. 🐳 Docker Compose (Easiest)

**Prerequisites:**
- Docker & Docker Compose installed

**Steps:**
```bash
# 1. Clone repository
git clone https://github.com/yourusername/learnsphere-pro.git
cd learnsphere-pro

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start all services
docker-compose up -d

# 4. Access application
# Frontend: http://localhost:8501
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 2. ☁️ Render (Free Tier)

#### Backend Deployment

1. **Create PostgreSQL Database**
   - Go to Render Dashboard
   - New → PostgreSQL
   - Copy the Internal Database URL

2. **Deploy Backend**
   - New → Web Service
   - Connect your GitHub repo
   - Settings:
     - Name: `learnsphere-backend`
     - Environment: `Python 3`
     - Build Command: `pip install -r backend/requirements.txt`
     - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     DATABASE_URL=<your-postgres-url>
     SECRET_KEY=<generate-random-string>
     GROQ_API_KEY=<your-groq-key>
     ```

#### Frontend Deployment

1. **Deploy Frontend**
   - New → Web Service
   - Connect your GitHub repo
   - Settings:
     - Name: `learnsphere-frontend`
     - Environment: `Python 3`
     - Build Command: `pip install -r frontend/requirements.txt`
     - Start Command: `cd frontend && streamlit run Home.py --server.port $PORT --server.address 0.0.0.0`
   - Environment Variables:
     ```
     API_BASE_URL=<your-backend-url>
     ```

### 3. 🌐 Heroku

#### Backend
```bash
# 1. Create Heroku app
heroku create learnsphere-backend

# 2. Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# 3. Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set GROQ_API_KEY=your-groq-key

# 4. Deploy
git subtree push --prefix backend heroku main
```

#### Frontend
```bash
# 1. Create Heroku app
heroku create learnsphere-frontend

# 2. Set environment variables
heroku config:set API_BASE_URL=https://learnsphere-backend.herokuapp.com

# 3. Deploy
git subtree push --prefix frontend heroku main
```

### 4. ☁️ AWS (Production)

#### Architecture
- **Frontend**: S3 + CloudFront (or EC2)
- **Backend**: ECS/Fargate or EC2
- **Database**: RDS PostgreSQL
- **Cache**: ElastiCache Redis

#### Steps

1. **Database Setup (RDS)**
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier learnsphere-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password <password> \
  --allocated-storage 20
```

2. **Backend Deployment (ECS)**
```bash
# Build and push Docker image
docker build -t learnsphere-backend ./backend
docker tag learnsphere-backend:latest <ecr-repo-url>:latest
docker push <ecr-repo-url>:latest

# Create ECS service
aws ecs create-service \
  --cluster learnsphere-cluster \
  --service-name backend \
  --task-definition learnsphere-backend \
  --desired-count 2
```

3. **Frontend Deployment (S3 + CloudFront)**
```bash
# Build static files (if using React)
# For Streamlit, deploy to EC2 or ECS

# Upload to S3
aws s3 sync ./frontend s3://learnsphere-frontend

# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name learnsphere-frontend.s3.amazonaws.com
```

### 5. 🌍 Google Cloud Platform

#### Backend (Cloud Run)
```bash
# 1. Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/learnsphere-backend ./backend

# 2. Deploy to Cloud Run
gcloud run deploy learnsphere-backend \
  --image gcr.io/PROJECT_ID/learnsphere-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=<db-url>,SECRET_KEY=<key>,GROQ_API_KEY=<key>
```

#### Frontend (Cloud Run)
```bash
# 1. Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/learnsphere-frontend ./frontend

# 2. Deploy to Cloud Run
gcloud run deploy learnsphere-frontend \
  --image gcr.io/PROJECT_ID/learnsphere-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_BASE_URL=<backend-url>
```

### 6. 🔷 Azure

#### Backend (App Service)
```bash
# 1. Create resource group
az group create --name learnsphere-rg --location eastus

# 2. Create App Service plan
az appservice plan create \
  --name learnsphere-plan \
  --resource-group learnsphere-rg \
  --sku B1 \
  --is-linux

# 3. Create web app
az webapp create \
  --resource-group learnsphere-rg \
  --plan learnsphere-plan \
  --name learnsphere-backend \
  --runtime "PYTHON:3.11"

# 4. Deploy code
az webapp up \
  --name learnsphere-backend \
  --resource-group learnsphere-rg \
  --runtime "PYTHON:3.11"
```

## 🔒 Security Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong random string
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up CORS properly
- [ ] Configure rate limiting
- [ ] Enable database backups
- [ ] Set up monitoring and logging
- [ ] Use strong database passwords
- [ ] Enable firewall rules
- [ ] Set up CDN for static assets

## 📊 Monitoring

### Application Monitoring
- **Sentry**: Error tracking
- **DataDog**: Performance monitoring
- **New Relic**: APM

### Infrastructure Monitoring
- **Prometheus + Grafana**: Metrics
- **ELK Stack**: Logging
- **CloudWatch** (AWS): Cloud monitoring

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK_BACKEND }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK_FRONTEND }}
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check DATABASE_URL format
   - Verify database is running
   - Check firewall rules

2. **API Key Errors**
   - Verify GROQ_API_KEY is set
   - Check API key is valid
   - Ensure no extra spaces

3. **CORS Errors**
   - Update CORS settings in backend
   - Add frontend URL to allowed origins

4. **Port Already in Use**
   - Change port in docker-compose.yml
   - Kill existing process: `lsof -ti:8000 | xargs kill`

## 📞 Support

For deployment help:
- Documentation: https://docs.learnsphere.pro
- Discord: https://discord.gg/learnsphere
- Email: support@learnsphere.pro
