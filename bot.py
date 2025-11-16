import aiohttp
import random
from datetime import datetime
from collections import defaultdict, deque
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import json
import os
import matplotlib.pyplot as plt
import io
from telegram import InputMediaPhoto
from io import BytesIO

import json
import asyncio
from datetime import datetime

REMINDERS_FILE = "reminders.json"

def load_reminders():
    try:
        with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_reminders(data):
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

reminders = load_reminders()

# --- старт и меню ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я бот! Напиши /menu 😼")

import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# --- обновлённое меню с анимацией ---
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📊 Мои результаты", callback_data="menu_stats"),
            InlineKeyboardButton("🍽 Продукты", callback_data="menu_foods"),
        ],
        [
            InlineKeyboardButton("📈 Графики", callback_data="menu_graphs"),
            InlineKeyboardButton("🌤 Погода", callback_data="menu_weather"),
        ],
        [
            InlineKeyboardButton("🤣 Мемы и шутки", callback_data="menu_fun"),
        ],
    ]
    await update.message.reply_text("Выбери раздел:", reply_markup=InlineKeyboardMarkup(keyboard))


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    from datetime import date

    # --- мини-анимация перед реакцией ---
    await query.edit_message_text("⏳ Думаю...")
    await asyncio.sleep(0.4)

    # --- подменю: результаты ---
    if query.data == "menu_stats":
        await query.edit_message_text("📊 Открываю твои результаты...")
        await asyncio.sleep(0.5)
        keyboard = [
            [InlineKeyboardButton("📅 Сегодня", callback_data="show_day")],
            [InlineKeyboardButton("📊 Неделя", callback_data="show_week")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        await query.edit_message_text("Раздел «📊 Мои результаты»", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "show_day":
        await query.edit_message_text("📆 Смотрю твой день...")
        await asyncio.sleep(0.4)
        day = str(date.today())
        stats = user_stats.get(user_id, {}).get(day)
        if not stats:
            await query.edit_message_text("Сегодня ты ещё ничего не записывал 😼")
        else:
            msg = (
                f"📅 За сегодня:\n"
                f"🔥 Калории: {stats['kcal']:.0f}\n"
                f"🥩 Белки: {stats['p']:.1f} г\n"
                f"🧈 Жиры: {stats['f']:.1f} г\n"
                f"🍞 Углеводы: {stats['c']:.1f} г"
            )
            await query.edit_message_text(msg)

    elif query.data == "show_week":
        await query.edit_message_text("📊 Считаю неделю...")
        await asyncio.sleep(0.6)
        await week_stats(update, context)

    # --- подменю: продукты ---
    elif query.data == "menu_foods":
        await query.edit_message_text("🍽 Загружаю базу продуктов...")
        await asyncio.sleep(0.5)
        keyboard = [
            [InlineKeyboardButton("➕ Добавить", callback_data="food_add")],
            [InlineKeyboardButton("✏️ Изменить", callback_data="food_edit")],
            [InlineKeyboardButton("📋 Моя база", callback_data="food_list")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        await query.edit_message_text("Раздел «🍽 Продукты»", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "food_add":
        await query.edit_message_text("Чтобы добавить продукт:\n`/addfood название ккал белки жиры углеводы`", parse_mode="Markdown")

    elif query.data == "food_edit":
        await query.edit_message_text("Чтобы изменить продукт:\n`/editfood название ккал белки жиры углеводы`", parse_mode="Markdown")

    elif query.data == "food_list":
        await query.edit_message_text("📋 Загружаю твою базу...")
        await asyncio.sleep(0.5)
        await my_foods(update, context)

    # --- подменю: графики ---
    elif query.data == "menu_graphs":
        await query.edit_message_text("📈 Готовлю графики...")
        await asyncio.sleep(0.5)
        keyboard = [
            [InlineKeyboardButton("🔥 Калории", callback_data="graph_kcal")],
            [
                InlineKeyboardButton("🥩 Белки", callback_data="graph_p"),
                InlineKeyboardButton("🧈 Жиры", callback_data="graph_f"),
                InlineKeyboardButton("🍞 Углеводы", callback_data="graph_c")
            ],
            [InlineKeyboardButton("📊 Всё вместе", callback_data="graph_all")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        await query.edit_message_text("Раздел «📈 Графики»", reply_markup=InlineKeyboardMarkup(keyboard))

    # --- подменю: погода ---
    elif query.data == "menu_weather":
        await query.edit_message_text("🌤 Проверяю небо над головой...")
        await asyncio.sleep(0.4)
        await query.edit_message_text("Чтобы узнать погоду, напиши:\n`/weather <город>` 🌤", parse_mode="Markdown")

    # --- подменю: мемы и шутки ---
    elif query.data == "menu_fun":
        await query.edit_message_text("🤣 Подбираю весёлое...")
        await asyncio.sleep(0.5)
        keyboard = [
            [InlineKeyboardButton("🤣 Мем", callback_data="fun_meme")],
            [InlineKeyboardButton("😂 Шутка", callback_data="fun_joke")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        await query.edit_message_text("Раздел «🤣 Мемы и шутки»", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "fun_meme":
        await query.edit_message_text("📸 Ищу мем...")
        await asyncio.sleep(0.4)
        await meme(update, context)

    elif query.data == "fun_joke":
        await query.edit_message_text("😂 Думаю над шуткой...")
        await asyncio.sleep(0.4)
        await joke(update, context)

    # --- возврат в главное меню ---
    elif query.data == "main_menu":
        await query.edit_message_text("⬅️ Возвращаюсь в главное меню...")
        await asyncio.sleep(0.4)
        await menu(update, context)

import asyncio

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    from datetime import date

    # helper для плавного перехода
    async def animate_thinking(texts, delay=0.6):
        for t in texts:
            await query.edit_message_text(t)
            await asyncio.sleep(delay)

    # --- раздел «📊 Мои результаты» ---
    if query.data == "menu_stats":
        await animate_thinking(["⏳ Думаю...", "📊 Загружаю твои данные..."])
        keyboard = [
            [InlineKeyboardButton("📅 Сегодня", callback_data="show_day")],
            [InlineKeyboardButton("📊 Неделя", callback_data="show_week")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        await query.edit_message_text("Раздел «📊 Мои результаты»", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "show_day":
        await animate_thinking(["📆 Смотрю твой день..."])
        day = str(date.today())
        stats = user_stats.get(user_id, {}).get(day)
        if not stats:
            await query.edit_message_text("Сегодня ты ещё ничего не записывал 😼")
        else:
            msg = (
                f"📅 За сегодня:\n"
                f"🔥 Калории: {stats['kcal']:.0f}\n"
                f"🥩 Белки: {stats['p']:.1f} г\n"
                f"🧈 Жиры: {stats['f']:.1f} г\n"
                f"🍞 Углеводы: {stats['c']:.1f} г"
            )
            await query.edit_message_text(msg)

    elif query.data == "show_week":
        await animate_thinking(["📊 Считаю неделю...", "📈 Подготавливаю результаты..."])
        await week_stats(update, context)

    # --- раздел «🍽 Продукты» ---
    elif query.data == "menu_foods":
        await animate_thinking(["🍽 Загружаю базу...", "📦 Обновляю список..."])
        keyboard = [
            [InlineKeyboardButton("➕ Добавить", callback_data="food_add")],
            [InlineKeyboardButton("✏️ Изменить", callback_data="food_edit")],
            [InlineKeyboardButton("📋 Моя база", callback_data="food_list")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        await query.edit_message_text("Раздел «🍽 Продукты»", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "food_add":
        await animate_thinking(["🧠 Думаю, как добавить...", "✅ Готово!"])
        await query.edit_message_text("Чтобы добавить продукт:\n`/addfood название ккал белки жиры углеводы`", parse_mode="Markdown")

    elif query.data == "food_edit":
        await animate_thinking(["✏️ Открываю редактор...", "✅ Готово!"])
        await query.edit_message_text("Чтобы изменить продукт:\n`/editfood название ккал белки жиры углеводы`", parse_mode="Markdown")

    elif query.data == "food_list":
        await animate_thinking(["📋 Загружаю твою базу..."])
        await my_foods(update, context)

    # --- раздел «📈 Графики» ---
    elif query.data == "menu_graphs":
        await animate_thinking(["📈 Готовлю графики..."])
        keyboard = [
            [InlineKeyboardButton("🔥 Калории", callback_data="graph_kcal")],
            [
                InlineKeyboardButton("🥩 Белки", callback_data="graph_p"),
                InlineKeyboardButton("🧈 Жиры", callback_data="graph_f"),
                InlineKeyboardButton("🍞 Углеводы", callback_data="graph_c")
            ],
            [InlineKeyboardButton("📊 Всё вместе", callback_data="graph_all")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        await query.edit_message_text("Раздел «📈 Графики»", reply_markup=InlineKeyboardMarkup(keyboard))

    # --- раздел «🌤 Погода» ---
    elif query.data == "menu_weather":
        await animate_thinking(["🌤 Проверяю небо над головой...", "💨 Ветер шепчет цифры..."])
        await query.edit_message_text("Чтобы узнать погоду, напиши:\n`/weather <город>` 🌤", parse_mode="Markdown")

    # --- раздел «🤣 Мемы и шутки» ---
    elif query.data == "menu_fun":
        await animate_thinking(["🤣 Подбираю весёлое..."])
        keyboard = [
            [InlineKeyboardButton("🤣 Мем", callback_data="fun_meme")],
            [InlineKeyboardButton("😂 Шутка", callback_data="fun_joke")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        await query.edit_message_text("Раздел «🤣 Мемы и шутки»", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "fun_meme":
        await animate_thinking(["📸 Ищу мем...", "📷 Почти готово..."])
        await meme(update, context)

    elif query.data == "fun_joke":
        await animate_thinking(["😂 Думаю над шуткой...", "😏 Хмм... хорошая попалась!"])
        await joke(update, context)

    # --- возврат в главное меню ---
    elif query.data == "main_menu":
        await animate_thinking(["⬅️ Возвращаюсь в меню...", "✨ Готово!"])
        await menu(update, context)
        
# --- погода ---
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напиши город, например: /weather Astana")
        return

    city = " ".join(context.args)
    url = f"https://wttr.in/{city}?format=j1"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                temp = data["current_condition"][0]["temp_C"]
                desc = data["current_condition"][0]["weatherDesc"][0]["value"]
                await update.message.reply_text(f"🌤 В {city}: {temp}°C, {desc.lower()}")
    except Exception:
        await update.message.reply_text("Не получилось получить погоду, попробуй позже.")

# --- мемы ---
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://meme-api.com/gimme"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                meme_url = data.get("url")
                title = data.get("title", "Мем 😼")

                # если вызов из кнопки — отвечаем через callback
                if update.message:
                    await update.message.reply_photo(photo=meme_url, caption=title)
                else:
                    await update.callback_query.message.reply_photo(photo=meme_url, caption=title)
    except Exception as e:
        msg = f"Ошибка при получении мема: {e}"
        if update.message:
            await update.message.reply_text(msg)
        else:
            await update.callback_query.message.reply_text(msg)

# --- шутки ---
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://v2.jokeapi.dev/joke/Programming,Miscellaneous?type=single"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                joke_text = data.get("joke", "Шутка потерялась в продакшене 😿")

                if update.message:
                    await update.message.reply_text(joke_text)
                else:
                    await update.callback_query.message.reply_text(joke_text)
    except Exception as e:
        msg = f"Ошибка при получении шутки: {e}"
        if update.message:
            await update.message.reply_text(msg)
        else:
            await update.callback_query.message.reply_text(msg)

# --- память и общение ---
user_memory = defaultdict(lambda: deque(maxlen=5))

async def smart_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower()
    user_memory[user_id].append(text)
    history = " ".join(user_memory[user_id])

    # приветствие
    if any(x in text for x in ["привет", "hi", "hello", "здравствуй", "ку"]):
        await update.message.reply_text("Привет 😼 Рад тебя видеть!")
    # что умеешь
    elif any(x in text for x in ["умеешь", "что можешь", "что умеешь", "что делаешь"]):
        await update.message.reply_text(
            "Я умею показывать погоду, мемы и шутки 😼, а также умею считать калории. Попробуй /menu или /weather Astana."
        )
    # устал
    elif "устал" in text or "тяжело" in text:
        await update.message.reply_text("Понимаю... сделай паузу и отдохни немного 💪")
    # как дела
    elif "как дела" in text or "как ты" in text:
        await update.message.reply_text("Отлично! Код компилируется, ошибок нет 😼 А у тебя как?")
    # погода
    elif "погода" in text or "weather" in text:
        await update.message.reply_text("Хочешь узнать погоду? Напиши `/weather <город>` 🌤")
    # мем
    elif "мем" in text or "meme" in text:
        await update.message.reply_text("Пиши `/meme`, и я покажу тебе котиков 😼")
    # шутка
    elif "шутк" in text or "joke" in text:
        await update.message.reply_text("Команда `/joke` тебе в помощь 😂")
    # спасибо
    elif "спасибо" in text or "thank" in text:
        await update.message.reply_text("Пожалуйста 😺")
    # пока
    elif "пока" in text or "bye" in text:
        await update.message.reply_text("До встречи 🐾")
    # бот
    elif "бот" in text:
        await update.message.reply_text("Да-да, я тут 😼")
    # остальное
    else:
        await update.message.reply_text("Хмм... интересно. Расскажи подробнее 😼")

import re, json
from datetime import date

FOOD_FILE = "food_data.json"

def load_food_data():
    if os.path.exists(FOOD_FILE):
        with open(FOOD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "рис": {"kcal":130, "p":2.7, "f":0.3, "c":28},
        "курица": {"kcal":165, "p":31, "f":3.6, "c":0},
        "гречка": {"kcal":110, "p":4.5, "f":1.6, "c":23},
        "манты": {"kcal":250, "p":10, "f":12, "c":24},
        "яблоко": {"kcal":52, "p":0.3, "f":0.2, "c":14},
        "пирожок": {"kcal":200, "p":5, "f":8, "c":26},
        "творог": {"kcal":120, "p":16, "f":5, "c":3},
        "банан": {"kcal":89, "p":1.1, "f":0.3, "c":23},
        "макароны": {"kcal":140, "p":5, "f":1, "c":28}
    }

def save_food_data(data):
    with open(FOOD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

food_data = load_food_data()

import json, os

DATA_FILE = "nutrition_data.json"

def load_data():
    # Проверяем, существует ли файл и не пустой ли он
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                print("✅ Файл данных загружен:", data)
                return data
            except json.JSONDecodeError:
                print("⚠️ Ошибка чтения JSON, создаю пустой файл.")
                return {}
    else:
        print("⚠️ Файл не найден или пуст. Создаю новый словарь.")
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
user_stats = load_data()

# --- авто-очистка при новом дне ---
# from datetime import date
# today = str(date.today())
#
# for user_id, days in list(user_stats.items()):
#     for day in list(days.keys()):
#         if day != today:
#             del user_stats[user_id][day]
# save_data(user_stats)
save_data(user_stats)


def normalize_word(word):
    base_words = list(food_data.keys())
    for base in base_words:
        if word.startswith(base[:3]):
            return base
    return word

def guess_product(word):
    word = word.lower()
    for name in food_data.keys():
        if name.startswith(word[:3]) or word in name:
            return name
    return None

async def calories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower()
    matches = re.findall(r"(\d+)\s*г\s*([а-яa-z]+)", text)

    if not matches:
        await update.message.reply_text("Напиши, что ты ел, например: 'съел 200 г курицы и 150 г риса' 😼")
        return

    total_kcal = total_p = total_f = total_c = 0
    lines = []

    for grams, product in matches:
        grams = int(grams)
        base = normalize_word(product)
        data = food_data.get(base)

        # Если продукта нет, бот угадывает и добавляет примерный
        if not data:
            similar = guess_product(base)
            if similar:
                data = food_data[similar]
                lines.append(f"🤔 Не нашёл '{product}', но использую похожий '{similar}'")
            else:
                # Средние значения — универсальные
                data = {"kcal": 250, "p": 15, "f": 10, "c": 20}
                food_data[base] = data
                save_food_data(food_data)
                lines.append(f"🤷 '{product}' не найден, добавил примерный продукт (250 ккал на 100 г).")

        kcal = grams * data["kcal"] / 100
        p = grams * data["p"] / 100
        f = grams * data["f"] / 100
        c = grams * data["c"] / 100

        total_kcal += kcal
        total_p += p
        total_f += f
        total_c += c

        lines.append(f"🍽 {product.capitalize()} {grams} г → {kcal:.0f} ккал, Б:{p:.1f} Ж:{f:.1f} У:{c:.1f}")

    # сохраняем за день
    day = str(date.today())
    if user_id not in user_stats:
        user_stats[user_id] = {}
    if day not in user_stats[user_id]:
        user_stats[user_id][day] = {"kcal": 0, "p": 0, "f": 0, "c": 0}

    user_stats[user_id][day]["kcal"] += total_kcal
    user_stats[user_id][day]["p"] += total_p
    user_stats[user_id][day]["f"] += total_f
    user_stats[user_id][day]["c"] += total_c

    result = "\n".join(lines)
    result += f"\n\n🔥 Всего: {total_kcal:.0f} ккал\n🥩 Б:{total_p:.1f} г  🧈 Ж:{total_f:.1f} г  🍞 У:{total_c:.1f} г"

    # --- небольшой анализ ---
    comment = ""
    if total_p > total_f * 2 and total_p > total_c:
        comment = "💪 Белковый день! Мышцы говорят спасибо 😼"
    elif total_f > total_p and total_f > total_c:
        comment = "🧈 Ну, жирненько сегодня... но вкусно ведь 😹"
    elif total_c > total_p and total_c > total_f:
        comment = "🍞 Углеводов прилично — энергия есть, лишь бы не вся в сон ушла 😼"
    elif total_kcal < 500:
        comment = "😿 Слишком мало калорий. Так не проживёшь, дружок."
    elif total_kcal > 2500:
        comment = "🍕 Серьёзная атака на холодильник. Но главное — без чувства вины 😸"
    else:
        comment = "😺 Неплохой баланс на день. Так держать!"

    await update.message.reply_text(result + "\n\n" + comment)
    save_data(user_stats)

async def day_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    day = str(date.today())
    stats = user_stats.get(user_id, {}).get(day)

    if not stats:
        await update.message.reply_text("Сегодня ты ещё ничего не записывал 😼")
        return

    msg = (
        f"📅 За сегодня:\n"
        f"🔥 Калории: {stats['kcal']:.0f}\n"
        f"🥩 Белки: {stats['p']:.1f} г\n"
        f"🧈 Жиры: {stats['f']:.1f} г\n"
        f"🍞 Углеводы: {stats['c']:.1f} г"
    )
    await update.message.reply_text(msg)

    # --- анализ баланса ---
    total = stats['p'] * 4 + stats['f'] * 9 + stats['c'] * 4
    if total > 0:
        perc_p = stats['p'] * 4 / total * 100
        perc_f = stats['f'] * 9 / total * 100
        perc_c = stats['c'] * 4 / total * 100
        comment = f"\n📊 Соотношение макронутриентов:\n🥩 Белки: {perc_p:.1f}% 🧈 Жиры: {perc_f:.1f}% 🍞 Углеводы: {perc_c:.1f}%"

        # --- оценка ---
        if 25 <= perc_p <= 35 and 20 <= perc_f <= 30 and 40 <= perc_c <= 55:
            comment += "\n✅ Почти идеальный баланс. Красота!"
        elif perc_f > 40:
            comment += "\n🧈 Многовато жиров — аккуратнее с вкусняшками."
        elif perc_c > 60:
            comment += "\n🍞 Перебор с углеводами — энергии вагон, но жирку не рад."
        elif perc_p < 20:
            comment += "\n🥩 Белков маловато. Мышцы тихо грустят."
        else:
            comment += "\n😼 Баланс средний, но жить можно."

        await update.message.reply_text(comment)

from datetime import timedelta
async def week_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    today = date.today()
    week_data = []
    
    for i in range(7):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        stats = user_stats.get(user_id, {}).get(day)
        if stats:
            week_data.append((day, stats))

    if not week_data:
        await update.message.reply_text("За последние 7 дней ничего не записано 😿")
        return

    msg = "📅 <b>Статистика за последние 7 дней:</b>\n\n"
    total_kcal = total_p = total_f = total_c = 0

    for day, s in sorted(week_data):
        msg += f"{day}: 🔥 {s['kcal']:.0f} ккал, Б:{s['p']:.1f} Ж:{s['f']:.1f} У:{s['c']:.1f}\n"
        total_kcal += s["kcal"]
        total_p += s["p"]
        total_f += s["f"]
        total_c += s["c"]

    avg_kcal = total_kcal / len(week_data)
    avg_p = total_p / len(week_data)
    avg_f = total_f / len(week_data)
    avg_c = total_c / len(week_data)

    msg += f"\n📊 <b>Среднее за неделю:</b>\n🔥 {avg_kcal:.0f} ккал, Б:{avg_p:.1f} Ж:{avg_f:.1f} У:{avg_c:.1f}"
    await update.message.reply_text(msg, parse_mode="HTML")

async def add_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 5:
        await update.message.reply_text("Используй формат: /addfood название ккал белки жиры углеводы 😺")
        return

    name, kcal, p, f, c = context.args
    try:
        kcal, p, f, c = float(kcal), float(p), float(f), float(c)
        food_data[name.lower()] = {"kcal": kcal, "p": p, "f": f, "c": c}
        save_food_data(food_data)
        await update.message.reply_text(f"Добавил продукт: {name} ({kcal} ккал, Б:{p} Ж:{f} У:{c}) ✅")
        save_food_data(food_data)
    except ValueError:
        await update.message.reply_text("Проверь числа — должны быть только цифры 😼")

async def edit_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 5:
        await update.message.reply_text("Используй формат: /editfood название ккал белки жиры углеводы 😼")
        return

    name, kcal, p, f, c = context.args
    name = name.lower()
    if name not in food_data:
        await update.message.reply_text(f"❌ Продукт '{name}' не найден. Добавь его через /addfood.")
        return

    try:
        kcal, p, f, c = float(kcal), float(p), float(f), float(c)
        food_data[name] = {"kcal": kcal, "p": p, "f": f, "c": c}
        save_food_data(food_data)
        await update.message.reply_text(f"Обновил продукт: {name} ✅")
        save_food_data(food_data)
    except ValueError:
        await update.message.reply_text("Ошибка: все значения должны быть числами 😼")

async def my_foods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not food_data:
        await update.message.reply_text("⚠️ В базе пока нет продуктов.")
        return

    msg = "📋 <b>Твоя база продуктов:</b>\n\n"
    for name, info in food_data.items():
        msg += f"🍽 <b>{name.capitalize()}</b> — {info['kcal']} ккал, Б:{info['p']} Ж:{info['f']} У:{info['c']}\n"

    await update.message.reply_text(msg, parse_mode="HTML")

from datetime import timedelta

import matplotlib.pyplot as plt
from io import BytesIO
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 Калории", callback_data="graph_kcal")],
        [
            InlineKeyboardButton("🥩 Белки", callback_data="graph_p"),
            InlineKeyboardButton("🧈 Жиры", callback_data="graph_f"),
            InlineKeyboardButton("🍞 Углеводы", callback_data="graph_c")
        ],
        [InlineKeyboardButton("📊 Всё вместе", callback_data="graph_all")]
    ]
    await update.message.reply_text("Выбери, что показать:", reply_markup=InlineKeyboardMarkup(keyboard))

async def graph_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    today = date.today()
    week_data = []

    for i in range(7):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        stats = user_stats.get(user_id, {}).get(day)
        if stats:
            week_data.append((day, stats))

    if not week_data:
        await query.edit_message_text("😿 За последние 7 дней ничего не записано.")
        return

    week_data.sort()
    days = [d for d, _ in week_data]
    kcal = [s["kcal"] for _, s in week_data]
    p = [s["p"] for _, s in week_data]
    f = [s["f"] for _, s in week_data]
    c = [s["c"] for _, s in week_data]

    metric = query.data.replace("graph_", "")
    plt.figure(figsize=(8, 5))

    if metric == "kcal":
        plt.plot(days, kcal, label="Калории", color="orange", linewidth=2)
        title = "🔥 Калории за 7 дней"
    elif metric == "p":
        plt.plot(days, p, label="Белки", color="blue", linewidth=2)
        title = "🥩 Белки за 7 дней"
    elif metric == "f":
        plt.plot(days, f, label="Жиры", color="green", linewidth=2)
        title = "🧈 Жиры за 7 дней"
    elif metric == "c":
        plt.plot(days, c, label="Углеводы", color="red", linewidth=2)
        title = "🍞 Углеводы за 7 дней"
    else:
        plt.plot(days, kcal, label="Калории", color="orange", linewidth=2)
        plt.plot(days, p, label="Белки", color="blue", linewidth=2)
        plt.plot(days, f, label="Жиры", color="green", linewidth=2)
        plt.plot(days, c, label="Углеводы", color="red", linewidth=2)
        title = "📊 Макронутриенты за 7 дней"

    plt.xlabel("Дата")
    plt.ylabel("Количество")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    await query.message.reply_photo(photo=buf, caption=title)

# --- запуск ---
from dotenv import load_dotenv
import os

load_dotenv()

app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if len(context.args) < 2:
        await update.message.reply_text(
            "Используй формат: /remind 13:00 текст напоминания ⏰", parse_mode="Markdown"
        )
        return

    time_str = context.args[0]
    text = " ".join(context.args[1:])

    if user_id not in reminders:
        reminders[user_id] = []
    reminders[user_id].append({"time": time_str, "text": text})
    save_reminders(reminders)

    await update.message.reply_text(f"✅ Напоминание установлено на {time_str}: {text}")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("weather", weather))
app.add_handler(CommandHandler("meme", meme))
app.add_handler(CommandHandler("joke", joke))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("г"), calories))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_reply))
app.add_handler(CommandHandler("day", day_stats))
app.add_handler(CommandHandler("remind", remind))
app.add_handler(CommandHandler("addfood", add_food))
app.add_handler(CommandHandler("editfood", edit_food))
app.add_handler(CommandHandler("myfoods", my_foods))
app.add_handler(CommandHandler("weekstats", week_stats))
app.add_handler(CommandHandler("graph", graph))
app.add_handler(CallbackQueryHandler(graph_choice, pattern="^graph_"))
app.add_handler(CallbackQueryHandler(button))

import asyncio

async def reminder_loop():
    while True:
        now = datetime.now().strftime("%H:%M")
        for user_id, items in reminders.items():
            for reminder in items:
                if reminder["time"] == now:
                    try:
                        await app.bot.send_message(
                            chat_id=user_id,
                            text=f"⏰ Напоминание: {reminder['text']}"
                        )
                    except Exception as e:
                        print(f"Ошибка при отправке напоминания: {e}")
        await asyncio.sleep(60)

async def run_bot():
    asyncio.create_task(reminder_loop())
    print("Бот запущен 🐱 (с напоминаниями)")
    await app.run_polling()

import nest_asyncio
import asyncio

import nest_asyncio
import asyncio

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(run_bot())
    
import asyncio
import nest_asyncio
import signal
import sys

if __name__ == "__main__":
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()

    # делаем нормальное завершение по Ctrl+C
    def shutdown_handler(sig, frame):
        print("\n🐱 Бот выключен без драмы. Спокойной ночи.")
        loop.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)

    try:
        loop.run_until_complete(run_bot())
    except Exception:
        pass