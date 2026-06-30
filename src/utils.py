"""Утилиты для работы с данными."""
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import pandas as pd
# from pathlib import Path

logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Парсинг даты из разных форматов.

    Args:
        date_str: строка с датой

    Returns:
        объект datetime или None
    """
    if not date_str:
        return None

    # Если это уже объект datetime
    if isinstance(date_str, datetime):
        return date_str

    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%d.%m.%Y %H:%M:%S',
        '%Y-%m-%d',
        '%d.%m.%Y',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y',
        '%Y%m%d',
        '%d.%m.%y'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(str(date_str), fmt)
        except ValueError:
            continue

    logger.warning(f"Не удалось распарсить дату: {date_str}")
    return None


def load_transactions_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """Загрузка транзакций из Excel-файла."""
    try:
        logger.info(f"Загрузка данных из файла: {file_path}")
        df = pd.read_excel(file_path)

        # Заменяем NaN на пустые строки в колонке "Категория"
        if 'Категория' in df.columns:
            df['Категория'] = df['Категория'].fillna('Без категории')

        transactions = df.to_dict('records')

        for trans in transactions:
            # Нормализация даты
            if 'Дата операции' in trans:
                trans_date = trans['Дата операции']
                if isinstance(trans_date, (datetime, date, pd.Timestamp)):
                    trans['Дата операции'] = trans_date.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(trans_date, str):
                    parsed = parse_date(trans_date)
                    if parsed:
                        trans['Дата операции'] = parsed.strftime('%Y-%m-%d %H:%M:%S')

            # Дополнительная проверка для NaN
            if 'Категория' in trans:
                if pd.isna(trans['Категория']):
                    trans['Категория'] = 'Без категории'

            # Нормализация сумм
            if 'Сумма операции' in trans:
                trans['Сумма операции'] = float(trans['Сумма операции'])
            if 'Сумма платежа' in trans:
                trans['Сумма платежа'] = float(trans['Сумма платежа'])

        logger.info(f"Загружено {len(transactions)} транзакций")
        return transactions

    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        raise


def filter_transactions_by_date_range(
        transactions: List[Dict[str, Any]],
        end_date: str,
        date_column: str = 'Дата операции'
) -> List[Dict[str, Any]]:
    """Фильтрация транзакций с начала месяца по указанную дату."""
    try:
        end_dt = parse_date(end_date)
        if not end_dt:
            logger.error(f"Неверный формат конечной даты: {end_date}")
            return []

        start_dt = end_dt.replace(day=1, hour=0, minute=0, second=0)

        filtered = []
        for trans in transactions:
            trans_date_str = trans.get(date_column, '')
            if trans_date_str:
                trans_date = parse_date(trans_date_str)
                if trans_date and start_dt <= trans_date <= end_dt:
                    filtered.append(trans)

        logger.info(f"Отфильтровано {len(filtered)} транзакций за период с {start_dt} по {end_dt}")
        return filtered

    except Exception as e:
        logger.error(f"Ошибка фильтрации по дате: {e}")
        return []


def get_greeting() -> str:
    """Определение приветствия по текущему времени."""
    current_hour = datetime.now().hour

    if 6 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        return "Добрый день"
    elif 18 <= current_hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def format_date(date_str: str, from_format: str = '%Y-%m-%d %H:%M:%S', to_format: str = '%d.%m.%Y') -> str:
    """Форматирование даты."""
    try:
        dt = datetime.strptime(date_str, from_format)
        return dt.strftime(to_format)
    except (ValueError, TypeError) as e:
        logger.warning(f"Ошибка форматирования даты '{date_str}': {e}")
        return date_str
