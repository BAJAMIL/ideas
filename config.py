"""Runtime configuration shared by the marketplace clients.

HARAJ_SERVER_KEY is a public client-side key embedded in Haraj's web app, not a
private credential. It is centralised here so it has exactly one rotation point:
set the HARAJ_SERVER_KEY environment variable (or a .env entry) to override the
default without editing any client.
"""

import os

HARAJ_SERVER_KEY = os.environ.get("HARAJ_SERVER_KEY", "haraj_server_8472965246285103")

# Google News RSS is licensed for personal, non-commercial use only
# (https://www.google.com/intl/en_us/terms_google_news.html, section 2, and the
# feed's own <copyright> element). This agent produces commercial product ideas,
# so the source is DISABLED by default and must be explicitly opted into.
_TRUTHY = frozenset({"1", "true", "yes", "on"})

GOOGLE_NEWS_RSS_ENABLED = (
    os.environ.get("GOOGLE_NEWS_RSS_ENABLED", "").strip().lower() in _TRUTHY
)
