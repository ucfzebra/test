#!/usr/bin/env python3
"""
LaMetric Time AI Icon Selector
===============================
Uses Claude AI (claude-opus-4-6) to select the most semantically appropriate
LaMetric Time icon for a given notification message.

Usage modes
-----------
1. AppDaemon app  — drop into your `apps/` folder and configure via YAML.
   Registers the `lametric_ai/notify` HA service.

2. Standalone CLI — call from a shell_command or terminal:
       python lametric_ai_selector.py --message "Laundry is done" \
           --ha-url http://homeassistant.local:8123 \
           --ha-token <long-lived-access-token> \
           --notify-service notify.lametric_time

Environment variables (standalone):
    ANTHROPIC_API_KEY   — Claude API key (required)
    HA_URL              — Home Assistant base URL
    HA_TOKEN            — HA long-lived access token
    HA_NOTIFY_SERVICE   — notify service entity (default: notify.lametric_time)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Optional

import anthropic
import requests
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# LaMetric icon catalog
# Each entry: id (integer sent to LaMetric), name, and semantic tags.
# Full icon library: https://developer.lametric.com/icons
# Adjust or extend this list to match your LaMetric icon preferences.
# ---------------------------------------------------------------------------
ICON_CATALOG: list[dict] = [
    # ── Communication ──────────────────────────────────────────────────────
    {"id": 2,   "tags": ["message", "notification", "alert", "general", "speech", "default"]},
    {"id": 9,   "tags": ["phone", "call", "telephone", "ring", "mobile"]},
    {"id": 95,  "tags": ["email", "mail", "inbox", "letter", "send"]},
    {"id": 98,  "tags": ["sms", "text message", "smartphone", "chat"]},
    # ── Home / Rooms ────────────────────────────────────────────────────────
    {"id": 3,   "tags": ["home", "house", "arrived", "smart home", "domestic"]},
    {"id": 108, "tags": ["door", "entry", "doorbell", "arrival", "opened", "closed"]},
    {"id": 109, "tags": ["window", "open", "closed", "blind", "curtain"]},
    {"id": 130, "tags": ["lock", "security", "locked", "arm", "secure"]},
    {"id": 131, "tags": ["unlock", "disarm", "open", "access", "unlocked"]},
    # ── Time / Scheduling ───────────────────────────────────────────────────
    {"id": 4,   "tags": ["clock", "time", "hour", "minute", "watch"]},
    {"id": 5,   "tags": ["alarm", "bell", "reminder", "wake", "ring"]},
    {"id": 8,   "tags": ["calendar", "date", "event", "appointment", "schedule", "meeting"]},
    {"id": 58,  "tags": ["timer", "stopwatch", "countdown", "done", "finished", "complete"]},
    # ── Weather ─────────────────────────────────────────────────────────────
    {"id": 6,   "tags": ["weather", "outdoor", "forecast", "conditions"]},
    {"id": 14,  "tags": ["cloud", "cloudy", "overcast", "grey sky"]},
    {"id": 15,  "tags": ["sun", "sunny", "clear", "daytime", "bright", "hot"]},
    {"id": 16,  "tags": ["moon", "night", "sleep", "bedtime", "dark", "evening"]},
    {"id": 52,  "tags": ["temperature", "thermometer", "heat", "fever", "degrees", "warm", "cold"]},
    {"id": 53,  "tags": ["humidity", "water", "moisture", "damp", "wet"]},
    {"id": 55,  "tags": ["snow", "snowflake", "winter", "freezing", "ice", "frost"]},
    {"id": 56,  "tags": ["rain", "precipitation", "storm", "drizzle", "wet weather"]},
    {"id": 57,  "tags": ["wind", "breeze", "gust", "air", "ventilation", "fan"]},
    {"id": 54,  "tags": ["fire", "flame", "heat", "burning", "fireplace", "overheat"]},
    # ── Energy / Smart Home ─────────────────────────────────────────────────
    {"id": 40,  "tags": ["lightning", "electricity", "power", "energy", "bolt", "voltage"]},
    {"id": 134, "tags": ["battery full", "charged", "battery high", "power ok"]},
    {"id": 135, "tags": ["battery empty", "battery low", "low power", "charge needed"]},
    {"id": 140, "tags": ["wifi", "wireless", "connected", "network", "internet"]},
    {"id": 141, "tags": ["bluetooth", "pairing", "wireless", "connected device"]},
    # ── Media / Entertainment ───────────────────────────────────────────────
    {"id": 36,  "tags": ["music", "audio", "song", "playing", "speaker", "media"]},
    {"id": 240, "tags": ["game", "gaming", "controller", "entertainment", "play"]},
    # ── Health / Wellness ───────────────────────────────────────────────────
    {"id": 37,  "tags": ["heart", "love", "health", "medical", "pulse", "heart rate"]},
    {"id": 120, "tags": ["person", "user", "profile", "individual", "human"]},
    {"id": 122, "tags": ["people", "group", "family", "multiple", "team", "crowd"]},
    # ── Transport ───────────────────────────────────────────────────────────
    {"id": 22,  "tags": ["car", "vehicle", "driving", "transport", "auto", "arrived"]},
    {"id": 23,  "tags": ["airplane", "flight", "travel", "plane", "airport", "trip"]},
    # ── Kitchen / Food ──────────────────────────────────────────────────────
    {"id": 82,  "tags": ["coffee", "morning", "breakfast", "drink", "cafe", "tea"]},
    {"id": 170, "tags": ["food", "meal", "eat", "dinner", "lunch", "cooking", "kitchen"]},
    {"id": 175, "tags": ["drink", "beer", "party", "celebration", "beverage", "bar"]},
    # ── Shopping / Finance ──────────────────────────────────────────────────
    {"id": 104, "tags": ["shopping", "cart", "purchase", "order", "buy", "store", "delivery"]},
    {"id": 106, "tags": ["money", "dollar", "payment", "finance", "price", "cost", "bank"]},
    # ── Status / System ─────────────────────────────────────────────────────
    {"id": 150, "tags": ["checkmark", "done", "complete", "success", "ok", "tick", "finished", "ready"]},
    {"id": 151, "tags": ["error", "fail", "X", "problem", "issue", "wrong", "bug", "broken"]},
    {"id": 155, "tags": ["info", "information", "notice", "detail", "note"]},
    {"id": 156, "tags": ["question", "unknown", "help", "unsure", "query"]},
    {"id": 145, "tags": ["settings", "gear", "configure", "options", "setup", "cog"]},
    {"id": 215, "tags": ["refresh", "reload", "sync", "update", "retry"]},
    {"id": 210, "tags": ["trash", "delete", "remove", "clean", "garbage"]},
    {"id": 220, "tags": ["download", "save", "import", "incoming"]},
    {"id": 225, "tags": ["upload", "share", "export", "send", "outgoing"]},
    # ── Data / Work ─────────────────────────────────────────────────────────
    {"id": 230, "tags": ["chart", "graph", "statistics", "analytics", "data", "trend"]},
    {"id": 235, "tags": ["news", "article", "feed", "read", "headline"]},
    {"id": 110, "tags": ["laptop", "computer", "work", "tech", "coding", "server"]},
    # ── Nature / Environment ────────────────────────────────────────────────
    {"id": 165, "tags": ["leaf", "plant", "eco", "nature", "green", "garden", "water plants"]},
    {"id": 200, "tags": ["globe", "world", "internet", "earth", "global"]},
    # ── Celebrations / Special ──────────────────────────────────────────────
    {"id": 180, "tags": ["gift", "present", "birthday", "surprise", "package", "parcel"]},
    {"id": 62,  "tags": ["trophy", "achievement", "winner", "gold", "first place"]},
    {"id": 63,  "tags": ["medal", "award", "recognition", "star", "honor"]},
    {"id": 160, "tags": ["rocket", "launch", "startup", "fast", "boost"]},
    # ── People / Life ───────────────────────────────────────────────────────
    {"id": 185, "tags": ["baby", "child", "new", "infant", "born", "young"]},
    {"id": 190, "tags": ["dog", "pet", "animal", "paw", "puppy"]},
    {"id": 195, "tags": ["cat", "pet", "feline", "meow", "kitten"]},
]

# Build a compact catalog string for the prompt (id + top tags only)
_CATALOG_TEXT = "\n".join(
    f"  {entry['id']}: {', '.join(entry['tags'][:5])}"
    for entry in ICON_CATALOG
)

_SYSTEM_PROMPT = f"""\
You are an icon-selector assistant for LaMetric Time smart displays.
Your ONLY job is to pick the single most visually appropriate icon ID from the
catalog below for the notification message the user provides.

