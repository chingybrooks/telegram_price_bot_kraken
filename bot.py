import telebot
import requests
import config  # Импортируем файл с конфигурациями

TELEGRAM_TOKEN = config.TELEGRAM_TOKEN

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_crypto_price(symbol: str) -> float:
    # Преобразование BTC к XBT для Kraken
    kraken_symbol = "XBT" if symbol.upper() == "BTC" else symbol.upper()
    
    # Сначала проверяем, существует ли такая пара на Kraken
    asset_pairs_url = "https://api.kraken.com/0/public/AssetPairs"
    pairs_response = requests.get(asset_pairs_url)
    
    if pairs_response.status_code == 200:
        pairs_data = pairs_response.json()
        available_pairs = pairs_data['result'].keys()

        # Ищем нужную пару
        target_pair = f"X{kraken_symbol}ZUSD"
        if target_pair not in available_pairs:
            return None  # пара не найдена на Kraken
        
        url = f'https://api.kraken.com/0/public/Ticker?pair={target_pair}'
        response = requests.get(url)
        print(f"URL: {url} - Status: {response.status_code}")  # Сокращенное логирование

        if response.status_code == 200:
            data = response.json()
            if 'result' in data and target_pair in data['result']:
                return float(data['result'][target_pair]['c'][0])

    return None

@bot.message_handler(commands=['p'])
def send_price(message):
    coin = message.text.split()[1] if len(message.text.split()) > 1 else None

    if not coin:
        bot.reply_to(message, "Пожалуйста, укажите монету. Пример: /p btc")
        return

    price = get_crypto_price(coin)
    if price:
        bot.reply_to(message, f"Текущая цена {coin.upper()}: ${price}")
    else:
        bot.reply_to(message, f"Не удалось получить цену для {coin.upper()} или такой пары нет на Kraken.")

bot.polling(none_stop=True)
