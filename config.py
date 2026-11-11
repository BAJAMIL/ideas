"""Runtime configuration shared by the marketplace clients.

HARAJ_SERVER_KEY is a public client-side key embedded in Haraj's web app, not a
private credential. It is centralised here so it has exactly one rotation point:
set the HARAJ_SERVER_KEY environment variable (or a .env entry) to override the
default without editing any client.
"""

import os

HARAJ_SERVER_KEY = os.environ.get("HARAJ_SERVER_KEY", "haraj_server_8472965246285103")
