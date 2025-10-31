import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters
import sqlite3

# Настройки
BOT_TOKEN = "8283353760:AAEWh--gnJkMW3lwl601EqvCs_7_mnuLBOA"
ADMIN_ID = 7739672364

# Подключение к БД
def get_db():
    conn = sqlite3.connect('bot_database.db')
    return conn

# Проверка прав админа
def check_admin_rights(user_id, right_type):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {right_type} FROM admins WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

# Клавиатуры
def main_admin_keyboard():
    return ReplyKeyboardMarkup([
        ["▷Продолжить▷"]
    ], resize_keyboard=True)

def post_type_keyboard():
    return ReplyKeyboardMarkup([
        ["Текст", "Картина", "GIF"],
        ["Видео", "Файл", "🔙Назад"]
    ], resize_keyboard=True)

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id == ADMIN_ID or check_admin_rights(user_id, "can_post"):
        await update.message.reply_text(
            "*Привет! Я бот для автоматизации постинга в Telegram каналы.*\n\n"
            "• Пересылаю контент во все подключенные каналы\n"
            "• Поддержка текста, медиа и форматирования\n\n"
            "_Создано при поддержке @GordScripts_\n"
            "Для сотрудничества: @akookd",
            parse_mode='Markdown',
            reply_markup=main_admin_keyboard()
        )
    else:
        await update.message.reply_text("❌ *Недостаточно прав!*", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "▷Продолжить▷":
        if user_id == ADMIN_ID or check_admin_rights(user_id, "can_add_channels"):
            await update.message.reply_text(
                "📋 *Добавьте бота в нужный канал* \n\n"
                "⚠️ *ОБЯЗАТЕЛЬНО ВКЛЮЧИТЕ ДОСТУП К УПРАВЛЕНИЮ СООБЩЕНИЯМИ!*\n"
                "Не перепутайте с управлением каналом!",
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardMarkup([["Я добавил✔️"]], resize_keyboard=True)
            )
        else:
            await update.message.reply_text("❌ *Недостаточно прав для добавления каналов!*", parse_mode='Markdown')
    
    elif text == "Я добавил✔️":
        await update.message.reply_text("📝 *Отправьте Username канала* (например, @channel_name)", parse_mode='Markdown')

# Добавление канала в БД
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_username = update.message.text
    user_id = update.effective_user.id
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO channels (username, added_by) VALUES (?, ?)", (channel_username, user_id))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(f"✅ *Канал {channel_username} успешно добавлен!*", parse_mode='Markdown')
        
        # Предлагаем создать пост
        await update.message.reply_text(
            "📮 *Выберите тип поста:*",
            reply_markup=post_type_keyboard(),
            parse_mode='Markdown'
        )
        
    except sqlite3.IntegrityError:
        await update.message.reply_text("❌ *Этот канал уже добавлен!*", parse_mode='Markdown')

# Обработка медиа-контента
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика обработки фото, видео, GIF и файлов
    # Сохраняем в context.user_data и переходим к настройкам форматирования
    pass

# Настройка форматирования поста
async def post_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Разметка: Text", callback_data="markup_text")],
        [InlineKeyboardButton("Превью ссылок: Откл.", callback_data="preview_off")],
        [InlineKeyboardButton("Отмена", callback_data="cancel")]
    ]
    
    await update.message.reply_text(
        "⚙️ *Настройки поста:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Панель управления админа
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        keyboard = [
            ["Создать пост во все каналы"],
            ["Назначить администратора", "Добавить канал для постинга"]
        ]
        
        await update.message.reply_text(
            "🛠 *ВЫ АДМИН!*\nВыберите действие:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
            parse_mode='Markdown'
        )

# Назначение прав админа
async def set_admin_rights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика изменения прав через инлайн кнопки с галочками/крестиками
    pass

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.run_polling()

if __name__ == "__main__":
    main()
