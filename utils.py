from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes
from telegram.error import Forbidden, BadRequest
from io import BytesIO
from enums import States
from keyboards import get_image_edit_keyboard, get_confirmation_keyboard, get_back_keyboard, get_text_edit_keyboard
from image_api import generate_valentine_image
from gpt_api import generate_valentine_text
import re
from db import SqliteDb

async def generate_image():
        img = generate_valentine_image()
        
        # Конвертируем PIL Image в bytes для отправки
        bio = BytesIO()
        bio.name = 'valentine.png'
        img.save(bio, 'PNG')
        bio.seek(0)
        return bio


async def generate_text(topic):
    text = await generate_valentine_text(topic)
    return text

def is_valid_username(username: str) -> bool:
    """
    Проверяет корректность Telegram username
    """
    if not username:
        return False
    
    # Убираем @ если есть
    if username.startswith('@'):
        username = username[1:]
    
    # Проверка: длина 5-32, только буквы, цифры, _, начинается с буквы
    return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$', username))

async def select_recipient(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение username получателя с проверкой существования"""
    import os
    db = SqliteDb(os.getenv("SQLITE_PATH"))
    username_input = update.message.text.strip()
    
    # Убираем @ если пользователь ввёл
    clean_username = username_input.replace('@', '')
    
    if not clean_username:
        await update.message.reply_text(
            "❌ Имя пользователя не может быть пустым.\n"
            "Пожалуйста, введите @ник_в_телеграме получателя корректно:",
            reply_markup=get_back_keyboard()
        )
        return States.SELECTING_RECIPIENT
    elif not is_valid_username(clean_username):
        await update.message.reply_text(
            f"❌ {clean_username} - некорректное имя пользователя в Telegram!\n"
            "Пожалуйста, введите @ник_в_телеграме получателя корректно:",
            reply_markup=get_back_keyboard()
        )
        return States.SELECTING_RECIPIENT
    elif not db.username_exists(clean_username):
        await update.message.reply_text(
            f"❌ Пользователь {clean_username} ещё не стартовал работу с ботом. Придумайте, как заставить его это сделать!\n"
            "Можете ввести имя другого пользователя!",
            reply_markup=get_back_keyboard()
        )
        return States.SELECTING_RECIPIENT
    
    try:
        context.user_data['recipient'] = clean_username
        context.user_data['recipient_id'] = db.get_telegram_id_by_username(clean_username)
        
        status_msg = await update.message.reply_text(
            f"🎨 Генерирую валентинку для @{clean_username}...\n\n"
            f"⏱ Это может занять определенное время, но вы же готовы подождать ради своей любви? 🙏❤️\n\n"
            f"Не переживайте, все будет. (не гоните лошадей)"
        )
        try:
            bio = await generate_image()

            await status_msg.delete()

            caption = (
                f"❤️ **Валентинка для @{clean_username}** ❤️\n\n"
                f"💝 Нажми кнопки ниже, чтобы настроить или отправить"
            )
            
            sent_message = await update.message.reply_photo(
                    photo=bio,
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=get_image_edit_keyboard()
                )
            
            context.user_data['generated_image'] = sent_message.photo[-1].file_id
        except Exception as e:
            await status_msg.delete()

            await update.message.reply_text(
                text=f"⚠️ Не удалось сгенерировать изображение.\n",
                reply_markup=get_back_keyboard()
            )
            
        return States.GENERATING_IMAGE

    except BadRequest as e:
        error_text = str(e).lower()
        
        if "chat not found" in error_text:
            await update.message.reply_text("❌ Пользователь не найден. Убедитесь, что username правильный и пользователь писал боту хотя бы раз.")
        elif "user is deactivated" in error_text:
            await update.message.reply_text("❌ Аккаунт пользователя деактивирован.",
                                            reply_markup=get_back_keyboard())
        else:
            await update.message.reply_text("❌ Пользователь не найден или недоступен. Попробуйте снова.",
                                            reply_markup=get_back_keyboard())
        
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
    
    await confirm_valentine(update, context)
    
    return States.CONFIRMING


async def confirm_valentine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение валентинки перед отправкой"""
    # Получаем данные из context.user_data
    recipient = context.user_data.get('recipient', 'не указан')
    text = context.user_data.get('text', 'С днём Святого Валентина! ❤️')
    image_file_id = context.user_data.get('generated_image')
    
    # Проверяем, есть ли сохраненное фото
    if not image_file_id:
        await update.callback_query.edit_message_text(
            "❌ **Ошибка:** Изображение не найдено!\n"
            "Пожалуйста, создайте новую валентинку.",
            parse_mode='Markdown'
        )
        return
    
    # Отправляем фото с текстом
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=image_file_id,
        caption=(
            "💝 **ВСЁ ГОТОВО К ОТПРАВКЕ!**\n\n"
            f"📤 **Получатель:** @{recipient}\n"
            f"📝 **Текст:** {text}\n\n"
            "✅ Проверь данные. Всё верно?"
        ),
        parse_mode='Markdown',
        reply_markup=get_confirmation_keyboard()
    )
    
    # Удаляем предыдущее сообщение с кнопкой
    try:
        await update.callback_query.delete_message()
    except:
        pass


