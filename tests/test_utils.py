"""Тесты для модуля utils."""
import unittest
import logging
from datetime import datetime
from src.utils import parse_date, get_greeting, format_date


class TestUtils(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Включаем логирование."""
        logging.disable(logging.NOTSET)

    def test_parse_date(self):
        """Тест парсинга дат в разных форматах."""
        # Формат YYYY-MM-DD HH:MM:SS
        result = parse_date('2023-12-20 15:30:00')
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2023)
        self.assertEqual(result.month, 12)
        self.assertEqual(result.day, 20)

        # Формат DD.MM.YYYY HH:MM:SS
        result = parse_date('20.12.2023 15:30:00')
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2023)
        self.assertEqual(result.month, 12)
        self.assertEqual(result.day, 20)

        # Пустая строка
        result = parse_date('')
        self.assertIsNone(result)

        # Некорректная дата
        result = parse_date('invalid date')
        self.assertIsNone(result)

    def test_format_date(self):
        """Тест форматирования даты."""
        result = format_date('2023-12-20 15:30:00')
        self.assertEqual(result, '20.12.2023')

        # Неверный формат - функция должна вернуть исходную строку
        result = format_date('invalid date')
        self.assertEqual(result, 'invalid date')

        # Пустая строка
        result = format_date('')
        self.assertEqual(result, '')

    def test_format_date_with_custom_format(self):
        """Тест форматирования с пользовательским форматом."""
        result = format_date('20.12.2023', '%d.%m.%Y', '%Y-%m-%d')
        self.assertEqual(result, '2023-12-20')

    def test_get_greeting(self):
        """Тест приветствия."""
        greeting = get_greeting()
        self.assertIn(greeting, ['Доброе утро', 'Добрый день', 'Добрый вечер', 'Доброй ночи'])


if __name__ == '__main__':
    unittest.main()
