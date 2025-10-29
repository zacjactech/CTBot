# Windows User Guide

## 🪟 Quick Start for Windows

This guide is specifically for Windows users. The bot works perfectly on Windows with the provided scripts!

## 📋 Prerequisites

1. **Python 3.10+** - [Download from python.org](https://www.python.org/downloads/)
2. **Poetry** - Install with: `pip install poetry`
3. **Git** (optional) - [Download from git-scm.com](https://git-scm.com/downloads)

## 🚀 Installation

### Step 1: Get the Code

**Option A: With Git**
```powershell
git clone <repository-url>
cd ctbot
```

**Option B: Download ZIP**
1. Download the ZIP file
2. Extract to a folder
3. Open PowerShell in that folder

### Step 2: Install Dependencies

```powershell
.\run.ps1 install
```

### Step 3: Configure API Keys

```powershell
# Copy the example file
copy .env.example .env

# Edit .env with Notepad
notepad .env
```

Add your Binance Testnet API keys:
```
BINANCE_API_KEY="your_api_key_here"
BINANCE_API_SECRET="your_api_secret_here"
```

## 🎯 Using the Bot

### PowerShell Commands

All commands use the `run.ps1` script:

```powershell
# View all available commands
.\run.ps1 help

# Launch web UI (easiest!)
.\run.ps1 web

# Launch interactive terminal UI
.\run.ps1 interactive

# Test connection
.\run.ps1 ping

# View order history
.\run.ps1 db-history

# View trading statistics
.\run.ps1 db-stats
```

### Command Prompt (CMD) Commands

If you prefer CMD, use `run.bat`:

```cmd
REM View all available commands
run.bat help

REM Launch web UI
run.bat web

REM Launch interactive terminal UI
run.bat interactive

REM Test connection
run.bat ping
```

## 🌐 Web UI (Recommended)

The easiest way to use the bot on Windows:

```powershell
.\run.ps1 web
```

Then open your browser to: **http://localhost:5000**

Features:
- Modern dark theme interface
- Real-time price updates
- Visual order forms
- Order management
- Mobile-friendly

## 💻 Interactive Terminal UI

Beautiful menu-driven interface in your terminal:

```powershell
.\run.ps1 interactive
```

Navigate with number keys:
- 1 - Place Market Order
- 2 - Place Limit Order
- 3 - Place Stop Order
- 4 - Check Order Status
- 5 - Cancel Order
- 6 - View Symbol Info
- 7 - Test Connection
- 0 - Exit

## 📊 Database Features

View your trading history:

```powershell
# View all orders
.\run.ps1 db-history

# View activity logs
.\run.ps1 db-logs

# View statistics
.\run.ps1 db-stats
```

## 🧪 Testing

Run the test suite:

```powershell
.\run.ps1 test
```

Should show: `5 passed`

## 📝 Direct CLI Usage

For advanced users who want direct CLI access:

```powershell
# Test connection
poetry run python -m src.cli ping

# Place market order
poetry run python -m src.cli order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Place limit order
poetry run python -m src.cli order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 2000 --timeInForce GTC

# Check order status
poetry run python -m src.cli status --symbol BTCUSDT --orderId 123456789

# Cancel order
poetry run python -m src.cli cancel --symbol BTCUSDT --orderId 123456789
```

## 🔧 Troubleshooting

### "Execution Policy" Error

If you get an error about execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try again.

### "Poetry not found"

Install Poetry:

```powershell
pip install poetry
```

Or use the official installer:
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### "Python not found"

1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Restart PowerShell

### Port 5000 Already in Use

If web UI won't start:

```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

### Database Locked Error

If you get a database locked error:

```powershell
# Close all instances of the bot
# Delete the database file
del trading_bot.db

# Restart the bot
.\run.ps1 web
```

## 📁 File Locations

- **Database:** `trading_bot.db` (in project root)
- **Logs:** `logs/bot.log`
- **Config:** `.env` (create from `.env.example`)
- **Cache:** `exchange_info.json`

## 🎓 Tips for Windows Users

### 1. Use PowerShell (Not CMD)

PowerShell has better features and colors:
- Right-click folder → "Open in Windows Terminal"
- Or: `Win + X` → "Windows PowerShell"

### 2. Pin PowerShell to Taskbar

For quick access to your trading bot.

### 3. Create Desktop Shortcut

Create a shortcut with target:
```
powershell.exe -NoExit -Command "cd 'C:\path\to\ctbot'; .\run.ps1 web"
```

### 4. Use Windows Terminal

Download from Microsoft Store for better experience:
- Multiple tabs
- Better colors
- Split panes

### 5. Keep PowerShell Open

When running the web UI, keep PowerShell window open. Closing it stops the server.

## 🚀 Quick Reference

### Most Common Commands

```powershell
# Start web UI
.\run.ps1 web

# View order history
.\run.ps1 db-history

# View statistics
.\run.ps1 db-stats

# Test connection
.\run.ps1 ping

# Run tests
.\run.ps1 test
```

### Sample Trading Session

```powershell
# 1. Start the bot
.\run.ps1 web

# 2. Open browser to http://localhost:5000

# 3. Place some orders through the web UI

# 4. In another PowerShell window, view history:
.\run.ps1 db-history

# 5. View statistics:
.\run.ps1 db-stats
```

## 📞 Getting Help

If you encounter issues:

1. Check this guide
2. Read the error message carefully
3. Check `logs/bot.log` for details
4. Verify your API keys in `.env`
5. Test connection: `.\run.ps1 ping`

## ✅ Verification Checklist

Before submitting or using:

- [ ] Python 3.10+ installed
- [ ] Poetry installed
- [ ] Dependencies installed (`.\run.ps1 install`)
- [ ] `.env` file created with API keys
- [ ] Connection test passes (`.\run.ps1 ping`)
- [ ] Tests pass (`.\run.ps1 test`)
- [ ] Web UI starts (`.\run.ps1 web`)

## 🎉 You're Ready!

Your trading bot is fully functional on Windows. Enjoy trading on the testnet!

**Recommended workflow:**
1. `.\run.ps1 web` - Start web UI
2. Trade through browser
3. `.\run.ps1 db-stats` - Check your performance

Happy trading! 🚀
