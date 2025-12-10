"""
Slack API client for fetching thread messages.
"""

import requests
from urllib.parse import urlparse
from datetime import datetime
from typing import Optional


class SlackClient:
    """Client for interacting with Slack API."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {token}",
        }
    
    def parse_slack_url(self, url: str) -> tuple[str, str, Optional[str]]:
        """
        Parse a Slack URL to extract channel ID and message timestamp.
        
        Supports formats:
        - https://workspace.slack.com/archives/C01234567/p1234567890123456
        - https://workspace.slack.com/archives/C01234567/p1234567890123456?thread_ts=1234567890.123456
        """
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 3 or path_parts[0] != 'archives':
            raise ValueError(f"Invalid Slack URL format: {url}")
        
        channel_id = path_parts[1]
        message_id = path_parts[2]
        
        # Convert message ID (p1234567890123456) to timestamp (1234567890.123456)
        if message_id.startswith('p'):
            ts = message_id[1:]
            # Insert decimal point: 1234567890123456 -> 1234567890.123456
            if len(ts) > 6:
                thread_ts = f"{ts[:-6]}.{ts[-6:]}"
            else:
                thread_ts = ts
        else:
            thread_ts = message_id
        
        # Check for thread_ts in query params
        query_thread_ts = None
        if parsed.query:
            for param in parsed.query.split('&'):
                if param.startswith('thread_ts='):
                    query_thread_ts = param.split('=')[1]
                    break
        
        return channel_id, thread_ts, query_thread_ts
    
    def get_channel_info(self, channel_id: str) -> dict:
        """Get information about a channel."""
        response = requests.get(
            f"{self.base_url}/conversations.info",
            headers=self.headers,
            params={"channel": channel_id}
        )
        data = response.json()
        if not data.get("ok"):
            raise Exception(f"Failed to get channel info: {data.get('error', 'Unknown error')}")
        return data.get("channel", {})
    
    def get_user_info(self, user_id: str) -> dict:
        """Get information about a user."""
        response = requests.get(
            f"{self.base_url}/users.info",
            headers=self.headers,
            params={"user": user_id}
        )
        data = response.json()
        if not data.get("ok"):
            return {"name": user_id, "real_name": user_id}
        user = data.get("user", {})
        return {
            "name": user.get("name", user_id),
            "real_name": user.get("real_name", user.get("name", user_id))
        }
    
    def get_thread_messages(self, channel_id: str, thread_ts: str) -> list[dict]:
        """Fetch all messages from a Slack thread."""
        messages = []
        cursor = None
        
        while True:
            params = {
                "channel": channel_id,
                "ts": thread_ts,
                "limit": 100
            }
            if cursor:
                params["cursor"] = cursor
            
            response = requests.get(
                f"{self.base_url}/conversations.replies",
                headers=self.headers,
                params=params
            )
            data = response.json()
            
            if not data.get("ok"):
                # If thread not found, try to get single message
                if data.get("error") == "thread_not_found":
                    return self._get_single_message(channel_id, thread_ts)
                raise Exception(f"Failed to fetch thread: {data.get('error', 'Unknown error')}")
            
            messages.extend(data.get("messages", []))
            
            # Check for pagination
            cursor = data.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        return messages
    
    def _get_single_message(self, channel_id: str, ts: str) -> list[dict]:
        """Get a single message by timestamp."""
        response = requests.get(
            f"{self.base_url}/conversations.history",
            headers=self.headers,
            params={
                "channel": channel_id,
                "latest": ts,
                "oldest": ts,
                "inclusive": "true",
                "limit": 1
            }
        )
        data = response.json()
        if not data.get("ok"):
            raise Exception(f"Failed to fetch message: {data.get('error', 'Unknown error')}")
        return data.get("messages", [])
    
    def format_messages(self, messages: list[dict]) -> str:
        """Format messages into readable text for AI analysis."""
        formatted = []
        user_cache = {}
        
        for msg in messages:
            user_id = msg.get("user", "Unknown")
            if user_id not in user_cache:
                user_cache[user_id] = self.get_user_info(user_id)
            
            user_name = user_cache[user_id].get("real_name", user_id)
            timestamp = datetime.fromtimestamp(float(msg.get("ts", 0)))
            text = msg.get("text", "")
            
            # Handle attachments
            attachments = msg.get("attachments", [])
            for att in attachments:
                if att.get("text"):
                    text += f"\n[Attachment: {att.get('text')}]"
                if att.get("title"):
                    text += f"\n[Attachment Title: {att.get('title')}]"
            
            # Handle files
            files = msg.get("files", [])
            for f in files:
                text += f"\n[File: {f.get('name', 'unnamed')} - {f.get('mimetype', 'unknown type')}]"
            
            formatted.append(f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] {user_name}:\n{text}\n")
        
        return "\n".join(formatted)
