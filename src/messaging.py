import sys
import json
import struct
import logging
from typing import Any, Dict, Optional

from config import MESSAGES

logger = logging.getLogger(__name__)


def read_message() -> Optional[Dict[str, Any]]:
    """Read a length-prefixed JSON message from Chrome via stdin."""
    try:
        raw_length = sys.stdin.buffer.read(4)
        if not raw_length:
            logger.warning("No message length received (possible disconnection)")
            return None
        message_length = struct.unpack("<I", raw_length)[0]
        message = sys.stdin.buffer.read(message_length).decode("utf-8")
        return json.loads(message)
    except Exception as e:
        logger.error(f"Error reading message: {e}")
        return None


def send_message(message: Dict[str, Any]) -> bool:
    """Send a length-prefixed JSON message back to Chrome via stdout."""
    try:
        encoded = json.dumps(message).encode("utf-8")
        sys.stdout.buffer.write(struct.pack("<I", len(encoded)))
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        return True
    except (IOError, BrokenPipeError):
        logger.error("Connection lost with Chrome (Cancellation detected)")
        return False


def send_progress(percent: float, status: str) -> bool:
    """Send a formatted progress update message to the extension."""
    return send_message({
        "type": MESSAGES["PROGRESS"],
        "percent": percent,
        "status": status,
    })


def send_done() -> bool:
    """Notify the extension that the download finished successfully."""
    return send_message({"type": MESSAGES["DONE"]})


def send_error(message: str) -> bool:
    """Notify the extension that an error or cancellation occurred."""
    return send_message({
        "type": MESSAGES["ERROR"],
        "message": message,
    })