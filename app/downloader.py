from __future__ import annotations

import asyncio
import functools
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Dict, Any

from yt_dlp import YoutubeDL

from .utils import sanitize_filename


@dataclass
class ProgressInfo:
    status: str
    downloaded_bytes: int | None = None
    total_bytes: int | None = None
    speed: float | None = None
    eta: int | None = None
    filename: str | None = None


class DownloaderService:
    def __init__(self, download_dir: Path, max_concurrent: int = 2, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.loop = loop or asyncio.get_event_loop()

    async def download(self, url: str, on_progress: Callable[[ProgressInfo], asyncio.Future | None]) -> Path:
        async with self.semaphore:
            return await asyncio.to_thread(self._download_blocking, url, on_progress)

    def _download_blocking(self, url: str, on_progress: Callable[[ProgressInfo], asyncio.Future | None]) -> Path:
        last_filename: Path | None = None

        def _hook(d: Dict[str, Any]) -> None:
            nonlocal last_filename
            status = d.get('status')
            filename = d.get('filename') or d.get('info_dict', {}).get('filepath')
            if filename:
                last_filename = Path(filename)
            info = ProgressInfo(
                status=status or "",
                downloaded_bytes=d.get('downloaded_bytes') or d.get('info_dict', {}).get('downloaded_bytes'),
                total_bytes=d.get('total_bytes') or d.get('info_dict', {}).get('total_bytes'),
                speed=d.get('speed'),
                eta=d.get('eta'),
                filename=filename,
            )
            if on_progress:
                try:
                    self.loop.call_soon_threadsafe(asyncio.create_task, on_progress(info))
                except RuntimeError:
                    pass

        outtmpl = str(self.download_dir / '%(title).150B [%(id)s].%(ext)s')

        ydl_opts = {
            'outtmpl': outtmpl,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
            'progress_hooks': [_hook],
            'concurrent_fragment_downloads': 1,
            'retries': 3,
            'fragment_retries': 3,
            'restrictfilenames': False,
            'trim_file_name': 200,
            'postprocessors': [
                {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
            ],
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_path = ydl.prepare_filename(info)
            if info.get('ext') and not final_path.endswith(info['ext']):
                base = os.path.splitext(final_path)[0]
                final_path = f"{base}.{info['ext']}"

        return Path(final_path)