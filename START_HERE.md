# 🚀 START HERE - Quick Setup Guide

## You have two options to run this FinTech platform:

---

## ✅ Option 1: Install Docker (Recommended - Easiest)

**Why Docker?** Everything works with one command - database, Redis, and app all start automatically.

### Quick Steps:

1. **Install Docker Desktop**:
   - Download: https://www.docker.com/products/docker-desktop/
   - See detailed instructions: [INSTALL_DOCKER.md](./INSTALL_DOCKER.md)

2. **After Docker is installed**, run:
   ```powershell
   # Setup environment
   Copy-Item env.example .env
   notepad .env  # Edit SECRET_KEY and ENCRYPTION_KEY
   
   # Start everything
   docker compose up -d
   
   # Run migrations
   docker compose exec app alembic upgrade head
   ```

3. **Access**: http://localhost:8000/api/docs

**Full guide**: [SETUP_WINDOWS.md](./SETUP_WINDOWS.md) - Option 1

---

## ✅ Option 2: Run Locally (No Docker Needed)

**You already have Python 3.14.0 installed!** You can run it locally right now.

### Quick Steps:

1. **Run the setup script**:
   ```powershell
   .\setup_local.ps1
   ```
   
   This will:
   - Create virtual environment
   - Install all dependencies
   - Create .env file

2. **Install PostgreSQL** (if not installed):
   - Download: https://www.postgresql.org/download/windows/
   - Or use portable version
   - Create database: `CREATE DATABASE fintech_db;`

3. **Configure and run**:
   ```powershell
   # Activate virtual environment
   .\venv\Scripts\Activate.ps1
   
   # Edit .env file
   notepad .env
   # Set: SECRET_KEY, ENCRYPTION_KEY, DATABASE_URL
   
   # Run migrations
   alembic upgrade head
   
   # Start server
   uvicorn app.main:app --reload
   ```

4. **Access**: http://localhost:8000/api/docs

**Full guide**: [SETUP_WINDOWS.md](./SETUP_WINDOWS.md) - Option 2

---

## 🎯 Which Should You Choose?

| If you... | Choose... |
|-----------|-----------|
| Want the easiest setup | **Docker (Option 1)** |
| Don't want to install Docker | **Local Setup (Option 2)** |
| Are learning/developing | **Docker (Option 1)** |
| Want production-like environment | **Docker (Option 1)** |
| Already have PostgreSQL | **Local Setup (Option 2)** |

---

## 📚 Detailed Guides

- **Windows Setup**: [SETUP_WINDOWS.md](./SETUP_WINDOWS.md) - Complete Windows instructions
- **Docker Installation**: [INSTALL_DOCKER.md](./INSTALL_DOCKER.md) - Step-by-step Docker install
- **Quick Start**: [QUICK_START.md](./QUICK_START.md) - Once everything is running
- **Learning Guide**: [docs/LEARNING_GUIDE.md](./docs/LEARNING_GUIDE.md) - Step-by-step learning

---

## ⚡ Quick Start (After Setup)

Once you have Docker OR local setup running:

1. **Test the API**: http://localhost:8000/api/docs
2. **Register a user**: Use the `/api/v1/auth/register` endpoint
3. **Login**: Use the `/api/v1/auth/login` endpoint
4. **Explore**: Try different endpoints

See [QUICK_START.md](./QUICK_START.md) for API examples.

---

## 📦 Version Control (Git)

**Want to use Git for version control?**

1. **Install Git** (if not installed):
   - See: [INSTALL_GIT.md](./INSTALL_GIT.md)

2. **Setup Git repository**:
   ```powershell
   .\setup_git.ps1
   ```
   Or follow: [GIT_SETUP.md](./GIT_SETUP.md)

## 🆘 Need Help?

**Docker not working?**
- See [INSTALL_DOCKER.md](./INSTALL_DOCKER.md)
- Check Docker Desktop is running (whale icon in system tray)

**Python issues?**
- Make sure Python is in PATH: `python --version`
- Use the setup script: `.\setup_local.ps1`

**Database connection errors?**
- Check PostgreSQL is running
- Verify DATABASE_URL in .env file

**Git not working?**
- See [INSTALL_GIT.md](./INSTALL_GIT.md)
- Run setup script: `.\setup_git.ps1`

---

## 🎓 Next Steps After Setup

1. ✅ Get the application running (choose Option 1 or 2 above)
2. 📖 Read [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) to understand what you built
3. 🎯 Follow [docs/LEARNING_GUIDE.md](./docs/LEARNING_GUIDE.md) for step-by-step learning
4. 🔍 Explore the API at http://localhost:8000/api/docs

**Ready to start?** Pick an option above and follow the steps! 🚀

