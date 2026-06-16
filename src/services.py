"""Модуль для сервисов поиска с элементами функционального программирования."""
import logging
import re
import json
from typing import List, Dict, Any, Callable
from functools import reduce
from src.utils import format_date

logger = logging.getLogger(__name__)


def contains_string(query: str) -> Callable:
    """Создает предикат для поиска строки в описании или категории."""
    query_lower = query.lower()
    return lambda trans: (
            query_lower in trans.get('Описание', '').lower() or
            query_lower in trans.get('Категория', '').lower()
    )


def contains_phone() -> Callable:
    """Создает предикат для поиска транзакций с телефонными номерами."""
    phone_pattern = re.compile(r'[+()]?[\d\-()\s]{10,20}')
    return lambda trans: bool(phone_pattern.search(trans.get('Описание', '')))


def is_transfer_to_individual() -> Callable:
    """Создает предикат для поиска переводов физическим лицам."""
    transfer_keywords = ['перевод', 'физическому лицу', 'частному лицу']
    name_pattern = re.compile(r'[А-Я][а-я]+\s[А-Я]\.')

    def predicate(trans):
        description = trans.get('Описание', '').lower()
        category = trans.get('Категория', '').lower()

        is_transfer = any(keyword in description or keyword in category for keyword in transfer_keywords)
        has_name = bool(name_pattern.search(trans.get('Описание', '')))

        return is_transfer and has_name and trans.get('Сумма операции', 0) < 0

    return predicate


def is_expense() -> Callable:
    """Создает предикат для фильтрации расходов."""
    return lambda trans: trans.get('Сумма операции', 0) < 0


def is_income() -> Callable:
    """Создает предикат для фильтрации доходов."""
    return lambda trans: trans.get('Сумма операции', 0) > 0


# Функции-трансформеры для форматирования результата
def format_transaction(trans: Dict[str, Any]) -> Dict[str, Any]:
    """Форматирует транзакцию для вывода."""
    return {
        'date': format_date(trans.get('Дата операции', ''), '%Y-%m-%d %H:%M:%S', '%d.%m.%Y'),
        'amount': trans.get('Сумма операции', 0),
        'category': trans.get('Категория', ''),
        'description': trans.get('Описание', ''),
        'merchant': trans.get('Контрагент', '')
    }


def extract_phone_from_description(trans: Dict[str, Any]) -> Dict[str, Any]:
    """Извлекает телефон из описания транзакции."""
    phone_pattern = re.compile(r'[+()]?[\d\-()\s]{10,20}')
    phones = phone_pattern.findall(trans.get('Описание', ''))

    result = format_transaction(trans)
    if phones:
        result['phone_found'] = phones[0].strip()

    return result


def filter_transactions(transactions: List[Dict[str, Any]], predicate: Callable) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции с использованием предиката.

    Args:
        transactions: список транзакций
        predicate: функция-предикат для фильтрации

    Returns:
        отфильтрованный список
    """
    return list(filter(predicate, transactions))


def map_transactions(transactions: List[Dict[str, Any]], transformer: Callable) -> List[Dict[str, Any]]:
    """
    Преобразует транзакции с использованием функции-трансформера.

    Args:
        transactions: список транзакций
        transformer: функция для преобразования

    Returns:
        преобразованный список
    """
    return list(map(transformer, transactions))


def compose(*functions: Callable) -> Callable:
    """
    Композиция функций.

    Args:
        functions: список функций для последовательного применения

    Returns:
        композированная функция
    """

    def compose_two(f: Callable, g: Callable) -> Callable:
        return lambda x: f(g(x))

    return reduce(compose_two, functions, lambda x: x)


def simple_search(transactions: List[Dict[str, Any]], query: str) -> str:
    """
    Простой поиск по описанию транзакций с использованием функционального подхода.

    Args:
        transactions: список транзакций
        query: поисковый запрос

    Returns:
        JSON-строка с найденными транзакциями
    """
    logger.info(f"Поиск по запросу: '{query}'")

    # Создаем пайплайн обработки
    search_pipeline = compose(
        lambda x: filter_transactions(x, contains_string(query)),
        lambda x: map_transactions(x, format_transaction)
    )

    results = search_pipeline(transactions)

    logger.info(f"Найдено {len(results)} транзакций")
    return json.dumps(results, ensure_ascii=False, indent=2, default=str)


def search_by_phone(transactions: List[Dict[str, Any]], phone_number: str = None) -> str:
    """
    Поиск транзакций по телефонным номерам.

    Args:
        transactions: список транзакций
        phone_number: опциональный номер телефона для конкретного поиска

    Returns:
        JSON-строка с найденными транзакциями
    """
    logger.info(f"Поиск по телефонам" + (f": '{phone_number}'" if phone_number else ""))

    def normalize_phone(phone: str) -> str:
        """Нормализация телефонного номера."""
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 11 and digits[0] == '8':
            digits = '7' + digits[1:]
        elif len(digits) == 10:
            digits = '7' + digits
        return digits

    def contains_specific_phone(target_phone: str) -> Callable:
        """Создает предикат для поиска конкретного номера."""
        normalized_target = normalize_phone(target_phone) if target_phone else None

        def check_phone(trans):
            description = trans.get('Описание', '')
            phones = re.findall(r'[+()]?[\d\-()\s]{10,20}', description)

            if normalized_target:
                # Поиск конкретного номера
                return any(normalized_target == normalize_phone(p) for p in phones)
            else:
                # Поиск любых номеров
                return len(phones) > 0

        return check_phone

    # Выбираем предикат
    if phone_number:
        check_phone = contains_specific_phone(phone_number)
    else:
        check_phone = contains_phone()

    # Пайплайн обработки
    search_pipeline = compose(
        lambda x: filter_transactions(x, predicate),
        lambda x: map_transactions(x, extract_phone_from_description)
    )

    results = search_pipeline(transactions)

    logger.info(f"Найдено {len(results)} транзакций")
    return json.dumps(results, ensure_ascii=False, indent=2, default=str)


def search_transfers_to_individuals(transactions: List[Dict[str, Any]]) -> str:
    """
    Поиск переводов физическим лицам.

    Args:
        transactions: список транзакций

    Returns:
        JSON-строка с переводами физическим лицам
    """
    logger.info("Поиск переводов физическим лицам")

    def extract_recipient(trans: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает получателя из описания."""
        result = format_transaction(trans)
        result['amount'] = abs(result['amount'])
        result['recipient'] = trans.get('Контрагент', '')

        # Пытаемся извлечь имя из описания
        name_pattern = re.compile(r'([А-Я][а-я]+\s[А-Я]\.)')
        names = name_pattern.findall(trans.get('Описание', ''))
        if names:
            result['recipient_name'] = names[0]

        return result

    # Пайплайн обработки
    search_pipeline = compose(
        lambda x: filter_transactions(x, is_transfer_to_individual()),
        lambda x: map_transactions(x, extract_recipient)
    )

    results = search_pipeline(transactions)

    logger.info(f"Найдено {len(results)} переводов физическим лицам")
    return json.dumps(results, ensure_ascii=False, indent=2, default=str)


def search_by_category(transactions: List[Dict[str, Any]], category: str) -> str:
    """
    Поиск транзакций по категории.

    Args:
        transactions: список транзакций
        category: категория для поиска

    Returns:
        JSON-строка с найденными транзакциями
    """
    logger.info(f"Поиск по категории: '{category}'")

    def contains_category(cat: str) -> Callable:
        """Создает предикат для поиска по категории."""
        cat_lower = cat.lower()
        return lambda trans: trans.get('Категория', '').lower() == cat_lower

    search_pipeline = compose(
        lambda x: filter_transactions(x, contains_category(category)),
        lambda x: map_transactions(x, format_transaction)
    )

    results = search_pipeline(transactions)

    logger.info(f"Найдено {len(results)} транзакций")
    return json.dumps(results, ensure_ascii=False, indent=2, default=str)
