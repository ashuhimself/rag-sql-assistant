# Deployment Guide

This guide covers deploying the RAG-based AI SQL Assistant to production environments.

## Production Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Load Balancer │    │     Reverse      │    │   Application   │
│    (nginx)      │◄──►│     Proxy        │◄──►│    Servers      │
│                 │    │    (nginx)       │    │   (gunicorn)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
            ┌───────▼───┐  ┌────▼────┐  ┌──▼──────┐
            │PostgreSQL │  │ Qdrant  │  │ Redis   │
            │ Cluster   │  │Cluster  │  │Cluster  │
            └───────────┘  └─────────┘  └─────────┘
```

## Environment Setup

### 1. Production Environment Variables

Create a production `.env` file:

```env
# Production Database
DATABASE_URL=postgresql://user:password@prod-db-host:5432/banking_db
POSTGRES_DB=banking_db
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=secure_password

# Vector Database
QDRANT_URL=http://prod-qdrant-host:6333

# Cache
REDIS_URL=redis://prod-redis-host:6379

# Ollama Configuration
OLLAMA_URL=http://prod-ollama-host:11434
OLLAMA_MODEL=llama3.1:70b

# Django Production Settings
DEBUG=False
SECRET_KEY=super-secure-secret-key-change-this
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Security Settings
SQL_QUERY_TIMEOUT=30
MAX_RESULT_ROWS=1000

# Logging
LOG_LEVEL=INFO

# SSL/TLS
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

### 2. Docker Production Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - backend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - backend
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - QDRANT_URL=${QDRANT_URL}
      - REDIS_URL=${REDIS_URL}
      - OLLAMA_URL=${OLLAMA_URL}
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    depends_on:
      - postgres
      - qdrant
      - redis
    networks:
      - backend
      - frontend
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - REACT_APP_API_URL=https://api.yourdomain.com
    networks:
      - frontend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  qdrant_data:
  redis_data:

networks:
  frontend:
  backend:
```

### 3. Production Dockerfiles

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]
```

Create `frontend/Dockerfile.prod`:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## Server Configuration

### 1. Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# Main application
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}

# API server
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 2. SSL Certificate Setup

#### Using Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Using Custom Certificate

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy your certificate files
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem

# Set proper permissions
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem
```

## Database Configuration

### 1. PostgreSQL Production Setup

```sql
-- Create production database and user
CREATE DATABASE banking_db;
CREATE USER prod_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE banking_db TO prod_user;

-- Performance tuning (adjust based on your server specs)
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.7;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

### 2. Database Backup Strategy

Create backup script `scripts/backup_db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="banking_db"
DB_USER="prod_user"

mkdir -p $BACKUP_DIR

# Create backup
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

## Monitoring and Logging

### 1. Application Monitoring

Install monitoring tools:

```bash
# Install Prometheus and Grafana
docker run -d --name prometheus -p 9090:9090 prom/prometheus
docker run -d --name grafana -p 3001:3000 grafana/grafana
```

### 2. Log Management

Configure centralized logging in `backend/config/settings_prod.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/app/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}
```

## Deployment Process

### 1. Initial Deployment

```bash
# 1. Clone repository on server
git clone https://github.com/yourusername/rag-sql-assistant.git
cd rag-sql-assistant

# 2. Set up environment
cp .env.example .env
# Edit .env with production values

# 3. Set up SSL certificates
# (See SSL setup section above)

# 4. Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d --build

# 5. Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 6. Create embeddings
docker-compose -f docker-compose.prod.yml exec backend python manage.py shell < scripts/embed_schemas.py

# 7. Test deployment
python scripts/test_system.py
```

### 2. Update Deployment

Create deployment script `scripts/deploy.sh`:

```bash
#!/bin/bash

set -e

echo "🚀 Starting deployment..."

# Pull latest code
git pull origin main

# Build new images
docker-compose -f docker-compose.prod.yml build

# Deploy with zero-downtime
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Test deployment
python scripts/test_system.py

echo "✅ Deployment completed successfully"
```

## Scaling Considerations

### 1. Horizontal Scaling

For high traffic, consider:

1. **Multiple Backend Instances**:
   ```yaml
   backend:
     deploy:
       replicas: 4
   ```

2. **Load Balancing**:
   - Use nginx upstream with multiple backend servers
   - Implement health checks

3. **Database Scaling**:
   - Read replicas for query distribution
   - Connection pooling with pgbouncer

### 2. Vertical Scaling

Optimize resource allocation:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

## Security Hardening

### 1. Server Security

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Install fail2ban
sudo apt install fail2ban
```

### 2. Application Security

Update `backend/config/settings_prod.py`:

```python
# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF protection
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
```

## Troubleshooting

### Common Production Issues

1. **502 Bad Gateway**:
   ```bash
   # Check backend container
   docker-compose logs backend

   # Verify backend is listening
   docker-compose exec backend netstat -tlnp
   ```

2. **Database Connection Issues**:
   ```bash
   # Test database connection
   docker-compose exec backend python manage.py dbshell

   # Check database logs
   docker-compose logs postgres
   ```

3. **SSL Certificate Issues**:
   ```bash
   # Test certificate
   openssl s_client -connect yourdomain.com:443

   # Check certificate expiry
   openssl x509 -in /path/to/cert.pem -text -noout
   ```

### Performance Issues

1. **High CPU Usage**:
   - Monitor with `htop` or `docker stats`
   - Scale horizontally with more instances
   - Optimize database queries

2. **High Memory Usage**:
   - Check for memory leaks in application logs
   - Tune gunicorn worker count
   - Implement proper caching

3. **Slow Responses**:
   - Enable database query logging
   - Use APM tools like New Relic or DataDog
   - Optimize Ollama model size vs. performance

## Backup and Recovery

### 1. Full System Backup

```bash
#!/bin/bash
# backup_system.sh

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec postgres pg_dump -U postgres banking_db > $BACKUP_DIR/database.sql

# Volume backups
docker run --rm -v rag-sql-assistant_postgres_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
docker run --rm -v rag-sql-assistant_qdrant_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/qdrant_data.tar.gz -C /data .

# Application backup
tar czf $BACKUP_DIR/application.tar.gz --exclude='.git' --exclude='node_modules' .

echo "Backup completed in $BACKUP_DIR"
```

### 2. Disaster Recovery

```bash
#!/bin/bash
# restore_system.sh

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: $0 <backup_directory>"
    exit 1
fi

# Stop services
docker-compose down

# Restore volumes
docker volume create rag-sql-assistant_postgres_data
docker volume create rag-sql-assistant_qdrant_data

docker run --rm -v rag-sql-assistant_postgres_data:/data -v $BACKUP_DIR:/backup alpine tar xzf /backup/postgres_data.tar.gz -C /data
docker run --rm -v rag-sql-assistant_qdrant_data:/data -v $BACKUP_DIR:/backup alpine tar xzf /backup/qdrant_data.tar.gz -C /data

# Start services
docker-compose up -d

echo "Recovery completed from $BACKUP_DIR"
```

This deployment guide provides a comprehensive approach to deploying the RAG-based AI SQL Assistant in production environments with proper security, monitoring, and scaling considerations.