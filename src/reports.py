"""Модуль для формирования отчетов с декоратором."""
import logging
import json
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


def report_decorator(filename: str = None):
    """
    Декоратор для сохранения результата функции в JSON-файл.

    Args:
        filename: имя файла для сохранения (если None, генерируется автоматически)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_name = f"{func.__name__}_{timestamp}.json"
            else:
                file_name = filename

            file_path = Path(file_name)
            file_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2, default=str),
                encoding='utf-8'
            )

            logger.info(f"Отчет сохранен в файл: {file_name}")
            return result
        return wrapper
    return decorator


@report_decorator("spending_by_weekday_report.json")
def spending_by_weekday(transactions: List[Dict[str, Any]], date: Optional[str] = None) -> Dict[str, Any]:
    """
    Отчет по средним тратам по дням недели за последние 3 месяца.

    Returns:
        словарь с отчетом по дням недели
    """
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    start_date = end_date - timedelta(days=90)

    logger.info(f"Формирование отчета по дням недели за период {start_date} - {end_date}")

    # Преобразуем в DataFrame для удобства
    df = pd.DataFrame(transactions)

    # Проверяем наличие данных
    if df.empty:
        logger.warning("Нет транзакций для анализа")
        return {
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            },
            'average_spending_by_weekday': []
        }

    # Фильтруем по дате и расходам
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    mask = (df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date) & (df['Сумма операции'] < 0)
    filtered_df = df[mask].copy()

    # ✅ Возвращаем словарь вместо DataFrame
    if filtered_df.empty:
        logger.warning("Нет данных за указанный период")
        return {
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            },
            'average_spending_by_weekday': []
        }

    # Добавляем день недели
    filtered_df['weekday'] = filtered_df['Дата операции'].dt.day_name(locale='ru_RU')
    filtered_df['amount'] = filtered_df['Сумма операции'].abs()

    # Группируем по дням недели и считаем среднее
    weekday_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    spending_by_day = filtered_df.groupby('weekday')['amount'].mean().round(2)

    # Приводим к нужному порядку
    result_df = pd.DataFrame({
        'weekday': weekday_order,
        'average_spending': [spending_by_day.get(day, 0) for day in weekday_order]
    })

    # ✅ Возвращаем JSON-сериализуемый словарь
    return {
        'period': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        },
        'average_spending_by_weekday': result_df.to_dict('records')
    }


def get_top_cashback_categories(transactions: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
    """
    Получение топ категорий по кешбэку.

    Args:
        transactions: список транзакций
        top_n: количество категорий

    Returns:
        список категорий с кешбэком
    """
    categories_cashback = {}

    for trans in transactions:
        amount = trans.get('Сумма операции', 0)
        if amount < 0:  # Только расходы
            category = trans.get('Категория', 'Другое')
            abs_amount = abs(amount)
            cashback = abs_amount // 100  # 1 рубль на каждые 100

            if cashback > 0:
                categories_cashback[category] = categories_cashback.get(category, 0) + cashback

    # Сортируем по кешбэку
    sorted_cats = sorted(categories_cashback.items(), key=lambda x: x[1], reverse=True)
    top = sorted_cats[:top_n]

    return [{'category': cat, 'cashback': int(amount)} for cat, amount in top]
