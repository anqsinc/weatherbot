import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

class WeatherForecast:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city):
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ru'
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            weather_info = {
                'city': city,
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return weather_info
            
        except requests.exceptions.RequestException as e:
            return f"Ошибка при запросе погоды для {city}: {str(e)}"
        except KeyError:
            return f"Не удалось обработать данные для {city}"

    def format_weather(self, weather_info):
        if isinstance(weather_info, dict):
            return (
                f"Погода в {weather_info['city']}:\n"
                f"Температура: {weather_info['temperature']}°C\n"
                f"Ощущается как: {weather_info['feels_like']}°C\n"
                f"Описание: {weather_info['description']}\n"
                f"Влажность: {weather_info['humidity']}%\n"
                f"Скорость ветра: {weather_info['wind_speed']} м/с\n"
                f"Время обновления: {weather_info['timestamp']}"
            )
        return weather_info

# Замените на ваши ключи
API_KEY = 'f2a9b80c417d4c74cf59c9d6de5160cd'
BOT_TOKEN = '6450033087:AAEEKI4FyvJsd-FUWLbxm5IfE2Zb-PhqRXE'

weather_checker = WeatherForecast(API_KEY)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот погоды. Используйте команды:\n"
        "/weather <город> - получить погоду\n"
        "Или просто напишите название города"
    )

# Команда /weather
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите город после команды /weather")
        return
    
    city = " ".join(context.args)
    weather = weather_checker.get_weather(city)
    response = weather_checker.format_weather(weather)
    await update.message.reply_text(response)

# Обработка текстовых сообщений (названий городов)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    weather = weather_checker.get_weather(city)
    response = weather_checker.format_weather(weather)
    await update.message.reply_text(response)

# Обработка ошибок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")

def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error)

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()