Telegram Nutrition & Reminder Bot

A simple Telegram bot that helps track food, calories, macronutrients and daily reminders.
The bot is written in Python and uses JSON files for data storage.

Features

Add foods with calories, proteins, fats and carbs
Track what you eat today
Show total calories and macros
Save and show reminders
Menu with buttons
Optional: weather, jokes and extra tools

Project Structure

telegram_bot/
  bot.py
  food_data.json
  nutrition_data.json
  reminders.json
  .github/
  
Technologies Used

Python 3
Telegram Bot API
aiogram / pyTelegramBotAPI
JSON storage
How to Run

Install dependencies:

pip install -r requirements.txt

Set your bot token:

export BOT_TOKEN=your_token_here

Start the bot:

python bot.py

Commands & Description

/start
Start the bot
/menu
Open menu
/addfood name kcal protein fat carbs
Add a food item
/today
Show today’s meals
/remind HH:MM text
Create a reminder
/weather city
Weather info (optional)

Data Storage

food_data.json – saved foods
nutrition_data.json – daily nutrition
reminders.json – user reminders

A personal study project for learning Python and Telegram bot development.
