from telegram import Update, InputMediaPhoto
from telegram.ext import ConversationHandler, ContextTypes
from telegram.helpers import escape_markdown
from enums import States
from keyboards import (get_start_keyboard, get_image_edit_keyboard, get_text_creation_keyboard, 
                       get_text_edit_keyboard, get_back_keyboard)
from utils import send_valentine, confirm_valentine, generate_image, generate_text
from db import SqliteDb
import os

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
        db = SqliteDb(os.getenv("SQLITE_PATH"))
        user = update.effective_user
        telegram_id = user.id
        username = user.username if user.username else ""
        if not db.user_exists(telegram_id):
            db.add_user(telegram_id, username)
        await update.message.reply_text(welcome_text, reply_markup=get_start_keyboard())
    else:
        query = update.callback_query
        await query.answer()
        
        # Проверяем, есть ли в сообщении фото
        if query.message.photo:
            # Это сообщение с фото - нужно удалить и отправить новое
            await query.message.delete()
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=welcome_text,
                reply_markup=get_start_keyboard()
            )
        else:
            # Обычное текстовое сообщение - можно редактировать
            await query.edit_message_text(welcome_text, reply_markup=get_start_keyboard())


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
            "📋 **Напиши @ник_в_телеграме получателя**\n"
            "(можно с символом @ или без - бот поймёт оба варианта)\n\n"
            "Пример: @MikhailDOOMER или просто MikhailDOOMER"
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
            await query.edit_message_caption(
                caption="🔄 **Генерирую новую открытку...**\n\nМожет пройти до 30 секунд...",
                parse_mode='Markdown'
            )

            bio = await generate_image()

            await query.message.delete()

            caption = (
                f"❤️ **Валентинка для @{recipient}** ❤️\n\n"
                f"✨ Открытка сгенерирована специально для вас!\n"
                f"💝 Нажмите кнопки ниже, чтобы настроить или отправить"
            )
            sent_message = await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=bio,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=get_image_edit_keyboard()
            )
            context.user_data['generated_image'] = sent_message.photo[-1].file_id
        await query.answer()

        return States.GENERATING_IMAGE
    
    elif query.data == "keep_image":
        # Редактируем ТОЛЬКО подпись и клавиатуру, фото остается
        
        existing_text = context.user_data.get('text')
        
        if existing_text:
            # Если текст уже есть - переходим к подтверждению
            await query.edit_message_caption(
                caption="✅ **Изображение сохранено!**\n\n📝 **Текст уже есть!** Переходим к подтверждению...",
                parse_mode='Markdown'
            )
            
            # Вызываем подтверждение
            await confirm_valentine(update, context)
            return States.CONFIRMING
        else:
            # Если текста нет - предлагаем создать
            await query.edit_message_caption(
                caption="✅ **Изображение сохранено!**\n\n📝 Теперь займемся текстом. Выбери способ:",
                parse_mode='Markdown',
                reply_markup=get_text_creation_keyboard()
            )
            return States.GENERATING_TEXT
    
    elif query.data == "generate_text":
        await query.edit_message_caption(
            caption="⏳ **Генерируем текст...**\nЭто займет пару секунд",
            parse_mode='Markdown'
        )
        
        generated_text = await generate_text()
        
        context.user_data['text'] = generated_text
        
        await query.edit_message_caption(
            caption=f"✨ **Сгенерированный текст:**\n\n{generated_text}\n\n"
                    "📌 Что делаем дальше?",
            parse_mode='Markdown',
            reply_markup=get_text_edit_keyboard()
        )
        return States.GENERATING_TEXT
    
    elif query.data == "edit_text_manual":
        current_text = context.user_data.get('text', '')
        
        # Редактируем caption
        await query.delete_message()
        
        # Отправляем отдельное сообщение с текстом для удобного копирования
        if current_text:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"📝 **Текущий текст:**\n\n"
                    f"`{current_text}`\n\n"
                    f"👆 Нажми на текст, чтобы скопировать\n\n"
                    f"✏️ Отправь новый вариант текста:",
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"📨 Отправь свой текст:",
                parse_mode='Markdown'
            )
        
        return States.EDITING_TEXT
    
    elif query.data == "keep_text":
        await confirm_valentine(update, context)
        return States.CONFIRMING
    
    elif query.data == "send_valentine":
        await send_valentine(update, context)
        return ConversationHandler.END
    
    elif query.data == "cancel":
        context.user_data.clear()  # Очищаем данные при отмене
        # await query.edit_message_text("❌ Создание валентинки отменено.")
        await start(update, context)
        return ConversationHandler.END
    
    return ConversationHandler.END  # По умолчанию завершаем