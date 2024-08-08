from bs4 import BeautifulSoup
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException
import random


api_key = 'api_key'
api_secret = 'api_secret'

client = Client(api_key, api_secret)

def fetch_scraped_symbols(url, class_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all('span', class_=class_name)

    scraped_symbols = []
    for element in elements:
        token_name_element = element.find_parent('a')
        if token_name_element:
            text = token_name_element.text.strip()
            words = text.split()
            if len(words) >= 2:
                scraped_symbols.append(words[1])
            else:
                print("Yeterli veri yok")
    return scraped_symbols


def buy_tokens():
    print("Satın alma işlemi başlatılıyor...")
    url = 'https://cfgi.io'
    class_name = 'badge badge-pill badge-light-light-danger'
    scraped_symbols = fetch_scraped_symbols(url, class_name)

    binance_symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'AVAX', 'DOT', 'TRX', 'LINK', 'UNI', 'MATIC', 'LTC', 'FIL', 'ATOM', 'HBAR', 'XLM', 'VET', 'THETA', 'FLOW','NEAR','ZEC']

    valid_symbols = [symbol for symbol in scraped_symbols if symbol in binance_symbols]

    if not valid_symbols:
        print("İşlem yapılacak uygun sembol bulunamadı.")
        print("Satın alma işlemi tamamlandı.")
        return

    selected_symbol = random.choice(valid_symbols) + 'USDT'

    try:
        order = client.create_order(
            symbol=selected_symbol,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quoteOrderQty=15 
        )
        print(f"Satın alma işlemi başarılı: {selected_symbol}", order)
    except BinanceAPIException as e:
        print(f"Satın alma işlemi başarısız: {e}")

    print("Satın alma işlemi tamamlandı.")

def sell_tokens():
    print("Satış işlemi başlatılıyor...")
    url = 'https://cfgi.io'
    class_name = 'badge badge-pill badge-light-success'
    scraped_symbols = fetch_scraped_symbols(url, class_name)

    account = client.get_account()
    balances = {balance['asset']: float(balance['free']) for balance in account['balances'] if float(balance['free']) > 0}

    for symbol in scraped_symbols:
        if symbol in balances and balances[symbol] > 0:
            sell_symbol = symbol + 'USDT'
            quantity = balances[symbol]

            try:
                info = client.get_symbol_info(sell_symbol)
                if not info:
                    print(f"Sembol bilgisi bulunamadı: {sell_symbol}")
                    continue

                lot_size_filter = next((f for f in info['filters'] if f['filterType'] == 'LOT_SIZE'), None)
                if lot_size_filter:
                    step_size = float(lot_size_filter['stepSize'])
                    quantity = round(quantity // step_size * step_size, 8) 

                min_notional_filter = next((f for f in info['filters'] if f['filterType'] == 'MIN_NOTIONAL'), None)
                if min_notional_filter:
                    min_notional = float(min_notional_filter['minNotional'])
                    current_price = float(client.get_symbol_ticker(symbol=sell_symbol)['price'])
                    notional_value = quantity * current_price
                    if notional_value < min_notional:
                        print(f"Min notional değeri karşılanamıyor: {sell_symbol}")
                        continue

                order = client.create_order(
                    symbol=sell_symbol,
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantity
                )
                print(f"Başarıyla satıldı: {quantity} {sell_symbol}", order)
            except BinanceAPIException as e:
                print(f"Satış işlemi başarısız: {sell_symbol}, Hata: {e}")

    print("Satış işlemi tamamlandı.")

