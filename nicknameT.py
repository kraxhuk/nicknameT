import logging
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
import logging
logging.basicConfig(level=logging.INFO)
# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Стани розмови
CHOOSE_LANGUAGE, CHOOSE_PLATFORM, CHOOSE_THEME, CHOOSE_ACTION, GENERATE_NICKS, SET_CONDITIONS, ADD_EMOJI, CONFIRM_NICK, CONFIRM_FINAL, CREATOR_INPUT_NAME, CREATOR_GENERATE = range(11)

# Бази даних для генерації
UKRAINIAN_WORDS = [
    'Фенікс', 'Мисливець', 'Геній', 'Воїн', 'Тінь', 'Вітер', 'Беркут', 
    'Козак', 'Сокіл', 'Буревій', 'Гром', 'Метелик', 'Дракон', 'Ворон',
    'Привид', 'Титан', 'Яструб', 'Бистрий', 'Невидимий', 'Фантом'
]

EMOJIS = ['🔥', '🌟', '🎮', '📸', '🎭', '💫', '⚡', '❤️', '👑', '🐺', '🦅', '🐉']

# Теми для платформ
PLATFORM_THEMES = {
    'instagram': ['Фотографія', 'Подорожі', 'Мода', 'Їжа', 'Мистецтво', 'Спорт'],
    'tiktok': ['Танці', 'Комедія', 'Життя', 'Челленджі', 'Музика', 'Освіта'],
    'youtube': ['Геймінг', 'Влоги', 'Навчання', 'Огляди', 'DIY', 'Кулінарія'],
    'twitch': ['Стрими', 'Геймінг', 'Музика', 'Творчість', 'Спілкування', 'IRL'],
    'telegram': ['Анонімність', 'Технології', 'Меми', 'Новини', 'Спільноти', 'Бізнес'],
    'snapchat': ['Друзі', 'Події', 'Селфі', 'Розваги', 'Секрети', 'Тренди']
}

