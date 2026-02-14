import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from dotenv import load_dotenv
import os

from enums import States
from handlers import button_handler, start, help_command
from utils import select_recipient, edit_text_manual, handle_topic_input

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Запуск бота"""
    load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Создаем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_handler, pattern="^create_valentine$")
        ],
        states={
            States.SELECTING_RECIPIENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_recipient)
            ],
            States.GENERATING_IMAGE: [
                CallbackQueryHandler(button_handler)  # Обработчик кнопок в этом состоянии
            ],
            States.GENERATING_TEXT: [
                CallbackQueryHandler(button_handler)  # Обработчик кнопок в этом состоянии
            ],
            States.EDITING_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_text_manual)
            ],
            States.ENTERING_TOPIC: [  # Новое состояние для ввода темы
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic_input)
            ],
            States.CONFIRMING: [
                CallbackQueryHandler(button_handler)  # Обработчик кнопок в этом состоянии
            ]
        },
        fallbacks=[
            CallbackQueryHandler(button_handler, pattern="^cancel$")
        ],
        name="valentine_conversation",
        persistent=False
    )
    
    # ВАЖНО: Регистрируем обработчики в правильном порядке
    # Сначала ConversationHandler, потом общие обработчики
    application.add_handler(conv_handler)
    
    # Регистрируем остальные обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^back_to_start$"))
    
    print("❤️ Бот для валентинок запущен! ❤️")
    print("Нажми Ctrl+C для остановки")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()