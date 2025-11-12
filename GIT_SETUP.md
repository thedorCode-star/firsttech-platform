# Git Setup Guide for FinTech Project

## Step 1: Install Git (if not installed)

See [INSTALL_GIT.md](./INSTALL_GIT.md) for installation instructions.

## Step 2: Configure Git (First Time Only)

```powershell
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch to 'main'
git config --global init.defaultBranch main

# Verify configuration
git config --list
```

## Step 3: Initialize Git Repository

```powershell
# Make sure you're in the project directory
cd C:\Users\kalem\Documents\Tresor_cursor\Personal\research-build-network\finTech

# Initialize git repository
git init

# Check status
git status
```

## Step 4: Create Initial Commit

```powershell
# Add all files
git add .

# Check what will be committed
git status

# Create initial commit
git commit -m "Initial commit: FinTech platform with POPIA compliance and HA architecture"
```

## Step 5: Create .gitignore (Already Created!)

The project already has a `.gitignore` file that excludes:
- Python cache files (`__pycache__/`)
- Virtual environments (`venv/`)
- Environment files (`.env`)
- IDE files (`.vscode/`, `.idea/`)
- Database files
- Logs
- Secrets

**Important**: Never commit `.env` files with real secrets!

## Step 6: (Optional) Connect to Remote Repository

### GitHub

1. **Create a new repository on GitHub**:
   - Go to: https://github.com/new
   - Name: `fintech-platform` (or your choice)
   - Don't initialize with README (we already have one)
   - Click "Create repository"

2. **Connect local to remote**:

```powershell
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/fintech-platform.git

# Or if using SSH:
git remote add origin git@github.com:YOUR_USERNAME/fintech-platform.git

# Verify remote
git remote -v
```

3. **Push to GitHub**:

```powershell
# Push to main branch
git push -u origin main
```

### GitLab

```powershell
# Create repository on GitLab, then:
git remote add origin https://gitlab.com/YOUR_USERNAME/fintech-platform.git
git push -u origin main
```

### Bitbucket

```powershell
# Create repository on Bitbucket, then:
git remote add origin https://bitbucket.org/YOUR_USERNAME/fintech-platform.git
git push -u origin main
```

## Step 7: Create a Branch for Development

```powershell
# Create and switch to development branch
git checkout -b develop

# Or use the new syntax:
git switch -c develop

# Work on your changes, then commit
git add .
git commit -m "Your commit message"

# Push branch
git push -u origin develop
```

## Common Git Commands

### Daily Workflow

```powershell
# Check status
git status

# Add files
git add .                    # Add all changes
git add filename.py          # Add specific file

# Commit
git commit -m "Description of changes"

# Push to remote
git push

# Pull latest changes
git pull

# View commit history
git log --oneline

# View changes
git diff
```

### Branching

```powershell
# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main
git switch main              # New syntax

# List branches
git branch

# Merge branch
git checkout main
git merge feature-name

# Delete branch
git branch -d feature-name
```

### Undo Changes

```powershell
# Unstage files (keep changes)
git reset HEAD filename

# Discard changes in working directory
git checkout -- filename
git restore filename         # New syntax

# Undo last commit (keep changes)
git reset --soft HEAD~1

# View previous commit
git show HEAD
```

## Best Practices

### Commit Messages

Use clear, descriptive commit messages:

```powershell
# Good
git commit -m "Add MFA authentication endpoint"
git commit -m "Fix database connection pooling issue"
git commit -m "Update POPIA compliance documentation"

# Bad
git commit -m "fix"
git commit -m "changes"
git commit -m "asdf"
```

### Commit Frequency

- Commit often (small, logical changes)
- Commit before major refactoring
- Commit working code (don't commit broken code)
- Use branches for features

### What NOT to Commit

- `.env` files with real secrets
- Database files (`.db`, `.sqlite`)
- Log files
- Compiled Python files (`__pycache__/`)
- IDE-specific files (unless team uses same IDE)

## Security: Protecting Secrets

### Before First Commit

1. **Check `.env` is in `.gitignore`**:
   ```powershell
   git check-ignore .env
   # Should output: .env
   ```

2. **Verify no secrets in code**:
   ```powershell
   # Search for potential secrets
   git diff --cached | grep -i "password\|secret\|key"
   ```

3. **Use environment variables**:
   - Never hardcode secrets
   - Use `.env` file (already in `.gitignore`)
   - Use secrets management in production

### If You Accidentally Committed Secrets

```powershell
# Remove from history (DANGEROUS - only if needed)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: This rewrites history)
git push origin --force --all
```

**Better**: Rotate the secrets and commit the new ones properly.

## Git Workflow for This Project

### Recommended Branch Structure

```
main          # Production-ready code
├── develop   # Development branch
    ├── feature/popia-compliance
    ├── feature/mfa-authentication
    ├── feature/transaction-api
    └── bugfix/database-connection
```

### Workflow

1. **Start new feature**:
   ```powershell
   git checkout develop
   git pull
   git checkout -b feature/new-feature
   ```

2. **Work and commit**:
   ```powershell
   git add .
   git commit -m "Add new feature"
   ```

3. **Push feature branch**:
   ```powershell
   git push -u origin feature/new-feature
   ```

4. **Create Pull Request** (on GitHub/GitLab)

5. **Merge to develop**, then to `main` when ready

## Next Steps

1. ✅ Install Git (if needed)
2. ✅ Initialize repository
3. ✅ Make initial commit
4. ✅ (Optional) Push to GitHub/GitLab
5. ✅ Start developing!

## Resources

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com/
- **Learn Git**: https://learngitbranching.js.org/ (Interactive tutorial)
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf

---

**Ready to start?** Run the commands in Step 3-4 above! 🚀

