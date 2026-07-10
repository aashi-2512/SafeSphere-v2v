from dotenv import load_dotenv
import os

load_dotenv()

# ── JWT ──────────────────────────────────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_EXPIRY_MINUTES = int(os.getenv("TOKEN_EXPIRY_MINUTES", "120"))

# ── Session behaviour ────────────────────────────────────────────────────────
SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "4"))
RING_BUFFER_SIZE = int(os.getenv("RING_BUFFER_SIZE", "10"))
GRACE_PERIOD_SECONDS = int(os.getenv("GRACE_PERIOD_SECONDS", "30"))

# ── Safety-map data paths ─────────────────────────────────────────────────────
# Resolve project root relative to this file:
#   config.py  →  app/  →  voice-feature/  →  SafeSphere-v2v/  (project root)
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

DATA_DIR = os.path.abspath(
    os.getenv("DATA_DIR", os.path.join(_PROJECT_ROOT, "data"))
)
MODEL_PATH = os.path.abspath(
    os.getenv("MODEL_PATH", os.path.join(_PROJECT_ROOT, "model.pkl"))
)
SCRIPT_DIR = os.path.abspath(
    os.getenv("SCRIPT_DIR", os.path.join(_PROJECT_ROOT, "script"))
)