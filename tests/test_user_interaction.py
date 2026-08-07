from src.user_interaction import (
    filter_aeroplanes_by_country,
    filter_aeroplanes_by_altitude_range,
    filter_aeroplanes_by_speed_range,
    get_top_aeroplanes_by_altitude,
    sort_aeroplanes_by_speed,
    parse_altitude_range
)
from src.planes_models import Aeroplane


class TestUserInteraction:
    """Тесты для функций взаимодействия с пользователем."""

    def create_test_aeroplanes(self):
        """Создание набора тестовых самолетов."""
        return [
            Aeroplane(
                icao24="4b1812",
                callsign="SWR438A",
                country="Switzerland",
                time_position=1766166618,
                last_contact=1766166618,
                longitude=-0.0168,
                latitude=51.0888,
                baro_altitude=4267.2,
                on_ground=False,
                velocity=189.7,
                true_track=129.39,
                vertical_rate=14.63,
                geo_altitude=4282.44,
                squawk="2061"
            ),
            Aeroplane(
                icao24="4b1813",
                callsign="LUFTHANSA",
                country="Germany",
                time_position=1766166619,
                last_contact=1766166619,
                longitude=0.0168,
                latitude=52.0888,
                baro_altitude=3000.0,
                on_ground=False,
                velocity=150.0,
                true_track=130.0,
                vertical_rate=10.0,
                geo_altitude=3000.0,
                squawk="2062"
            ),
            Aeroplane(
                icao24="4b1814",
                callsign="AIRFRANCE",
                country="France",
                time_position=1766166620,
                last_contact=1766166620,
                longitude=-0.0168,
                latitude=49.0888,
                baro_altitude=5000.0,
                on_ground=False,
                velocity=200.0,
                true_track=128.0,
                vertical_rate=20.0,
                geo_altitude=5000.0,
                squawk="2063"
            )
        ]

    def test_filter_aeroplanes_by_country(self):
        """Тест фильтрации по стране."""
        aeroplanes = self.create_test_aeroplanes()

        filtered = filter_aeroplanes_by_country(aeroplanes, ["Switzerland"])
        assert len(filtered) == 1
        assert filtered[0].icao24 == "4b1812"

        filtered = filter_aeroplanes_by_country(aeroplanes, ["Germany", "France"])
        assert len(filtered) == 2
        icao_codes = [a.icao24 for a in filtered]
        assert "4b1813" in icao_codes
        assert "4b1814" in icao_codes

        filtered = filter_aeroplanes_by_country(aeroplanes, ["NonExistent"])
        assert len(filtered) == 0

        filtered = filter_aeroplanes_by_country(aeroplanes, [])
        assert len(filtered) == 3

    def test_filter_aeroplanes_by_altitude_range(self):
        """Тест фильтрации по диапазону высот."""
        aeroplanes = self.create_test_aeroplanes()

        # Фильтрация от 4000 до 6000
        filtered = filter_aeroplanes_by_altitude_range(aeroplanes, 4000, 6000)
        assert len(filtered) == 2
        icao_codes = [a.icao24 for a in filtered]
        assert "4b1812" in icao_codes
        assert "4b1814" in icao_codes

        # Фильтрация от 4500 и выше
        filtered = filter_aeroplanes_by_altitude_range(aeroplanes, 4500, None)
        assert len(filtered) == 1
        assert filtered[0].icao24 == "4b1814"

        # Фильтрация до 3500
        filtered = filter_aeroplanes_by_altitude_range(aeroplanes, None, 3500)
        assert len(filtered) == 1
        assert filtered[0].icao24 == "4b1813"

        # Пустой диапазон
        filtered = filter_aeroplanes_by_altitude_range(aeroplanes, None, None)
        assert len(filtered) == 3

    def test_filter_aeroplanes_by_speed_range(self):
        """Тест фильтрации по диапазону скорости."""
        aeroplanes = self.create_test_aeroplanes()

        # Фильтрация от 170 до 210
        filtered = filter_aeroplanes_by_speed_range(aeroplanes, 170, 210)
        assert len(filtered) == 2
        icao_codes = [a.icao24 for a in filtered]
        assert "4b1812" in icao_codes
        assert "4b1814" in icao_codes

        # Фильтрация от 190 и выше
        filtered = filter_aeroplanes_by_speed_range(aeroplanes, 190, None)
        assert len(filtered) == 1
        assert filtered[0].icao24 == "4b1814"

        # Фильтрация до 160
        filtered = filter_aeroplanes_by_speed_range(aeroplanes, None, 160)
        assert len(filtered) == 1
        assert filtered[0].icao24 == "4b1813"

    def test_get_top_aeroplanes_by_altitude(self):
        """Тест получения топ N по высоте."""
        aeroplanes = self.create_test_aeroplanes()

        # Топ 1
        top = get_top_aeroplanes_by_altitude(aeroplanes, 1)
        assert len(top) == 1
        assert top[0].icao24 == "4b1814"  # 5000 м - самая высокая

        # Топ 2
        top = get_top_aeroplanes_by_altitude(aeroplanes, 2)
        assert len(top) == 2
        assert top[0].icao24 == "4b1814"
        assert top[1].icao24 == "4b1812"  # 4267.2 м

        # Топ с N больше количества
        top = get_top_aeroplanes_by_altitude(aeroplanes, 5)
        assert len(top) == 3

    def test_sort_aeroplanes_by_speed(self):
        """Тест сортировки по скорости."""
        aeroplanes = self.create_test_aeroplanes()

        # По убыванию
        sorted_planes = sort_aeroplanes_by_speed(aeroplanes, reverse=True)
        assert sorted_planes[0].icao24 == "4b1814"  # 200 м/с - самая быстрая
        assert sorted_planes[1].icao24 == "4b1812"  # 189.7 м/с
        assert sorted_planes[2].icao24 == "4b1813"  # 150 м/с

        # По возрастанию
        sorted_planes = sort_aeroplanes_by_speed(aeroplanes, reverse=False)
        assert sorted_planes[0].icao24 == "4b1813"  # 150 м/с
        assert sorted_planes[1].icao24 == "4b1812"  # 189.7 м/с
        assert sorted_planes[2].icao24 == "4b1814"  # 200 м/с

    def test_parse_altitude_range(self):
        """Тест парсинга диапазона высот."""
        # Полный диапазон
        min_val, max_val = parse_altitude_range("1000-5000")
        assert min_val == 1000.0
        assert max_val == 5000.0

        # Только максимум
        min_val, max_val = parse_altitude_range("5000")
        assert min_val == 0.0
        assert max_val == 5000.0

        # Только минимум
        min_val, max_val = parse_altitude_range("1000-")
        assert min_val == 1000.0
        assert max_val is None

        # Только максимум с дефисом
        min_val, max_val = parse_altitude_range("-5000")
        assert min_val is None
        assert max_val == 5000.0

        # Пустая строка
        min_val, max_val = parse_altitude_range("")
        assert min_val is None
        assert max_val is None

        # Некорректный ввод
        min_val, max_val = parse_altitude_range("invalid")
        assert min_val is None
        assert max_val is None

        min_val, max_val = parse_altitude_range("1000-invalid")
        assert min_val is None
        assert max_val is None
