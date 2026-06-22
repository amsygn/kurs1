"""Модуль для генерации JSON-ответов для веб-страниц."""
import logging
import json
import requests

from typing import List, Dict, Any
from datetime import datetime, timedelta
from xml.etree.ElementTree import fromstring

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
    """
    Получение курсов валют от API ЦБ РФ.

    Args:
        currencies: список кодов валют

    Returns:
        список словарей с курсами валют
    """
    rates = []
    try:
        # Используем API ЦБ РФ
        url = "https://www.cbr.ru/scripts/XML_daily.asp"
        response = requests.get(url)

        if response.status_code == 200:
            root = fromstring(response.content)

            for currency_element in root.findall('.//Valute'):
                char_code = currency_element.find('CharCode').text
                if char_code in currencies:
                    value = float(currency_element.find('Value').text.replace(',', '.'))
                    nominal = int(currency_element.find('Nominal').text)
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
    """
    Получение цен акций от API MOEX.

    Args:
        stocks: список тикеров акций

    Returns:
        список словарей с ценами акций
    """
    prices = []
    try:
        for stock in stocks:
            url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{stock}.json"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                # Получаем последнюю цену
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
    """
    Получение данных по картам.

    Args:
        transactions: список транзакций

    Returns:
        список данных по картам
    """
    cards_data = {}

    for trans in transactions:
        card_number = trans.get('Номер карты', '')
        if not card_number:
            continue

        amount = trans.get('Сумма операции', 0)
        # Учитываем только расходы (отрицательные суммы или специальное поле)
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


def get_date_range(date_str: str, range_type: str = 'M') -> tuple:
    """
    Определение диапазона дат в зависимости от типа.

    Args:
        date_str: исходная дата в формате YYYY-MM-DD HH:MM:SS
        range_type: тип диапазона ('W', 'M', 'Y', 'ALL')

    Returns:
        кортеж (дата_начала, дата_конца)
    """
    end_dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

    if range_type == 'W':
        # Начало недели (понедельник)
        start_dt = end_dt - timedelta(days=end_dt.weekday())
        start_dt = start_dt.replace(hour=0, minute=0, second=0)
    elif range_type == 'M':
        # Начало месяца
        start_dt = end_dt.replace(day=1, hour=0, minute=0, second=0)
    elif range_type == 'Y':
        # Начало года
        start_dt = end_dt.replace(month=1, day=1, hour=0, minute=0, second=0)
    elif range_type == 'ALL':
        # Все данные до указанной даты (используем минимальную дату)
        start_dt = datetime(2000, 1, 1)
    else:
        # По умолчанию месяц
        start_dt = end_dt.replace(day=1, hour=0, minute=0, second=0)

    return start_dt, end_dt


def aggregate_expenses(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Агрегация расходов по категориям.

    Args:
        transactions: список транзакций

    Returns:
        словарь с расходами
    """
    categories = {}
    transfers_and_cash = {}

    for trans in transactions:
        amount = trans.get('Сумма операции', 0)
        if amount < 0:  # Только расходы
            category = trans.get('Категория', 'Другое')
            abs_amount = abs(amount)

            # Отделяем переводы и наличные
            if 'перевод' in category.lower():
                transfers_and_cash['Переводы'] = transfers_and_cash.get('Переводы', 0) + abs_amount
            elif 'наличные' in category.lower():
                transfers_and_cash['Наличные'] = transfers_and_cash.get('Наличные', 0) + abs_amount
            else:
                categories[category] = categories.get(category, 0) + abs_amount

    # Сортируем категории по убыванию
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    top_7 = sorted_categories[:7]
    other_sum = sum(amount for _, amount in sorted_categories[7:])

    main_categories = [{'category': cat, 'amount': round(amount)} for cat, amount in top_7]
    if other_sum > 0:
        main_categories.append({'category': 'Остальное', 'amount': round(other_sum)})

    # Сортируем переводы и наличные
    sorted_transfers = sorted(transfers_and_cash.items(), key=lambda x: x[1], reverse=True)
    transfers_cash_list = [{'category': cat, 'amount': round(amount)} for cat, amount in sorted_transfers]

    total_expenses = sum(abs(t.get('Сумма операции', 0)) for t in transactions if t.get('Сумма операции', 0) < 0)

    return {
        'total_amount': round(total_expenses),
        'main': main_categories,
        'transfers_and_cash': transfers_cash_list
    }


def aggregate_income(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Агрегация поступлений по категориям.

    Args:
        transactions: список транзакций

    Returns:
        словарь с поступлениями
    """
    categories = {}

    for trans in transactions:
        amount = trans.get('Сумма операции', 0)
        if amount > 0:  # Только поступления
            category = trans.get('Категория', 'Другое')
            categories[category] = categories.get(category, 0) + amount

    # Сортируем по убыванию
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)

    main_income = [{'category': cat, 'amount': round(amount)} for cat, amount in sorted_categories]

    total_income = sum(t.get('Сумма операции', 0) for t in transactions if t.get('Сумма операции', 0) > 0)

    return {
        'total_amount': round(total_income),
        'main': main_income
    }


def events_page(date_time_str: str, range_type: str = 'M') -> str:
    """
    Главная функция для страницы "События".

    Args:
        date_time_str: строка с датой и временем в формате YYYY-MM-DD HH:MM:SS
        range_type: тип диапазона ('W', 'M', 'Y', 'ALL')

    Returns:
        JSON-строка с данными для страницы событий
    """
    logger.info(f"Генерация данных для страницы событий на дату: {date_time_str}, тип диапазона: {range_type}")

    # Загружаем транзакции
    transactions = load_transactions_from_excel('data/operations.xlsx')

    # Определяем диапазон дат
    start_date, end_date = get_date_range(date_time_str, range_type)
    logger.info(f"Диапазон данных: с {start_date} по {end_date}")

    # Фильтруем транзакции
    filtered_transactions = []
    for trans in transactions:
        trans_date_str = trans.get('Дата операции', '')
        if trans_date_str:
            trans_date = datetime.strptime(trans_date_str, '%Y-%m-%d %H:%M:%S')
            if start_date <= trans_date <= end_date:
                filtered_transactions.append(trans)

    # Загружаем настройки
    settings = load_user_settings()

    # Агрегируем данные
    expenses_data = aggregate_expenses(filtered_transactions)
    income_data = aggregate_income(filtered_transactions)

    # Получаем курсы валют и цены акций
    currency_rates = get_currency_rates(settings.get('user_currencies', []))
    stock_prices = get_stock_prices(settings.get('user_stocks', []))

    # Формируем JSON-ответ
    response = {
        "expenses": expenses_data,
        "income": income_data,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    return json.dumps(response, ensure_ascii=False, indent=2)


def main(date_time_str: str) -> str:
    """Главная функция для главной страницы."""
    logger.info(f"Генерация данных для главной страницы на дату: {date_time_str}")

    # Фильтруем по дате
    filtered_transactions = filter_transactions_by_date_range(transactions, date_time_str)

    # Загружаем настройки
    settings = load_user_settings()

    # Получаем данные
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