def generate_random_nick(length=None):
    """Генерує абсолютно випадковий нік з англійських літер"""
    if length is None:
        length = random.randint(4, 7)
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def generate_name_based_nicks(name, language):
    """Генерує ніки на основі імені"""
    name = name.lower().strip()
    variants = set()
    
    while len(variants) < 6:
        if language == 'ukrainian':
            # Українські варіанти
            suffix = random.choice(['кс', 'сс', 'нко', 'чок', 'ич', 'юга', 'яра', 'іна'])
            prefix = random.choice(['', 'super', 'ultra', 'мад', 'про'])
            nick = f"{prefix}{name[:3]}{suffix}"
            
            # Додаємо варіанти з перестановкою букв
            if random.random() > 0.5:
                nick = name[:2] + ''.join(random.sample(name[2:] + 'xyz', 3))
        else:
            # Англійські варіанти
            suffix = random.choice(['x', 'ss', 'er', 'ex', 'ox', 'ix', 'as', 'os'])
            prefix = random.choice(['', 'super', 'ultra', 'pro_', 'neo'])
            nick = f"{prefix}{name[:3]}{suffix}"
            
            # Додаємо варіанти з додаванням випадкових букв
            if random.random() > 0.5:
                nick = name[:2] + ''.join(random.choice(string.ascii_lowercase) for _ in range(3))
        
        # Додаємо числа у 30% випадків
        if random.random() > 0.7:
            nick += str(random.randint(1, 999))
        
        variants.add(nick)
    
    return list(variants)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Перевіряємо, чи є повідомлення
    if not update.message:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Будь ласка, почніть з команди /start")
        return ConversationHandler.END
    
    user = update.message.from_user
    logger.info("Користувач %s розпочав взаємодію", user.first_name)
    
    keyboard = [
        [InlineKeyboardButton("🇺🇦 Українська", callback_data='ukrainian')],
        [InlineKeyboardButton("🇬🇧 English (random letters)", callback_data='english')],
        [InlineKeyboardButton("✨ Створювач", callback_data='creator')]
    ]
    
    await update.message.reply_text(
        f"👋 Привіт, {user.first_name}! Виберіть опцію:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CHOOSE_LANGUAGE

async def start_from_scratch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Нова функція для запуску з початку
    keyboard = [
        [InlineKeyboardButton("🇺🇦 Українська", callback_data='ukrainian')],
        [InlineKeyboardButton("🇬🇧 English (random letters)", callback_data='english')],
        [InlineKeyboardButton("✨ Створювач", callback_data='creator')]
    ]
    
    await update.callback_query.message.reply_text(
        "👋 Виберіть опцію:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CHOOSE_LANGUAGE


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    if choice == 'creator':
        await query.edit_message_text(
            text="✏️ Введіть своє ім'я (або будь-яке слово), на основі якого я згенерую ніки:"
        )
        return CREATOR_INPUT_NAME
    
    context.user_data['language'] = choice
    logger.info("Обрана опція: %s", choice)
    
    keyboard = [
        [InlineKeyboardButton("Instagram", callback_data='instagram'),
         InlineKeyboardButton("TikTok", callback_data='tiktok')],
        [InlineKeyboardButton("YouTube", callback_data='youtube'),
         InlineKeyboardButton("Twitch", callback_data='twitch')],
        [InlineKeyboardButton("Telegram", callback_data='telegram'),
         InlineKeyboardButton("Snapchat", callback_data='snapchat')]
    ]
    
    await query.edit_message_text(
        text="Оберіть платформу:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CHOOSE_PLATFORM

async def choose_platform(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    platform = query.data
    context.user_data['platform'] = platform
    logger.info("Обрана платформа: %s", platform)
    
    themes = PLATFORM_THEMES[platform]
    keyboard = [[InlineKeyboardButton(theme, callback_data=f"theme_{i}")] for i, theme in enumerate(themes)]
    
    await query.edit_message_text(
        text=f"Обрано платформу: {platform.capitalize()}\nОберіть тему:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CHOOSE_THEME

async def choose_theme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    platform = context.user_data['platform']
    theme_index = int(query.data.split('_')[1])
    theme = PLATFORM_THEMES[platform][theme_index]
    context.user_data['theme'] = theme
    logger.info("Обрана тема: %s", theme)
    
    keyboard = [
        [InlineKeyboardButton("🎲 Згенерувати", callback_data='generate'),
         InlineKeyboardButton("⚙️ Вказати умови", callback_data='conditions')],
        [InlineKeyboardButton("😊 Додати емоджі", callback_data='emoji')]
    ]
    
    await query.edit_message_text(
        text=f"Обрана тема: {theme}\nОберіть дію:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CHOOSE_ACTION

async def choose_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    action = query.data
    
    if action == 'generate':
        return await generate_nicks(update, context)
    elif action == 'conditions':
        await query.edit_message_text(
            text="📝 Вкажіть свої умови для нікнейма (довжина, стиль, особливі побажання):\n"
                 "Наприклад: 'хочу нік з 5 букв у стилі фентезі'"
        )
        return SET_CONDITIONS
    elif action == 'emoji':
        await query.edit_message_text(
            text="Введіть емоджі які хочете додати до нікнейма (наприклад: 🔥🌟):"
        )
        return ADD_EMOJI

async def creator_input_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        name = update.message.text
        context.user_data['creator_name'] = name
        await update.message.reply_text(
            f"🔮 Добре, {name}! Тепер оберіть мову для нікнеймів:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🇺🇦 Українська", callback_data='creator_ukrainian')],
                [InlineKeyboardButton("🇬🇧 English", callback_data='creator_english')]
            ])
        )
        return CREATOR_GENERATE
    return CHOOSE_LANGUAGE

async def creator_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    language = query.data.replace('creator_', '')
    name = context.user_data.get('creator_name', 'User')
    
    nicks = generate_name_based_nicks(name, language)
    context.user_data['nicks'] = nicks
    
    keyboard = [[InlineKeyboardButton(nick, callback_data=f"nick_{i}")] for i, nick in enumerate(nicks)]
    
    await query.edit_message_text(
        text=f"🎉 Ось унікальні ніки на основі імені {name}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CONFIRM_NICK

async def generate_nicks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query:
        await query.answer()
    
    language = context.user_data.get('language', 'english')
    theme = context.user_data.get('theme', '')
    
    # Генерація 6 унікальних нікнеймів
    nicks = set()
    while len(nicks) < 6:
        if language == 'ukrainian':
            word1 = random.choice(UKRAINIAN_WORDS)
            word2 = random.choice(UKRAINIAN_WORDS)
            nick = f"{word1}_{word2}"
            if random.random() > 0.7:
                nick += str(random.randint(1, 999))
        else:
            nick = generate_random_nick()
            if random.random() > 0.5:
                nick += str(random.randint(1, 999))
        
        nicks.add(nick)
    
    nicks = list(nicks)
    context.user_data['nicks'] = nicks
    
    keyboard = [[InlineKeyboardButton(nick, callback_data=f"nick_{i}")] for i, nick in enumerate(nicks)]
    
    if query:
        await query.edit_message_text(
            text="🎉 Ось 6 варіантів нікнеймів:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text="🎉 Ось 6 варіантів нікнеймів:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    return CONFIRM_NICK

async def set_conditions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_text = update.message.text
    context.user_data['conditions'] = user_text
    logger.info("Користувач вказав умови: %s", user_text)
    
    await update.message.reply_text("🔮 Генерую ніки з урахуванням ваших побажань...")
    return await generate_nicks(update, context)

async def add_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_emojis = update.message.text
    context.user_data['emojis'] = user_emojis
    
    if 'nicks' not in context.user_data:
        await update.message.reply_text("Спочатку згенеруйте нікнейми!")
        return await generate_nicks(update, context)
    
    nicks = context.user_data['nicks']
    emoji_list = [e for e in user_emojis if e in EMOJIS]
    
    if not emoji_list:
        emoji_list = random.sample(EMOJIS, 2)
    
    modified_nicks = []
    for nick in nicks:
        if random.random() > 0.5:
            modified = f"{random.choice(emoji_list)}{nick}{random.choice(emoji_list)}"
        else:
            modified = f"{nick}{''.join(random.sample(emoji_list, 2))}"
        modified_nicks.append(modified)
    
    context.user_data['nicks'] = modified_nicks
    
    keyboard = [[InlineKeyboardButton(nick, callback_data=f"nick_{i}")] for i, nick in enumerate(modified_nicks)]
    
    await update.message.reply_text(
        text="😊 Ось ніки з емоджі:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CONFIRM_NICK

async def confirm_nick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    nick_index = int(query.data.split('_')[1])
    chosen_nick = context.user_data['nicks'][nick_index]
    context.user_data['chosen_nick'] = chosen_nick
    
    keyboard = [
        [InlineKeyboardButton("✅ Так", callback_data='confirm_yes'),
         InlineKeyboardButton("❌ Ні", callback_data='confirm_no')]
    ]
    
    await query.edit_message_text(
        text=f"Ви обрали: {chosen_nick}\nВи впевнені?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CONFIRM_FINAL

async def confirm_final(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm_yes':
        chosen_nick = context.user_data['chosen_nick']
        await query.edit_message_text(
            text=f"🎉 Ваш нікнейм: {chosen_nick}\nГарного використання!"
        )
        context.user_data.clear()
        return ConversationHandler.END
    else:
        # Створюємо нове повідомлення замість повторного використання старого
        await query.edit_message_text("Почнемо спочатку!")
        return await start_from_scratch(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('До побачення! Якщо захочете новий нік - просто напишіть /start')
    context.user_data.clear()
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Помилка: %s", context.error, exc_info=True)
    if update.message:
        await update.message.reply_text('Сталася помилка. Спробуйте ще раз.')

def main() -> None:
    application = Application.builder().token("7711097869:AAEEBOX2OT_W_fQm0P30IKlEIPvUUmYoqiE").build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE_LANGUAGE: [CallbackQueryHandler(choose_language)],
            CREATOR_INPUT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, creator_input_name)],
            CREATOR_GENERATE: [CallbackQueryHandler(creator_generate)],
            CHOOSE_PLATFORM: [CallbackQueryHandler(choose_platform)],
            CHOOSE_THEME: [CallbackQueryHandler(choose_theme)],
            CHOOSE_ACTION: [CallbackQueryHandler(choose_action)],
            GENERATE_NICKS: [
                CallbackQueryHandler(generate_nicks, pattern='^generate$'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, generate_nicks)
            ],
            SET_CONDITIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_conditions)],
            ADD_EMOJI: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_emoji)],
            CONFIRM_NICK: [CallbackQueryHandler(confirm_nick, pattern='^nick_')],
            CONFIRM_FINAL: [CallbackQueryHandler(confirm_final, pattern='^confirm_')],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    application.run_polling()
    print("Бот запущено!")

if __name__ == '__main__':
    main()