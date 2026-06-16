"""Модуль для генерации JSON-ответов для веб-страниц."""
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from pathlib import Path

from src.utils import (
    load_transactions_from_excel,
    filter_transactions_by_date_range,
    get_greeting,
    format_date
)

logger = logging.getLogger(__name__)


def load_user_settings() -> Dict[str, Any]:
    """Загрузка пользовательских настроек."""
    try:
        with open('user_settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            logger.info(f"Загружены настройки: {settings}")
            return settings
    except Exception as e:
        logger.error(f"Ошибка загрузки настроек: {e}")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": []}


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Получение курсов валют от API ЦБ РФ."""
    rates = []
    try:
        # Используем API ЦБ РФ
        url = "https://www.cbr.ru/scripts/XML_daily.asp"
        response = requests.get(url)

        if response.status_code == 200:
            import xml.etree.ElementTree as ETree
            root = ETree.fromstring(response.content)

            for currency in root.findall('.//Valute'):
                char_code = currency.find('CharCode').text
                if char_code in currencies:
                    value = float(currency.find('Value').text.replace(',', '.'))
                    nominal = int(currency.find('Nominal').text)
                    rate = value / nominal
                    rates.append({
                        "currency": char_code,
                        "rate": round(rate, 4)
                    })
        else:
            # Fallback курсы для тестирования
            fallback_rates = {"USD": 92.5, "EUR": 100.2}
            for curr in currencies:
                if curr in fallback_rates:
                    rates.append({"currency": curr, "rate": fallback_rates[curr]})

    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
        # Возвращаем тестовые курсы
        for curr in currencies:
            rates.append({"currency": curr, "rate": 90.0})

    return rates


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """Получение цен акций от API MOEX."""
    prices = []
    try:
        for stock in stocks:
            url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{stock}.json"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                market_data = data.get('marketdata', {}).get('data', [])
                if market_data and len(market_data) > 0:
                    last_price = market_data[0][3]  # LAST цена
                    prices.append({
                        "stock": stock,
                        "price": round(float(last_price), 2)
                    })
                else:
                    prices.append({"stock": stock, "price": 0.0})
            else:
                # Fallback цена для тестирования
                fallback_prices = {"AAPL": 175.50, "GOOGL": 135.20, "MSFT": 380.30, "AMZN": 145.80, "TSLA": 240.50}
                prices.append({"stock": stock, "price": fallback_prices.get(stock, 100.0)})

    except Exception as e:
        logger.error(f"Ошибка получения цен акций: {e}")
        for stock in stocks:
            prices.append({"stock": stock, "price": 0.0})

    return prices


def get_card_data(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Получение данных по картам."""
    cards_data = {}

    for trans in transactions:
        card_number = trans.get('Номер карты', '')
        if not card_number:
            continue

        amount = trans.get('Сумма операции', 0)
        if amount < 0 or trans.get('Тип операции') == 'Расход':
            abs_amount = abs(amount)

            if card_number not in cards_data:
                cards_data[card_number] = {
                    'last_digits': card_number[-4:],
                    'total_expenses': 0,
                    'cashback': 0,
                    'transactions': []
                }

            cards_data[card_number]['total_expenses'] += abs_amount
            cards_data[card_number]['cashback'] = abs_amount // 100  # 1 рубль на каждые 100
            cards_data[card_number]['transactions'].append({
                'date': format_date(trans.get('Дата операции', ''), '%Y-%m-%d %H:%M:%S', '%d.%m.%Y'),
                'amount': abs_amount,
                'category': trans.get('Категория', 'Другое'),
                'description': trans.get('Описание', '')
            })

    # Получаем топ-5 транзакций для каждой карты
    result = []
    for card_num, data in cards_data.items():
        top_transactions = sorted(data['transactions'], key=lambda x: x['amount'], reverse=True)[:5]
        result.append({
            'last_digits': data['last_digits'],
            'total_expenses': round(data['total_expenses']),
            'cashback': int(data['cashback']),
            'top_transactions': top_transactions
        })

    return result


def main(date_time_str: str) -> str:
    """Главная функция для генерации JSON-ответа."""
    logger.info(f"Генерация данных для веб-страницы на дату: {date_time_str}")

    transactions = load_transactions_from_excel('data/operations.xlsx')

    filtered_transactions = filter_transactions_by_date_range(transactions, date_time_str)

    settings = load_user_settings()

    greeting = get_greeting()
    cards_data = get_card_data(filtered_transactions)
    currency_rates = get_currency_rates(settings.get('user_currencies', []))
    stock_prices = get_stock_prices(settings.get('user_stocks', []))

    # Формируем JSON-ответ
    response = {
        "greeting": greeting,
        "cards": cards_data,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    return json.dumps(response, ensure_ascii=False, indent=2)
