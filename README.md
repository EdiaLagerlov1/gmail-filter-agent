# Gmail Filter Agent Builder

A Claude Code agent configuration for building production-ready Gmail filtering applications using Google's Agent Development Kit (ADK).

## Overview

This agent automates the creation of complete Gmail filtering applications that can:
- Filter emails using natural language queries
- Extract currency amounts from email content
- Export filtered results to CSV
- Be distributed as standalone executables for non-technical users

## What This Agent Does

The `gmail-filter-agent-builder` agent is a specialized AI assistant that systematically creates a full-stack Gmail filtering application with:

### Core Features
- 📧 **Gmail API Integration** - OAuth 2.0 authentication with read-only access
- 🔍 **Natural Language Processing** - Convert plain English filters to Gmail query syntax
- 💰 **Amount Extraction** - Parse and filter emails by currency amounts
- 📊 **CSV Export** - Export filtered emails with comprehensive metadata
- 📦 **Executable Distribution** - Build standalone apps using PyInstaller

### Technical Implementation
- **Framework**: Google Agent Development Kit (ADK)
- **Model**: gemini-2.0-flash-001
- **Language**: Python 3.10+
- **API**: Gmail API (read-only scope)
- **Build System**: PyInstaller for cross-platform executables

## Usage

### Prerequisites
- Claude Code CLI
- Access to Claude AI

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/EdiaLagerlov1/gmail-filter-agent.git
   cd gmail-filter-agent
   ```

2. Copy the agent configuration to your Claude Code agents directory:
   ```bash
   mkdir -p ~/.claude/agents
   cp .claude/agents/gmail-filter-agent-builder.md ~/.claude/agents/
   ```

### Using the Agent

In Claude Code, invoke the agent with:

```
@gmail-filter-agent-builder Please build a complete Gmail filtering application
```

The agent will create a complete project with:
- Python application code
- Gmail API integration tools
- Natural language to Gmail query converter
- Amount extraction and filtering logic
- CSV export functionality
- PyInstaller build configuration
- Comprehensive documentation

## What Gets Created

When you run this agent, it builds a complete project structure:

```
gmail-filter-app/
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore patterns
├── agent.py                   # Main ADK agent configuration
├── build.py                   # PyInstaller build script
├── tools/
│   ├── __init__.py
│   ├── gmail_tools.py        # Gmail API operations
│   ├── parser_tools.py       # Amount extraction
│   └── export_tools.py       # CSV export
├── csv_files/                 # Output directory
├── README.md                  # Technical documentation
├── README.txt                 # User quick-start guide
├── USER_INSTRUCTIONS.txt      # Detailed user manual
└── BUILD_INSTRUCTIONS.md      # Distribution guide
```

## Agent Capabilities

### 1. Gmail Query Conversion
Converts natural language to Gmail query operators:
- "emails from john@example.com last week" → `from:john@example.com after:YYYY/MM/DD`
- "invoices with attachments" → `subject:invoice has:attachment`
- "receipts in the last 30 days" → `subject:receipt after:YYYY/MM/DD`

### 2. Amount Extraction
Detects and filters by currency amounts:
- Supports: $, €, £, ¥, USD, EUR, GBP, JPY
- Formats: $100, $1,000.00, 100 USD, etc.
- Filter by min/max amounts

### 3. CSV Export
Generates structured CSV files with:
- ID, Date, From, To, Subject
- Email snippet
- Labels and attachments status
- Detected amounts
- Timestamped filenames

### 4. Executable Distribution
Creates standalone executables for:
- Windows (.exe)
- macOS (Unix executable)
- Linux (Unix executable)

## Example Prompts

Ask the agent to build applications like:

```
"Build a Gmail filter app that finds all invoices over $100 from the last 3 months"

"Create an expense tracker that extracts receipts with amounts from my Gmail"

"Build an executable that lets users search emails by natural language and export to CSV"
```

## Security & Privacy

The agent creates applications that:
- ✅ Use **read-only** Gmail API access (cannot send/delete emails)
- ✅ Process data **locally** (no external API calls)
- ✅ Require **user OAuth authentication** (each user has their own credentials)
- ✅ Follow security best practices (credentials never committed to Git)

## Requirements for Generated Applications

Applications created by this agent require:
- Python 3.10+
- Google Cloud project with Gmail API enabled
- OAuth 2.0 Desktop credentials (credentials.json)
- Dependencies listed in generated requirements.txt

## Documentation

The agent generates three levels of documentation:

1. **README.md** - Technical documentation for developers
2. **README.txt** - Quick-start guide (50 lines max, simple language)
3. **USER_INSTRUCTIONS.txt** - Step-by-step guide for non-technical users
4. **BUILD_INSTRUCTIONS.md** - How to build and distribute

## Contributing

Contributions to improve the agent are welcome! Please submit pull requests or issues.

## License

MIT License - See LICENSE file for details

## Author

Created as a specialized Claude Code agent for building Gmail filtering applications.

## Acknowledgments

- Built for use with [Claude Code](https://claude.com/claude-code)
- Uses [Google Agent Development Kit (ADK)](https://github.com/google/adk)
- Integrates with [Gmail API](https://developers.google.com/gmail/api)

---

**Note:** This repository contains the agent configuration, not the Gmail filtering application itself. The agent builds the application when invoked in Claude Code.
