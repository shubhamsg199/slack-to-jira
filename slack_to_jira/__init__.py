"""
Slack to Jira Issue Creator

A tool that fetches Slack thread discussions, analyzes them with AI,
and creates Jira issues automatically.
"""

from .converter import SlackToJira
from .slack_client import SlackClient
from .ai_analyzer import GroqAnalyzer
from .jira_client import JiraClient

__all__ = [
    "SlackToJira",
    "SlackClient",
    "GroqAnalyzer",
    "JiraClient",
]

__version__ = "1.0.0"
