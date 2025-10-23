# Gmail Filter Agent - Setup Instructions

Complete guide to setting up and using the Gmail Filter Agent application.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google Cloud Setup](#google-cloud-setup)
3. [Installation](#installation)
4. [First Run](#first-run)
5. [Usage Examples](#usage-examples)
6. [Building Executable](#building-executable)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **Operating System**: macOS, Linux, or Windows
- **Internet Connection**: Required for Gmail API access
- **Google Account**: With Gmail enabled

### Required Software
- Python 3.10+
- pip (Python package manager)
- Git (optional, for cloning)

---

## Google Cloud Setup

**⚠️ CRITICAL:** You must create your own Google Cloud credentials. Each user needs their own `credentials.json` file.

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: "Gmail Filter Agent" (or any name you prefer)
4. Click **"Create"**
5. Wait for project creation to complete

### Step 2: Enable Gmail API

1. Ensure your new project is selected (check top bar)
2. Navigate to **"APIs & Services"** → **"Library"**
3. Search for **"Gmail API"**
4. Click on "Gmail API" in results
5. Click **"Enable"** button
6. Wait for API to be enabled

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type
3. Click **"Create"**

**App Information:**
4. Enter **App name**: "Gmail Filter Agent" (or your choice)
5. Enter **User support email**: Your email address
6. Enter **Developer contact email**: Your email address
7. Click **"Save and Continue"**

**Scopes:**
8. Click **"Add or Remove Scopes"**
9. Search for "gmail"
10. Select: `https://www.googleapis.com/auth/gmail.readonly`
11. Click **"Update"**
12. Click **"Save and Continue"**

**Test Users:**
13. Click **"+ ADD USERS"**
14. Enter your Gmail address (the one you'll use with the app)
15. Click **"Add"**
16. Click **"Save and Continue"**

**Summary:**
17. Review your settings
18. Click **"Back to Dashboard"**

### Step 4: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"**
3. Select **"OAuth client ID"**
4. Choose application type: **"Desktop app"**
5. Enter name: "Gmail Filter Agent Client" (or your choice)
6. Click **"Create"**

**Download Credentials:**
7. A dialog appears with your Client ID and Client Secret
8. Click **"Download JSON"** (download icon on the right)
9. The file will be named something like `client_secret_XXXXX.json`
10. **Rename this file to `credentials.json`**
11. **Important:** Keep this file secure and never share it

### Step 5: Place Credentials File

1. Move `credentials.json` to the project root directory:
   ```
   gmail-filter-agent/
   ├── credentials.json  ← Place here
   ├── agent.py
   ├── tools/
   └── ...
   ```

**Security Note:** `credentials.json` is already in `.gitignore` and will NOT be committed to Git.

---

## Installation

### 1. Clone or Download Repository

**Option A: Using Git**
```bash
git clone https://github.com/EdiaLagerlov1/gmail-filter-agent.git
cd gmail-filter-agent
```

**Option B: Download ZIP**
1. Download from GitHub
2. Extract the archive
3. Open terminal in the extracted folder

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `google-adk` - Google Agent Development Kit
- `google-auth-oauthlib` - OAuth authentication
- `google-auth-httplib2` - HTTP library
- `google-api-python-client` - Gmail API client
- `pandas` - Data manipulation for CSV export
- `pyinstaller` - For building executables

### 4. Verify Installation

```bash
python -c "import google_adk; print('ADK installed successfully')"
```

If successful, you'll see: `ADK installed successfully`

---

## First Run

### 1. Ensure Credentials are in Place

```bash
# Check if credentials.json exists
ls credentials.json
```

If not found, review [Step 5: Place Credentials File](#step-5-place-credentials-file)

### 2. Run the Agent

```bash
python agent.py
```

### 3. Browser Authentication (First Time Only)

**What happens:**
1. A browser window opens automatically
2. You're redirected to Google sign-in

**Steps to complete:**
1. **Sign in** with your Google account (the one added as test user)
2. You may see **"This app isn't verified"**:
   - This is normal for apps in testing mode
   - Click **"Advanced"**
   - Click **"Go to Gmail Filter Agent (unsafe)"**
   - This is safe - it's YOUR app
3. Review permissions:
   - "View your email messages and settings"
   - This is read-only access
4. Click **"Allow"**
5. Browser may show "localhost" page or redirect - this is OK
6. Return to your terminal

**Token Saved:**
After successful authentication, `token.json` is created and saved. Future runs won't require re-authentication.

### 4. Interact with the Agent

Once authenticated, you can enter queries like:

```
Find all emails from john@example.com in the last week

Show me invoices with amounts over $100

Export receipts from the last 30 days
```

The agent will:
1. Convert your query to Gmail search syntax
2. Fetch matching emails
3. Extract amounts (if requested)
4. Export to CSV in `csv_files/` directory
5. Show you a summary

---

## Usage Examples

### Basic Searches

**By Sender:**
```
Find emails from support@company.com
```

**By Date Range:**
```
Show emails from the last 7 days
Get messages between 2024-01-01 and 2024-01-31
```

**By Subject:**
```
Find invoices
Search for receipts
```

**With Attachments:**
```
Emails with PDF attachments
Messages with attachments from last month
```

### Amount Filtering

**Minimum Amount:**
```
Find invoices over $500
Receipts with amounts greater than 100 EUR
```

**Amount Range:**
```
Invoices between $100 and $1000
Payments from $50 to $500
```

**Specific Amounts:**
```
Find emails with exactly $99.99
```

### Combined Filters

```
Find invoices from vendor@company.com over $1000 in the last 30 days

Get receipts with PDF attachments from January 2024

Show me payment confirmations with amounts between €50 and €500
```

### Export Options

**Default (Always Exports to CSV):**
The agent automatically exports results to:
```
csv_files/filtered_emails_YYYYMMDD_HHMMSS.csv
```

**View CSV:**
```bash
# On macOS
open csv_files/filtered_emails_*.csv

# On Linux
xdg-open csv_files/filtered_emails_*.csv

# On Windows
start csv_files\filtered_emails_*.csv
```

---

## Building Executable

### Create Standalone Executable

Run the build script:

```bash
python build.py
```

**What happens:**
1. PyInstaller bundles the application
2. Creates a single executable file
3. Includes all dependencies
4. Places executable in `dist/` folder

**Output locations:**
- **macOS/Linux**: `dist/gmail_filter_agent`
- **Windows**: `dist/gmail_filter_agent.exe`

### Distribute the Executable

**Package contents:**
1. The executable from `dist/`
2. `credentials.json.example` (as a template)
3. `README.txt` (user instructions)
4. `csv_files/` folder (empty, for outputs)

**Recipients must:**
1. Create their own `credentials.json` (following this guide)
2. Place it next to the executable
3. Run the executable
4. Complete OAuth authentication on first run

---

## Troubleshooting

### Common Issues

#### "credentials.json not found"

**Solution:**
- Ensure `credentials.json` is in the project root
- Check filename is exactly `credentials.json` (not `client_secret_XXX.json`)
- Verify file is not empty

#### "This app isn't verified"

**This is normal!**
- Your app is in testing mode
- Click "Advanced" → "Go to [app name] (unsafe)"
- Only you and test users can access it
- It's safe because it's YOUR app

#### "Access blocked: Authorization Error"

**Cause:** Your email isn't added as a test user

**Solution:**
1. Go to OAuth consent screen in Google Cloud Console
2. Under "Test users", click "+ ADD USERS"
3. Add your Gmail address
4. Wait 5 minutes for changes to propagate
5. Delete `token.json` if it exists
6. Try authenticating again

#### "No module named 'google_adk'"

**Solution:**
```bash
pip install -r requirements.txt
```

Or specifically:
```bash
pip install google-adk
```

#### Browser doesn't open

**Solution 1: Manual URL**
1. Look for a URL in the terminal starting with `https://accounts.google.com/o/oauth2/auth?...`
2. Copy the entire URL
3. Paste it in your browser
4. Complete authentication
5. Copy the redirect URL (starting with `http://localhost`) from your browser
6. Paste it back in the terminal when prompted

**Solution 2: Check default browser**
- Ensure you have a default browser set
- Try running with a specific browser open

#### "Invalid grant" or "Token expired"

**Solution:**
1. Delete `token.json`
   ```bash
   rm token.json
   ```
2. Run the agent again
3. Re-authenticate in the browser

#### CSV file is empty

**Check:**
1. Did the search find any emails? (check terminal output)
2. Look in `csv_files/` directory for the file
3. Check file permissions

#### Amount extraction not working

**Ensure amounts are in supported formats:**
- ✅ $100, $1,000.00, $1,000,000
- ✅ €50, £25, ¥1000
- ✅ 100 USD, 50.00 EUR
- ❌ "one hundred dollars" (not supported)

---

## Advanced Configuration

### Changing the Model

Edit `agent.py`:
```python
agent = LlmAgent(
    model="gemini-2.0-flash-001",  # Change this
    # ...
)
```

Available models:
- `gemini-2.0-flash-001` (default, fast)
- `gemini-1.5-pro-latest` (more capable)

### Increasing Email Limit

By default, searches return up to 100 emails. To change:

Edit `tools/gmail_tools.py`:
```python
max_results = 500  # Change from 100
```

### Custom CSV Columns

Edit `tools/export_tools.py` to customize CSV output format.

---

## Security Best Practices

### DO:
✅ Keep `credentials.json` private
✅ Use read-only Gmail scope
✅ Review OAuth permissions before granting
✅ Revoke access if suspicious activity detected

### DON'T:
❌ Share `credentials.json` with others
❌ Commit `credentials.json` to Git
❌ Request more permissions than needed
❌ Use on untrusted devices

### Revoking Access

1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find "Gmail Filter Agent"
3. Click "Remove Access"
4. Delete `token.json` from your local machine

---

## Getting Help

**Documentation:**
- [README.md](README.md) - Overview and quick start
- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) - Building executables

**Google Resources:**
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)

**Issues:**
- Check existing issues on GitHub
- Create new issue with:
  - Error message (remove sensitive info)
  - Steps to reproduce
  - Your OS and Python version

---

## Next Steps

After successful setup:

1. **Test with simple query**: "Find emails from today"
2. **Try filtering**: "Invoices over $100"
3. **Check CSV output**: Open file in `csv_files/`
4. **Build executable** (optional): Run `python build.py`
5. **Share with others** (optional): Package executable + instructions

Enjoy filtering your Gmail! 📧✨
