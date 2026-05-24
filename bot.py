"""
Телеграм-бот: Подстилочный материал зоотехнический
ООО «Дэлрой Экспо» — Производство Вологда / Киров
Продажи: ИП Файзиев Эмиль Энгельсович
"""

import os, logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)

TOKEN       = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_СЮДА")
ADMIN_ID    = int(os.getenv("ADMIN_ID", "0"))
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "+7 XXX XXX XX XX")

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

(MAIN_MENU, ANIMAL_TYPE, QUANTITY, DISTRICT,
 CONTACT_NAME, CONTACT_PHONE, CONFIRM) = range(7)

PRODUCT = {
    "name":     "Материал подстилочный зоотехнический",
    "wood":     "Ель / Сосна (хвойные породы)",
    "fraction": "0,5–3 см",
    "moisture": "8–12%",
    "package":  "Брикеты 60×30×40 см, ~20 кг, 0,25 м³",
    "truck":    "16–18,8 тонн (800–880 брикетов)",
    "price_kg": 12.0,
    "cert":     "Сертификат качества на каждую партию",
    "origin":   "Собственное производство — Вологда / Киров",
}

ANIMALS = {
    "🐴 Лошади / Конный двор":           "Мировой стандарт. Московские ипподромы используют этот продукт.",
    "🐄 КРС (коровы, быки)":             "Подходит для коровников. Влажность 8–12% — оптимально.",
    "🐓 Птицеводство (бройлеры)":        "Цикл 42 дня — отлично. Применяется на птицефабриках.",
    "🥚 Несушки / Родительское стадо":   "Применимо при хорошей вентиляции помещения.",
    "🐷 Свиноводство":                   "Подходит для свинарников и откорма.",
    "🔀 Смешанное хозяйство":            "Универсальный вариант для нескольких видов животных.",
}

def main_keyboard():
    return ReplyKeyboardMarkup([
        ["📦 Оформить заказ"],
        ["🧮 Калькулятор расхода", "📋 О продукте"],
        ["📞 Связаться с менеджером"],
    ], resize_keyboard=True)

def animal_keyboard():
    return ReplyKeyboardMarkup([
        ["🐴 Лошади / Конный двор"],
        ["🐄 КРС (коровы, быки)"],
        ["🐓 Птицеводство (бройлеры)"],
        ["🥚 Несушки / Родительское стадо"],
        ["🐷 Свиноводство"],
        ["🔀 Смешанное хозяйство"],
        ["🔙 Назад в меню"],
    ], resize_keyboard=True)

def confirm_keyboard():
    return ReplyKeyboardMarkup([
        ["✅ Подтвердить заказ"],
        ["✏️ Изменить данные", "❌ Отменить"],
    ], resize_keyboard=True)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Здравствуйте, {user.first_name}!\n\n"
        "🌿 *Подстилочный материал зоотехнический*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🪵 Древесная стружка · Ель и Сосна\n"
        "📦 Брикеты · удобная фасовка\n"
        "💧 Влажность 8–12% · готова к применению\n"
        "🏭 Собственное производство · Вологда / Киров\n"
        "✅ Сертификат качества на каждую партию\n\n"
        "🐴 Лошади · 🐄 КРС · 🐓 Птица · 🐷 Свиноводство\n\n"
        "Выберите действие 👇",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )
    return MAIN_MENU

async def main_menu_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "📦 Оформить заказ":
        await update.message.reply_text(
            "📦 *Оформление заказа*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Шаг 1️⃣ из 4️⃣ — Вид животных\n\n"
            "🐾 Для каких животных нужна подстилка?",
            parse_mode="Markdown", reply_markup=animal_keyboard()
        )
        return ANIMAL_TYPE
    elif text == "🧮 Калькулятор расхода":
        await calculator_start(update, ctx); return MAIN_MENU
    elif text == "📋 О продукте":
        await about_product(update, ctx); return MAIN_MENU
    elif text == "📞 Связаться с менеджером":
        await contact_manager(update, ctx); return MAIN_MENU
    else:
        await update.message.reply_text("👇 Выберите пункт из меню:", reply_markup=main_keyboard())
        return MAIN_MENU

async def animal_type_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "🔙 Назад в меню":
        await update.message.reply_text("🏠 Главное меню:", reply_markup=main_keyboard())
        return MAIN_MENU
    if text not in ANIMALS:
        await update.message.reply_text("⚠️ Выберите из предложенных вариантов:", reply_markup=animal_keyboard())
        return ANIMAL_TYPE
    ctx.user_data["animal"] = text
    await update.message.reply_text(
        f"📦 *Оформление заказа*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Шаг 2️⃣ из 4️⃣ — Количество\n\n"
        f"✅ {text}\n"
        f"_{ANIMALS[text]}_\n\n"
        f"🚛 *1 фура = 16–18,8 тонн*\n"
        f"💰 Цена: 12 руб/кг · доставка оплачивается отдельно\n\n"
        f"Укажите нужный объём:\n"
        f"• Количество фур: *1 фура*, *2 фуры*\n"
        f"• Или тоннаж: *16 тонн*, *35 тонн*",
        parse_mode="Markdown", reply_markup=ReplyKeyboardRemove()
    )
    return QUANTITY

