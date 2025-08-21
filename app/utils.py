import re
from pathlib import Path


_URL_RE = re.compile(r"^(https?://)[\w.-]+(?:/[^\s]*)?$")


def is_url(text: str) -> bool:
    if not text:
        return False
    return bool(_URL_RE.match(text.strip()))


def sanitize_filename(name: str, replacement: str = "_") -> str:
    name = re.sub(r"[\\/:*?\"<>|]", replacement, name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:200] if len(name) > 200 else name


def human_size(num_bytes: int) -> str:
    step = 1024.0
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for unit in units:
        if size < step:
            return f"{size:.1f} {unit}"
        size /= step
    return f"{size:.1f} PB"


def guess_is_video(path: Path) -> bool:
    return path.suffix.lower() in {'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'}