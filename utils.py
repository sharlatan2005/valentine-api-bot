from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes
from telegram.error import Forbidden, BadRequest
from io import BytesIO

from enums import States
from keyboards import get_image_edit_keyboard, get_confirmation_keyboard
from image_api import generate_valentine_image

async def generate_image():
        img = generate_valentine_image()
        
        # Конвертируем PIL Image в bytes для отправки
        bio = BytesIO()
        bio.name = 'valentine.png'
        img.save(bio, 'PNG')
        bio.seek(0)
        return bio

async def select_recipient(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение username получателя с проверкой существования"""
    username_input = update.message.text.strip()
    
    # Убираем @ если пользователь ввёл
    clean_username = username_input.replace('@', '')
    
    if not clean_username:
        await update.message.reply_text(
            "❌ Имя пользователя не может быть пустым.\n"
            "Пожалуйста, введите @username получателя:"
        )
        return States.SELECTING_RECIPIENT
    
    try:
        # Пытаемся отправить действие "печатает" для проверки доступности
        # await context.bot.send_chat_action(
        #     chat_id=f"@{clean_username}", 
        #     action="typing"
        # )
        
        # Если дошли сюда - бот может писать пользователю
        context.user_data['recipient'] = clean_username
        
        status_msg = await update.message.reply_text(
            f"🎨 Генерирую валентинку для @{clean_username}...\n"
            f"⏱ Это может занять до 30 секунд"
        )
        try:
            bio = await generate_image()

            await status_msg.delete()

            caption = (
                f"❤️ **Валентинка для @{clean_username}** ❤️\n\n"
                f"✨ Открытка сгенерирована специально для вас!\n"
                f"💝 Нажмите кнопки ниже, чтобы настроить или отправить"
            )
            
            await update.message.reply_photo(
                    photo=bio,
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=get_image_edit_keyboard()
                )
        except Exception as e:
            await status_msg.delete()
            
            # Fallback на демо-режим
            await update.message.reply_text(
                text=f"⚠️ Не удалось сгенерировать изображение.\n"
                    f"🖼 [ДЕМО] Валентинка для @{clean_username}\n"
                    f"❤️ ❤️ ❤️",
                reply_markup=get_image_edit_keyboard()
            )
            
        return States.GENERATING_IMAGE

    except BadRequest as e:
        error_text = str(e).lower()
        
        if "chat not found" in error_text:
            await update.message.reply_text("❌ Пользователь не найден. Убедитесь, что username правильный и пользователь писал боту хотя бы раз.")
        elif "user is deactivated" in error_text:
            await update.message.reply_text("❌ Аккаунт пользователя деактивирован.")
        else:
            await update.message.reply_text("❌ Пользователь не найден или недоступен. Попробуйте снова.")
        
        return States.SELECTING_RECIPIENT
    
    except Forbidden:
        await update.message.reply_text("❌ У бота нет прав писать этому пользователю. Возможно, он заблокировал бота.")
        return States.SELECTING_RECIPIENT
    
    except Exception as e:
        await update.message.reply_text(
            "❌ Ошибка при проверке пользователя.\n"
            "Пожалуйста, попробуйте снова:"
        )
        return States.SELECTING_RECIPIENT



async def edit_text_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ручной ввод текста"""
    text = update.message.text
    
    # Сохраняем текст
    context.user_data['text'] = text
    
    await update.message.reply_text("✅ Текст сохранен!")
    await confirm_valentine(update, context)
    
    return States.CONFIRMING


async def confirm_valentine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение валентинки перед отправкой"""
    # Получаем данные из context.user_data
    recipient = context.user_data.get('recipient', 'не указан')
    text = context.user_data.get('text', 'С днём Святого Валентина! ❤️')
    
    confirmation_text = f"""
    💝 **ВСЁ ГОТОВО К ОТПРАВКЕ!**
    
    📤 **Получатель:** @{recipient}
    📝 **Текст:** {text}
    
    Проверь данные. Всё верно?
    """
    
    # Демо-изображение для подтверждения
    demo_image_text = f"[ДЕМО] Валентинка для @{recipient}"
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🖼 **ИЗОБРАЖЕНИЕ:**\n{demo_image_text}\n\n{confirmation_text}",
        reply_markup=get_confirmation_keyboard(),
        parse_mode='Markdown'
    )


async def send_valentine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка валентинки (демо-режим)"""
    query = update.callback_query
    
    # Получаем данные из context.user_data
    recipient = context.user_data.get('recipient', 'пользователь')
    text = context.user_data.get('text', 'С днём Святого Валентина! ❤️')
    
    # Демо-отправка
    await query.edit_message_text(
        f"📤 ОТПРАВЛЯЮ ВАЛЕНТИНКУ...\n\n"
        f"Кому: @{recipient}\n"
        f"Текст: {text}\n\n"
        f"[ДЕМО-РЕЖИМ] Валентинка не была отправлена реальному пользователю"
    )
    
    # Имитация отправки
    valentine_preview = f"""
    💌 ВАЛЕНТИНКА @{recipient} УСПЕШНО ОТПРАВЛЕНА!
    
    Текст сообщения:
    {text}
    
    ❤️ С днём Святого Валентина! ❤️
    """
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=valentine_preview
    )
    
    # Очищаем user_data (ConversationHandler сделает это сам, но для надёжности)
    context.user_data.clear()