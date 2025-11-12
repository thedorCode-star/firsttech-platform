# Windows Setup Guide

## Option 1: Install Docker Desktop (Recommended)

Docker makes it easy to run the entire system (database, Redis, app) with one command.

### Step 1: Install Docker Desktop

1. **Download Docker Desktop for Windows**:
   - Visit: https://www.docker.com/products/docker-desktop/
   - Download the installer for Windows
   - Run the installer and follow the setup wizard

2. **System Requirements**:
   - Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
   - OR Windows 11 64-bit
   - WSL 2 feature enabled (Docker Desktop will guide you if needed)
   - Virtualization enabled in BIOS

3. **After Installation**:
   - Restart your computer if prompted
   - Launch Docker Desktop
   - Wait for Docker to start (whale icon in system tray)

### Step 2: Verify Installation

Open PowerShell and run:

```powershell
docker --version
docker compose version
```

You should see version numbers. If you see errors, Docker Desktop might not be running - check the system tray.

### Step 3: Run the Application

```powershell
# Navigate to project directory
cd C:\Users\kalem\Documents\Tresor_cursor\Personal\research-build-network\finTech

# Copy environment file
Copy-Item env.example .env

# Edit .env file (use Notepad or any text editor)
notepad .env
# At minimum, change SECRET_KEY and ENCRYPTION_KEY to random strings

# Start all services
docker compose up -d

# Check if services are running
docker compose ps

# Run database migrations
docker compose exec app alembic upgrade head

# View logs
docker compose logs -f app
```

### Step 4: Access the Application

- API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

### Troubleshooting Docker

**If Docker Desktop won't start:**
- Check if virtualization is enabled in BIOS
- Ensure WSL 2 is installed: `wsl --install`
- Restart your computer

**If you get "WSL 2 installation is incomplete":**
```powershell
# Install WSL 2
wsl --install
# Restart computer, then try Docker Desktop again
```

---

## Option 2: Run Without Docker (Local Setup)

If you prefer not to install Docker, you can run everything locally.

### Prerequisites

1. **Python 3.9+**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: `python --version`

2. **PostgreSQL**
   - Download from: https://www.postgresql.org/download/windows/
   - Or use portable version: https://www.postgresql.org/download/windows/
   - Default port: 5432
   - Default user: postgres
   - Set a password during installation

3. **Redis (Optional)**
   - Download from: https://github.com/microsoftarchive/redis/releases
   - Or use Windows Subsystem for Linux (WSL)

### Step 1: Setup Python Environment

```powershell
# Navigate to project
cd C:\Users\kalem\Documents\Tresor_cursor\Personal\research-build-network\finTech

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Setup Database

1. **Create Database**:
   - Open pgAdmin (comes with PostgreSQL) or use command line:
   ```powershell
   # Using psql (if in PATH)
   psql -U postgres
   # Then in psql:
   CREATE DATABASE fintech_db;
   \q
   ```

2. **Or use pgAdmin GUI**:
   - Right-click "Databases" → Create → Database
   - Name: `fintech_db`

### Step 3: Configure Environment

```powershell
# Copy environment file
Copy-Item env.example .env

# Edit .env file
notepad .env
```

Update these values in `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/fintech_db
SECRET_KEY=your-random-secret-key-min-32-characters-long
ENCRYPTION_KEY=your-32-byte-encryption-key-here
```

**Generate secure keys:**
```powershell
# In Python (run python in terminal)
python
>>> import secrets
>>> secrets.token_urlsafe(32)  # For SECRET_KEY
>>> secrets.token_urlsafe(32)  # For ENCRYPTION_KEY
>>> exit()
```

### Step 4: Run Migrations

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Run migrations
alembic upgrade head
```

### Step 5: Start the Application

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Start the server
uvicorn app.main:app --reload
```

### Step 6: Access the Application

- API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

---

## Quick Comparison

| Feature | Docker (Option 1) | Local (Option 2) |
|---------|------------------|------------------|
| Setup Time | ~15 minutes | ~30 minutes |
| Complexity | Easy (one command) | Medium (multiple steps) |
| Database | Automatic | Manual setup |
| Redis | Automatic | Optional/Manual |
| Isolation | Complete | System-wide |
| Best For | Learning, Development | Production-like |

---

## Recommended: Start with Docker

For learning and development, **Docker is recommended** because:
- ✅ Everything works out of the box
- ✅ No need to install PostgreSQL separately
- ✅ Easy to reset/clean up
- ✅ Same environment as production
- ✅ One command to start everything

## Next Steps

Once you have the application running:

1. **Test the API**: Visit http://localhost:8000/api/docs
2. **Register a user**: Use the `/api/v1/auth/register` endpoint
3. **Login**: Use the `/api/v1/auth/login` endpoint
4. **Explore**: Try different endpoints

See [QUICK_START.md](./QUICK_START.md) for more examples.

---

## Need Help?

**Docker Issues:**
- Check Docker Desktop is running (whale icon in system tray)
- Restart Docker Desktop
- Check Windows updates

**Python Issues:**
- Make sure Python is in PATH: `python --version`
- Use full path: `C:\Python39\python.exe` if needed

**Database Issues:**
- Check PostgreSQL service is running: Services → PostgreSQL
- Verify connection: `psql -U postgres -d fintech_db`

**Port Already in Use:**
- Change port in `.env` or `docker-compose.yml`
- Or stop the service using port 8000

