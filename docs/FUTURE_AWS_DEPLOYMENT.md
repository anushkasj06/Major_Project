# Future AWS Deployment Guide

When ready to move from local Docker Compose to AWS, follow this migration plan.
All environment variables are already externalized so the code changes are minimal.

## Architecture Target (AWS)

```
Route 53 (DNS)
    │
CloudFront (CDN + HTTPS)
    │
ALB (Application Load Balancer)
    ├──/api/* ──► ECS Fargate (Backend + AI Services)
    └──/*     ──► S3 Static (React build)

ECS Services:
  - arambh-backend (FastAPI)
  - arambh-ai-services (RAG)
  - arambh-crawler (Celery + FastAPI)

Managed Services:
  - MongoDB Atlas (or AWS DocumentDB)
  - Qdrant Cloud (or self-hosted EC2)
  - AWS ElastiCache (Redis)
  - AWS S3 (file uploads)
  - AWS Secrets Manager (API keys)
```

## Step-by-Step Migration

### 1. Databases
- **MongoDB**: Create MongoDB Atlas cluster (M0 free / M10 paid)
  - Update `MONGODB_URL` in Secrets Manager
- **Redis**: Create ElastiCache Redis cluster
  - Update `REDIS_URL`
- **Qdrant**: Either Qdrant Cloud or deploy on EC2
  - Update `QDRANT_URL`

### 2. File Storage (S3)
Replace local file storage:
```python
# In document_service.py, replace local save with:
import boto3
s3 = boto3.client('s3')
s3.upload_fileobj(file.file, 'arambh-uploads', unique_name)
file_url = f"s3://arambh-uploads/{unique_name}"
```
Set `UPLOAD_DIR=s3://arambh-uploads`

### 3. ECS Fargate Deployment
```bash
# Build and push images
aws ecr create-repository --repository-name arambh-backend
docker build -t arambh-backend ./backend
docker tag arambh-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/arambh-backend:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/arambh-backend:latest

# Repeat for ai-services and crawler
```

### 4. Task Definitions
Create ECS task definitions for each service using the pushed images.
Memory recommendations:
- backend: 512MB
- ai-services: 4096MB (embedding model)
- crawler: 1024MB

### 5. Secrets Manager
```bash
aws secretsmanager create-secret --name arambh/prod \
  --secret-string '{"GEMINI_API_KEY":"...", "GROQ_API_KEY":"...", "JWT_SECRET_KEY":"..."}'
```

### 6. Frontend (S3 + CloudFront)
```bash
cd frontend && npm run build
aws s3 sync dist/ s3://arambh-frontend --delete
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
```

### Cost Estimate (Monthly)
| Service | Tier | Cost |
|---------|------|------|
| ECS Fargate (3 services) | t3.small equivalent | ~$30 |
| MongoDB Atlas | M10 | ~$57 |
| ElastiCache Redis | cache.t3.micro | ~$12 |
| Qdrant Cloud | Starter | ~$25 |
| S3 + CloudFront | Light traffic | ~$5 |
| **Total** | | **~$130/month** |
