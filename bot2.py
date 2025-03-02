import os
import json
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token olish
TOKEN = os.getenv("7175780601:AAFYx70OWdpUeSKdBgYEbAVq-XWBlLUu7Vw", "7175780601:AAFYx70OWdpUeSKdBgYEbAVq-XWBlLUu7Vw")

# Bot va Dispatcher yaratish
bot = Bot(token=TOKEN)
dp = Dispatcher()

# JSON Fayl nomi
DATA_FILE = "user_groups.json"


# JSON faylni yuklash
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"users": {}, "groups": {}}  # Bo'sh JSON agar fayl mavjud bo'lmasa


# JSON faylni saqlash
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(user_groups, file, indent=4)


# Ma’lumotlarni yuklash
user_groups = load_data()


@dp.message(Command("start"))
async def start_command(message: types.Message):
    if message.chat.type == "private":
        user_id = str(message.from_user.id)  # JSON uchun str ishlatamiz

        if user_id not in user_groups["users"]:  # Agar mavjud bo'lmasa, qo'shamiz
            user_groups["users"][user_id] = []
            save_data()  # JSON faylni yangilaymiz

        logger.info(f"Foydalanuvchi {user_id} /start yozdi, user_groups: {user_groups}")
        await message.reply(f"Salom! Meni guruhga qo‘shing. \nSizning ID’ingiz: {user_id}")
    else:
        logger.info(f"Guruhda /start ishlatildi: {message.chat.id}")
        # await message.reply("Guruhda salom! Meni admin qiling.")


# @dp.my_chat_member()
# async def handle_chat_member_update(update: types.ChatMemberUpdated):
#     logger.info(f"Chat member yangilanishi: {update.new_chat_member.user.id}, Status: {update.new_chat_member.status}")
#
#     if update.new_chat_member.user.id == bot.id and update.new_chat_member.status == "member":
#         group_id = str(update.chat.id)  # JSON uchun string format
#         added_by = str(update.from_user.id)
#
#         # Guruh ma’lumotlarini saqlash
#         if group_id not in user_groups["groups"]:
#             user_groups["groups"][group_id] = {"title": update.chat.title, "added_by": added_by}
#             save_data()  # JSON yangilaymiz
#             logger.info(f"Bot {group_id} guruhiga qo‘shildi, qo‘shuvchi: {added_by}")
#
#             try:
#                 await bot.send_message(added_by, f"Men {update.chat.title} guruhiga qo‘shildim!")
#                 logger.info(f"Qo‘shilish xabari {added_by} ga yuborildi")
#             except Exception as e:
#                 logger.error(f"Qo‘shilish xabarini yuborishda xato: {e}")


@dp.message()
async def handle_message(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        group_id = str(message.chat.id)  # Guruh ID string formatda
        user_id = str(message.from_user.id)
        username = message.from_user.username or "Username yo‘q"
        text = message.text or "Matn yo‘q"
        group_name = message.chat.title
        logger.info(f"Guruh xabari: {group_id}, Matn: {text}, Foydalanuvchi: {user_id}")

        # Xabarni guruhni qo‘shgan userga yuborish
        if group_id in user_groups["groups"]:
            owner_id = user_groups["groups"][group_id]["added_by"]
            logger.info(f"{owner_id} ga xabar yuborilmoqda")
            try:
                await bot.send_message(
                    owner_id,
                    f"📩 *Guruh:* {group_name}\n👤 *ID:* {user_id}\n🔗 *Username:* @{username}\n💬 *Xabar:* {text}",
                    parse_mode="Markdown"
                )
                logger.info(f"Xabar {owner_id} ga muvaffaqiyatli yuborildi")
            except Exception as e:
                logger.error(f"Xabar yuborishda xato: {e}")
        else:
            logger.warning(f"{group_id} guruhi hech kimning ro‘yxatida topilmadi")


async def main():
    logger.info("Bot polling rejimida boshlanmoqda")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
