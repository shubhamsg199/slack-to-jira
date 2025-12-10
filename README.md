# Slack to Jira Issue Creator

Automatically create Jira issues from Slack thread discussions using AI-powered analysis.

## ✨ Features

- **Fetch Slack Threads** — Extracts all messages from a Slack thread URL
- **AI-Powered Analysis** — Uses Groq AI (free & fast) to generate meaningful titles and descriptions
- **Auto-Create Jira Issues** — Creates issues with proper formatting and links back to the Slack thread
- **Smart Fallbacks** — Handles restricted Jira fields gracefully
- **Dry Run Mode** — Preview what would be created before actually creating

## 📁 Project Structure

```
jira-slack/
├── config.py                 # Configuration (credentials go here)
├── requirements.txt          # Python dependencies
├── run_slack_to_jira.py      # Entry point script
└── slack_to_jira/            # Main package
    ├── __init__.py
    ├── ai_analyzer.py        # Groq AI integration
    ├── cli.py                # Command-line interface
    ├── converter.py          # Main orchestrator
    ├── jira_client.py        # Jira API client
    └── slack_client.py       # Slack API client
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /path/to/jira-slack
pip install -r requirements.txt
```

### 2. Configure Credentials

Edit `config.py` with your credentials:

```python
# Slack Bot Token (get from https://api.slack.com/apps)
SLACK_BOT_TOKEN = "xoxb-your-token-here"

# Jira Configuration
JIRA_BASE_URL = "https://your-jira-instance.atlassian.net"
JIRA_API_TOKEN = "your-jira-api-token"
JIRA_PROJECT_KEY = "TEST"  # e.g., "SAT", "IT", "OPS"
JIRA_ISSUE_TYPE = "task"      # task, bug, story, etc.

# Groq AI (FREE - get from https://console.groq.com/keys)
GROQ_API_KEY = "gsk_your-groq-key"
```

### 3. Run

```bash
python run_slack_to_jira.py "<slack-thread-url>"
```
## Example
```bash
python run_slack_to_jira.py "https://test.slack.com/archives/K0B2GK3URC3/p1765759151825349"
```

## 📖 Usage

### Basic Usage

```bash
python run_slack_to_jira.py "<slack-thread-url>"
```

### Options

| Option | Description |
|--------|-------------|
| `-p, --project` | Override default Jira project key |
| `-t, --type` | Override issue type (Bug, Task, Story, Improvement) |
| `--dry-run` | Preview without creating the issue |
| `--json` | Output result as JSON |

### Examples

```bash
# Create issue from Slack thread
python run_slack_to_jira.py "https://myworkspace.slack.com/archives/C0123/p1234567890"

# Preview what would be created (dry run)
python run_slack_to_jira.py --dry-run "https://..."

# Override project and issue type
python run_slack_to_jira.py -p MYPROJECT -t bug "https://..."

# Get JSON output
python run_slack_to_jira.py --json "https://..."
```

## 🔑 Getting API Keys

### Slack Bot Token

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Create a new app or select existing
3. Navigate to **OAuth & Permissions**
4. Add these Bot Token Scopes:
   - `channels:history`
   - `channels:read`
   - `users:read`
5. Install the app to your workspace
6. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

### Jira API Token

1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Copy the generated token

### Groq API Key (FREE)

1. Go to [Groq Console](https://console.groq.com/keys)
2. Sign up for a free account
3. Create an API key
4. Copy the key (starts with `gsk_`)

## 🤖 How It Works

1. **Parse URL** — Extracts channel ID and thread timestamp from Slack URL
2. **Fetch Messages** — Retrieves all messages in the thread via Slack API
3. **AI Analysis** — Sends conversation to Groq AI (Llama 3.1) to generate:
   - Concise issue title
   - Detailed description with context
   - Suggested issue type and priority
4. **Create Issue** — Creates the Jira issue with the generated content
5. **Add Source Link** — Includes a link back to the original Slack thread

## 📝 Output Example

```
🔗 Processing Slack URL: https://workspace.slack.com/archives/C0123/p1234567890

📋 Parsing Slack URL...
   Channel: C0123, Thread: 1234567890.123456
   Channel name: #engineering

💬 Fetching thread messages...
   Found 5 message(s)
   Thread content: 1234 characters

🤖 Analyzing thread with Groq AI...
   Generated title: Fix authentication timeout in production
   Suggested type: Bug
   Suggested priority: Major

🎫 Creating Jira issue in project SAT...

✅ Successfully created: SAT-1234
   URL: https://jira.example.com/browse/SAT-1234
```

## 🐛 Troubleshooting

### "Anonymous users do not have permission"
- Check that your `JIRA_API_TOKEN` is correct
- Ensure the token has permissions to create issues in the project

### "Field cannot be set"
- The tool automatically handles restricted fields by using minimal creation
- Details are added as comments when fields are restricted

### Slack API errors
- Verify your `SLACK_BOT_TOKEN` is valid
- Ensure the bot is added to the channel you're trying to read

## 📄 License

MIT License

