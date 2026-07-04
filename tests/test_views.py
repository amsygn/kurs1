"""Тесты для модуля views."""
import unittest
import json
from datetime import datetime
from unittest.mock import patch, Mock, mock_open
import pandas as pd

from src.views import (
    get_card_data,
    get_date_range,
    aggregate_expenses,
    aggregate_income,
    load_user_settings,
    get_currency_rates,
    get_stock_prices,
    main,
    events_page
)


class TestViews(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных."""
        self.test_transactions = [
            {
                'Номер карты': '1234567890123456',
                'Сумма операции': -1500,
                'Дата операции': '2023-12-15 10:30:00',
                'Категория': 'Рестораны',
                'Описание': 'Обед в кафе',
                'Контрагент': 'Кафе Уют'
            },
            {
                'Номер карты': '1234567890123456',
                'Сумма операции': -500,
                'Дата операции': '2023-12-16 15:20:00',
                'Категория': 'Супермаркеты',
                'Описание': 'Покупка продуктов',
                'Контрагент': 'Магнит'
            },
            {
                'Номер карты': '1234567890123456',
                'Сумма операции': 10000,
                'Дата операции': '2023-12-17 09:00:00',
                'Категория': 'Пополнение',
                'Описание': 'Пополнение счета',
                'Контрагент': 'Банк'
            },
            {
                'Номер карты': '9876543210987654',
                'Сумма операции': -3000,
                'Дата операции': '2023-12-18 14:00:00',
                'Категория': 'Переводы',
                'Описание': 'Перевод Ивану С.',
                'Контрагент': 'Иван С.'
            },
            {
                'Номер карты': '9876543210987654',
                'Сумма операции': -200,
                'Дата операции': '2023-12-19 11:00:00',
                'Категория': 'Наличные',
                'Описание': 'Снятие наличных',
                'Контрагент': 'Банкомат'
            }
        ]

    def test_get_card_data(self):
        """Тест получения данных по картам."""
        result = get_card_data(self.test_transactions)

        # Должно быть 2 карты
        self.assertEqual(len(result), 2)

        # Проверяем первую карту
        card1 = result[0]
        self.assertEqual(card1['last_digits'], '3456')
        self.assertEqual(card1['total_expenses'], 2000)  # 1500 + 500

        # ✅ Кешбэк накапливается: 1500//100=15, 500//100=5, итого 20
        # Но! Кешбэк добавляется при каждой транзакции
        self.assertEqual(card1['cashback'], 20)
        self.assertEqual(len(card1['top_transactions']), 2)

        # Проверяем вторую карту
        card2 = result[1]
        self.assertEqual(card2['last_digits'], '7654')
        self.assertEqual(card2['total_expenses'], 3200)  # 3000 + 200
        self.assertEqual(card2['cashback'], 32)  # 30 + 2

    def test_get_card_data_empty(self):
        """Тест получения данных по картам с пустым списком."""
        result = get_card_data([])
        self.assertEqual(result, [])

    def test_get_card_data_with_nan_card(self):
        """Тест обработки NaN в номере карты."""
        transactions = [
            {
                'Номер карты': float('nan'),
                'Сумма операции': -1500,
                'Дата операции': '2023-12-15 10:30:00',
                'Категория': 'Рестораны',
                'Описание': 'Обед'
            }
        ]
        result = get_card_data(transactions)
        self.assertEqual(result, [])

    def test_get_date_range_month(self):
        """Тест диапазона дат - месяц."""
        start, end = get_date_range('2023-12-20 15:30:00', 'M')
        self.assertEqual(start.year, 2023)
        self.assertEqual(start.month, 12)
        self.assertEqual(start.day, 1)
        self.assertEqual(start.hour, 0)
        self.assertEqual(start.minute, 0)
        self.assertEqual(end.year, 2023)
        self.assertEqual(end.month, 12)
        self.assertEqual(end.day, 20)

    def test_get_date_range_week(self):
        """Тест диапазона дат - неделя."""
        start, end = get_date_range('2023-12-20 15:30:00', 'W')
        # 20.12.2023 - среда, начало недели - понедельник 18.12.2023
        self.assertEqual(start.day, 18)
        self.assertEqual(start.month, 12)
        self.assertEqual(start.year, 2023)

    def test_get_date_range_year(self):
        """Тест диапазона дат - год."""
        start, end = get_date_range('2023-12-20 15:30:00', 'Y')
        self.assertEqual(start.year, 2023)
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)

    def test_get_date_range_all(self):
        """Тест диапазона дат - все данные."""
        start, end = get_date_range('2023-12-20 15:30:00', 'ALL')
        self.assertEqual(start.year, 2000)
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)

    def test_aggregate_expenses(self):
        """Тест агрегации расходов."""
        result = aggregate_expenses(self.test_transactions)

        # Общая сумма расходов: 1500 + 500 + 3000 + 200 = 5200
        self.assertEqual(result['total_amount'], 5200)

        # Проверяем основные категории
        main_categories = result['main']
        # ✅ Категории: Рестораны (1500), Супермаркеты (500)
        # Остальное не добавляется, так как нет других категорий
        self.assertEqual(len(main_categories), 2)

        # Проверяем названия категорий
        category_names = [item['category'] for item in main_categories]
        self.assertIn('Рестораны', category_names)
        self.assertIn('Супермаркеты', category_names)

        # Проверяем суммы
        for item in main_categories:
            if item['category'] == 'Рестораны':
                self.assertEqual(item['amount'], 1500)
            elif item['category'] == 'Супермаркеты':
                self.assertEqual(item['amount'], 500)

        # Проверяем переводы и наличные
        transfers_cash = result['transfers_and_cash']
        self.assertEqual(len(transfers_cash), 2)

        # Проверяем, что переводы и наличные есть
        transfer_amounts = {item['category']: item['amount'] for item in transfers_cash}
        self.assertIn('Переводы', transfer_amounts)
        self.assertEqual(transfer_amounts['Переводы'], 3000)
        self.assertIn('Наличные', transfer_amounts)
        self.assertEqual(transfer_amounts['Наличные'], 200)

    def test_aggregate_income(self):
        """Тест агрегации доходов."""
        result = aggregate_income(self.test_transactions)

        # Общая сумма доходов: 10000
        self.assertEqual(result['total_amount'], 10000)

        # Проверяем категории
        main_income = result['main']
        self.assertEqual(len(main_income), 1)
        self.assertEqual(main_income[0]['category'], 'Пополнение')
        self.assertEqual(main_income[0]['amount'], 10000)

    def test_aggregate_expenses_empty(self):
        """Тест агрегации расходов с пустым списком."""
        result = aggregate_expenses([])
        self.assertEqual(result['total_amount'], 0)
        self.assertEqual(result['main'], [])
        self.assertEqual(result['transfers_and_cash'], [])

    def test_load_user_settings(self):
        """Тест загрузки настроек пользователя."""
        mock_content = '{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}'

        # ✅ Исправленный мок
        with patch('builtins.open', mock_open(read_data=mock_content)):
            result = load_user_settings()
            self.assertEqual(result['user_currencies'], ["USD", "EUR"])
            self.assertEqual(result['user_stocks'], ["AAPL", "GOOGL"])

    def test_load_user_settings_fallback(self):
        """Тест загрузки настроек при ошибке."""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = load_user_settings()
            self.assertIn('user_currencies', result)
            self.assertIn('user_stocks', result)
            self.assertEqual(len(result['user_currencies']), 3)
            self.assertEqual(len(result['user_stocks']), 5)

    def test_get_currency_rates(self):
        """Тест получения курсов валют."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'''<?xml version="1.0" encoding="windows-1251"?>
        <ValCurs Date="2023-12-20">
            <Valute ID="R01235">
                <CharCode>USD</CharCode>
                <Nominal>1</Nominal>
                <Value>73,7650</Value>
            </Valute>
            <Valute ID="R01239">
                <CharCode>EUR</CharCode>
                <Nominal>1</Nominal>
                <Value>84,5863</Value>
            </Valute>
        </ValCurs>'''

        with patch('requests.get', return_value=mock_response):
            result = get_currency_rates(['USD', 'EUR'])
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['currency'], 'USD')
            self.assertEqual(result[0]['rate'], 73.765)
            self.assertEqual(result[1]['currency'], 'EUR')
            self.assertEqual(result[1]['rate'], 84.5863)

    def test_get_currency_rates_fallback(self):
        """Тест получения курсов валют при ошибке API."""
        with patch('requests.get', side_effect=Exception('API Error')):
            result = get_currency_rates(['USD', 'EUR'])
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['currency'], 'USD')
            self.assertEqual(result[0]['rate'], 90.0)

    def test_get_stock_prices(self):
        """Тест получения цен акций."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'marketdata': {
                'data': [[None, None, None, 175.50]]
            }
        }

        with patch('requests.get', return_value=mock_response):
            result = get_stock_prices(['AAPL'])
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['stock'], 'AAPL')
            self.assertEqual(result[0]['price'], 175.50)

    def test_main(self):
        """Тест главной функции."""
        with patch('src.views.load_user_settings') as mock_settings, \
             patch('src.views.get_currency_rates') as mock_rates, \
             patch('src.views.get_stock_prices') as mock_stocks, \
             patch('src.views.get_greeting') as mock_greeting, \
             patch('src.views.get_card_data') as mock_cards:

            mock_settings.return_value = {
                'user_currencies': ['USD', 'EUR'],
                'user_stocks': ['AAPL', 'GOOGL']
            }
            mock_rates.return_value = [{'currency': 'USD', 'rate': 73.765}]
            mock_stocks.return_value = [{'stock': 'AAPL', 'price': 175.50}]
            mock_greeting.return_value = 'Добрый день'
            mock_cards.return_value = [{
                'last_digits': '3456',
                'total_expenses': 2000,
                'cashback': 20,
                'top_transactions': []
            }]

            result_json = main(self.test_transactions, '2023-12-20 15:30:00')
            result = json.loads(result_json)

            self.assertIn('greeting', result)
            self.assertIn('cards', result)
            self.assertIn('currency_rates', result)
            self.assertIn('stock_prices', result)
            self.assertEqual(result['greeting'], 'Добрый день')

    def test_events_page(self):
        """Тест страницы событий."""
        with patch('src.views.load_user_settings') as mock_settings, \
             patch('src.views.get_currency_rates') as mock_rates, \
             patch('src.views.get_stock_prices') as mock_stocks:

            mock_settings.return_value = {
                'user_currencies': ['USD', 'EUR'],
                'user_stocks': ['AAPL', 'GOOGL']
            }
            mock_rates.return_value = [{'currency': 'USD', 'rate': 73.765}]
            mock_stocks.return_value = [{'stock': 'AAPL', 'price': 175.50}]

            result_json = events_page(self.test_transactions, '2023-12-20 15:30:00', 'M')
            result = json.loads(result_json)

            self.assertIn('expenses', result)
            self.assertIn('income', result)
            self.assertIn('currency_rates', result)
            self.assertIn('stock_prices', result)
            self.assertIsInstance(result['expenses'], dict)
            self.assertIsInstance(result['income'], dict)

    def test_get_card_data_cashback_calculation(self):
        """Тест расчета кешбэка."""
        # Создаем транзакции с разными суммами
        transactions = [
            {
                'Номер карты': '1234567890123456',
                'Сумма операции': -150,
                'Дата операции': '2023-12-15 10:30:00',
                'Категория': 'Рестораны',
                'Описание': 'Обед'
            },
            {
                'Номер карты': '1234567890123456',
                'Сумма операции': -250,
                'Дата операции': '2023-12-16 15:20:00',
                'Категория': 'Супермаркеты',
                'Описание': 'Продукты'
            }
        ]

        result = get_card_data(transactions)
        self.assertEqual(len(result), 1)
        # 150 // 100 = 1, 250 // 100 = 2, итого 3
        self.assertEqual(result[0]['cashback'], 3)

    def test_aggregate_expenses_with_more_categories(self):
        """Тест агрегации расходов с большим количеством категорий."""
        transactions = [
            {'Сумма операции': -1000, 'Категория': 'Категория1'},
            {'Сумма операции': -900, 'Категория': 'Категория2'},
            {'Сумма операции': -800, 'Категория': 'Категория3'},
            {'Сумма операции': -700, 'Категория': 'Категория4'},
            {'Сумма операции': -600, 'Категория': 'Категория5'},
            {'Сумма операции': -500, 'Категория': 'Категория6'},
            {'Сумма операции': -400, 'Категория': 'Категория7'},
            {'Сумма операции': -300, 'Категория': 'Категория8'},
            {'Сумма операции': -200, 'Категория': 'Категория9'},
        ]

        result = aggregate_expenses(transactions)

        # Должно быть 7 основных категорий + Остальное
        self.assertEqual(len(result['main']), 8)  # 7 + Остальное
        self.assertEqual(result['main'][-1]['category'], 'Остальное')
        self.assertEqual(result['main'][-1]['amount'], 500)  # 300 + 200


if __name__ == '__main__':
    unittest.main()
