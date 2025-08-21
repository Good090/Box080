from __future__ import annotations

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import uvloop  # type: ignore
    uvloop.install()
except Exception:
    pass

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile

from .config import settings
from .keyboards import main_menu_kb
from .utils import is_url, human_size, guess_is_video
from .downloader import DownloaderService, ProgressInfo


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
)
logger = logging.getLogger("tg-downloader")


async def format_progress_text(prefix: str, p: ProgressInfo) -> str:
    parts = [prefix]
    if p.total_bytes and p.downloaded_bytes:
        parts.append(f"{human_size(p.downloaded_bytes)} / {human_size(p.total_bytes)}")
    if p.speed:
        parts.append(f"⚡ {human_size(int(p.speed))}/s")
    if p.eta:
        parts.append(f"⏳ ~{p.eta}s")
    return "\n".join(parts)


async def handle_link(message: Message, url: str, downloader: DownloaderService) -> None:
    status_msg = await message.answer("Загружаю…", reply_markup=main_menu_kb().as_markup())

    last_edit = 0.0

    async def on_progress(p: ProgressInfo):
        nonlocal last_edit
        now = asyncio.get_event_loop().time()
        if now - last_edit < 1.0:
            return
        last_edit = now
        try:
            if p.status == 'downloading':
                await status_msg.edit_text(await format_progress_text("Скачивание:", p), reply_markup=main_menu_kb().as_markup())
            elif p.status == 'postprocessing':
                await status_msg.edit_text("Обработка видео…", reply_markup=main_menu_kb().as_markup())
        except Exception:
            pass

    try:
        path: Path = await downloader.download(url, on_progress)
    except Exception as e:
        logger.exception("Download failed")
        await status_msg.edit_text("❌ Не удалось скачать. Попробуйте другую ссылку или позже.")
        return

    try:
        file_size = path.stat().st_size
        limit_bytes = settings.telegram_upload_limit_mb * 1024 * 1024
        caption = f"Готово: {path.name}\nРазмер: {human_size(file_size)}"

        if file_size > limit_bytes:
            await status_msg.edit_text(
                "⚠️ Файл слишком большой для Telegram (>{} MB). Ссылка на оригинал: {}".format(
                    settings.telegram_upload_limit_mb, url
                )
            )
            return

        input_file = FSInputFile(str(path))
        if guess_is_video(path):
            await message.answer_video(video=input_file, caption=caption)
        else:
            await message.answer_document(document=input_file, caption=caption)
        await status_msg.delete()
    finally:
        try:
            if path.exists():
                path.unlink()
        except Exception:
            pass


async def main() -> None:
    if settings.timezone:
        os.environ['TZ'] = settings.timezone

    bot = Bot(token=settings.bot_token, parse_mode='HTML')
    dp = Dispatcher()

    downloader = DownloaderService(download_dir=settings.download_dir, max_concurrent=settings.max_concurrent_downloads)

    @dp.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        text = (
            "👋 Привет! Пришли ссылку на видео из TikTok / YouTube / Instagram / X / VK и я скачаю его для тебя.\n\n"
            "Поддерживаются десятки платформ: см. кнопку ниже."
        )
        await message.answer(text, reply_markup=main_menu_kb().as_markup())

    @dp.message(Command('help'))
    async def cmd_help(message: Message) -> None:
        await message.answer(
            "Отправь ссылку на видео. Я скачаю лучший доступный формат и пришлю файл.\n"
            "Если файл окажется слишком большим (> ~1.9 ГБ), я сообщу об ограничении.",
            reply_markup=main_menu_kb().as_markup(),
        )

    @dp.message(F.text)
    async def on_text(message: Message) -> None:
        text = (message.text or '').strip()
        if not is_url(text):
            return
        await handle_link(message, text, downloader)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass