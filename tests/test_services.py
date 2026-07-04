"""Тесты для модуля services."""
import unittest
import json
import logging
from src.services import (
    simple_search,
    contains_string,
    is_transfer_to_individual,
    filter_transactions,
    map_transactions,
    format_transaction,
    search_by_phone,
    search_transfers_to_individuals
)

# Отключаем логи для чистоты тестов
logging.disable(logging.CRITICAL)


class TestServices(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных."""
        self.test_transactions = [
            {
                'Дата операции': '2023-12-15 10:30:00',
                'Сумма операции': -1500,
                'Категория': 'Рестораны',
                'Описание': 'Обед в кафе +7 921 123-45-67',
                'Контрагент': 'Кафе Уют'
            },
            {
                'Дата операции': '2023-12-16 15:20:00',
                'Сумма операции': 50000,
                'Категория': 'Пополнение',
                'Описание': 'Пополнение с карты 1234',
                'Контрагент': 'Банк'
            },
            {
                'Дата операции': '2023-12-17 12:00:00',
                'Сумма операции': -2000,
                'Категория': 'Переводы',
                'Описание': 'Перевод Ивану С.',
                'Контрагент': 'Иван С.'
            }
        ]

    def test_contains_string(self):
        """Тест поиска строки."""
        predicate = contains_string('кафе')
        self.assertTrue(predicate(self.test_transactions[0]))
        self.assertFalse(predicate(self.test_transactions[1]))

        # Поиск с заглавной буквы
        predicate = contains_string('Кафе')
        self.assertTrue(predicate(self.test_transactions[0]))

        # Поиск по категории
        predicate = contains_string('рестораны')
        self.assertTrue(predicate(self.test_transactions[0]))

    def test_is_transfer_to_individual(self):
        """Тест поиска переводов физлицам."""
        predicate = is_transfer_to_individual()
        self.assertTrue(predicate(self.test_transactions[2]))
        self.assertFalse(predicate(self.test_transactions[0]))
        self.assertFalse(predicate(self.test_transactions[1]))

    def test_format_transaction(self):
        """Тест форматирования транзакции."""
        formatted = format_transaction(self.test_transactions[0])
        self.assertIn('date', formatted)
        self.assertIn('amount', formatted)
        self.assertIn('category', formatted)
        self.assertIn('description', formatted)
        self.assertIn('merchant', formatted)
        self.assertEqual(formatted['amount'], -1500)
        self.assertEqual(formatted['category'], 'Рестораны')

    def test_filter_transactions(self):
        """Тест фильтрации транзакций."""
        predicate = lambda x: x['Сумма операции'] < 0
        filtered = filter_transactions(self.test_transactions, predicate)
        self.assertEqual(len(filtered), 2)

    def test_map_transactions(self):
        """Тест преобразования транзакций."""
        transformer = lambda x: x['Категория']
        mapped = map_transactions(self.test_transactions, transformer)
        self.assertEqual(mapped, ['Рестораны', 'Пополнение', 'Переводы'])

    def test_simple_search(self):
        """Тест простого поиска."""
        # Поиск по описанию
        result_json = simple_search(self.test_transactions, "кафе")
        result = json.loads(result_json)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['category'], 'Рестораны')

        # Поиск по категории
        result_json = simple_search(self.test_transactions, "рестораны")
        result = json.loads(result_json)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['category'], 'Рестораны')

        # Поиск, который ничего не найдет
        result_json = simple_search(self.test_transactions, "несуществующее")
        result = json.loads(result_json)
        self.assertEqual(len(result), 0)

    def test_search_by_phone(self):
        """Тест поиска по телефону."""
        # Поиск всех телефонов
        result_json = search_by_phone(self.test_transactions)
        result = json.loads(result_json)
        self.assertEqual(len(result), 1)
        self.assertIn('phone_found', result[0])
        self.assertEqual(result[0]['phone_found'], '+7 921 123-45-67')

        # Поиск конкретного телефона
        result_json = search_by_phone(self.test_transactions, "+7 921 123-45-67")
        result = json.loads(result_json)
        self.assertEqual(len(result), 1)

        # Поиск несуществующего телефона
        result_json = search_by_phone(self.test_transactions, "+7 999 999-99-99")
        result = json.loads(result_json)
        self.assertEqual(len(result), 0)

    def test_search_transfers_to_individuals(self):
        """Тест поиска переводов физическим лицам."""
        result_json = search_transfers_to_individuals(self.test_transactions)
        result = json.loads(result_json)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['category'], 'Переводы')
        self.assertEqual(result[0]['amount'], 2000)

    def test_search_by_phone_normalize(self):
        """Тест нормализации телефонных номеров."""
        # Разные форматы одного номера
        phones = [
            "+7 921 123-45-67",
            "8 921 123-45-67",
            "89211234567",
            "+79211234567"
        ]

        for phone in phones:
            result_json = search_by_phone(self.test_transactions, phone)
            result = json.loads(result_json)
            self.assertEqual(len(result), 1, f"Не найден номер: {phone}")


if __name__ == '__main__':
    unittest.main()