async def quantity_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["quantity"] = update.message.text.strip()
    await update.message.reply_text(
        "📦 *Оформление заказа*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Шаг 3️⃣ из 4️⃣ — Хозяйство и район\n\n"
        "📍 Укажите район и название хозяйства:\n"
        "_Например: Арский район, ООО Агрофирма Север_\n\n"
        "ℹ️ Нужно для расчёта стоимости доставки",
        parse_mode="Markdown"
    )
    return DISTRICT

async def district_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["district"] = update.message.text.strip()
    await update.message.reply_text(
        "📦 *Оформление заказа*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Шаг 4️⃣ из 4️⃣ — Ваши контакты\n\n"
        "👤 Ваше имя и должность:\n"
        "_Например: Иван Иванов, главный зоотехник_",
        parse_mode="Markdown"
    )
    return CONTACT_NAME

async def contact_name_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["contact_name"] = update.message.text.strip()
    await update.message.reply_text(
        "📞 Номер телефона для связи:\n_Например: +7 900 123 45 67_",
        parse_mode="Markdown"
    )
    return CONTACT_PHONE

async def contact_phone_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["contact_phone"] = update.message.text.strip()
    d = ctx.user_data
    price_note = "💰 Цена: 12 руб/кг (без доставки)\n"
    try:
        qty = d.get("quantity", "")
        if "фур" in qty.lower():
            n = float(''.join(c for c in qty.split()[0] if c.isdigit() or c=='.'))
            price_note = f"💰 Ориентировочно: *{int(n*17000*12):,} руб.* (без доставки)\n".replace(",", " ")
        elif "тонн" in qty.lower() or "тн" in qty.lower():
            n = float(''.join(c for c in qty.split()[0] if c.isdigit() or c=='.'))
            price_note = f"💰 Ориентировочно: *{int(n*1000*12):,} руб.* (без доставки)\n".replace(",", " ")
    except: pass
    await update.message.reply_text(
        f"📋 *Проверьте вашу заявку*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🐾 Животные: {d.get('animal','—')}\n"
        f"🪵 Стружка ель/сосна, фракция 0,5–3 см\n"
        f"💧 Влажность: 8–12%\n"
        f"⚖️ Количество: {d.get('quantity','—')}\n"
        f"📍 Хозяйство: {d.get('district','—')}\n"
        f"👤 Контакт: {d.get('contact_name','—')}\n"
        f"📞 Телефон: {d.get('contact_phone','—')}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{price_note}"
        f"🚚 Доставка рассчитывается индивидуально\n"
        f"💳 Оплата: 100% предоплата\n"
        f"📄 Сертификат качества прилагается",
        parse_mode="Markdown", reply_markup=confirm_keyboard()
    )
    return CONFIRM

async def confirm_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    d = ctx.user_data
    if text == "✅ Подтвердить заказ":
        user = update.effective_user
        try:
            await ctx.bot.send_message(chat_id=ADMIN_ID, parse_mode="Markdown", text=(
                f"🆕 *НОВАЯ ЗАЯВКА*\n━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 {d.get('contact_name','—')}\n📞 {d.get('contact_phone','—')}\n\n"
                f"🐾 {d.get('animal','—')}\n🪵 Стружка ель/сосна, 0,5–3 см, 8–12%\n"
                f"⚖️ {d.get('quantity','—')}\n📍 {d.get('district','—')}\n\n"
                f"Telegram: @{user.username or '—'} (ID: `{user.id}`)"
            ))
        except Exception as e: logger.error(e)
        await update.message.reply_text(
            f"✅ *Заявка успешно принята!*\n\n"
            f"👋 Менеджер свяжется с вами по номеру\n📞 *{d.get('contact_phone','—')}*\n"
            f"⏰ в течение 2 рабочих часов\n\n"
            f"По срочным вопросам: 📱 *{ADMIN_PHONE}*\n\n🙏 Спасибо за обращение!",
            parse_mode="Markdown", reply_markup=main_keyboard()
        )
        ctx.user_data.clear(); return MAIN_MENU
    elif text == "✏️ Изменить данные":
        ctx.user_data.clear()
        await update.message.reply_text("🔄 Начнём заново:", reply_markup=animal_keyboard())
        return ANIMAL_TYPE
    elif text == "❌ Отменить":
        ctx.user_data.clear()
        await update.message.reply_text("❌ Отменено.\n🏠 Главное меню:", reply_markup=main_keyboard())
        return MAIN_MENU
    return CONFIRM

