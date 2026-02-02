# OpenClaw Doctor 🩺

[![PyPI version](https://badge.fury.io/py/openclaw-doctor.svg)](https://badge.fury.io/py/openclaw-doctor)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A CLI tool to diagnose, validate, and auto-fix [OpenClaw](https://github.com/openclaw/openclaw) AI assistant installations.

```
╭─────────────────────────────────────────────────────────╮
│                   OpenClaw Doctor 🩺                    │
│           Diagnosing your OpenClaw installation         │
╰─────────────────────────────────────────────────────────╯

[✓] Node.js v20.10.0 installed
[✓] OpenClaw v1.2.3 installed
[✓] Docker 24.0.7 running
[✓] System requirements met (8GB RAM, 50GB free)
[✓] Folder structure OK
[✓] Configuration valid
[!] API key missing for Anthropic
[✓] Network connectivity OK
[✓] No errors in logs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary: 8 passed, 1 warning, 0 failed
```

## ✨ Features

- 🔍 **9 Comprehensive Health Checks** - Everything from Node.js to network connectivity
- 🔧 **Auto-Fix Capabilities** - Automatically resolve common issues
- 💡 **Smart Suggestions** - Plain language explanations and solutions
- 📋 **Log Parsing** - Finds errors in logs and explains them simply
- 🎨 **Beautiful Output** - Rich terminal UI with colors and icons
- 📊 **JSON Output** - CI/CD friendly format

## 📦 Installation

```bash
pip install openclaw-doctor
```

Or install from source:

```bash
git clone https://github.com/Okediya/openclaw-doctor.git
cd openclaw-doctor
pip install -e .
```

## 🚀 Quick Start

```bash
# Run all health checks
openclaw-doctor

# Run with auto-fix
openclaw-doctor --fix

# Show detailed output
openclaw-doctor --verbose
```

## 📋 Commands

### Run All Checks

```bash
openclaw-doctor
```

### Run with Auto-Fix

Automatically fix issues where possible:

```bash
openclaw-doctor --fix
```

### Run Specific Check

```bash
openclaw-doctor check nodejs
openclaw-doctor check docker
openclaw-doctor check config
openclaw-doctor check logs
```

### List All Available Checks

```bash
openclaw-doctor list-checks
```

### Other Options

```bash
# Verbose output with details
openclaw-doctor --verbose

# JSON output for CI/CD
openclaw-doctor --json

# Show version
openclaw-doctor --version

# Get help
openclaw-doctor --help
```

## 🔍 Health Checks

| Check | What it Verifies | Auto-Fix |
|-------|------------------|----------|
| **Node.js** | Node.js >= 18.x installed | ✅ Install guide |
| **OpenClaw** | OpenClaw CLI installation | ✅ Runs install script |
| **Docker** | Docker & Docker Compose (optional) | 💡 Suggestions |
| **System** | RAM (2GB+), Disk (20GB+), CPU cores | 💡 Suggestions |
| **Folders** | ~/.openclaw/, skills/, channels/, workspaces/ | ✅ Creates directories |
| **Config** | config.yaml syntax and required fields | ✅ Creates default |
| **API Keys** | Environment vars, .env files, config files | ✅ Setup wizard |
| **Network** | Connectivity to AI provider APIs | 💡 Suggestions |
| **Logs** | Parses logs for errors with explanations | 💡 Detailed analysis |

## 📝 Log Error Detection

The Logs check parses OpenClaw logs and explains errors in plain language:

| Error Type | What You'll See |
|------------|-----------------|
| **Rate Limits** | "You've made too many API calls. Wait 60 seconds or upgrade your plan." |
| **Auth Failures** | "Your API key is invalid or expired. Get a new key from your provider." |
| **Connection Issues** | "Could not connect to the server. Check your internet connection." |
| **Config Errors** | "Your config file has invalid YAML syntax. Use a validator to find errors." |
| **Permission Denied** | "OpenClaw doesn't have permission to access this file." |
| **Out of Memory** | "The system ran out of memory. Close other applications." |
| **Model Errors** | "The specified AI model doesn't exist or isn't available." |

Run `openclaw-doctor check logs --fix` for detailed error analysis!

## 🔧 Configuration Locations

OpenClaw Doctor checks these locations:

| Type | Paths Checked |
|------|---------------|
| **Home Directory** | `~/.openclaw/`, `~/.config/openclaw/` |
| **Config Files** | `config.yaml`, `config.yml`, `config.json` |
| **Environment Files** | `.env` in OpenClaw dirs or current directory |
| **Log Files** | `~/.openclaw/logs/` |
| **Windows** | `%APPDATA%\Local\openclaw\` |

## 🤖 CI/CD Integration

Use JSON output for automated pipelines:

```bash
openclaw-doctor --json
```

Example output:

```json
{
  "version": "0.1.0",
  "checks": [
    {
      "name": "Node.js",
      "status": "pass",
      "message": "Node.js v20.10.0 installed"
    }
  ],
  "summary": {
    "passed": 8,
    "warnings": 1,
    "failed": 0
  }
}
```

Exit codes:
- `0` - All checks passed
- `1` - One or more checks failed

## 🛠️ Development

```bash
# Clone the repo
git clone https://github.com/Okediya/openclaw-doctor.git
cd openclaw-doctor

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=openclaw_doctor
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [OpenClaw](https://github.com/openclaw/openclaw) - The AI assistant this tool supports
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output
