import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
user_groups = {}

@dp.message(Command("start"))
async def start_command(message: types.Message):
    if message.chat.type == "private":
        user_id = message.from_user.id
        if user_id not in user_groups:
            user_groups[user_id] = []
        logger.info(f"Foydalanuvchi {user_id} /start yozdi")
        await message.reply(f"Salom! Meni guruhga qo‘shing va admin qiling.\nSizning ID’ingiz: {user_id}")
    else:
        logger.info(f"Guruhda /start ishlatildi: {message.chat.id}")
        await message.reply("Guruhda salom! Meni admin qiling.")

@dp.chat_member()
async def handle_chat_member_update(update: types.ChatMemberUpdated):
    if update.new_chat_member.user.id == bot.id and update.new_chat_member.status == "member":
        group_id = update.chat.id
        added_by = update.from_user.id
        logger.info(f"Bot {group_id} guruhiga qo‘shildi, qo‘shuvchi: {added_by}")
        if added_by not in user_groups:
            user_groups[added_by] = []
        if group_id not in user_groups[added_by]:
            user_groups[added_by].append(group_id)
            await bot.send_message(added_by, f"Men {update.chat.title} guruhiga qo‘shildim!")

@dp.message()
async def handle_message(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        group_id = message.chat.id
        user_id = message.from_user.id
        username = message.from_user.username or "Username yo‘q"
        text = message.text or "Matn yo‘q"
        group_name = message.chat.title
        logger.info(f"Guruh xabari: {group_id}, Matn: {text}, Foydalanuvchi: {user_id}")
        for owner_id, groups in user_groups.items():
            if group_id in groups:
                logger.info(f"{owner_id} ga xabar yuborilmoqda")
                try:
                    await bot.send_message(owner_id, f"Guruh: {group_name}\nID: {user_id}\nUsername: @{username}\nXabar: {text}")
                    logger.info(f"Xabar {owner_id} ga muvaffaqiyatli yuborildi")
                except Exception as e:
                    logger.error(f"Xabar yuborishda xato: {e}")
                break

async def main():
    logger.info("Bot polling rejimida boshlanmoqda")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