Icon catalog (id: semantic tags):
{_CATALOG_TEXT}

Rules:
- Return ONLY valid JSON matching the schema: {{"icon_id": <integer>, "reason": "<one sentence>"}}
- "icon_id" must be one of the integer IDs listed above.
- If nothing fits well, return icon_id 2 (general notification).
- Do NOT return markdown, code fences, or any extra text.
"""


# ---------------------------------------------------------------------------
# Pydantic schema for structured output
# ---------------------------------------------------------------------------
class IconSelection(BaseModel):
    icon_id: int
    reason: str


# ---------------------------------------------------------------------------
# Core selection logic (shared by both modes)
# ---------------------------------------------------------------------------
def select_icon(message: str, title: str = "", api_key: Optional[str] = None) -> IconSelection:
    """Call Claude to pick the best LaMetric icon for *message*."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError(
            "Anthropic API key not found. "
            "Set ANTHROPIC_API_KEY or pass api_key= explicitly."
        )

    client = anthropic.Anthropic(api_key=key)
    prompt = f"Notification: {title + ': ' if title else ''}{message}"

    response = client.messages.parse(
        model="claude-opus-4-6",
        max_tokens=256,
        thinking={"type": "adaptive"},
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
        output_format=IconSelection,
    )
    return response.parsed_output


