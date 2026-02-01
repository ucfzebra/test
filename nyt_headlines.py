#!/usr/bin/env python3
"""
NYT Headlines Summary - Fetch and summarize today's top stories from the New York Times.

Outputs summary to stdout and sends to Home Assistant.

Required environment variables:
    NYT_API_KEY  - New York Times API key (get from developer.nytimes.com)
    HA_URL       - Home Assistant base URL (e.g., http://homeassistant.local:8123)
    HA_TOKEN     - Home Assistant long-lived access token
"""

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class NYTHeadlines:
    """Fetches and summarizes NYT headlines."""

    NYT_TOP_STORIES_URL = "https://api.nytimes.com/svc/topstories/v2/{section}.json"
    SECTIONS = ["home", "world", "us", "politics", "business", "technology", "science", "health"]

    def __init__(self, api_key: str, sections: Optional[List[str]] = None):
        self.api_key = api_key
        self.sections = sections or ["home"]
        self.stories: List[Dict] = []

    def fetch_stories(self, section: str = "home") -> List[Dict]:
        """Fetch top stories from a specific section."""
        url = self.NYT_TOP_STORIES_URL.format(section=section)
        params = {"api-key": self.api_key}

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {section} stories: {e}")
            return []

    def fetch_all_sections(self) -> None:
        """Fetch stories from all configured sections."""
        seen_urls = set()
        for section in self.sections:
            logger.info(f"Fetching {section} stories...")
            stories = self.fetch_stories(section)
            for story in stories:
                url = story.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    story["_section"] = section
                    self.stories.append(story)
        logger.info(f"Fetched {len(self.stories)} unique stories")

    def get_top_stories(self, count: int = 10) -> List[Dict]:
        """Get the top N stories, prioritizing by section order and position."""
        return self.stories[:count]

    def group_by_section(self) -> Dict[str, List[Dict]]:
        """Group stories by their section."""
        grouped = defaultdict(list)
        for story in self.stories:
            section = story.get("_section", story.get("section", "general"))
            grouped[section].append(story)
        return dict(grouped)

    def format_story(self, story: Dict, include_abstract: bool = True) -> str:
        """Format a single story for display."""
        title = story.get("title", "No title")
        abstract = story.get("abstract", "")
        section = story.get("section", story.get("_section", ""))
        byline = story.get("byline", "")

        lines = [f"  - {title}"]
        if include_abstract and abstract:
            # Wrap abstract to reasonable length
            if len(abstract) > 150:
                abstract = abstract[:147] + "..."
            lines.append(f"    {abstract}")
        return "\n".join(lines)

    def generate_summary(self, max_stories: int = 10, include_abstracts: bool = True) -> str:
        """Generate a formatted summary of today's top stories."""
        if not self.stories:
            return "No stories available."

        now = datetime.now()
        lines = [
            "=" * 60,
            f"NEW YORK TIMES - TOP STORIES",
            f"{now.strftime('%A, %B %d, %Y at %I:%M %p')}",
            "=" * 60,
            ""
        ]

        # Get top stories
        top_stories = self.get_top_stories(max_stories)

        # Group by section for organized display
        section_stories = defaultdict(list)
        for story in top_stories:
            section = story.get("section", story.get("_section", "general")).upper()
            section_stories[section].append(story)

        # Display by section
        for section, stories in section_stories.items():
            lines.append(f"\n{section}")
            lines.append("-" * len(section))
            for story in stories:
                lines.append(self.format_story(story, include_abstracts))

        lines.append("\n" + "=" * 60)
        lines.append(f"Total: {len(top_stories)} stories")

        return "\n".join(lines)

    def generate_compact_summary(self, max_stories: int = 5) -> str:
        """Generate a compact summary suitable for Home Assistant notifications."""
        if not self.stories:
            return "No stories available."

        top_stories = self.get_top_stories(max_stories)
        headlines = [story.get("title", "No title") for story in top_stories]

        now = datetime.now()
        summary = f"NYT {now.strftime('%m/%d %I:%M%p')}\n"
        summary += "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))

        return summary


