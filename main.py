"""Главный модуль приложения."""
import json
import logging
import os

from pathlib import Path
from dotenv import load_dotenv

from src.views import main as views_main, events_page
from src.reports import spending_by_weekday, get_top_cashback_categories
from src.services import simple_search, search_by_phone, search_transfers_to_individuals
from src.utils import get_greeting, load_transactions_from_excel


class ColoredFormatter(logging.Formatter):
    COLORS = {'DEBUG': '\033[94m', 'INFO': '\033[92m', 'WARNING': '\033[93m',
              'ERROR': '\033[91m', 'CRITICAL': '\033[95m'}

    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelname, '')}%(message)s\033[0m"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:', handlers=[logging.StreamHandler()])
logging.getLogger().handlers[0].setFormatter(ColoredFormatter())

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
    greeting = get_greeting()
    print(f"  {greeting}!")

    logger.info("Запуск приложения анализа транзакций")

    data_path = os.getenv('DATA_PATH', 'data/operations.xlsx')

    if not Path(data_path).exists():
        logger.error(f"Файл данных не найден: {data_path}")
        print(f"Ошибка: Файл данных не найден: {data_path}")
        return

    try:
        transactions = load_transactions_from_excel(data_path)
        print(f"✅ Загружено {len(transactions)} транзакций\n")
    except Exception as e:
        logger.error(f"Ошибка загрузки транзакций: {e}")
        print(f"\n❌ Ошибка загрузки данных: {e}")
        return

    # Генерация данных для веб-страницы
    print("\n••• ГЕНЕРАЦИЯ ДАННЫХ ДЛЯ ВЕБ-СТРАНИЦЫ •••")

    date_time = "2023-12-20 15:30:00"
    web_data_json = views_main(transactions, date_time)

    try:
        web_data = json.loads(web_data_json)

        # Курсы валют
        if 'currency_rates' in web_data and web_data['currency_rates']:
            print("\n КУРСЫ ВАЛЮТ:")
            for rate in web_data['currency_rates']:
                print(f"  {rate['currency']}: {rate['rate']:.4f} руб.")
        else:
            print("\n КУРСЫ ВАЛЮТ: данные не получены")

        # Цены акций
        if 'stock_prices' in web_data and web_data['stock_prices']:
            print("\n ЦЕНЫ АКЦИЙ:")
            for stock in web_data['stock_prices']:
                print(f"  {stock['stock']}: ${stock['price']:.2f}")
        else:
            print("\n ЦЕНЫ АКЦИЙ: данные не получены")

    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON: {e}")
        print(f"JSON для веб-страницы:\n{web_data_json[:500]}...")

    # Страница событий
    print("\n••• СТРАНИЦА СОБЫТИЙ •••")
    events_json = events_page(transactions, date_time, 'M')
    print(f"\nJSON для страницы событий:\n{events_json[:500]}...")

    # Отчет по дням недели
    print("\n••• ОТЧЕТ ПО ДНЯМ НЕДЕЛИ •••")
    weekday_report = spending_by_weekday(transactions)
    print(f"Отчет по дням недели сохранен в файл src/spending_by_weekday_report.json")
    print("Содержимое отчета:")
    print(json.dumps(weekday_report, ensure_ascii=False, indent=2))

    # Топ по кешбэку
    print("\n••• ТОП-3 КАТЕГОРИИ ПО КЕШБЭКУ •••")

    top_cashback = get_top_cashback_categories(transactions, 3)
    for cat in top_cashback:
        print(f"{cat['category']}: {cat['cashback']} руб.")

    # Пример поиска
    print("\n••• ПОИСК ТРАНЗАКЦИЙ •••")

    # Простой поиск
    search_query = "магазин"
    search_results = simple_search(transactions, search_query)
    result_dict = eval(search_results)
    print(f"Результаты поиска по '{search_query}': {len(result_dict)} транзакций")

    # Поиск по телефону
    phone = "+7 900 123-45-67"
    phone_results = search_by_phone(transactions, phone)
    phone_dict = eval(phone_results)
    print(f"Результаты поиска по телефону {phone}: {len(phone_dict)} транзакций")

    # Поиск переводов физлицам
    transfers = search_transfers_to_individuals(transactions)
    transfers_dict = eval(transfers)
    print(f"Переводы физическим лицам: {len(transfers_dict)} транзакций")

    logger.info("Приложение завершило работу")


if __name__ == "__main__":
    main()
