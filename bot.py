"""
Телеграм-бот: Подстилочный материал зоотехнический
ИП Файзиев Эмиль Энгельсович
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

(MAIN_MENU, ANIMAL_TYPE, MARK_CHOICE,
 QUANTITY, DISTRICT, CONTACT_NAME, CONTACT_PHONE, CONFIRM) = range(8)

PRODUCTS = {
    "М25": {
        "name": "М 25 — мелкодисперсная",
        "fraction": "0,5–2 мм",
        "moisture": "до 8%",
        "absorption": "700%",
        "density": 125,
        "best_for": "Птицеводство, КРС (родильные боксы, телятники)",
        "icon": "🌿",
        "tag": "⭐ Самый популярный",
    },
    "М35": {
        "name": "М 35 — лёгкая фракция",
        "fraction": "5–15 мм",
        "moisture": "до 12%",
        "absorption": "330–380%",
        "density": 95,
        "best_for": "Свиноводство, молодняк КРС",
        "icon": "🌾",
        "tag": "",
    },
    "М45": {
        "name": "М 45 — стандарт КРС",
        "fraction": "15–30 мм",
        "moisture": "до 10%",
        "absorption": "336%+",
        "density": 80,
        "best_for": "Коровники, стойловые места",
        "icon": "🍂",
        "tag": "",
    },
    "М65": {
        "name": "М 65 — крупная фракция",
        "fraction": "2–4 см",
        "moisture": "до 12%",
        "absorption": "высокая",
        "density": 45,
        "best_for": "Крупные фермы с разбрасывателем",
        "icon": "🪵",
        "tag": "",
    },
}

# ── КЛАВИАТУРЫ ───────────────────────────────────────────────────────────────
def main_keyboard():
    return ReplyKeyboardMarkup([
        ["📦 Оформить заказ"],
        ["🧮 Калькулятор расхода", "📋 Наша продукция"],
        ["📞 Связаться с менеджером"],
    ], resize_keyboard=True)

def animal_keyboard():
    return ReplyKeyboardMarkup([
        ["🐄 КРС (коровы, быки)"],
        ["🐓 Птицеводство (бройлеры, несушки)"],
        ["🐷 Свиноводство"],
        ["🔀 Смешанное хозяйство"],
        ["🔙 Назад в меню"],
    ], resize_keyboard=True)

def confirm_keyboard():
    return ReplyKeyboardMarkup([
        ["✅ Подтвердить заказ"],
        ["✏️ Изменить данные", "❌ Отменить"],
    ], resize_keyboard=True)

def mark_inline_keyboard():
    rows = []
    for mark, p in PRODUCTS.items():
        label = f"{p['icon']} {mark}  {p['tag']}  — {p['best_for'][:28]}"
        rows.append([InlineKeyboardButton(label, callback_data=f"mark_{mark}")])
    return InlineKeyboardMarkup(rows)

# ── /START ────────────────────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Здравствуйте, {user.first_name}!\n\n"
        "🌿 *Подстилочный материал зоотехнический*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🪵 Древесная стружка 4 марок на выбор\n"
        "🛡️ Термически обеззаражена при t = 200°С\n"
        "📐 Для КРС, птицеводства и свиноводства\n"
        "🚚 Доставка до вашего склада\n"
        "📄 Полный пакет документов\n\n"
        "Выберите действие 👇",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )
    return MAIN_MENU

# ── ГЛАВНОЕ МЕНЮ ──────────────────────────────────────────────────────────────
async def main_menu_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text

    if text == "📦 Оформить заказ":
        await update.message.reply_text(
            "📦 *Оформление заказа*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Шаг 1️⃣ из 5️⃣ — Вид хозяйства\n\n"
            "🐾 Выберите вид животных:",
            parse_mode="Markdown",
            reply_markup=animal_keyboard()
        )
        return ANIMAL_TYPE

    elif text == "🧮 Калькулятор расхода":
        await calculator_start(update, ctx)
        return MAIN_MENU

    elif text == "📋 Наша продукция":
        await about_products(update, ctx)
        return MAIN_MENU

    elif text == "📞 Связаться с менеджером":
        await contact_manager(update, ctx)
        return MAIN_MENU

    else:
        await update.message.reply_text(
            "👇 Выберите пункт из меню:",
            reply_markup=main_keyboard()
        )
        return MAIN_MENU

# ── ВИД ЖИВОТНЫХ ──────────────────────────────────────────────────────────────
async def animal_type_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text

    if text == "🔙 Назад в меню":
        await update.message.reply_text("🏠 Главное меню:", reply_markup=main_keyboard())
        return MAIN_MENU

    animals_map = {
        "🐄 КРС (коровы, быки)":                "КРС",
        "🐓 Птицеводство (бройлеры, несушки)":  "Птицеводство",
        "🐷 Свиноводство":                      "Свиноводство",
        "🔀 Смешанное хозяйство":               "Смешанное хозяйство",
    }

    if text not in animals_map:
        await update.message.reply_text(
            "⚠️ Выберите из предложенных вариантов:",
            reply_markup=animal_keyboard()
        )
        return ANIMAL_TYPE

    ctx.user_data["animal"] = animals_map[text]

    hints = {
        "КРС": (
            "🐄 Для *КРС* чаще всего берут:\n\n"
            "🌿 *М25* — влагопоглощение 700%, идеален для\n"
            "    родильных боксов и телятников ⭐\n"
            "🍂 *М45* — стандарт для коровников\n"
            "🪵 *М65* — для ферм с разбрасывателем\n\n"
            "👇 Выберите любую марку:"
        ),
        "Птицеводство": (
            "🐓 Для *птицеводства* рекомендуется:\n\n"
            "🌿 *М25* — мелкодисперсная, 700% влагопоглощение,\n"
            "    безопасна для лап птицы ⭐\n\n"
            "👇 Или выберите другую марку:"
        ),
        "Свиноводство": (
            "🐷 Для *свиноводства* рекомендуется:\n\n"
            "🌾 *М35* — лёгкая фракция, хорошее влагопоглощение\n"
            "🌿 *М25* — если нужна максимальная чистота\n\n"
            "👇 Выберите марку:"
        ),
        "Смешанное хозяйство": (
            "🔀 *Смешанное хозяйство*\n\n"
            "Выберите марку для вашего\n"
            "основного направления:\n"
        ),
    }

    hint = hints.get(ctx.user_data["animal"], "👇 Выберите марку:")

    await update.message.reply_text(
        f"📦 *Оформление заказа*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Шаг 2️⃣ из 5️⃣ — Выбор марки\n\n"
        f"{hint}",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    await update.message.reply_text(
        "👇 Нажмите на нужную марку:",
        reply_markup=mark_inline_keyboard()
    )
    return MARK_CHOICE

# ── ВЫБОР МАРКИ ───────────────────────────────────────────────────────────────
async def mark_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    mark = query.data.replace("mark_", "")
    if mark not in PRODUCTS:
        return MARK_CHOICE

    ctx.user_data["mark"] = mark
    prod = PRODUCTS[mark]

    await query.edit_message_text(
        f"{prod['icon']} *Выбрана марка {mark}*\n\n"
        f"📌 {prod['name']}\n"
        f"📐 Фракция: {prod['fraction']}\n"
        f"💧 Влажность: {prod['moisture']}\n"
        f"🌊 Влагопоглощение: {prod['absorption']}\n"
        f"🐾 Применение: _{prod['best_for']}_\n"
        f"🛡️ Обеззаражена при t = 200°С",
        parse_mode="Markdown"
    )
    await query.message.reply_text(
        f"📦 *Оформление заказа*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Шаг 3️⃣ из 5️⃣ — Количество\n\n"
        f"📊 1 фура = 18–20 тонн\n\n"
        f"Укажите нужный объём:\n"
        f"• *1 фура*, *2 фуры* — если считаете фурами\n"
        f"• *20 тонн*, *40 тонн* — если считаете тоннами",
        parse_mode="Markdown"
    )
    return QUANTITY

# ── КОЛИЧЕСТВО ────────────────────────────────────────────────────────────────
async def quantity_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["quantity"] = update.message.text.strip()
    await update.message.reply_text(
        f"📦 *Оформление заказа*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Шаг 4️⃣ из 5️⃣ — Хозяйство и район\n\n"
        f"📍 Укажите район и название хозяйства:\n"
        f"_Например: Арский район, ООО Агрофирма Север_",
        parse_mode="Markdown"
    )
    return DISTRICT

# ── РАЙОН ─────────────────────────────────────────────────────────────────────
async def district_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["district"] = update.message.text.strip()
    await update.message.reply_text(
        f"📦 *Оформление заказа*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Шаг 5️⃣ из 5️⃣ — Контакт\n\n"
        f"👤 Ваше имя и должность:\n"
        f"_Например: Иван Иванов, главный зоотехник_",
        parse_mode="Markdown"
    )
    return CONTACT_NAME

# ── ИМЯ ───────────────────────────────────────────────────────────────────────
async def contact_name_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["contact_name"] = update.message.text.strip()
    await update.message.reply_text(
        f"📞 Номер телефона для связи:\n"
        f"_Например: +7 900 123 45 67_",
        parse_mode="Markdown"
    )
    return CONTACT_PHONE

# ── ТЕЛЕФОН + ИТОГ ────────────────────────────────────────────────────────────
async def contact_phone_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["contact_phone"] = update.message.text.strip()
    d = ctx.user_data
    prod = PRODUCTS.get(d.get("mark", "М25"), {})

    summary = (
        f"📋 *Проверьте вашу заявку*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🐾 Хозяйство: {d.get('animal', '—')}\n"
        f"{prod.get('icon','')} Марка: *{d.get('mark', '—')}* — {prod.get('name','')}\n"
        f"⚖️ Количество: {d.get('quantity', '—')}\n"
        f"📍 Адрес: {d.get('district', '—')}\n"
        f"👤 Контакт: {d.get('contact_name', '—')}\n"
        f"📞 Телефон: {d.get('contact_phone', '—')}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Стоимость и доставку уточним после отправки\n"
        f"⏱️ Срок поставки: 14 рабочих дней с оплаты\n"
        f"💳 Оплата: 100% предоплата\n"
    )
    await update.message.reply_text(
        summary, parse_mode="Markdown", reply_markup=confirm_keyboard()
    )
    return CONFIRM

# ── ПОДТВЕРЖДЕНИЕ ─────────────────────────────────────────────────────────────
async def confirm_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    d = ctx.user_data

    if text == "✅ Подтвердить заказ":
        user = update.effective_user
        prod = PRODUCTS.get(d.get("mark", "М25"), {})

        admin_msg = (
            f"🆕 *НОВАЯ ЗАЯВКА НА ПОДСТИЛКУ*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 {d.get('contact_name', '—')}\n"
            f"📞 {d.get('contact_phone', '—')}\n\n"
            f"🐾 {d.get('animal', '—')}\n"
            f"{prod.get('icon','')} Марка: *{d.get('mark', '—')}*\n"
            f"⚖️ Количество: {d.get('quantity', '—')}\n"
            f"📍 {d.get('district', '—')}\n\n"
            f"Telegram: @{user.username or '—'} (ID: `{user.id}`)"
        )
        try:
            await ctx.bot.send_message(
                chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки: {e}")

        await update.message.reply_text(
            f"✅ *Заявка успешно принята!*\n\n"
            f"👋 Наш менеджер свяжется с вами по номеру\n"
            f"📞 *{d.get('contact_phone', '—')}*\n"
            f"⏰ в течение 2 рабочих часов\n\n"
            f"По срочным вопросам звоните напрямую:\n"
            f"📱 *{ADMIN_PHONE}*\n\n"
            f"🙏 Спасибо за обращение!",
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )
        ctx.user_data.clear()
        return MAIN_MENU

    elif text == "✏️ Изменить данные":
        ctx.user_data.clear()
        await update.message.reply_text(
            "🔄 Начнём заново. Выберите вид животных:",
            reply_markup=animal_keyboard()
        )
        return ANIMAL_TYPE

    elif text == "❌ Отменить":
        ctx.user_data.clear()
        await update.message.reply_text(
            "❌ Заявка отменена.\n🏠 Главное меню:",
            reply_markup=main_keyboard()
        )
        return MAIN_MENU

    return CONFIRM

# ── КАЛЬКУЛЯТОР ───────────────────────────────────────────────────────────────
async def calculator_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🐓 Бройлеры (М25)", callback_data="calc_broiler"),
         InlineKeyboardButton("🥚 Несушки (М25)",  callback_data="calc_hen")],
        [InlineKeyboardButton("🐄 КРС + М25 (5 см)", callback_data="calc_krs_m25"),
         InlineKeyboardButton("🐄 КРС + М45 (5 см)", callback_data="calc_krs_m45")],
        [InlineKeyboardButton("🐂 КРС + М65 с разбрасывателем", callback_data="calc_krs65")],
        [InlineKeyboardButton("🐷 Свиноводство М35",  callback_data="calc_pig")],
    ])
    await update.message.reply_text(
        "🧮 *Калькулятор расхода подстилки*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Выберите вид животных и марку 👇",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def calculator_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    configs = {
        "calc_broiler":  ("🐓 Бройлеры",            "М25", 125, 5,  20,   "бройлеров"),
        "calc_hen":      ("🥚 Несушки",              "М25", 125, 5,  7.5,  "несушек"),
        "calc_krs_m25":  ("🐄 КРС (М25)",            "М25", 125, 5,  1/9,  "коров (9 м²/гол)"),
        "calc_krs_m45":  ("🐄 КРС (М45)",            "М45", 80,  5,  1/9,  "коров (9 м²/гол)"),
        "calc_krs65":    ("🐂 КРС + разбрасыватель", "М65", 45,  3,  1/9,  "коров"),
        "calc_pig":      ("🐷 Свиноводство",         "М35", 95,  5,  1,    "свиней (1 м²/гол)"),
    }

    if data not in configs:
        return

    anim, mark, density, layer_cm, apm, unit = configs[data]
    truck_kg = 19000
    per_m2   = density * (layer_cm / 100)
    m2_truck = truck_kg / per_m2

    if apm >= 1:
        per_truck = round(m2_truck * apm / 1000) * 1000
        anim_str  = f"≈ {per_truck:,} {unit}".replace(",", " ")
        div       = str(per_truck)
    else:
        per_truck = round(m2_truck * apm)
        anim_str  = f"≈ {per_truck} {unit}"
        div       = str(per_truck)

    await query.edit_message_text(
        f"🧮 *Расчёт: {anim} · Марка {mark}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📐 Слой: {layer_cm} см\n"
        f"⚖️ Плотность: {density} кг/м³\n"
        f"💧 Расход: *{per_m2:.2f} кг/м²*\n\n"
        f"🚛 *1 фура (19 тонн) покрывает:*\n"
        f"📏 ~{round(m2_truck):,} м² пола\n".replace(",", " ") +
        f"🐾 {anim_str}\n\n"
        f"📊 *Сколько фур нужно вам?*\n"
        f"Поголовье ÷ {div} = количество фур\n\n"
        f"_Напишите /start чтобы оформить заказ_ 👇",
        parse_mode="Markdown"
    )

# ── О ПРОДУКЦИИ ───────────────────────────────────────────────────────────────
async def about_products(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lines = [
        "📋 *Линейка продукции*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
    ]
    for mark, p in PRODUCTS.items():
        tag = f"  {p['tag']}" if p['tag'] else ""
        lines.append(
            f"{p['icon']} *{mark}*{tag}\n"
            f"   📐 Фракция: {p['fraction']}\n"
            f"   💧 Влажность: {p['moisture']}\n"
            f"   🌊 Влагопоглощение: *{p['absorption']}*\n"
            f"   🐾 _{p['best_for']}_\n"
        )
    lines.append(
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🛡️ Все марки обеззаражены при *t = 200°С*\n"
        "📦 Кипы 18–20 кг на поддонах, стрейч-плёнка\n"
        "📄 Акт обеззараживания по запросу"
    )
    await update.message.reply_text(
        "\n".join(lines), parse_mode="Markdown", reply_markup=main_keyboard()
    )

# ── КОНТАКТ ───────────────────────────────────────────────────────────────────
async def contact_manager(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📞 *Связь с менеджером*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 Файзиев Эмиль Энгельсович\n"
        f"📱 {ADMIN_PHONE}\n\n"
        f"⏰ Режим работы: пн–пт, 9:00–18:00\n\n"
        f"💬 Или оставьте заявку через бота —\n"
        f"перезвоним в течение 2 рабочих часов 👆",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

# ── ОТМЕНА ────────────────────────────────────────────────────────────────────
async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data.clear()
    await update.message.reply_text(
        "❌ Отменено.\n🏠 Главное меню:",
        reply_markup=main_keyboard()
    )
    return MAIN_MENU

# ── ЗАПУСК ────────────────────────────────────────────────────────────────────
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
            MARK_CHOICE:   [CallbackQueryHandler(mark_callback, pattern="^mark_")],
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
