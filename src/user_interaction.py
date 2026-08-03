# src/utils/user_interaction.py
from typing import List, Optional, Tuple
from src.planes_models import Aeroplane
from src.api.aeroplanes_api import AeroplanesAPI
from src.storage.json_storage import JSONStorage
from src.storage.csv_storage import CSVStorage
from src.storage.txt_storage import TXTStorage


def display_aeroplane(aeroplane: Aeroplane, index: int = None) -> None:
    """Вывод информации о самолете в консоль."""
    prefix = f"{index + 1}. " if index is not None else ""
    print(f"{prefix}✈️  {aeroplane.callsign or 'N/A'}")
    print(f"   ICAO24: {aeroplane.icao24}")
    print(f"   Страна: {aeroplane.country}")
    print(
        f"   Скорость: {aeroplane.velocity:.1f} м/с ({aeroplane.speed_kmh:.1f} км/ч)" if aeroplane.velocity is not None else "   Скорость: N/A")
    print(
        f"   Высота: {aeroplane.baro_altitude:.1f} м ({aeroplane.altitude_ft:.0f} фт)" if aeroplane.baro_altitude is not None else "   Высота: N/A")
    print(
        f"   Координаты: {aeroplane.latitude:.4f}°, {aeroplane.longitude:.4f}°" if aeroplane.latitude is not None and aeroplane.longitude is not None else "   Координаты: N/A")
    print(f"   Статус: {'В воздухе' if aeroplane.is_active else 'На земле'}")
    print(f"   Время: {aeroplane.position_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def display_aeroplanes(aeroplanes: List[Aeroplane], title: str = "Самолеты") -> None:
    """Вывод списка самолетов в консоль."""
    if not aeroplanes:
        print(f"ℹ️  {title}: самолеты не найдены")
        return

    print(f"\n{'=' * 60}")
    print(f"  {title} ({len(aeroplanes)} шт.)")
    print(f"{'=' * 60}\n")

    for i, aeroplane in enumerate(aeroplanes):
        display_aeroplane(aeroplane, i)


def filter_aeroplanes_by_country(aeroplanes: List[Aeroplane], countries: List[str]) -> List[Aeroplane]:
    """Фильтрация самолетов по странам регистрации."""
    if not countries:
        return aeroplanes

    countries_lower = [c.lower() for c in countries]
    return [a for a in aeroplanes if a.country.lower() in countries_lower]


def filter_aeroplanes_by_altitude_range(aeroplanes: List[Aeroplane], min_alt: Optional[float],
                                        max_alt: Optional[float]) -> List[Aeroplane]:
    """Фильтрация самолетов по диапазону высот."""
    result = []
    for a in aeroplanes:
        if a.baro_altitude is None:
            continue
        if min_alt is not None and a.baro_altitude < min_alt:
            continue
        if max_alt is not None and a.baro_altitude > max_alt:
            continue
        result.append(a)
    return result


def filter_aeroplanes_by_speed_range(aeroplanes: List[Aeroplane], min_speed: Optional[float],
                                     max_speed: Optional[float]) -> List[Aeroplane]:
    """Фильтрация самолетов по диапазону скорости (дополнительная функция)."""
    result = []
    for a in aeroplanes:
        if a.velocity is None:
            continue
        if min_speed is not None and a.velocity < min_speed:
            continue
        if max_speed is not None and a.velocity > max_speed:
            continue
        result.append(a)
    return result


def get_top_aeroplanes_by_altitude(aeroplanes: List[Aeroplane], top_n: int) -> List[Aeroplane]:
    """Получение топ N самолетов по высоте (сортировка DESC)."""
    valid = [a for a in aeroplanes if a.baro_altitude is not None]
    sorted_aeroplanes = sorted(valid, key=lambda a: a.baro_altitude, reverse=True)
    return sorted_aeroplanes[:top_n]


def sort_aeroplanes_by_speed(aeroplanes: List[Aeroplane], reverse: bool = True) -> List[Aeroplane]:
    """Сортировка самолетов по скорости (дополнительная функция)."""
    valid = [a for a in aeroplanes if a.velocity is not None]
    return sorted(valid, key=lambda a: a.velocity, reverse=reverse)


def parse_altitude_range(input_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Парсинг строки диапазона высот."""
    if not input_str or input_str.strip() == '':
        return None, None

    parts = input_str.replace(' ', '').split('-')
    if len(parts) == 1:
        try:
            value = float(parts[0])
            return 0, value
        except ValueError:
            return None, None

    try:
        min_val = float(parts[0]) if parts[0] else None
        max_val = float(parts[1]) if parts[1] else None
        return min_val, max_val
    except ValueError:
        return None, None


def user_interaction() -> None:
    """Главная функция взаимодействия с пользователем."""
    print("\n" + "=" * 70)
    print(" СИСТЕМА ОТСЛЕЖИВАНИЯ САМОЛЕТОВ ")
    print("=" * 70 + "\n")

    api = AeroplanesAPI()
    json_storage = JSONStorage()

    while True:
        print("\nДоступные команды:")
        print("  1 - Получить данные о самолетах по стране")
        print("  2 - Показать топ N самолетов по высоте")
        print("  3 - Фильтрация по стране регистрации")
        print("  4 - Фильтрация по диапазону высот")
        print("  5 - Фильтрация по диапазону скорости")
        print("  6 - Показать все сохраненные самолеты")
        print("  7 - Очистить хранилище")
        print("  0 - Выход")
        print("-" * 70)

        choice = input("Выберите команду (0-7): ").strip()

        if choice == '0':
            print("\nДо свидания!")
            break

        elif choice == '1':
            country = input("Введите название страны: ").strip()
            if not country:
                print("Ошибка: название страны не может быть пустым")
                continue

            print(f"Получение данных о самолетах для страны '{country}'...")
            data = api.get_aeroplanes_by_country(country)

            if not data or 'states' not in data:
                print(f"Не удалось получить данные для страны '{country}'")
                continue

            aeroplanes = Aeroplane.cast_to_object_list(data)

            if not aeroplanes:
                print(f"В воздушном пространстве '{country}' самолеты не обнаружены")
            else:
                display_aeroplanes(aeroplanes, f"Самолеты в воздушном пространстве '{country}'")

                # Сохраняем данные
                save_choice = input("Сохранить данные в файл? (y/n): ").strip().lower()
                if save_choice == 'y':
                    json_storage.add_aeroplanes(aeroplanes)
                    print("Данные сохранены в JSON-файл")

        elif choice == '2':
            try:
                top_n = int(input("Введите количество самолетов для топа (N): ").strip())
                if top_n <= 0:
                    print("N должно быть положительным числом")
                    continue
            except ValueError:
                print("Ошибка: введите целое число")
                continue

            all_aeroplanes = json_storage.get_all_aeroplanes()
            if not all_aeroplanes:
                print("Нет сохраненных данных. Сначала получите данные по стране (команда 1)")
                continue

            top_aeroplanes = get_top_aeroplanes_by_altitude(all_aeroplanes, top_n)
            display_aeroplanes(top_aeroplanes, f"Топ {top_n} самолетов по высоте")

        elif choice == '3':
            countries_input = input("Введите страны регистрации для фильтрации (через пробел): ").strip()
            if not countries_input:
                print("Ошибка: список стран не может быть пустым")
                continue

            countries = [c.strip() for c in countries_input.split() if c.strip()]

            all_aeroplanes = json_storage.get_all_aeroplanes()
            if not all_aeroplanes:
                print("Нет сохраненных данных. Сначала получите данные по стране (команда 1)")
                continue

            filtered = filter_aeroplanes_by_country(all_aeroplanes, countries)
            display_aeroplanes(filtered, f"Самолеты по странам: {', '.join(countries)}")

        elif choice == '4':
            alt_range = input("Введите диапазон высот (например: 1000-10000 или 5000-): ").strip()
            min_alt, max_alt = parse_altitude_range(alt_range)

            if min_alt is None and max_alt is None:
                print("Ошибка: некорректный диапазон высот")
                continue

            all_aeroplanes = json_storage.get_all_aeroplanes()
            if not all_aeroplanes:
                print("Нет сохраненных данных. Сначала получите данные по стране (команда 1)")
                continue

            filtered = filter_aeroplanes_by_altitude_range(all_aeroplanes, min_alt, max_alt)
            display_aeroplanes(filtered, f"Самолеты по высоте {alt_range}")

        elif choice == '5':
            speed_range = input("Введите диапазон скорости в м/с (например: 50-200 или 100-): ").strip()
            min_speed, max_speed = parse_altitude_range(speed_range)

            if min_speed is None and max_speed is None:
                print("Ошибка: некорректный диапазон скорости")
                continue

            all_aeroplanes = json_storage.get_all_aeroplanes()
            if not all_aeroplanes:
                print("Нет сохраненных данных. Сначала получите данные по стране (команда 1)")
                continue

            filtered = filter_aeroplanes_by_speed_range(all_aeroplanes, min_speed, max_speed)
            display_aeroplanes(filtered, f"Самолеты по скорости {speed_range} м/с")

        elif choice == '6':
            all_aeroplanes = json_storage.get_all_aeroplanes()
            if not all_aeroplanes:
                print("Нет сохраненных данных")
            else:
                display_aeroplanes(all_aeroplanes, "Все сохраненные самолеты")

        elif choice == '7':
            confirm = input("Вы уверены, что хотите очистить хранилище? (y/n): ").strip().lower()
            if confirm == 'y':
                json_storage.clear_all()
                print("Хранилище очищено")

        else:
            print("Неизвестная команда. Пожалуйста, выберите 0-7.")


if __name__ == "__main__":
    user_interaction()