async def calculator_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 *Калькулятор расхода подстилки*\n━━━━━━━━━━━━━━━━━━━━\n\n"
        "🪵 Стружка ель/сосна · фракция 0,5–3 см\n\nВыберите вид животных 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🐴 Лошади (денник 12 м²)", callback_data="calc_horse")],
            [InlineKeyboardButton("🐄 КРС дойный (9 м²/гол)", callback_data="calc_dairy"),
             InlineKeyboardButton("🐄 КРС откорм (5 м²/гол)", callback_data="calc_beef")],
            [InlineKeyboardButton("🐓 Бройлеры (20 гол/м²)", callback_data="calc_broiler"),
             InlineKeyboardButton("🥚 Несушки (7,5 гол/м²)", callback_data="calc_hen")],
            [InlineKeyboardButton("🐷 Свиноматка (2,8 м²/гол)", callback_data="calc_sow"),
             InlineKeyboardButton("🐷 Откорм свиней (1 м²/гол)", callback_data="calc_pig")],
        ])
    )

async def calculator_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    configs = {
        "calc_horse":   ("🐴 Лошади",       12,  "m2", 10),
        "calc_dairy":   ("🐄 КРС дойный",    9,  "m2", 8),
        "calc_beef":    ("🐄 КРС откорм",    5,  "m2", 6),
        "calc_broiler": ("🐓 Бройлеры",      20, "hl", 7),
        "calc_hen":     ("🥚 Несушки",       7.5,"hl", 6),
        "calc_sow":     ("🐷 Свиноматка",    2.8,"m2", 7),
        "calc_pig":     ("🐷 Откорм свиней", 1.0,"m2", 5),
    }
    if query.data not in configs: return
    name, norm, mode, layer = configs[query.data]
    D = 85; truck = 17000
    per_m2 = D * (layer/100); m2t = truck/per_m2
    if mode == "hl":
        pt = round(m2t*norm/1000)*1000
        line = f"🐾 ~{pt:,} голов".replace(",", " ")
        div  = f"Поголовье ÷ {pt:,} = кол-во фур".replace(",", " ")
    else:
        pt = round(m2t/norm)
        line = f"🐾 ~{pt} голов (по {norm} м²/гол)"
        div  = f"Поголовье ÷ {pt} = кол-во фур"
    await query.edit_message_text(
        f"🧮 *{name}*\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📐 Слой: {layer} см · Расход: {per_m2:.1f} кг/м²\n\n"
        f"*1 фура (~17 тонн) покрывает:*\n"
        f"📏 ~{round(m2t):,} м² пола\n{line}\n\n".replace(",", " ") +
        f"💰 Стоимость 1 фуры: *~{truck*12:,} руб.* (без доставки)\n\n".replace(",", " ") +
        f"📊 *Ваш расчёт:*\n{div}\n\n_Напишите /start чтобы оформить заказ_ 👇",
        parse_mode="Markdown"
    )

async def about_product(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    p = PRODUCT
    await update.message.reply_text(
        f"📋 *О продукте*\n━━━━━━━━━━━━━━━━━━━━\n\n🪵 *{p['name']}*\n\n"
        f"🌲 Сырьё: {p['wood']}\n📐 Фракция: {p['fraction']}\n"
        f"💧 Влажность: {p['moisture']}\n📦 Упаковка: {p['package']}\n"
        f"🚛 1 фура: {p['truck']}\n💰 Цена: *12 руб/кг* (доставка отдельно)\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n✅ {p['cert']}\n🏭 {p['origin']}\n\n"
        f"*Применяется для:*\n🐴 Лошади  🐄 КРС  🐓 Птица  🐷 Свиноводство\n\n"
        f"🚚 Доставка рассчитывается индивидуально",
        parse_mode="Markdown", reply_markup=main_keyboard()
    )

async def contact_manager(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📞 *Связь с менеджером*\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 Файзиев Эмиль Энгельсович\n📱 {ADMIN_PHONE}\n\n"
        f"⏰ Пн–Пт, 9:00–18:00\n\n"
        f"💬 Или оставьте заявку через бота —\nперезвоним в течение 2 рабочих часов 👆",
        parse_mode="Markdown", reply_markup=main_keyboard()
    )

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data.clear()
    await update.message.reply_text("❌ Отменено.\n🏠 Главное меню:", reply_markup=main_keyboard())
    return MAIN_MENU

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler),
        ],
        states={
            MAIN_MENU:     [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            ANIMAL_TYPE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, animal_type_handler)],
            QUANTITY:      [MessageHandler(filters.TEXT & ~filters.COMMAND, quantity_handler)],
            DISTRICT:      [MessageHandler(filters.TEXT & ~filters.COMMAND, district_handler)],
            CONTACT_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_name_handler)],
            CONTACT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_phone_handler)],
            CONFIRM:       [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=False,
    )
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(calculator_callback, pattern="^calc_"))
    print("✅ Бот запущен.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
