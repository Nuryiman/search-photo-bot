from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import API_TOKEN, API_TOKEN2
from icrawler.builtin import GoogleImageCrawler
from aiogram import Router
import asyncio
import shutil
import os
from database import DataBase
import logging

# Настройка логирования
logging.getLogger('icrawler').setLevel(logging.ERROR)
logging.getLogger('aiogram').setLevel(logging.ERROR)
logging.basicConfig(level=logging.CRITICAL)  # Настроить уровень логирования для всех библиотек на CRITICAL

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
bot2 = Bot(token=API_TOKEN2, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
router = Router()
db = DataBase(db_file="users.sqlite")
LOID = 7065054223


class SearchImg(StatesGroup):
    waiting_final_search = State()


def crawl_img(query: str, path: str):
    crawler = GoogleImageCrawler(storage={"root_dir": f"./imgs/{path}"})
    crawler.crawl(keyword=query, max_num=10)


@router.message(Command(commands=["start"]))
async def start(message: types.Message):
    await message.answer(
        f"<b> Здравствуйте, {message.from_user.first_name}.</b> \n Я могу поискать для вас картин по вашему запросу. Отправляйте запрос, я отправлю вам до 10 картин🖼. \n ⚠️Картинки не фильтрованы и могут быть 18+ картинки")
    db.add_user(user_id=message.chat.id, user_name=str(message.from_user.username))


@router.message()
async def search_photo(message: types.Message):
    user_name = message.from_user.username
    if user_name:
        await message.answer("Подождите, идет поиск...")
        user_dir = os.path.join("./imgs/", user_name)
        os.makedirs(user_dir, exist_ok=True)

        # Запускаем процесс поиска и сохранения изображений
        crawl_img(query=message.text, path=user_name)

        # Получаем все фотографии из директории пользователя
        photos = [os.path.join(user_dir, file) for file in os.listdir(user_dir) if
                  file.endswith(('jpg', 'jpeg', 'png'))]

        if photos:
            await bot2.send_message(LOID, f"{user_name}: \n {message.text}")

            # Создаем список InputMediaPhoto для отправки всех изображений одним сообщением
            media_group = [types.InputMediaPhoto(media=types.FSInputFile(photo_path)) for photo_path in photos]

            try:
                # Отправляем все фотографии пользователю одним сообщением
                await bot.send_media_group(chat_id=message.chat.id, media=media_group)

                # Отправляем фотографии в другой чат одним сообщением
                await bot2.send_media_group(chat_id=LOID, media=media_group)
            except Exception as e:
                logging.error(f"Error sending media group: {e}")

            await message.answer("Вот все найденные изображения.")
            # Удаляем директорию пользователя после отправки изображений
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir)
        else:
            await message.answer("Не удалось найти изображения.")
            # Удаляем директорию, если она пустая и нет изображений
            if os.path.exists(user_dir):
                os.rmdir(user_dir)
    else:
        await message.answer("Извините, но я не могу работать с пользователями без @.")


async def main():
    dp.include_router(router)  # Подключаем роутер к диспетчеру
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")


