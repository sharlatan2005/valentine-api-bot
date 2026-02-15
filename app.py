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
    load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Создаем Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ВАЖНО: Явно запускаем JobQueue
    if application.job_queue:
        application.job_queue.start()
        logger.info("✅ JobQueue запущен")
        
        # Проверим, что он действительно работает
        import datetime
        async def test_job(context):
            logger.info("⚡ Тестовый JobQueue тик")
        
        # Запускаем тестовую задачу на 5 секунд
        application.job_queue.run_once(test_job, 5)
        logger.info("⏰ Тестовая задача в JobQueue создана")
    else:
        logger.error("❌ JobQueue не создан!")
        # Создаём принудительно
        from telegram.ext import JobQueue
        application.job_queue = JobQueue()
        application.job_queue.set_application(application)
        application.job_queue.start()
        logger.info("🔄 JobQueue создан и запущен принудительно")

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
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