async def send_valentine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка валентинки реальному пользователю"""
    query = update.callback_query
    
    # Получаем данные из context.user_data
    recipient_id = context.user_data.get('recipient_id')
    recipient = context.user_data.get('recipient')
    text = context.user_data.get('text', 'С днём Святого Валентина! ❤️')
    image_file_id = context.user_data.get('generated_image')
    
    try:
        # Удаляем сообщение с фото
        await query.delete_message()
        
        # Отправляем статус отправки
        status_msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📤 **Отправляю валентинку** @{recipient}...\n\n⏳ Пожалуйста, подождите...",
            parse_mode='Markdown'
        )
        
        # Отправляем фото получателю
        await context.bot.send_photo(
            chat_id=recipient_id,
            photo=image_file_id,
            caption=f"💌 **Вам валентинка от анонима!**\n\nТекст: {text}\n\n❤️ С днём всех влюбленных! ❤️",
            parse_mode='Markdown'
        )
        
        # Удаляем статус и отправляем сообщение об успехе
        await status_msg.delete()
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ **Валентинка @{recipient} успешно отправлена!**\n\n"
                 f"💫 Хочешь создать еще одну?",
            parse_mode='Markdown',
            reply_markup=get_back_keyboard()  # Клавиатура для нового создания
        )
        
    except Exception as e:
        error_message = str(e)
        if "chat not found" in error_message:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ **Ошибка:** Пользователь @{recipient} не найден!\n\n"
                     f"Убедитесь, что пользователь начал диалог с ботом.",
                parse_mode='Markdown',
                reply_markup=get_back_keyboard()
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ **Ошибка при отправке:**\n{error_message}",
                parse_mode='Markdown',
                reply_markup=get_back_keyboard()
            )
    
    context.user_data.clear()
    return ConversationHandler.END


async def handle_topic_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода темы валентинки"""
    topic = update.message.text
    context.user_data['valentine_topic'] = topic
    
    # Показываем процесс генерации
    wait_message = await update.message.reply_text(
        f"⏳ **Генерируем текст на тему:**\n\"{topic}\"\n\nЭто займет около 10 секунд...",
        parse_mode='Markdown'
    )
    
    # Генерируем текст
    generated_text = await generate_text(topic)
    context.user_data['text'] = generated_text
    
    # Удаляем сообщение о генерации
    await wait_message.delete()
    
    # Отправляем фото с готовым текстом
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=context.user_data.get('generated_image'),  # Сохраните file_id фото заранее
        caption=f"✨ **Сгенерированный текст:**\n\n{generated_text}\n\n"
                "📌 Что делаем дальше?",
        parse_mode='Markdown',
        reply_markup=get_text_edit_keyboard()
    )
    
    return States.GENERATING_TEXT