class HomeAssistantNotifier:
    """Sends notifications to Home Assistant."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def call_service(self, domain: str, service: str, data: Dict) -> bool:
        """Call a Home Assistant service."""
        url = f"{self.base_url}/api/services/{domain}/{service}"
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            logger.info(f"Successfully called {domain}.{service}")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to call {domain}.{service}: {e}")
            return False

    def send_notification(self, message: str, title: str = "NYT Headlines") -> bool:
        """Send a persistent notification to Home Assistant."""
        data = {
            "message": message,
            "title": title,
            "notification_id": "nyt_headlines"
        }
        return self.call_service("persistent_notification", "create", data)

    def update_sensor(self, entity_id: str, state: str, attributes: Optional[Dict] = None) -> bool:
        """Update or create an input_text entity with the headlines."""
        # For input_text entities
        if entity_id.startswith("input_text."):
            data = {"entity_id": entity_id, "value": state[:255]}  # input_text max length
            return self.call_service("input_text", "set_value", data)

        # For custom sensors via REST API
        url = f"{self.base_url}/api/states/{entity_id}"
        payload = {
            "state": state[:255] if len(state) > 255 else state,
            "attributes": attributes or {"friendly_name": "NYT Headlines"}
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            logger.info(f"Updated sensor {entity_id}")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to update sensor {entity_id}: {e}")
            return False


def get_env_or_exit(name: str) -> str:
    """Get an environment variable or exit with error."""
    value = os.environ.get(name)
    if not value:
        logger.error(f"Missing required environment variable: {name}")
        sys.exit(1)
    return value


def main():
    parser = argparse.ArgumentParser(
        description="Fetch NYT headlines and send to Home Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  NYT_API_KEY   New York Times API key (required)
  HA_URL        Home Assistant URL (optional, for HA integration)
  HA_TOKEN      Home Assistant access token (optional, for HA integration)

Examples:
  %(prog)s                          # Fetch home section, 10 stories
  %(prog)s -n 5                     # Fetch top 5 stories
  %(prog)s -s home world politics   # Fetch from multiple sections
  %(prog)s --compact                # Compact output for notifications
  %(prog)s --no-ha                  # Skip Home Assistant notification
        """
    )

    parser.add_argument(
        "-n", "--count",
        type=int,
        default=10,
        help="Number of stories to display (default: 10)"
    )
    parser.add_argument(
        "-s", "--sections",
        nargs="+",
        default=["home"],
        choices=NYTHeadlines.SECTIONS,
        help="Sections to fetch (default: home)"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Use compact format (better for notifications)"
    )
    parser.add_argument(
        "--no-abstract",
        action="store_true",
        help="Omit story abstracts from output"
    )
    parser.add_argument(
        "--no-ha",
        action="store_true",
        help="Skip sending to Home Assistant"
    )
    parser.add_argument(
        "--ha-entity",
        default="sensor.nyt_headlines",
        help="Home Assistant entity ID to update (default: sensor.nyt_headlines)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted text"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get NYT API key
    api_key = os.environ.get("NYT_API_KEY")
    if not api_key:
        logger.error("NYT_API_KEY environment variable is required")
        logger.error("Get your API key at: https://developer.nytimes.com/")
        sys.exit(1)

    # Fetch headlines
    nyt = NYTHeadlines(api_key, sections=args.sections)
    nyt.fetch_all_sections()

    if not nyt.stories:
        logger.error("No stories fetched. Check your API key and network connection.")
        sys.exit(1)

    # Generate output
    if args.json:
        output = json.dumps(nyt.get_top_stories(args.count), indent=2, default=str)
    elif args.compact:
        output = nyt.generate_compact_summary(args.count)
    else:
        output = nyt.generate_summary(args.count, include_abstracts=not args.no_abstract)

    # Print to stdout
    print(output)

    # Send to Home Assistant
    if not args.no_ha:
        ha_url = os.environ.get("HA_URL")
        ha_token = os.environ.get("HA_TOKEN")

        if ha_url and ha_token:
            ha = HomeAssistantNotifier(ha_url, ha_token)

            # Send as persistent notification
            compact_summary = nyt.generate_compact_summary(5)
            ha.send_notification(compact_summary)

            # Update sensor with full data
            top_stories = nyt.get_top_stories(args.count)
            headlines_list = [s.get("title", "") for s in top_stories]
            attributes = {
                "friendly_name": "NYT Headlines",
                "headlines": headlines_list,
                "last_updated": datetime.now().isoformat(),
                "story_count": len(top_stories),
                "sections": args.sections
            }
            ha.update_sensor(
                args.ha_entity,
                f"{len(top_stories)} stories",
                attributes
            )

            logger.info("Sent to Home Assistant")
        else:
            if not args.no_ha:
                logger.warning("HA_URL and HA_TOKEN not set - skipping Home Assistant")

    return 0


if __name__ == "__main__":
    sys.exit(main())
