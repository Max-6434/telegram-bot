import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TOKEN")  # Render’dan olinadi
bot = Bot(token=TOKEN)
dp = Dispatcher()
user_groups = {}

@dp.message(Command("start"))
async def start_command(message: types.Message):
    if message.chat.type == "private":
        user_id = message.from_user.id
        if user_id not in user_groups:
            user_groups[user_id] = []
        await message.reply(f"Salom! Meni guruhga qo‘shing va admin qiling.\nSizning ID’ingiz: {user_id}")

@dp.chat_member()
async def handle_chat_member_update(update: types.ChatMemberUpdated):
    if update.new_chat_member.user.id == bot.id and update.new_chat_member.status == "member":
        group_id = update.chat.id
        added_by = update.from_user.id
        if added_by in user_groups:
            if group_id not in user_groups[added_by]:
                user_groups[added_by].append(group_id)
                await bot.send_message(added_by, f"Men {update.chat.title} guruhiga qo‘shildim!")
        else:
            user_groups[added_by] = [group_id]
            await bot.send_message(added_by, f"Men {update.chat.title} guruhiga qo‘shildim!")

@dp.message()
async def handle_message(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        group_id = message.chat.id
        user_id = message.from_user.id
        username = message.from_user.username or "Username yo‘q"
        text = message.text or "Matn yo‘q"
        group_name = message.chat.title
        for owner_id, groups in user_groups.items():
            if group_id in groups:
                await bot.send_message(owner_id, f"Guruh: {group_name}\nID: {user_id}\nUsername: @{username}\nXabar: {text}")
                break

async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Bot ishga tushmadi: {e}")

if __name__ == "__main__":
    asyncio.run(main())