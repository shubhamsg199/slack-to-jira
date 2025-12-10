"""
AI analyzer using Groq to analyze Slack discussions.
"""

import re
import json
import requests


class GroqAnalyzer:
    """Use Groq AI (FREE) to analyze Slack discussions."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_thread(self, thread_content: str, channel_name: str = "") -> dict:
        """
        Analyze a Slack thread and generate Jira issue content.
        
        Returns:
            dict with 'title', 'summary', 'issue_type', and 'priority'
        """
        prompt = f"""Analyze the following Slack discussion and create a Jira issue based on it.

Channel: {channel_name if channel_name else 'Unknown'}

Slack Thread Content:
---
{thread_content[:4000]}
---

Based on this discussion, provide a JSON response with:
1. "title": A concise, descriptive title for the Jira issue (max 100 chars)
2. "summary": A detailed description capturing the problem, context, and any solutions discussed. Use Jira markup (* for bullets, *bold* for emphasis, h3. for headers)
3. "issue_type": One of: Bug, Task, Story, Improvement
4. "priority": One of: Blocker, Critical, Major, Minor, Trivial

Respond with ONLY valid JSON, no markdown, no explanation:"""

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates Jira issues from Slack discussions. Always respond with valid JSON only."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }

        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            error_msg = response.text
            try:
                error_json = response.json()
                if "error" in error_json:
                    error_msg = error_json["error"].get("message", response.text)
            except:
                pass
            raise Exception(f"Groq API error: {response.status_code} - {error_msg}")
        
        result = response.json()
        response_text = result["choices"][0]["message"]["content"]
        
        # Extract JSON from response
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned = re.sub(r'```json\s*', '', response_text)
            cleaned = re.sub(r'```\s*', '', cleaned)
            
            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', cleaned)
            if json_match:
                parsed = json.loads(json_match.group())
                # Validate required fields
                if "title" in parsed and "summary" in parsed:
                    return parsed
            raise ValueError("No valid JSON found in response")
        except (json.JSONDecodeError, ValueError):
            return self._fallback_analysis(thread_content)
    
    def _fallback_analysis(self, thread_content: str) -> dict:
        """Fallback if AI analysis fails - create basic issue from content."""
        # Extract first meaningful line for title
        lines = [l.strip() for l in thread_content.split('\n') if l.strip() and not l.startswith('[')]
        first_message = lines[0][:80] if lines else "Slack Discussion"
        
        return {
            "title": f"Issue from Slack: {first_message}",
            "summary": f"h3. Slack Discussion\n\n{thread_content[:4000]}\n\n----\n_Note: Auto-generated from Slack thread._",
            "issue_type": "Task",
            "priority": "Major"
        }
