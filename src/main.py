"""Главный модуль приложения."""
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

from src.views import main as views_main
from src.reports import spending_by_category, get_top_categories, get_top_cashback_categories
from src.services import simple_search, search_by_phone, search_transfers_to_individuals
from src.utils import load_transactions_from_excel

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Главная функция запуска приложения."""
    logger.info("Запуск приложения анализа транзакций")

    # Путь к файлу с данными
    data_path = os.getenv('DATA_PATH', 'data/operations.xlsx')

    if not Path(data_path).exists():
        logger.error(f"Файл данных не найден: {data_path}")
        print(f"Ошибка: Файл данных не найден: {data_path}")
        return

    # Загружаем транзакции
    try:
        transactions = load_transactions_from_excel(data_path)
        logger.info(f"Загружено {len(transactions)} транзакций")
    except Exception as e:
        logger.error(f"Ошибка загрузки транзакций: {e}")
        print(f"Ошибка загрузки данных: {e}")
        return

    # Пример использования веб-страницы
    print("\n" + "=" * 50)
    print("ГЕНЕРАЦИЯ ДАННЫХ ДЛЯ ВЕБ-СТРАНИЦЫ")
    print("=" * 50)
    date_time = "2023-12-20 15:30:00"
    web_data_json = views_main(date_time)
    print(f"JSON для веб-страницы:\n{web_data_json[:500]}...")

    # Пример использования отчета по категориям
    print("\n" + "=" * 50)
    print("ОТЧЕТ ПО КАТЕГОРИИ")
    print("=" * 50)
    category_report = spending_by_category(transactions, "Супермаркеты")
    print(f"Отчет по категории 'Супермаркеты':\n{category_report}")

    # Топ категорий
    print("\n" + "=" * 50)
    print("ТОП-7 КАТЕГОРИЙ")
    print("=" * 50)
    top_cats = get_top_categories(transactions, 7)
    for cat in top_cats:
        print(f"{cat['category']}: {cat['amount']} руб.")

    # Топ по кешбэку
    print("\n" + "=" * 50)
    print("ТОП-3 КАТЕГОРИИ ПО КЕШБЭКУ")
    print("=" * 50)
    top_cashback = get_top_cashback_categories(transactions, 3)
    for cat in top_cashback:
        print(f"{cat['category']}: {cat['cashback']} руб.")

    # Пример поиска
    print("\n" + "=" * 50)
    print("ПОИСК ТРАНЗАКЦИЙ")
    print("=" * 50)

    # Простой поиск
    search_query = "магазин"
    search_results = simple_search(transactions, search_query)
    print(f"Результаты поиска по '{search_query}': {len(search_results)} транзакций")

    # Поиск по телефону
    phone = "+7 900 123-45-67"
    phone_results = search_by_phone(transactions, phone)
    print(f"Результаты поиска по телефону {phone}: {len(phone_results)} транзакций")

    # Поиск переводов физлицам
    transfers = search_transfers_to_individuals(transactions)
    print(f"Переводы физическим лицам: {len(transfers)} транзакций")

    logger.info("Приложение завершило работу")


if __name__ == "__main__":
    main()
