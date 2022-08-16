from weather_bot import get_weather
from settings_app.API_token import telegram_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

telegram_bot = Bot(token=telegram_token)
storage = MemoryStorage()
dispatcher = Dispatcher(bot=telegram_bot, storage=storage)

url = "mysql://root:Ashley299792458@127.0.0.1/tg?charset=utf8"

executors = {
    'default': ThreadPoolExecutor(10),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = AsyncIOScheduler(executors=executors, job_defaults=job_defaults, timezone="Europe/Moscow")
scheduler.add_jobstore(SQLAlchemyJobStore(url), 'apscheduler')

buttons = ["Погода в СПб", "Погода в другом городе", "Ежедневная отправка погоды"]
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(*buttons)

users_id = list()


class Form(StatesGroup):
    city = State()


@dispatcher.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    await message.answer(f"Привет: {user_id}! Жми кнопку и погнали!", reply_markup=keyboard)


@dispatcher.message_handler(Text(equals="Погода в СПб"))
async def tg_get_weather_spb(message: types.Message):
    try:
        city_name, temp, humidity, description, weather, wind, lat, lon, sunrise, sunset = \
            get_weather("Санкт-Петербург")
        await message.answer(f"Прогноз погоды в {city_name}\n"
                             f"Температура: {temp}︒C\n"
                             f"Влажность: {humidity} %\n"
                             f"Погода: {description} {weather}\n"
                             f"Скорость ветра: {wind} м/с\n"
                             f"Координаты города: {lat}, {lon}\n"
                             f"Время рассвета: {sunrise}\n"
                             f"Время заката: {sunset}"
                             )
    except Warning:
        await message.reply("Проверь название города!")


@dispatcher.message_handler(Text(equals="Ежедневная отправка погоды"))
async def tg_daily_weather(message: types.Message):
    user_id = message.from_user.id
    if user_id in users_id:
        flag = True
    else:
        flag = False
    if flag:
        answer_buttons = ["Да", "Нет"]
        answer_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        answer_keyboard.add(*answer_buttons)
        await message.answer("Удалить ежедневную отправку данных о погоде?", reply_markup=answer_keyboard)

        @dispatcher.message_handler(Text(equals=["Да", "Нет"]))
        async def cron_status(answer_message: types.Message):
            if answer_message.text == "Да":
                users_id.remove(user_id)
                scheduler.remove_job(job_id=str(user_id))
                await answer_message.answer("Ежедневные напоминания удалены", reply_markup=keyboard)
            else:
                await answer_message.answer("Хорошо, оставим тебе напоминания", reply_markup=keyboard)
    else:
        time_buttons = ["7:00", "8:00", "9:00"]
        time_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        time_keyboard.add(*time_buttons)
        await message.answer("В какое время отправлять данные о погоде?", reply_markup=time_keyboard)

        @dispatcher.message_handler(Text(equals=["7:00", "8:00", "9:00"]))
        async def cron_weather(time_message: types.Message):
            if time_message.text == "7:00":
                hour = 7
                minutes = 0
            elif time_message.text == "8:00":
                hour = 8
                minutes = 0
            else:
                hour = 9
                minutes = 0
            users_id.append(user_id)
            scheduler.add_job(tg_cron_weather_spb, trigger="cron", hour=hour, minute=minutes, id=str(user_id),
                              args=(dispatcher, user_id,))
            await time_message.answer(f"Отправка уведомлений установлена на {time_message.text}", reply_markup=keyboard)


@dispatcher.message_handler(Text(equals="Погода в другом городе"))
async def tg_another_weather(message: types.Message):
    await Form.city.set()
    await message.answer("Пришли название города в чат...", reply_markup=types.ReplyKeyboardRemove())


@dispatcher.message_handler(state=Form.city)
async def tg_get_weather(city_message: types.Message, state: FSMContext):
    try:
        city_name, temp, humidity, description, weather, wind, lat, lon, sunrise, sunset = \
            get_weather(city_message.text)
        await city_message.answer(f"Прогноз погоды в {city_name}\n"
                                  f"Температура: {temp}︒C\n"
                                  f"Влажность: {humidity} %\n"
                                  f"Погода: {description} {weather}\n"
                                  f"Скорость ветра: {wind} м/с\n"
                                  f"Координаты города: {lat}, {lon}\n"
                                  f"Время рассвета: {sunrise}\n"
                                  f"Время заката: {sunset}"
                                  , reply_markup=keyboard)
    except Warning:
        await city_message.answer("Проверь название города!", reply_markup=keyboard)
    await state.finish()


async def tg_cron_weather_spb(dp: Dispatcher, user_id):
    try:
        city_name, temp, humidity, description, weather, wind, lat, lon, sunrise, sunset = \
            get_weather("Санкт-Петербург")
        await dp.bot.send_message(chat_id=user_id, text=f"Прогноз погоды в {city_name}\n"
                                                        f"Температура: {temp}︒C\n"
                                                        f"Влажность: {humidity} %\n"
                                                        f"Погода: {description} {weather}\n"
                                                        f"Скорость ветра: {wind} м/с\n"
                                                        f"Координаты города: {lat}, {lon}\n"
                                                        f"Время рассвета: {sunrise}\n"
                                                        f"Время заката: {sunset}"
                                  )
    except Warning:
        await dp.bot.send_message(chat_id=user_id, text="Чего-то не получается")


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dispatcher)
