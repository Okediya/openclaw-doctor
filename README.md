# OpenClaw Doctor 🩺

A CLI tool to diagnose, validate, and auto-fix [OpenClaw](https://github.com/openclaw/openclaw) AI assistant installations.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- ✅ **Comprehensive Health Checks** - Node.js, Docker, system resources, config, API keys, network
- 🔧 **Auto-Fix Capabilities** - Automatically resolve common issues
- 💡 **Smart Suggestions** - Helpful guidance for issues that can't be auto-fixed
- 🎨 **Beautiful Output** - Rich terminal UI with colors and status indicators
- 📊 **JSON Output** - CI/CD friendly output format

## Installation

```bash
pip install openclaw-doctor
```

Or install from source:

```bash
git clone https://github.com/openclaw-community/openclaw-doctor.git
cd openclaw-doctor
pip install -e .
```

## Usage

### Run All Checks

```bash
openclaw-doctor
```

### Run with Auto-Fix

```bash
openclaw-doctor --fix
```

### Run Specific Check

```bash
openclaw-doctor check nodejs
openclaw-doctor check docker
openclaw-doctor check config
```

### Other Options

```bash
# Verbose output
openclaw-doctor -v

# JSON output (for CI/CD)
openclaw-doctor --json

# Show version
openclaw-doctor --version
```

## Health Checks

| Check | Description | Auto-Fix |
|-------|-------------|----------|
| **Node.js** | Verifies Node.js >= 18.x is installed | ✅ Installation guide |
| **OpenClaw** | Checks OpenClaw CLI installation | ✅ Runs install script |
| **Docker** | Validates Docker & Compose setup | 💡 Suggestions |
| **System** | RAM (2GB+), Disk (20GB+), CPU | 💡 Suggestions |
| **Config** | Validates OpenClaw configuration | ✅ Creates default |
| **API Keys** | Checks AI provider keys configured | ✅ Interactive setup |
| **Network** | Tests connectivity to AI providers | 💡 Suggestions |

## Example Output

```
╭─────────────────────────────────────────────────────────╮
│                   OpenClaw Doctor 🩺                    │
│           Diagnosing your OpenClaw installation         │
╰─────────────────────────────────────────────────────────╯

[✓] Node.js v20.10.0 installed
[✓] OpenClaw v1.2.3 installed
[✓] Docker 24.0.7 running
[✓] System requirements met (8GB RAM, 50GB free)
[✓] Configuration valid
[!] API key missing for Anthropic
[✓] Network connectivity OK

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary: 6 passed, 1 warning, 0 failed

To fix issues, run: openclaw-doctor --fix
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.
