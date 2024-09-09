import os
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils import executor
from aiogram.utils.markdown import hbold
from uuid import uuid4

API_TOKEN = '7012947755:AAE8XJfd11EDkUh4iejIUtHVMu4Ln1mRn_s'
WEATHER_API_KEY = 'feef3a4839119c64f648cf41064f990e'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

async def get_weather(city: str) -> str:
    """Получаем прогноз погоды для указанного города через API OpenWeatherMap"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                city_name = data['name']
                temp = data['main']['temp']
                weather_desc = data['weather'][0]['description']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                return (
                    f"{hbold('Погода в городе:')} {city_name}\n"
                    f"{hbold('Температура:')} {temp}°C\n"
                    f"{hbold('Описание:')} {weather_desc}\n"
                    f"{hbold('Влажность:')} {humidity}%\n"
                    f"{hbold('Скорость ветра:')} {wind_speed} м/с"
                )
            else:
                return "Город не найден, попробуйте еще раз."

@dp.message_handler(commands=['weather'])
async def send_weather(message: types.Message):
    """Обработка команды /weather {город} в группе"""
    if len(message.text.split()) > 1:
        city = message.text.split(maxsplit=1)[1]
        weather_report = await get_weather(city)
        await message.reply(weather_report)
    else:
        await message.reply("Пожалуйста, укажите город после команды /weather")

@dp.inline_handler()
async def inline_weather(inline_query: types.InlineQuery):
    """Обработка inline-запроса с названием города"""
    query = inline_query.query.strip()
    if not query:
        return
    
    weather_report = await get_weather(query)
    
    result = InlineQueryResultArticle(
        id=str(uuid4()),
        title=f"Погода в {query}",
        input_message_content=InputTextMessageContent(weather_report)
    )
    
    await inline_query.answer([result], cache_time=1, is_personal=True)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)