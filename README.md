## Телеграм-бот: Скачивание видео из соцсетей (yt-dlp)

Красивый и надежный бот на Python (aiogram v3) с прогрессом загрузки, очередью, и Docker-сборкой. Поддерживаются десятки платформ через yt-dlp: TikTok, YouTube, Instagram, Twitter/X, VK и др.

### Быстрый старт (локально)
1. Установите зависимости Python 3.11+
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
2. Скопируйте `.env.example` в `.env` и пропишите `BOT_TOKEN`.
3. Убедитесь, что установлен `ffmpeg`:
```bash
# Debian/Ubuntu
sudo apt update && sudo apt install -y ffmpeg
```
4. Запустите бота:
```bash
python -m app.bot
```

### Запуск в Docker
```bash
docker build -t tg-downloader .
docker run --rm -it \
  -e BOT_TOKEN=123456:REPLACE_ME \
  -e TZ=Europe/Moscow \
  -v $(pwd)/data:/data \
  tg-downloader
```

### Использование
- Отправьте боту ссылку на видео из любой поддерживаемой платформы
- Бот покажет прогресс и отправит файл. Если файл слишком большой (> ~1.9 ГБ), бот сообщит об ограничении

### Переменные окружения
- `BOT_TOKEN` — токен Telegram бота
- `DOWNLOAD_DIR` — путь к папке для загрузок (по умолчанию `/data` в Docker или `/workspace/data` локально)
- `MAX_CONCURRENT_DOWNLOADS` — максимальное число одновременных загрузок
- `TZ` — таймзона для логов

### Примечания
- Ограничение Telegram: файл до 2 ГБ
- yt-dlp постоянно обновляется; при проблемах с конкретной платформой обновите версию

### Лицензия
MIT