"""
Main orchestrator for Slack to Jira conversion.
"""

import sys
from typing import Optional

from config import (
    SLACK_BOT_TOKEN,
    JIRA_BASE_URL,
    JIRA_API_TOKEN,
    JIRA_PROJECT_KEY,
    JIRA_ISSUE_TYPE,
    GROQ_API_KEY,
)
from .slack_client import SlackClient
from .ai_analyzer import GroqAnalyzer
from .jira_client import JiraClient


class SlackToJira:
    """Main orchestrator for Slack to Jira conversion."""
    
    def __init__(self):
        # Use configuration from config module
        self.slack_token = SLACK_BOT_TOKEN
        self.jira_url = JIRA_BASE_URL
        self.jira_token = JIRA_API_TOKEN
        self.jira_project = JIRA_PROJECT_KEY
        self.groq_key = GROQ_API_KEY
        self.default_issue_type = JIRA_ISSUE_TYPE
        
        self._validate_config()
        
        # Initialize clients
        self.slack = SlackClient(self.slack_token)
        self.ai = GroqAnalyzer(self.groq_key)
        self.jira = JiraClient(self.jira_url, self.jira_token)
    
    def _validate_config(self):
        """Validate required configuration."""
        missing = []
        if not self.slack_token or self.slack_token == "YOUR_SLACK_BOT_TOKEN_HERE":
            missing.append("SLACK_BOT_TOKEN")
        if not self.jira_url or self.jira_url == "YOUR_JIRA_URL_HERE":
            missing.append("JIRA_BASE_URL")
        if not self.jira_token or self.jira_token == "YOUR_JIRA_API_TOKEN_HERE":
            missing.append("JIRA_API_TOKEN")
        if not self.jira_project or self.jira_project == "YOUR_PROJECT_KEY":
            missing.append("JIRA_PROJECT_KEY")
        if not self.groq_key or self.groq_key == "YOUR_GROQ_API_KEY_HERE":
            missing.append("GROQ_API_KEY")
        
        if missing:
            print("Error: Missing required configuration. Please edit config.py and set:")
            for var in missing:
                print(f"  - {var}")
            print("\nGet your FREE Groq API key from: https://console.groq.com/keys")
            sys.exit(1)
    
    def process(
        self,
        slack_url: str,
        project_key: Optional[str] = None,
        issue_type: Optional[str] = None,
        dry_run: bool = False
    ) -> dict:
        """
        Process a Slack URL and create a Jira issue.
        
        Args:
            slack_url: The Slack thread URL
            project_key: Override default Jira project
            issue_type: Override issue type
            dry_run: If True, don't create the issue, just show what would be created
        
        Returns:
            dict with issue details and status
        """
        project = project_key or self.jira_project
        
        print(f"\n🔗 Processing Slack URL: {slack_url}")
        
        # Parse Slack URL
        print("📋 Parsing Slack URL...")
        channel_id, thread_ts, _ = self.slack.parse_slack_url(slack_url)
        print(f"   Channel: {channel_id}, Thread: {thread_ts}")
        
        # Get channel info
        try:
            channel_info = self.slack.get_channel_info(channel_id)
            channel_name = channel_info.get("name", "unknown")
            print(f"   Channel name: #{channel_name}")
        except Exception as e:
            channel_name = "unknown"
            print(f"   Could not get channel name: {e}")
        
        # Fetch thread messages
        print("💬 Fetching thread messages...")
        messages = self.slack.get_thread_messages(channel_id, thread_ts)
        print(f"   Found {len(messages)} message(s)")
        
        if not messages:
            raise Exception("No messages found in thread")
        
        # Format messages for analysis
        thread_content = self.slack.format_messages(messages)
        print(f"   Thread content: {len(thread_content)} characters")
        
        # Analyze with Groq
        print("🤖 Analyzing thread with Groq AI...")
        analysis = self.ai.analyze_thread(thread_content, channel_name)
        print(f"   Generated title: {analysis.get('title', 'N/A')}")
        print(f"   Suggested type: {analysis.get('issue_type', 'N/A')}")
        print(f"   Suggested priority: {analysis.get('priority', 'N/A')}")
        
        # Prepare issue details
        final_issue_type = issue_type or analysis.get("issue_type", self.default_issue_type)
        
        if dry_run:
            print("\n📝 DRY RUN - Would create issue:")
            print(f"   Project: {project}")
            print(f"   Type: {final_issue_type}")
            print(f"   Title: {analysis.get('title')}")
            print(f"   Priority: {analysis.get('priority')}")
            print(f"\n   Description:\n{'-' * 40}")
            print(analysis.get("summary", "No summary generated"))
            print(f"{'-' * 40}")
            return {
                "dry_run": True,
                "would_create": {
                    "project": project,
                    "type": final_issue_type,
                    "title": analysis.get("title"),
                    "summary": analysis.get("summary"),
                    "priority": analysis.get("priority")
                }
            }
        
        # Create Jira issue
        print(f"🎫 Creating Jira issue in project {project}...")
        issue = self.jira.create_issue(
            project_key=project,
            title=analysis.get("title", "Issue from Slack"),
            summary=analysis.get("summary", thread_content[:5000]),
            issue_type=final_issue_type,
            priority=analysis.get("priority"),
            slack_url=slack_url
        )
        
        issue_key = issue.get("key")
        issue_url = f"{self.jira_url}/browse/{issue_key}"
        
        print(f"\n✅ Successfully created: {issue_key}")
        print(f"   URL: {issue_url}")
        
        return {
            "success": True,
            "issue_key": issue_key,
            "issue_url": issue_url,
            "title": analysis.get("title"),
            "issue_type": final_issue_type,
            "priority": analysis.get("priority")
        }
