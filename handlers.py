from telegram import Update, InputMediaPhoto
from telegram.ext import ConversationHandler, ContextTypes
from enums import States
from keyboards import (get_start_keyboard, get_image_edit_keyboard, get_text_creation_keyboard, 
                       get_text_edit_keyboard, get_back_keyboard)
from utils import send_valentine, confirm_valentine, generate_image

# ==================== ОБРАБОТЧИКИ ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    welcome_text = f"""
    ❤️ Привет, {user.first_name}! ❤️
    
    Я помогу тебе создать валентинку и отправить её другому пользователю!
    
    Что я умею:
    🎨 Генерировать красивые картинки (демо-режим)
    ✍️ Придумывать романтичные подписи
    📤 Отправлять валентинки по @username
    
    Нажми кнопку ниже, чтобы начать!
    """
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=get_start_keyboard())
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=get_start_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик помощи"""
    query = update.callback_query
    await query.answer()
    
    help_text = """
    ❓ Как пользоваться ботом:
    
    1. Нажми "Создать валентинку"
    2. Введи @username получателя
    3. Сгенерируй тестовое изображение
    4. Напиши или сгенерируй текст
    5. Отправь валентинку!
    
    📝 Особенности:
    • Изображение можно перегенерировать сколько угодно раз
    • Текст можно написать свой или сгенерировать
    • Перед отправкой всё можно изменить
    """
    
    await query.edit_message_text(help_text, reply_markup=get_back_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главный обработчик инлайн-кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "create_valentine":
        await query.edit_message_text(
            "💝 Отлично! Давай создадим валентинку.\n\n"
            "📋 **Напиши @username получателя**\n"
            "(можно с символом @ или без - бот поймёт оба варианта)\n\n"
            "Пример: @durov или просто durov"
        )
        return States.SELECTING_RECIPIENT
    
    elif query.data == "help":
        await help_command(update, context)
        return None  # Не возвращаем состояние
    
    elif query.data == "back_to_start":
        context.user_data.clear()  # Очищаем данные при выходе
        await start(update, context)
        return ConversationHandler.END
    
    elif query.data == "regenerate_image":
        recipient = context.user_data.get('recipient')
        
        if recipient:
            # Генерируем изображение
            bio = generate_image()
            
            # РЕДАКТИРУЕМ ТЕКУЩЕЕ СООБЩЕНИЕ (то, на котором нажали кнопку)
            await query.edit_message_media(
                media=InputMediaPhoto(
                    media=bio,
                    caption=f"❤️ **Валентинка для @{recipient}** ❤️\n\n✨ Открытка сгенерирована!",
                    parse_mode='Markdown'
                ),
                reply_markup=get_image_edit_keyboard()  # Новая клавиатура
            )
        
        await query.answer()
    
    elif query.data == "keep_image":
        await query.edit_message_text("✅ Изображение сохранено!")
        await query.message.reply_text(
            "📝 Теперь займемся текстом. Выбери способ:",
            reply_markup=get_text_creation_keyboard()
        )
        return States.GENERATING_TEXT
    
    elif query.data == "generate_text":
        import random
        
        demo_texts = [
            "С днём Святого Валентина! Ты делаешь этот мир лучше! ❤️",
            "Спасибо, что ты есть! Ты самое лучшее, что со мной случалось! 💝",
            "Ты — причина моей улыбки каждый день! 💕",
            "С тобой каждый день как праздник! С днём всех влюблённых! 💖",
            "Ты особенный человек в моей жизни! 💗",
            "Люблю тебя больше жизни! С праздником! ❤️",
            "Ты — моё счастье! 💘",
            "Даже в самый хмурый день ты приносишь свет! 💓"
        ]
        generated_text = random.choice(demo_texts)
        
        recipient = context.user_data.get('recipient')
        if recipient:
            generated_text = f"@{recipient}, {generated_text}"
        
        # Сохраняем сгенерированный текст
        context.user_data['text'] = generated_text
        
        await query.edit_message_text(
            f"✨ Сгенерированный текст:\n\n{generated_text}\n\n"
            "Что делаем дальше?",
            reply_markup=get_text_edit_keyboard()
        )
        return States.GENERATING_TEXT
    
    elif query.data == "edit_text_manual":
        await query.edit_message_text(
            "✍️ Напиши свой текст для валентинки.\n\n"
            "Отправь сообщение с текстом:"
        )
        return States.EDITING_TEXT
    
    elif query.data == "keep_text":
        await confirm_valentine(update, context)
        return States.CONFIRMING
    
    elif query.data == "send_valentine":
        await send_valentine(update, context)
        await start(update, context)
        return ConversationHandler.END
    
    elif query.data == "cancel":
        context.user_data.clear()  # Очищаем данные при отмене
        await query.edit_message_text("❌ Создание валентинки отменено.")
        await start(update, context)
        return ConversationHandler.END
    
    return ConversationHandler.END  # По умолчанию завершаем