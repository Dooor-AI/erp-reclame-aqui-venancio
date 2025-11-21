# Venâncio RPA - Complete Deployment Guide

This guide covers deploying the Venâncio RPA system (frontend + backend) to various environments from local development to production.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Production Deployment Options](#production-deployment-options)
3. [Environment Variables](#environment-variables)
4. [Database Migration & Setup](#database-migration--setup)
5. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- Git
- PostgreSQL or SQLite (default)
- Google Generative AI API key (for Gemini)
- Chrome/Chromium (for Selenium scraper)

### Backend Setup

#### 1. Navigate to Backend Directory

```bash
cd backend
```

#### 2. Create and Activate Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database Configuration
DATABASE_URL=sqlite:///./venancio.db
# For PostgreSQL: postgresql://user:password@localhost:5432/venancio_rpa

# Gemini AI API
GEMINI_API_KEY=your_api_key_here

# Scraper Configuration
SCRAPER_INTERVAL=3600  # Run every hour (in seconds)
SCRAPER_ENABLED=true

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000

# Server Configuration
DEBUG=true
```

#### 5. Run Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Frontend Setup

#### 1. Navigate to Frontend Directory

```bash
cd frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Configure Environment Variables

Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 4. Run Development Server

```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Full Stack Running

Once both are running:

1. Navigate to http://localhost:3000
2. View the dashboard with KPIs
3. Navigate to Reclamações (Complaints) to see scraped data
4. Click "Gerar Resposta" to generate AI responses
5. Check backend API docs at http://localhost:8000/docs

---

## Production Deployment Options

### Option 1: Docker (Recommended)

#### Docker Setup

Create a `docker-compose.yml` in the project root:

```yaml
version: '3.9'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://venancio:password@postgres:5432/venancio_rpa
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      ALLOWED_ORIGINS: https://yourdomain.com
      DEBUG: false
    depends_on:
      - postgres
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: https://api.yourdomain.com
    depends_on:
      - backend
    restart: always

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: venancio
      POSTGRES_PASSWORD: secure_password_here
      POSTGRES_DB: venancio_rpa
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

EXPOSE 3000

CMD ["npm", "start"]
```

#### Deploy with Docker

```bash
docker-compose build
docker-compose up -d
```

---

### Option 2: Vercel (Frontend Only)

Vercel is ideal for deploying the Next.js frontend.

#### Prerequisites

- Vercel account (https://vercel.com)
- GitHub account with project pushed

#### Steps

1. **Push frontend to GitHub:**

```bash
cd frontend
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/projeto_venancio_frontend.git
git push -u origin main
```

2. **Import Project in Vercel:**
   - Go to https://vercel.com/new
   - Select "Import Git Repository"
   - Choose your frontend repository
   - Click "Import"

3. **Configure Environment Variables:**
   - In Vercel dashboard: Settings > Environment Variables
   - Add: `NEXT_PUBLIC_API_URL=https://your-backend-domain.com`

4. **Deploy:**
   - Vercel automatically deploys on git push
   - Your app will be available at `your-project.vercel.app`

5. **Update Backend CORS:**

Update your backend `.env`:

```env
ALLOWED_ORIGINS=https://your-project.vercel.app
```

---

### Option 3: Railway (Full Stack)

Railway is excellent for hosting both frontend and backend.

#### Prerequisites

- Railway account (https://railway.app)
- GitHub repository

#### Steps

1. **Connect GitHub to Railway:**
   - Go to https://railway.app/dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize and select your repository

2. **Create Backend Service:**
   - Add a new service
   - Select "GitHub repo"
   - Set root directory: `backend`
   - Add environment variables from `.env`
   - Railway will auto-detect Python and run `requirements.txt`

3. **Create Frontend Service:**
   - Add another service
   - Select "GitHub repo"
   - Set root directory: `frontend`
   - Add `NEXT_PUBLIC_API_URL` environment variable
   - Railway will auto-detect Node.js

4. **Create PostgreSQL Database:**
   - Add MySQL/PostgreSQL service
   - Link to backend service
   - Update backend `DATABASE_URL` to use Railway's connection string

5. **Configure Custom Domain:**
   - In Railway project settings
   - Add custom domain for both frontend and backend

#### Example Railway Configuration

Backend `railway.json`:

```json
{
  "build": {
    "builder": "python"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port 8000"
  }
}
```

---

### Option 4: AWS EC2 + RDS

For enterprise-level deployment.

#### Prerequisites

- AWS account
- EC2 instance (Ubuntu 22.04)
- RDS PostgreSQL database

#### Steps

1. **SSH into EC2 instance:**

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

2. **Install Dependencies:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Node.js, PostgreSQL client
sudo apt install -y python3 python3-venv nodejs npm postgresql-client

# Install Nginx (reverse proxy)
sudo apt install -y nginx
```

3. **Deploy Backend:**

```bash
# Clone repository
git clone https://github.com/yourusername/projeto_venancio.git
cd projeto_venancio/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env with RDS database URL
# IMPORTANT: Use RDS endpoint for DATABASE_URL
```

4. **Setup Systemd Service for Backend:**

Create `/etc/systemd/system/venancio-backend.service`:

```ini
[Unit]
Description=Venâncio RPA Backend
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/projeto_venancio/backend
ExecStart=/home/ubuntu/projeto_venancio/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable venancio-backend
sudo systemctl start venancio-backend
```

5. **Deploy Frontend:**

```bash
cd /home/ubuntu/projeto_venancio/frontend
npm install
npm run build

# Create next.config with output: 'standalone'
```

6. **Configure Nginx:**

Create `/etc/nginx/sites-available/venancio`:

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SSL (use Let's Encrypt)
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/venancio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Environment Variables

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///./venancio.db` | Database connection string |
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key for AI |
| `ALLOWED_ORIGINS` | No | `http://localhost:3000` | CORS allowed origins |
| `SCRAPER_ENABLED` | No | `true` | Enable automated scraping |
| `SCRAPER_INTERVAL` | No | `3600` | Scraper interval in seconds |
| `DEBUG` | No | `true` | Debug mode (false in production) |

### Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Backend API URL |

### Database Connection Strings

**SQLite (Development):**
```
sqlite:///./venancio.db
```

**PostgreSQL (Production):**
```
postgresql://user:password@localhost:5432/venancio_rpa
```

**PostgreSQL with SSL:**
```
postgresql://user:password@host:5432/venancio_rpa?sslmode=require
```

---

## Database Migration & Setup

### SQLite (Development)

SQLite is created automatically. No additional setup required.

### PostgreSQL (Production)

#### 1. Create Database

```bash
psql -U postgres
CREATE DATABASE venancio_rpa;
CREATE USER venancio WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE venancio_rpa TO venancio;
```

#### 2. Run Migrations (Using Alembic)

```bash
cd backend
alembic upgrade head
```

#### 3. Initial Data Seeding (Optional)

```bash
python -m app.scripts.seed_database
```

#### 4. Verify Tables

```bash
psql -U venancio -d venancio_rpa

\dt  # List all tables
```

### Database Backup

#### PostgreSQL Backup

```bash
# Full database backup
pg_dump -U venancio venancio_rpa > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -U venancio venancio_rpa < backup_20251117_150000.sql
```

#### SQLite Backup

```bash
# Simple file copy
cp venancio.db venancio.db.backup
```

---

## Troubleshooting

### Backend Issues

#### 1. Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

#### 2. ChromeDriver Not Found (Scraper Issues)

```bash
# Install ChromeDriver
# Download from: https://chromedriver.chromium.org/

# Or use system Chrome:
# Modify scraper to use system browser path
```

#### 3. Database Connection Failed

```bash
# Check DATABASE_URL in .env
# Verify database server is running
# For PostgreSQL:
psql -U user -h localhost -d venancio_rpa -c "SELECT 1;"
```

#### 4. Gemini API Errors

```bash
# Verify API key in .env
# Check API quotas at https://console.cloud.google.com/
# Ensure billing is enabled
```

### Frontend Issues

#### 1. API Connection Failed

Check `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Verify backend is running:
```bash
curl http://localhost:8000/health
```

#### 2. Build Failures

```bash
# Clear Next.js cache
rm -rf .next

# Rebuild
npm run build
```

#### 3. Port 3000 Already in Use

```bash
npm run dev -- -p 3001
```

### Docker Issues

#### 1. Container Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild image
docker-compose build --no-cache
```

#### 2. Database Connection in Docker

Ensure services are on same network:
```bash
docker network ls
docker inspect docker_default
```

### Performance Issues

#### Backend Optimization

- Enable query caching
- Index frequently queried columns
- Use connection pooling

#### Frontend Optimization

- Enable Next.js Image Optimization
- Use Code Splitting
- Enable ISR (Incremental Static Regeneration)

---

## Production Checklist

- [ ] Set `DEBUG=false` in backend `.env`
- [ ] Set strong database password
- [ ] Configure HTTPS/SSL certificates
- [ ] Enable CORS only for trusted origins
- [ ] Set up automated database backups
- [ ] Configure monitoring and logging
- [ ] Set up error tracking (Sentry, LogRocket)
- [ ] Enable rate limiting
- [ ] Configure CDN for static assets
- [ ] Set up CI/CD pipeline
- [ ] Document deployment process
- [ ] Test disaster recovery procedures

---

## Support

For issues or questions:
1. Check logs first
2. Review error messages carefully
3. Consult troubleshooting section
4. Check backend API docs at `/docs`
5. Review frontend README for component details

---

**Last Updated:** 2025-11-17
**Version:** 1.0.0
