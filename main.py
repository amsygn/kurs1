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

# Отключаем логи от сторонних библиотек
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("charset_normalizer").setLevel(logging.WARNING)

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
        print(f"Загружено {len(transactions)} транзакций\n")

    except Exception as e:
        logger.error(f"Ошибка загрузки транзакций: {e}")
        print(f"\n❌ Ошибка загрузки данных: {e}")
        return

    # Генерация данных для веб-страницы
    print("\n••• ГЕНЕРАЦИЯ ДАННЫХ ДЛЯ ВЕБ-СТРАНИЦЫ •••")

    date_time = "2020-12-20 15:30:00"
    web_data_json = views_main(transactions, date_time)

    try:
        web_data = json.loads(web_data_json)

        # Информация по картам с топ-5 транзакциями
        if 'cards' in web_data and web_data['cards']:
            print("\nИНФОРМАЦИЯ ПО КАРТАМ:")
            for card in web_data['cards']:
                print(f"\n  Карта ****{card['last_digits']}:")
                print(f"    Расходы: {card['total_expenses']:,} руб.")
                print(f"    Кешбэк: {card['cashback']} руб.")
                if card.get('top_transactions'):
                    print("    Топ-5 транзакций:")
                    for i, trans in enumerate(card['top_transactions'][:5], 1):
                        print(
                            f"      {i}. {trans['date']} - {trans['description']}: {trans['amount']:,} руб. ({trans['category']})")
                else:
                    print("    Топ-5 транзакций: нет данных")
        else:
            print("\n ИНФОРМАЦИЯ ПО КАРТАМ: данные не получены")

        # Курсы валют
        if 'currency_rates' in web_data and web_data['currency_rates']:
            print("\nКУРСЫ ВАЛЮТ:")
            for rate in web_data['currency_rates']:
                print(f"  {rate['currency']}: {rate['rate']:.4f} руб.")
        else:
            print("\nКУРСЫ ВАЛЮТ: данные не получены")

        # Цены акций
        if 'stock_prices' in web_data and web_data['stock_prices']:
            print("\nЦЕНЫ АКЦИЙ:")
            for stock in web_data['stock_prices']:
                print(f"  {stock['stock']}: ${stock['price']:.2f}")
        else:
            print("\nЦЕНЫ АКЦИЙ: данные не получены")

    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON: {e}")
        print(f"JSON для веб-страницы:\n{web_data_json[:500]}...")

    # Страница событий
    print("\n••• СТРАНИЦА СОБЫТИЙ •••")
    events_json = events_page(transactions, date_time, 'M')

    try:
        events_data = json.loads(events_json)

        if 'expenses' in events_data:
            print("\nРАСХОДЫ:")
            print(f"  Всего: {events_data['expenses'].get('total_amount', 0):,} руб.")
            print("  Основные категории:")
            for cat in events_data['expenses'].get('main', [])[:7]:
                print(f"    {cat['category']}: {cat['amount']:,} руб.")
            if events_data['expenses'].get('transfers_and_cash'):
                print("  Переводы и наличные:")
                for cat in events_data['expenses']['transfers_and_cash']:
                    print(f"    {cat['category']}: {cat['amount']:,} руб.")

        if 'income' in events_data:
            print("\nПОСТУПЛЕНИЯ:")
            print(f"  Всего: {events_data['income'].get('total_amount', 0):,} руб.")
            print("  Основные категории:")
            for cat in events_data['income'].get('main', [])[:7]:
                print(f"    {cat['category']}: {cat['amount']:,} руб.")

    except json.JSONDecodeError:
        print(f"JSON для страницы событий:\n{events_json[:500]}...")

    # Отчет по дням недели
    print("\n••• ОТЧЕТ ПО ДНЯМ НЕДЕЛИ •••")
    weekday_report = spending_by_weekday(transactions)
    print("Отчет по дням недели сохранен в файл src/spending_by_weekday_report.json")
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
    try:
        result_dict = json.loads(search_results) if isinstance(search_results, str) else search_results
        print(f"Результаты поиска по '{search_query}': {len(result_dict)} транзакций")
    except (json.JSONDecodeError, TypeError, ValueError):
        print(f"Результаты поиска по '{search_query}': {search_results[:200]}...")

    # Поиск по телефону
    phone = "+7 900 123-45-67"
    phone_results = search_by_phone(transactions, phone)
    try:
        phone_dict = json.loads(phone_results) if isinstance(phone_results, str) else phone_results
        print(f"Результаты поиска по телефону {phone}: {len(phone_dict)} транзакций")
    except (json.JSONDecodeError, TypeError, ValueError):
        print(f"Результаты поиска по телефону {phone}: {phone_results[:200]}...")

    # Поиск переводов физлицам
    transfers = search_transfers_to_individuals(transactions)
    try:
        transfers_dict = json.loads(transfers) if isinstance(transfers, str) else transfers
        print(f"Переводы физическим лицам: {len(transfers_dict)} транзакций")
    except (json.JSONDecodeError, TypeError, ValueError):
        print(f"Переводы физическим лицам: {transfers[:200]}...")

    logger.info("Приложение завершило работу")


if __name__ == "__main__":
    main()
