# Deployment Guide

## Local Development

### Quick Start

```bash
# 1. Clone and setup
git clone <your-repo>
cd notes

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Configure environment
# Edit .env with your credentials

# 4. Set up Supabase
# - Create project at supabase.com
# - Run supabase_schema.sql in SQL Editor
# - Copy URL and anon key to .env

# 5. Start services
docker-compose up

# 6. Test
python quick_test.py
```

### Manual Setup (Without Docker)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# 3. Install and start Redis
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Create directories
mkdir -p uploads data/chroma

# 6. Start Celery worker (in one terminal)
celery -A celery_app.celery worker --loglevel=info

# 7. Start FastAPI (in another terminal)
uvicorn main:app --reload
```

## Production Deployment

### Option 1: Docker Compose (Simple)

**Best for**: Small to medium deployments, single server

```bash
# 1. Prepare server
# - Ubuntu 20.04+ or similar
# - Install Docker and Docker Compose
# - Open ports 8000 (API)

# 2. Clone repository
git clone <your-repo>
cd notes

# 3. Configure production environment
cp .env.example .env
nano .env

# Set production values:
# - Real Supabase credentials
# - Strong API keys
# - Production LLM API keys

# 4. Modify docker-compose.yml for production
# - Remove --reload from uvicorn command
# - Add restart: always to all services
# - Configure proper volumes for backups

# 5. Start services
docker-compose up -d

# 6. Set up nginx reverse proxy (recommended)
sudo apt-get install nginx

# Create nginx config
sudo nano /etc/nginx/sites-available/notes-api

# Add:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/notes-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 7. Set up SSL with Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 8. Set up automatic backups
# See Backup section below
```

### Option 2: Kubernetes (Scalable)

**Best for**: Large deployments, high availability

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notes-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: notes-api
  template:
    metadata:
      labels:
        app: notes-api
    spec:
      containers:
      - name: api
        image: your-registry/notes-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: notes-secrets
              key: supabase-url
        # ... other env vars
        volumeMounts:
        - name: uploads
          mountPath: /app/uploads
        - name: chroma-data
          mountPath: /data/chroma
      volumes:
      - name: uploads
        persistentVolumeClaim:
          claimName: uploads-pvc
      - name: chroma-data
        persistentVolumeClaim:
          claimName: chroma-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: notes-api-service
spec:
  selector:
    app: notes-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Option 3: Cloud Platforms

#### AWS (ECS + RDS)

```bash
# 1. Build and push Docker image
docker build -t notes-api .
docker tag notes-api:latest <account>.dkr.ecr.<region>.amazonaws.com/notes-api:latest
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker push <account>.dkr.ecr.<region>.amazonaws.com/notes-api:latest

# 2. Create ECS cluster
aws ecs create-cluster --cluster-name notes-cluster

# 3. Create task definition
# See task-definition.json example

# 4. Create service
aws ecs create-service \
  --cluster notes-cluster \
  --service-name notes-api \
  --task-definition notes-api-task \
  --desired-count 2 \
  --launch-type FARGATE

# 5. Set up Application Load Balancer
# 6. Configure Auto Scaling
# 7. Set up CloudWatch monitoring
```

#### Google Cloud (Cloud Run)

```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/notes-api

# 2. Deploy to Cloud Run
gcloud run deploy notes-api \
  --image gcr.io/PROJECT_ID/notes-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=your-url,GEMINI_API_KEY=your-key

# 3. Set up Cloud Tasks for Celery
# 4. Configure Cloud Storage for uploads
```

#### Heroku

```bash
# 1. Create Heroku app
heroku create notes-api

# 2. Add Redis addon
heroku addons:create heroku-redis:hobby-dev

# 3. Set environment variables
heroku config:set SUPABASE_URL=your-url
heroku config:set GEMINI_API_KEY=your-key

# 4. Deploy
git push heroku main

