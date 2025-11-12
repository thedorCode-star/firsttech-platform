# Quick Start Guide

Get your FinTech platform up and running in minutes!

## Prerequisites

**Option 1: Docker (Recommended)**
- Docker Desktop for Windows ([Download](https://www.docker.com/products/docker-desktop/))
- See [SETUP_WINDOWS.md](./SETUP_WINDOWS.md) for detailed Windows installation

**Option 2: Local Setup**
- Python 3.9 or higher
- PostgreSQL 13+
- Redis (optional, for caching)

## Option 1: Docker Compose (Recommended)

> **Windows Users**: If `docker-compose` command doesn't work, try `docker compose` (space instead of hyphen). If Docker is not installed, see [SETUP_WINDOWS.md](./SETUP_WINDOWS.md) for installation instructions.

### Step 1: Setup

```powershell
# Windows PowerShell
cd C:\Users\kalem\Documents\Tresor_cursor\Personal\research-build-network\finTech
Copy-Item env.example .env
notepad .env  # Edit with your SECRET_KEY and ENCRYPTION_KEY
```

### Step 2: Start Services

```powershell
# Try this first (newer Docker)
docker compose up -d

# Or if that doesn't work, try:
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- Application server

### Step 3: Run Migrations

```powershell
docker compose exec app alembic upgrade head
# Or: docker-compose exec app alembic upgrade head
```

### Step 4: Access the Application

- API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

## Option 2: Local Development

### Step 1: Setup Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Setup Database

```bash
# Install PostgreSQL and create database
createdb fintech_db

# Or use Docker for PostgreSQL
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=fintech_db -p 5432:5432 postgres:15
```

### Step 3: Configure Environment

```bash
cp env.example .env
# Edit .env with your database URL and secrets
```

### Step 4: Run Migrations

```bash
alembic upgrade head
```

### Step 5: Start Application

```bash
uvicorn app.main:app --reload
```

## Testing the API

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

Save the `access_token` from the response.

### 3. Get User Info

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Create a Transaction

```bash
curl -X POST "http://localhost:8000/api/v1/transactions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "deposit",
    "amount": "1000.00",
    "currency": "ZAR",
    "description": "Test deposit"
  }'
```

### 5. Access Personal Data (POPIA)

```bash
curl -X GET "http://localhost:8000/api/v1/data-subject/access" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Next Steps

1. **Read the Documentation**
   - [Architecture Guide](./docs/ARCHITECTURE.md)
   - [POPIA Compliance](./docs/POPIA_COMPLIANCE.md)
   - [Learning Guide](./docs/LEARNING_GUIDE.md)

2. **Explore the API**
   - Visit http://localhost:8000/api/docs for interactive API documentation

3. **Setup MFA**
   - Use the `/api/v1/auth/mfa/setup` endpoint
   - Scan QR code with authenticator app (Google Authenticator, Authy)

4. **Configure for Production**
   - Review [Deployment Guide](./docs/DEPLOYMENT.md)
   - Set up proper secrets management
   - Configure cloud provider

## Troubleshooting

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps

# Check database logs
docker-compose logs db
```

### Port Already in Use

```bash
# Change port in docker-compose.yml or use different port
uvicorn app.main:app --port 8001
```

### Migration Errors

```bash
# Reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d
docker-compose exec app alembic upgrade head
```

## Getting Help

- Check the [Learning Guide](./docs/LEARNING_GUIDE.md) for step-by-step tutorials
- Review API documentation at `/api/docs`
- Check logs: `docker-compose logs -f app`

## Security Notes

⚠️ **Important for Production:**

1. Change `SECRET_KEY` and `ENCRYPTION_KEY` in `.env`
2. Use strong, random keys (min 32 characters)
3. Never commit `.env` to version control
4. Enable HTTPS in production
5. Configure proper CORS origins
6. Set up monitoring and alerting

Happy coding! 🚀

