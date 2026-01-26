import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import settings
from api_client import FastAPIClient
from handlers import (
    start_command,
    help_command,
    info_command,
    summarize_message,
    error_handler,
    setup_bot_commands
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application):
    await setup_bot_commands(application)


def main():
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    api_client = FastAPIClient(
        base_url=settings.FASTAPI_URL,
        timeout=settings.FASTAPI_TIMEOUT
    )

    application.bot_data['api_client'] = api_client

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, summarize_message)
    )
    application.add_error_handler(error_handler)

    application.post_init = post_init

    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
