from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ==================== КЛАВИАТУРЫ ====================

def get_start_keyboard():
    """Главное меню"""
    keyboard = [
        [InlineKeyboardButton("💝 Создать валентинку", callback_data="create_valentine")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_image_edit_keyboard():
    """Клавиатура для редактирования изображения"""
    keyboard = [
        [InlineKeyboardButton("🔄 Перегенерировать", callback_data="regenerate_image"),
         InlineKeyboardButton("✅ Оставить", callback_data="keep_image")],
        [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_text_creation_keyboard():
    """Клавиатура выбора способа создания текста"""
    keyboard = [
        #[InlineKeyboardButton("✨ Сгенерировать текст", callback_data="generate_text")],
        [InlineKeyboardButton("✍️ Написать самому", callback_data="edit_text_manual")],
        [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_text_edit_keyboard():
    """Клавиатура для редактирования текста"""
    keyboard = [
#        [InlineKeyboardButton("🔄 Перегенерировать", callback_data="generate_text")],
        [InlineKeyboardButton("✍️ Написать самому(отредактировать)", callback_data="edit_text_manual")],
        [InlineKeyboardButton("✅ Оставить этот", callback_data="keep_text")],
        [InlineKeyboardButton("🔙 Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard():
    """Клавиатура подтверждения перед отправкой"""
    keyboard = [
        [InlineKeyboardButton("📤 Отправить", callback_data="send_valentine")],
        [InlineKeyboardButton("🔄 Изменить изображение", callback_data="regenerate_image")],
        [InlineKeyboardButton("✍️ Изменить текст", callback_data="edit_text_manual")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Клавиатура возврата в главное меню"""
    keyboard = [[InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_start")]]
    return InlineKeyboardMarkup(keyboard)