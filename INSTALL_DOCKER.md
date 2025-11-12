# How to Install Docker Desktop on Windows

## Quick Installation Guide

### Step 1: Download Docker Desktop

1. Go to: https://www.docker.com/products/docker-desktop/
2. Click "Download for Windows"
3. Save the installer file (Docker Desktop Installer.exe)

### Step 2: Install Docker Desktop

1. **Run the installer** (Docker Desktop Installer.exe)
2. **Follow the wizard**:
   - Accept the license agreement
   - Choose installation location (default is fine)
   - Check "Use WSL 2 instead of Hyper-V" (recommended)
   - Click "Install"
3. **Wait for installation** to complete
4. **Click "Close and restart"** when prompted

### Step 3: Start Docker Desktop

1. **After restart**, look for Docker Desktop in Start Menu
2. **Launch Docker Desktop**
3. **Accept the service agreement** if prompted
4. **Wait for Docker to start** (whale icon appears in system tray)

### Step 4: Verify Installation

Open PowerShell and run:

```powershell
docker --version
```

You should see something like: `Docker version 24.0.0, build abc123`

Also test:

```powershell
docker compose version
```

You should see: `Docker Compose version v2.x.x`

## System Requirements

- **Windows 10 64-bit**: Pro, Enterprise, or Education (Build 19041 or higher)
- **OR Windows 11 64-bit**
- **WSL 2** (Windows Subsystem for Linux 2)
- **Virtualization** enabled in BIOS

## If WSL 2 is Not Installed

Docker Desktop will prompt you, or install manually:

```powershell
# Open PowerShell as Administrator
wsl --install

# Restart your computer
# Then try Docker Desktop again
```

## Troubleshooting

### "Docker Desktop won't start"

1. **Check virtualization is enabled**:
   - Restart computer
   - Enter BIOS (usually F2, F10, or Del during boot)
   - Enable "Virtualization Technology" or "VT-x"
   - Save and exit

2. **Check WSL 2**:
   ```powershell
   wsl --status
   # Should show: "Default Version: 2"
   ```

3. **Restart Docker Desktop**:
   - Right-click whale icon in system tray
   - Click "Restart Docker Desktop"

### "WSL 2 installation is incomplete"

```powershell
# Install WSL 2
wsl --install

# Set WSL 2 as default
wsl --set-default-version 2

# Restart computer
```

### "Hardware assisted virtualization and data execution protection must be enabled"

1. Enable virtualization in BIOS (see above)
2. Enable Hyper-V in Windows Features:
   - Search "Turn Windows features on or off"
   - Check "Hyper-V" and "Virtual Machine Platform"
   - Restart

## After Installation

Once Docker is running, you can use:

```powershell
# Navigate to your project
cd C:\Users\kalem\Documents\Tresor_cursor\Personal\research-build-network\finTech

# Start the application
docker compose up -d
```

## Alternative: Use Docker Without Desktop

If Docker Desktop doesn't work, you can use Docker via WSL 2 directly:

```powershell
# Install Docker in WSL
wsl
sudo apt update
sudo apt install docker.io
sudo service docker start
```

But Docker Desktop is much easier for Windows users!

## Need More Help?

- Docker Desktop Documentation: https://docs.docker.com/desktop/install/windows-install/
- Docker Community Forums: https://forums.docker.com/
- Stack Overflow: Search "docker windows installation"

