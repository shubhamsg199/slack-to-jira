"""
Jira client for creating issues.
"""

from typing import Optional
from jira import JIRA


class JiraClient:
    """Client for creating Jira issues using the jira library."""
    
    def __init__(self, server: str, token: str):
        self.server = server.rstrip('/')
        self.token = token
    
    def _get_jira(self) -> JIRA:
        """Create fresh authenticated JIRA connection."""
        return JIRA(server=self.server, token_auth=self.token)
    
    def create_issue(
        self,
        project_key: str,
        title: str,
        summary: str,
        issue_type: str = "Task",
        priority: Optional[str] = None,
        slack_url: Optional[str] = None,
        extra_fields: Optional[dict] = None
    ) -> dict:
        """Create a Jira issue with fallback for restricted fields."""
        
        # Build description with Slack reference
        description = summary
        if slack_url:
            description += f"\n\n----\n*Source:* Created from Slack discussion: {slack_url}"
        
        # Create fresh JIRA client (like working script does)
        jira = self._get_jira()
        
        # Try creating with full fields first
        issue_dict = {
            "project": {"key": project_key},
            "summary": title[:255],
            "description": description,
            "issuetype": {"name": issue_type}
        }
        
        try:
            issue = jira.create_issue(fields=issue_dict)
            return {"key": issue.key, "id": issue.id, "self": issue.self}
        except Exception as e:
            error_msg = str(e)
            # Check if error is about fields not being on screen
            if "cannot be set" in error_msg or "not on the appropriate screen" in error_msg:
                print("   ⚠️  Standard fields restricted, using minimal creation...")
                return self._create_minimal_issue(
                    project_key, issue_type, title, description, priority
                )
            raise
    
    def _create_minimal_issue(
        self,
        project_key: str,
        issue_type: str,
        title: str,
        description: str,
        priority: Optional[str] = None
    ) -> dict:
        """Create issue with only project/issuetype, add details as comment."""
        
        # Create fresh JIRA client
        jira = self._get_jira()
        
        # Create with minimal fields
        minimal_dict = {
            "project": {"key": project_key},
            "issuetype": {"name": issue_type}
        }
        
        issue = jira.create_issue(fields=minimal_dict)
        
        # Build comment with all the details
        comment_text = f"h3. {title}\n\n{description}"
        if priority:
            comment_text += f"\n\n*Suggested Priority:* {priority}"
        
        # Add as comment
        jira.add_comment(issue, comment_text)
        
        return {"key": issue.key, "id": issue.id, "self": issue.self}
