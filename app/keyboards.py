from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def main_menu_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text="Поддерживаемые платформы",
            url="https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md",
        )
    )
    return kb