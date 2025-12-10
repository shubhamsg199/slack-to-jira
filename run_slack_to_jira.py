#!/usr/bin/env python3
"""
Slack Thread to Jira Issue Creator

A standalone tool that:
1. Fetches messages from a Slack thread
2. Uses Groq AI (FREE) to analyze and generate title/summary
3. Creates a Jira issue automatically

Usage:
    python run_slack_to_jira.py <slack_thread_url>
    
Example:
    python run_slack_to_jira.py "https://myworkspace.slack.com/archives/C01234567/p1234567890123456"

Configuration:
    Edit slack_to_jira/config.py to set your credentials.
"""

from slack_to_jira.cli import main

if __name__ == "__main__":
    main()
