from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)

    bot_token: str = Field(alias='BOT_TOKEN')
    download_dir: Path = Field(default=Path(os.environ.get('DOWNLOAD_DIR', '/workspace/data')))
    max_concurrent_downloads: int = Field(default=int(os.environ.get('MAX_CONCURRENT_DOWNLOADS', 2)))
    telegram_upload_limit_mb: int = Field(default=int(os.environ.get('TELEGRAM_UPLOAD_LIMIT_MB', 1950)))
    timezone: str | None = Field(default=os.environ.get('TZ'))

    def ensure_dirs(self) -> None:
        self.download_dir.mkdir(parents=True, exist_ok=True)


settings = AppSettings()
settings.ensure_dirs()