# 5. Scale workers
heroku ps:scale worker=2
```

## Environment Configuration

### Production .env Template

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key  # Use service role key for production

# Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Chroma
CHROMA_PERSIST_DIR=/data/chroma

# LLM
GEMINI_API_KEY=your-production-gemini-key
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-pro

# Application
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=104857600  # 100MB
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Monitoring

### Health Checks

```bash
# Check API health
curl http://your-domain.com/health

# Check Celery workers (Flower)
# Access at http://your-domain.com:5555
```

### Logging

#### Docker Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f worker

# Save logs to file
docker-compose logs > logs.txt
```

#### Structured Logging (Production)

Add to `main.py`:

```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### Metrics & Monitoring

#### Prometheus + Grafana

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'notes-api'
    static_configs:
      - targets: ['app:8000']
  
  - job_name: 'celery'
    static_configs:
      - targets: ['flower:5555']
```

#### Application Metrics

Add to `requirements.txt`:
```
prometheus-client==0.19.0
prometheus-fastapi-instrumentator==6.1.0
```

Add to `main.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

## Backup & Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh - Run daily via cron

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup Chroma data
tar -czf $BACKUP_DIR/chroma.tar.gz /data/chroma

# Backup uploads
tar -czf $BACKUP_DIR/uploads.tar.gz /app/uploads

# Backup Supabase (via pg_dump if self-hosted)
# Or use Supabase's built-in backup features

# Upload to S3
aws s3 sync $BACKUP_DIR s3://your-backup-bucket/$(date +%Y%m%d)/

# Keep only last 30 days
find /backups -type d -mtime +30 -exec rm -rf {} \;
```

### Restore Process

```bash
# 1. Stop services
docker-compose down

# 2. Restore Chroma
cd /data
tar -xzf /backups/20251101/chroma.tar.gz

# 3. Restore uploads
cd /app
tar -xzf /backups/20251101/uploads.tar.gz

# 4. Restart services
docker-compose up -d
```

## Security

### API Authentication

Add JWT authentication:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/upload")
async def upload_pdf(
    file: UploadFile,
    user = Depends(verify_token)
):
    # ... upload logic
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/upload")
@limiter.limit("5/minute")
async def upload_pdf(request: Request, file: UploadFile):
    # ... upload logic
```

### HTTPS/SSL

```bash
# Let's Encrypt with Certbot
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  worker:
    build: .
    command: celery -A celery_app.celery worker --loglevel=info --concurrency=2
    deploy:
      replicas: 5  # Run 5 worker instances
```

### Vertical Scaling

```yaml
# docker-compose.yml
services:
  app:
    build: .
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### Load Balancing

```nginx
# nginx.conf
upstream notes_api {
    least_conn;
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://notes_api;
    }
}
```

## Cost Optimization

### LLM API Costs

1. **Cache responses**: Store summaries to avoid re-processing
2. **Batch requests**: Process multiple chunks together when possible
3. **Use free tiers**: Gemini offers generous free tier
4. **Local LLMs**: Consider running local models for sensitive data

### Infrastructure Costs

1. **Auto-scaling**: Scale down during low usage
2. **Spot instances**: Use spot/preemptible instances for workers
3. **Storage optimization**: Compress old files, clean up unused data
4. **CDN**: Use CDN for static assets

## Troubleshooting

### Common Issues

**Workers not picking up tasks**
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Restart workers
docker-compose restart worker
```

**Out of memory**
```bash
# Check memory usage
docker stats

# Reduce worker concurrency
# In docker-compose.yml: --concurrency=1
```

**Chroma persistence issues**
```bash
# Ensure volume is properly mounted
docker-compose down
docker volume ls
docker-compose up -d
```

## Support & Maintenance

### Regular Maintenance Tasks

1. **Weekly**: Review logs, check disk space
2. **Monthly**: Update dependencies, security patches
3. **Quarterly**: Review and optimize costs
4. **Annually**: Disaster recovery drill

### Updating

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Apply migrations (if any)
# Run database migrations

# Rolling update
docker-compose up -d --no-deps --build app
docker-compose up -d --no-deps --build worker
```
