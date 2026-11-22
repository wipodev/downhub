import sys
import os
import logging
from pathlib import Path

# -----------------------------
# App Metadata & Protocol
# -----------------------------
APP_VERSION = "1.2.2"
GITHUB_REPO = "wipodev/downhub"

MESSAGES = {
    "PROGRESS": "NATIVE_PROGRESS",
    "DONE": "NATIVE_DONE",
    "ERROR": "NATIVE_ERROR",
}

# -----------------------------
# Paths & Directories
# -----------------------------
BASE_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
LOG_FILE = BASE_DIR / "debug_native.log"
YTDLP_STAMP_FILE = BASE_DIR / "bin" / ".last_ytdlp_update"
APP_STAMP_FILE = BASE_DIR / ".last_app_update"

YTDLP_PATH = BASE_DIR / "bin" / "yt-dlp.exe"
FFMPEG_PATH = BASE_DIR / "bin" / "ffmpeg.exe"
DENO_PATH = BASE_DIR / "bin" / "deno.exe"
EXTENSION_DIR = BASE_DIR / "extension"


def get_downloads_folder() -> Path:
    """Return the current Windows user's Downloads directory."""
    return Path(os.environ["USERPROFILE"]) / "Downloads"


def setup_logging() -> None:
    """Configure file logging in the application base directory."""
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        filemode="w",
    )