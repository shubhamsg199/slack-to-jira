"""
Command-line interface for Slack to Jira converter.
"""

import sys
import json
import argparse

from .converter import SlackToJira


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create Jira issues from Slack thread discussions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://myworkspace.slack.com/archives/C01234/p1234567890123456"
  %(prog)s --project SAT --type Task "https://..."
  %(prog)s --dry-run "https://..." 

Configuration:
  Edit slack_to_jira/config.py to set your Slack, Jira, and Groq API credentials.
  
  Get your FREE Groq API key from: https://console.groq.com/keys
        """
    )
    
    parser.add_argument(
        "slack_url",
        help="Slack thread URL to process"
    )
    parser.add_argument(
        "-p", "--project",
        help="Jira project key (overrides default)"
    )
    parser.add_argument(
        "-t", "--type",
        help="Issue type (Bug, Task, Story, Improvement)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without actually creating"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    
    args = parser.parse_args()
    
    try:
        converter = SlackToJira()
        result = converter.process(
            slack_url=args.slack_url,
            project_key=args.project,
            issue_type=args.type,
            dry_run=args.dry_run
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

