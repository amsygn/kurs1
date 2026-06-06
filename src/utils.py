import logging
from datetime import datetime, date
from typing import List, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)


def load_transactions_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """Загрузка транзакций из Excel-файла."""
    try:
        logger.info(f"Загрузка данных из файла: {file_path}")
        df = pd.read_excel(file_path)

        transactions = df.to_dict('records')

        # Нормализуем данные
        for trans in transactions:
            if 'Дата операции' in trans:
                if isinstance(trans['Дата операции'], (datetime, date, pd.Timestamp)):
                    trans['Дата операции'] = trans['Дата операции'].strftime('%Y-%m-%d %H:%M:%S')

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
        end_dt = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        start_dt = end_dt.replace(day=1, hour=0, minute=0, second=0)

        filtered = []
        for trans in transactions:
            trans_date_str = trans.get(date_column, '')
            if trans_date_str:
                trans_date = datetime.strptime(trans_date_str, '%Y-%m-%d %H:%M:%S')
                if start_dt <= trans_date <= end_dt:
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
    except:
        return date_str
