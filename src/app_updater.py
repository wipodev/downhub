import time
import logging
import subprocess

from updater import GitHubUpdater
from config import (
    APP_VERSION,
    GITHUB_REPO,
    BASE_DIR,
    EXTENSION_DIR,
    APP_STAMP_FILE,
    YTDLP_PATH,
    YTDLP_STAMP_FILE,
)
from messaging import send_progress

logger = logging.getLogger(__name__)


def run_background_app_update() -> None:
    """Silently check GitHub Releases and hot-swap modified components for the next run."""
    targets = {
        "DownHubService.exe": BASE_DIR / "DownHubService.exe",
    }
    if EXTENSION_DIR.exists():
        targets["extension.zip"] = EXTENSION_DIR

    updater = GitHubUpdater(
        repo=GITHUB_REPO,
        current_version=APP_VERSION,
        asset_targets=targets,
        stamp_file=APP_STAMP_FILE,
    )
    result = updater.check_and_update()
    if result.updated:
        logger.info(f"DownHub silently updated to {result.latest_version} for next run.")


def ensure_ytdlp_updated(force: bool = False) -> None:
    """Update yt-dlp.exe if more than 24 hours have passed since the last check, or if forced."""
    if not YTDLP_PATH.exists():
        return

    now = time.time()
    update_interval = 86400

    if not force and YTDLP_STAMP_FILE.exists():
        try:
            last_check = float(YTDLP_STAMP_FILE.read_text(encoding="utf-8").strip())
            if (now - last_check) < update_interval:
                return
        except ValueError:
            pass

    logger.info("Checking for yt-dlp updates...")
    send_progress(0, "Verificando actualizaciones de motor...")

    try:
        result = subprocess.run(
            [str(YTDLP_PATH), "-U"],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        output = (result.stdout or "") + (result.stderr or "")
        logger.info(f"yt-dlp update output: {output.strip()}")
        YTDLP_STAMP_FILE.write_text(str(now), encoding="utf-8")
    except Exception as e:
        logger.warning(f"Could not auto-update yt-dlp: {e}")