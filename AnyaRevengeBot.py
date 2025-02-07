import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
import sqlite3

TOKEN = "7276119890:AAGuiWtUdsFcSg9atS-NYKxKN44Yd38A5Pc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключение к базе данных
conn = sqlite3.connect("karma.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS karma (user_id INTEGER PRIMARY KEY, score INTEGER DEFAULT 0, warnings INTEGER DEFAULT 0)''')
conn.commit()

# Функция изменения кармы
async def change_karma(message: Message, change: int):
    user_id = message.reply_to_message.from_user.id
    cursor.execute("SELECT score FROM karma WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        new_score = result[0] + change
        cursor.execute("UPDATE karma SET score = ? WHERE user_id = ?", (new_score, user_id))
    else:
        cursor.execute("INSERT INTO karma (user_id, score) VALUES (?, ?)", (user_id, change))

    conn.commit()
    await message.answer(f"Карма пользователя {message.reply_to_message.from_user.full_name}: {new_score}")

# Команды
async def is_admin(user_id: int, chat_id: int) -> bool:
    chat = await bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in chat)

@dp.message(Command("respect"))
async def respect(message: Message):
    if not await is_admin(message.from_user.id, message.chat.id):
        await message.answer("🚫 Только администраторы могут использовать эту команду!")
        return
    if message.reply_to_message:
        await change_karma(message, 1)

@dp.message(Command("disrespect"))
async def disrespect(message: Message):
    if not await is_admin(message.from_user.id, message.chat.id):
        await message.answer("🚫 Только администраторы могут использовать эту команду!")
        return
    if message.reply_to_message:
        await change_karma(message, -1)



@dp.message(Command("rating"))
async def rating(message: Message):
    cursor.execute("SELECT user_id, score FROM karma ORDER BY score DESC LIMIT 10")
    top_users = cursor.fetchall()
    text = "\n".join([f"{i+1}. User {user_id} – {score}" for i, (user_id, score) in enumerate(top_users)])
    await message.answer(f"🏆 Топ пользователей по карме:\n{text}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
