# How to Install Git on Windows

## Quick Installation

### Option 1: Git for Windows (Recommended)

1. **Download Git**:
   - Visit: https://git-scm.com/download/win
   - The download will start automatically
   - Or use direct link: https://github.com/git-for-windows/git/releases/latest

2. **Run the Installer**:
   - Double-click the downloaded `.exe` file
   - Follow the installation wizard:
     - **Select Components**: Keep defaults (Git Bash, Git GUI, etc.)
     - **Default Editor**: Choose your preferred editor (VS Code, Notepad++, etc.)
     - **PATH Environment**: Choose "Git from the command line and also from 3rd-party software" (recommended)
     - **Line Ending Conversions**: Choose "Checkout Windows-style, commit Unix-style line endings" (recommended)
     - **Terminal Emulator**: Choose "Use Windows' default console window"
     - Click "Install"

3. **Verify Installation**:
   - Close and reopen PowerShell
   - Run: `git --version`
   - You should see: `git version 2.x.x`

### Option 2: Install via Winget (Windows Package Manager)

If you have Windows 11 or Windows 10 with winget:

```powershell
winget install --id Git.Git -e --source winget
```

### Option 3: Install via Chocolatey

If you have Chocolatey installed:

```powershell
choco install git
```

## After Installation

1. **Configure Git** (first time setup):

```powershell
# Set your name
git config --global user.name "Your Name"

# Set your email
git config --global user.email "your.email@example.com"

# Set default branch name to 'main'
git config --global init.defaultBranch main

# Set line ending handling
git config --global core.autocrlf true
```

2. **Verify Configuration**:

```powershell
git config --list
```

## Troubleshooting

### "git is not recognized"

1. **Restart PowerShell/Terminal** after installation
2. **Check PATH**: 
   - Git should be in: `C:\Program Files\Git\cmd\`
   - If not, add it manually to System Environment Variables

3. **Manual PATH Setup**:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add: `C:\Program Files\Git\cmd`
   - Restart PowerShell

### Git Bash vs PowerShell

- **Git Bash**: Unix-like terminal (comes with Git)
- **PowerShell**: Windows native (what you're using)

Both work fine! Use whichever you prefer.

## Next Steps

Once Git is installed, you can:

1. Initialize your repository
2. Make your first commit
3. Connect to GitHub/GitLab/Bitbucket

See the Git setup guide in the project for next steps!

