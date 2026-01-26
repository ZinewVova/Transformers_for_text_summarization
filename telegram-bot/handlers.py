import logging
from telegram import Update, BotCommand
from telegram.ext import ContextTypes

from config import settings

logger = logging.getLogger(__name__)


async def setup_bot_commands(application):
    commands = [
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Помощь и инструкции"),
        BotCommand("info", "Информация о боте"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands menu set up successfully")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "👋 Привет! Я бот для реферирования текстов.\n\n"
        "📝 Просто отправьте мне текст, и я создам его краткое содержание.\n\n"
        "ℹ️ Используйте /help для получения дополнительной информации."
    )
    await update.message.reply_text(welcome_message)


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_message = (
        "ℹ️ Информация о боте\n\n"
        "🤖 Бот для автоматического реферирования текстов\n"
        "🧠 Модель: IlyaGusev/rut5_base_sum_gazeta\n"
        "🔧 Технология: FastAPI + Transformers\n"
        "🇷🇺 Язык: Русский\n\n"
        "📊 Возможности:\n"
        f"• Реферирование текстов ({settings.MIN_MESSAGE_LENGTH}-{settings.MAX_MESSAGE_LENGTH} символов)\n"
        "• Быстрая обработка (5-30 секунд)\n"
        "• Высокое качество резюме\n"
        "• Автоматическое обрезание длинных текстов\n\n"
        "💡 Используйте /help для получения инструкций"
    )
    await update.message.reply_text(info_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "📚 Как использовать бота:\n\n"
        "1️⃣ Отправьте мне любой текст на русском языке\n"
        "2️⃣ Подождите несколько секунд\n"
        "3️⃣ Получите краткое содержание текста\n\n"
        "⚙️ Технические детали:\n"
        f"• Минимальная длина текста: {settings.MIN_MESSAGE_LENGTH} символов\n"
        f"• Максимальная длина текста: {settings.MAX_MESSAGE_LENGTH} символов\n"
        "• Модель: IlyaGusev/rut5_base_sum_gazeta\n"
        "• Обработка текста занимает 5-30 секунд\n\n"
        "💡 Советы:\n"
        "• Отправляйте связные тексты (статьи, новости, документы)\n"
        "• Для лучших результатов используйте тексты длиной от 100 слов\n"
        "• Бот работает только с русским языком\n"
        "• Если текст длиннее максимума, он будет автоматически обрезан\n\n"
        "❓ Если возникли проблемы, попробуйте отправить текст снова."
    )
    await update.message.reply_text(help_message)


async def summarize_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < settings.MIN_MESSAGE_LENGTH:
        await update.message.reply_text(
            f"❌ Текст слишком короткий для реферирования. "
            f"Пожалуйста, отправьте текст длиной минимум {settings.MIN_MESSAGE_LENGTH} символов."
        )
        return

    original_length = len(text)
    if original_length > settings.MAX_MESSAGE_LENGTH:
        text = text[:settings.MAX_MESSAGE_LENGTH]
        logger.info(f"Text truncated from {original_length} to {settings.MAX_MESSAGE_LENGTH} characters")

    processing_message = await update.message.reply_text(
        "⏳ Обрабатываю текст... Это может занять несколько секунд."
    )

    try:
        api_client = context.bot_data.get('api_client')
        if not api_client:
            raise Exception("API client not initialized")

        result = await api_client.summarize_text(text)
        summary = result.get('summary', '')
        model_used = result.get('model_used', 'Unknown')

        await processing_message.delete()

        response_message = (
            f"📄 Реферат:\n\n{summary}\n\n"
            f"Модель: {model_used}"
        )
        await update.message.reply_text(response_message)

        logger.info(f"Successfully summarized message from user {update.effective_user.id}")

    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")

        try:
            await processing_message.delete()
        except:
            pass

        error_message = (
            "❌ Произошла ошибка при обработке текста.\n\n"
            "Возможные причины:\n"
            "• Сервис временно недоступен\n"
            "• Проблемы с подключением\n"
            "• Текст содержит некорректные символы\n\n"
            "Пожалуйста, попробуйте снова через несколько секунд."
        )
        await update.message.reply_text(error_message)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже."
            )
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")
