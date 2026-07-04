"""Тесты для модуля reports."""
import unittest
import json
import os
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from pathlib import Path

from src.reports import (
    report_decorator,
    spending_by_weekday,
    get_top_cashback_categories
)


class TestReports(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных."""
        self.test_transactions = [
            {
                'Сумма операции': -5000,
                'Категория': 'Супермаркеты',
                'Дата операции': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
                'Описание': 'Покупка продуктов',
                'Контрагент': 'Магнит'
            },
            {
                'Сумма операции': -3000,
                'Категория': 'Супермаркеты',
                'Дата операции': (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S'),
                'Описание': 'Закупка',
                'Контрагент': 'Пятерочка'
            },
            {
                'Сумма операции': -1500,
                'Категория': 'Рестораны',
                'Дата операции': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
                'Описание': 'Обед',
                'Контрагент': 'Кафе'
            },
            {
                'Сумма операции': -2000,
                'Категория': 'Транспорт',
                'Дата операции': (datetime.now() - timedelta(days=40)).strftime('%Y-%m-%d %H:%M:%S'),
                'Описание': 'Такси',
                'Контрагент': 'Яндекс.Такси'
            },
            {
                'Сумма операции': -100,
                'Категория': 'Переводы',
                'Дата операции': (datetime.now() - timedelta(days=50)).strftime('%Y-%m-%d %H:%M:%S'),
                'Описание': 'Перевод',
                'Контрагент': 'Иван С.'
            },
            {
                'Сумма операции': -50,
                'Категория': None,  # Пустая категория
                'Дата операции': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S'),
                'Описание': 'Покупка',
                'Контрагент': 'Продавец'
            }
        ]

    def test_get_top_cashback_categories(self):
        """Тест получения топ категорий по кешбэку."""
        result = get_top_cashback_categories(self.test_transactions, 3)

        self.assertEqual(len(result), 3)

        # Проверяем первую категорию (Супермаркеты: 8000 // 100 = 80)
        self.assertEqual(result[0]['category'], 'Супермаркеты')
        self.assertEqual(result[0]['cashback'], 80)

        # Проверяем вторую категорию (Транспорт: 2000 // 100 = 20)
        self.assertEqual(result[1]['category'], 'Транспорт')
        self.assertEqual(result[1]['cashback'], 20)

        # Проверяем третью категорию (Рестораны: 1500 // 100 = 15)
        self.assertEqual(result[2]['category'], 'Рестораны')
        self.assertEqual(result[2]['cashback'], 15)

    def test_get_top_cashback_categories_empty(self):
        """Тест получения топ категорий с пустым списком."""
        result = get_top_cashback_categories([])
        self.assertEqual(result, [])

    def test_get_top_cashback_categories_only_positive_amounts(self):
        """Тест: только расходы учитываются для кешбэка."""
        transactions = [
            {'Сумма операции': -1000, 'Категория': 'Категория1'},
            {'Сумма операции': 5000, 'Категория': 'Категория2'},  # Не учитывается
            {'Сумма операции': -2000, 'Категория': 'Категория1'},
        ]

        result = get_top_cashback_categories(transactions, 2)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['category'], 'Категория1')
        self.assertEqual(result[0]['cashback'], 30)  # (1000 + 2000) // 100 = 30

    def test_get_top_cashback_categories_with_nan_category(self):
        """Тест обработки NaN в категории."""
        import pandas as pd
        transactions = [
            {'Сумма операции': -1000, 'Категория': float('nan')},
            {'Сумма операции': -2000, 'Категория': None},
            {'Сумма операции': -3000, 'Категория': ''},
        ]

        result = get_top_cashback_categories(transactions, 2)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['category'], 'Без категории')
        self.assertEqual(result[0]['cashback'], 60)  # (1000+2000+3000) // 100 = 60

    def test_spending_by_weekday(self):
        """Тест отчета по дням недели."""
        result = spending_by_weekday(self.test_transactions)

        self.assertIn('period', result)
        self.assertIn('start', result['period'])
        self.assertIn('end', result['period'])
        self.assertIn('average_spending_by_weekday', result)
        self.assertEqual(len(result['average_spending_by_weekday']), 7)

    def test_spending_by_weekday_with_date(self):
        """Тест отчета по дням недели с указанной датой."""
        test_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        result = spending_by_weekday(self.test_transactions, test_date)

        self.assertIn('period', result)
        self.assertEqual(len(result['average_spending_by_weekday']), 7)

    def test_spending_by_weekday_empty(self):
        """Тест отчета по дням недели с пустым списком."""
        result = spending_by_weekday([])

        self.assertIn('period', result)
        self.assertEqual(result['average_spending_by_weekday'], [])

    def test_spending_by_weekday_no_expenses(self):
        """Тест отчета по дням недели без расходов."""
        transactions = [
            {'Сумма операции': 1000, 'Категория': 'Доход',
             'Дата операции': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'Сумма операции': 2000, 'Категория': 'Доход',
             'Дата операции': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ]

        result = spending_by_weekday(transactions)

        self.assertEqual(result['average_spending_by_weekday'], [])

    def test_report_decorator_without_filename(self):
        """Тест декоратора без указания имени файла."""

        @report_decorator()
        def test_func():
            return {"test": "data"}

        result = test_func()
        self.assertEqual(result, {"test": "data"})

        # Проверяем, что файл создан
        import glob
        files = glob.glob("test_func_*.json")
        self.assertEqual(len(files), 1)

        # Проверяем содержимое
        with open(files[0], 'r', encoding='utf-8') as f:
            content = json.load(f)
            self.assertEqual(content, {"test": "data"})

        # Очистка
        for f in files:
            Path(f).unlink()

    def test_report_decorator_with_filename(self):
        """Тест декоратора с указанием имени файла."""

        @report_decorator("test_report.json")
        def test_func():
            return {"test": "data"}

        result = test_func()
        self.assertEqual(result, {"test": "data"})

        # Проверяем, что файл создан с правильным именем
        self.assertTrue(Path("test_report.json").exists())

        # Проверяем содержимое
        with open("test_report.json", 'r', encoding='utf-8') as f:
            content = json.load(f)
            self.assertEqual(content, {"test": "data"})

        # Очистка
        Path("test_report.json").unlink()

    def test_report_decorator_with_path(self):
        """Тест декоратора с сохранением в поддиректорию."""

        @report_decorator("src/test_report.json")
        def test_func():
            return {"test": "data"}

        result = test_func()
        self.assertEqual(result, {"test": "data"})

        # Проверяем, что файл создан с правильным именем
        self.assertTrue(Path("src/test_report.json").exists())

        # Проверяем содержимое
        with open("src/test_report.json", 'r', encoding='utf-8') as f:
            content = json.load(f)
            self.assertEqual(content, {"test": "data"})

        # Очистка
        Path("src/test_report.json").unlink()

    def test_report_decorator_preserves_function_name(self):
        """Тест: декоратор сохраняет имя функции."""

        @report_decorator()
        def my_test_function():
            return {"test": "data"}

        self.assertEqual(my_test_function.__name__, "my_test_function")

    def test_spending_by_weekday_returns_dict_not_dataframe(self):
        """Тест: функция возвращает словарь, а не DataFrame."""
        result = spending_by_weekday(self.test_transactions)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['average_spending_by_weekday'], list)

    def test_spending_by_weekday_weekday_order(self):
        """Тест: дни недели в правильном порядке."""
        result = spending_by_weekday(self.test_transactions)

        weekdays = [item['weekday'] for item in result['average_spending_by_weekday']]
        expected = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

        self.assertEqual(weekdays, expected)

    def test_get_top_cashback_categories_less_than_top_n(self):
        """Тест: если категорий меньше, чем top_n."""
        transactions = [
            {'Сумма операции': -1000, 'Категория': 'Категория1'},
        ]

        result = get_top_cashback_categories(transactions, 5)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['category'], 'Категория1')
        self.assertEqual(result[0]['cashback'], 10)

    def test_get_top_cashback_categories_cashback_zero(self):
        """Тест: категории с нулевым кешбэком не включаются."""
        transactions = [
            {'Сумма операции': -50, 'Категория': 'Категория1'},  # 50//100=0
            {'Сумма операции': -99, 'Категория': 'Категория2'},  # 99//100=0
            {'Сумма операции': -100, 'Категория': 'Категория3'},  # 100//100=1
        ]

        result = get_top_cashback_categories(transactions, 3)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['category'], 'Категория3')
        self.assertEqual(result[0]['cashback'], 1)


# if __name__ == '__main__':
#     unittest.main()
