# -*- coding: utf8 -*-
import os
from weather_bot import get_weather
from server.DB import add_tg_user_to_db
from settings_app.API_token import telegram_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from geopy.geocoders import Nominatim

try:
    os.chdir('../')
    with open(os.path.join(os.getcwd(), 'settings_app', 'hello_text.txt'), 'r', encoding="utf-8") as text_file:
        text = text_file.read()
except FileNotFoundError:
    text = "В разработке"

telegram_bot = Bot(token=telegram_token)
storage = MemoryStorage()
dispatcher = Dispatcher(bot=telegram_bot, storage=storage)
geolocator = Nominatim(user_agent="Ashley")

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

first_row = ["Погода в СПб"]
second_row = ["Погода в другом городе"]
third_row = ["Настройки", "Инструкция"]
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(*first_row).add(*second_row).add(*third_row)


class Temp(StatesGroup):
    city = State()


users = dict()


@dispatcher.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    users[user_id] = dict()
    username = message.from_user.username
    users[user_id]['username'] = username
    add_tg_user_to_db(user_id, username)
    await message.answer(f"Привет! Жми кнопку и погнали!", reply_markup=keyboard)


@dispatcher.message_handler(Text(equals="Настройки"))
async def start_command(set_message: types.Message):
    set_buttons = ["Ежедневная отправка погоды"]
    phone = ["Поделиться контактом"]
    geo = ["Поделиться геопозицией"]
    settings_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    settings_keyboard.add(*set_buttons) \
        .add(types.KeyboardButton(*phone, request_contact=True)) \
        .add(types.KeyboardButton(*geo, request_location=True))
    await set_message.answer("Кнопка в разработке. Новые функции не за горами!", reply_markup=settings_keyboard)


@dispatcher.message_handler(content_types=types.ContentType.CONTACT)
async def get_number(message: types.Message):
    user_id = message.from_user.id
    number = message.contact.phone_number
    users[user_id]['phone'] = number
    await message.answer("", reply_markup=keyboard)


@dispatcher.message_handler(content_types=types.ContentType.LOCATION)
async def get_city(message: types.Message):
    user_id = message.from_user.id
    loc = message.location
    location = str(geolocator.reverse(f"{loc['latitude']}, {loc['longitude']}")).split(', ')
    city = location[-4]
    users[user_id]['city'] = city
    await message.answer("", reply_markup=keyboard)


@dispatcher.message_handler(Text(equals="Инструкция"))
async def start_command(message: types.Message):
    await message.answer(text=text, reply_markup=keyboard)


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
    if 'notifications' in users[user_id]:
        answer_buttons = ["Да", "Нет"]
        answer_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        answer_keyboard.add(*answer_buttons)
        await message.answer("Удалить ежедневную отправку данных о погоде?", reply_markup=answer_keyboard)

    else:
        time_buttons = ["7:00", "8:00", "9:00"]
        time_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        time_keyboard.add(*time_buttons)
        await message.answer("В какое время отправлять данные о погоде?", reply_markup=time_keyboard)


@dispatcher.message_handler(Text(equals=["7:00", "8:00", "9:00"]))
async def cron_weather(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "7:00":
        hour = 7
        minutes = 0
    elif message.text == "8:00":
        hour = 8
        minutes = 0
    else:
        hour = 9
        minutes = 0
    users_id.append(user_id)
    scheduler.add_job(func=tg_cron_weather_spb, args=(dispatcher, user_id,)
                      , trigger="cron", hour=hour, minute=minutes, id=str(user_id))
    print("Добавлена задача:", scheduler.get_job(job_id=str(user_id)))
    print("Список активных задач:", scheduler.get_jobs())
    await state.update_data(time_to_notif=message.text)
    await message.answer(f"Отправка уведомлений установлена на {message.text}", reply_markup=keyboard)


@dispatcher.message_handler(Text(equals=["Да", "Нет"]))
async def cron_status(message: types.Message):
    user_id = message.from_user.id
    if message.text == "Да":
        users[user_id].pop('notifications')
        print("Удалена задача:", scheduler.get_job(job_id=str(user_id)))
        scheduler.remove_job(job_id=str(user_id))
        print("Список активных задач:", scheduler.get_jobs())
        await message.answer("Ежедневные напоминания удалены", reply_markup=keyboard)
    else:
        await message.answer("Хорошо, оставим тебе напоминания", reply_markup=keyboard)


@dispatcher.message_handler(Text(equals="Погода в другом городе"))
async def tg_another_weather(message: types.Message):
    await Temp.city.set()
    await message.answer("Пришли название города в чат...", reply_markup=types.ReplyKeyboardRemove())


@dispatcher.message_handler(state=Temp.city)
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


async def tg_cron_weather_spb(dp: Dispatcher, user_id, city="Санкт-Петербург"):
    try:
        city_name, temp, humidity, description, weather, wind, lat, lon, sunrise, sunset = \
            get_weather(city)
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