# ---------------------------------------------------------------------------
# AppDaemon app (only imported when AppDaemon is present)
# ---------------------------------------------------------------------------
try:
    import appdaemon.plugins.hass.hassapi as hass  # type: ignore

    class LaMetricAISelector(hass.Hass):
        """AppDaemon app – registers the `lametric_ai/notify` HA service.

        apps/lametric_ai_selector.yaml config keys:
            anthropic_api_key: "sk-ant-..."   # or set ANTHROPIC_API_KEY env var
            lametric_entity: notify.lametric_time
            default_icon: 2
            icon_lifetime_ms: 5000            # ms each frame is displayed
        """

        def initialize(self) -> None:
            self._api_key: Optional[str] = self.args.get("anthropic_api_key") or os.environ.get(
                "ANTHROPIC_API_KEY"
            )
            self._entity: str = self.args.get("lametric_entity", "notify.lametric_time")
            self._default_icon: int = int(self.args.get("default_icon", 2))
            self._lifetime_ms: int = int(self.args.get("icon_lifetime_ms", 5000))

            self.register_service("lametric_ai/notify", self._handle_notify)
            self.log("LaMetric AI Icon Selector ready", level="INFO")

        # ------------------------------------------------------------------ #
        def _handle_notify(self, namespace, domain, service, kwargs) -> None:
            message: str = kwargs.get("message", "").strip()
            title: str = kwargs.get("title", "").strip()
            entity: str = kwargs.get("entity_id", self._entity)
            lifetime: int = int(kwargs.get("lifetime_ms", self._lifetime_ms))

            if not message:
                self.log("lametric_ai/notify called with empty message – skipped", level="WARNING")
                return

            icon_id = self._select_icon_safe(message, title)

            # Convert entity_id (notify.lametric_time) → service path (notify/lametric_time)
            svc_path = entity.replace(".", "/", 1)
            self.call_service(
                svc_path,
                message=message,
                data={
                    "icon": icon_id,
                    "lifetime": lifetime,
                },
            )
            self.log(
                f"LaMetric notified | icon={icon_id} | '{message}'", level="INFO"
            )

        def _select_icon_safe(self, message: str, title: str) -> int:
            try:
                result = select_icon(message, title, api_key=self._api_key)
                self.log(
                    f"Icon {result.icon_id} chosen: {result.reason}", level="DEBUG"
                )
                return result.icon_id
            except Exception as exc:
                self.log(f"Icon selection failed ({exc}); using default {self._default_icon}", level="ERROR")
                return self._default_icon

except ImportError:
    pass  # AppDaemon not installed – standalone mode only


# ---------------------------------------------------------------------------
# Standalone CLI / shell_command mode
# ---------------------------------------------------------------------------
def _send_ha_notification(
    *,
    ha_url: str,
    ha_token: str,
    notify_service: str,
    message: str,
    icon_id: int,
    lifetime_ms: int,
) -> None:
    """POST a notification to HA via the REST API."""
    service_path = notify_service.replace(".", "/", 1)
    url = f"{ha_url.rstrip('/')}/api/services/{service_path}"
    headers = {
        "Authorization": f"Bearer {ha_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "message": message,
        "data": {"icon": icon_id, "lifetime": lifetime_ms},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    log = logging.getLogger("lametric_ai")

    parser = argparse.ArgumentParser(
        description="Select a LaMetric icon with AI and optionally send a notification."
    )
    parser.add_argument("--message", "-m", required=True, help="Notification text")
    parser.add_argument("--title", "-t", default="", help="Optional title prefix")
    parser.add_argument("--anthropic-api-key", default=None, help="Override ANTHROPIC_API_KEY")
    parser.add_argument("--print-icon-only", action="store_true",
                        help="Print the selected icon ID to stdout and exit (no HA call)")
    # HA connection (only needed without --print-icon-only)
    parser.add_argument("--ha-url", default=os.environ.get("HA_URL", "http://homeassistant.local:8123"))
    parser.add_argument("--ha-token", default=os.environ.get("HA_TOKEN"))
    parser.add_argument("--notify-service", default=os.environ.get("HA_NOTIFY_SERVICE", "notify.lametric_time"))
    parser.add_argument("--lifetime-ms", type=int, default=5000, help="Icon display time in ms")
    args = parser.parse_args(argv)

    # Select icon
    try:
        selection = select_icon(args.message, args.title, api_key=args.anthropic_api_key)
    except Exception as exc:
        log.error("Failed to select icon: %s", exc)
        return 1

    log.info("Selected icon %d: %s", selection.icon_id, selection.reason)

    if args.print_icon_only:
        print(selection.icon_id)
        return 0

    # Send notification
    if not args.ha_token:
        log.error(
            "No HA token provided. Set HA_TOKEN env var or pass --ha-token. "
            "Use --print-icon-only to skip the HA call."
        )
        return 1

    try:
        _send_ha_notification(
            ha_url=args.ha_url,
            ha_token=args.ha_token,
            notify_service=args.notify_service,
            message=args.message,
            icon_id=selection.icon_id,
            lifetime_ms=args.lifetime_ms,
        )
        log.info("Notification sent to %s via %s", args.ha_url, args.notify_service)
    except requests.HTTPError as exc:
        log.error("HA API error: %s", exc)
        return 1
    except requests.ConnectionError as exc:
        log.error("Cannot reach Home Assistant: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
