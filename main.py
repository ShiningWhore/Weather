import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import escape_md

API_TOKEN = '7012947755:AAE8XJfd11EDkUh4iejIUtHVMu4Ln1mRn_s'
OWM_API_KEY = 'feef3a4839119c64f648cf41064f990e'

# Инициализируем бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# Функция для получения прогноза погоды
def get_weather(city: str) -> str:
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang=ru'
        response = requests.get(url)
        data = response.json()

        if data["cod"] != 200:
            return f"Ошибка: город {city} не найден."

        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return (f"Погода в городе {city}:\n"
                f"Состояние: {weather.capitalize()}\n"
                f"Температура: {temp}°C\n"
                f"Ощущается как: {feels_like}°C\n"
                f"Влажность: {humidity}%\n"
                f"Скорость ветра: {wind_speed} м/с")
    except requests.RequestException:
        return "Не удалось подключиться к серверу OpenWeatherMap."

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я бот для получения прогноза погоды. Введи /weather {город}, чтобы узнать погоду в нужном городе.")

# Команда /weather
@dp.message_handler(commands=['weather'])
async def weather(message: types.Message):
    args = message.get_args()
    if not args:
        await message.answer("Пожалуйста, укажите город. Пример: /weather Москва")
    else:
        city = args.strip()
        weather_info = get_weather(city)
        await message.answer(weather_info)

# Inline запрос
@dp.inline_handler()
async def inline_weather(inline_query: types.InlineQuery):
    city = inline_query.query.strip()
    if not city:
        return  # Если пользователь не ввел город, ничего не делаем

    weather_info = get_weather(city)

    result = InlineQueryResultArticle(
        id=city,
        title=f"Погода в {city}",
        input_message_content=InputTextMessageContent(weather_info)
    )

    await bot.answer_inline_query(inline_query.id, results=[result], cache_time=1)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)