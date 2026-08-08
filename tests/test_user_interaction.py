from unittest.mock import patch, MagicMock
from src.planes_models import Aeroplane
from src.user_interaction import (
    filter_aeroplanes_by_country,
    filter_aeroplanes_by_altitude_range,
    filter_aeroplanes_by_speed_range,
    get_top_aeroplanes_by_altitude,
    sort_aeroplanes_by_speed,
    parse_altitude_range,
    display_aeroplane,
    display_aeroplanes
)


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
            ),
            Aeroplane(
                icao24="4b1815",
                callsign="GROUNDED",
                country="UK",
                time_position=1766166621,
                last_contact=1766166621,
                longitude=-0.0168,
                latitude=51.5,
                baro_altitude=0.0,
                on_ground=True,
                velocity=0.0,
                true_track=0.0,
                vertical_rate=0.0,
                geo_altitude=0.0,
                squawk="2064"
            )
        ]

    def test_display_aeroplane(self, capsys):
        """Тест вывода информации о самолете."""
        aeroplane = self.create_test_aeroplanes()[0]
        display_aeroplane(aeroplane, 0)

        captured = capsys.readouterr()
        assert "SWR438A" in captured.out
        assert "4b1812" in captured.out
        assert "Switzerland" in captured.out
        assert "189.7" in captured.out
        assert "4267.2" in captured.out

    def test_display_aeroplane_with_none_values(self, capsys):
        """Тест вывода самолета с None значениями."""
        aeroplane = Aeroplane(
            icao24="4b1812",
            callsign=None,
            country="Switzerland",
            time_position=1766166618,
            last_contact=1766166618,
            longitude=None,
            latitude=None,
            baro_altitude=None,
            on_ground=True,
            velocity=None,
            true_track=None,
            vertical_rate=None,
            geo_altitude=None,
            squawk=None
        )
        display_aeroplane(aeroplane)

        captured = capsys.readouterr()
        assert "N/A" in captured.out
        assert "Скорость: N/A" in captured.out
        assert "Высота: N/A" in captured.out
        assert "Координаты: N/A" in captured.out

    def test_display_aeroplanes_empty(self, capsys):
        """Тест вывода пустого списка."""
        display_aeroplanes([], "Тест")
        captured = capsys.readouterr()
        assert "самолеты не найдены" in captured.out

    def test_display_aeroplanes_with_data(self, capsys):
        """Тест вывода списка самолетов."""
        aeroplanes = self.create_test_aeroplanes()
        display_aeroplanes(aeroplanes, "Тестовые самолеты")

        captured = capsys.readouterr()
        assert "Тестовые самолеты (4 шт.)" in captured.out
        assert "SWR438A" in captured.out
        assert "LUFTHANSA" in captured.out
        assert "AIRFRANCE" in captured.out

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
        assert len(filtered) == 4

    def test_filter_aeroplanes_by_altitude_range(self):
        """Тест фильтрации по диапазону высот."""
        aeroplanes = self.create_test_aeroplanes()

        filtered = filter_aeroplanes_by_altitude_range(aeroplanes, 4000, 6000)
        assert len(filtered) == 2
        icao_codes = [a.icao24 for a in filtered]
        assert "4b1812" in icao_codes
        assert "4b1814" in icao_codes

        filtered = filter_aeroplanes_by_altitude_range(aeroplanes, 4500, None)
        assert len(filtered) == 1
        assert filtered[0].icao24 == "4b1814"

        filtered = filter_aeroplanes_by_altitude_range(aeroplanes, None, 3500)
        assert len(filtered) == 2  # Germany (3000) и GROUNDED (0)
        icao_codes = [a.icao24 for a in filtered]
        assert "4b1813" in icao_codes
        assert "4b1815" in icao_codes

        filtered = filter_aeroplanes_by_altitude_range(aeroplanes, None, None)
        assert len(filtered) == 4

    def test_filter_aeroplanes_by_speed_range(self):
        """Тест фильтрации по диапазону скорости."""
        aeroplanes = self.create_test_aeroplanes()

        filtered = filter_aeroplanes_by_speed_range(aeroplanes, 170, 210)
        assert len(filtered) == 2
        icao_codes = [a.icao24 for a in filtered]
        assert "4b1812" in icao_codes
        assert "4b1814" in icao_codes

        filtered = filter_aeroplanes_by_speed_range(aeroplanes, 190, None)
        assert len(filtered) == 1
        assert filtered[0].icao24 == "4b1814"

        filtered = filter_aeroplanes_by_speed_range(aeroplanes, None, 160)
        assert len(filtered) == 2  # Germany (150) и GROUNDED (0)
        icao_codes = [a.icao24 for a in filtered]
        assert "4b1813" in icao_codes
        assert "4b1815" in icao_codes

        filtered = filter_aeroplanes_by_speed_range(aeroplanes, None, None)
        assert len(filtered) == 4

    def test_get_top_aeroplanes_by_altitude(self):
        """Тест получения топ N по высоте."""
        aeroplanes = self.create_test_aeroplanes()

        top = get_top_aeroplanes_by_altitude(aeroplanes, 1)
        assert len(top) == 1
        assert top[0].icao24 == "4b1814"  # 5000 м

        top = get_top_aeroplanes_by_altitude(aeroplanes, 2)
        assert len(top) == 2
        assert top[0].icao24 == "4b1814"
        assert top[1].icao24 == "4b1812"  # 4267.2 м

        top = get_top_aeroplanes_by_altitude(aeroplanes, 5)
        assert len(top) == 4

    def test_sort_aeroplanes_by_speed(self):
        """Тест сортировки по скорости."""
        aeroplanes = self.create_test_aeroplanes()

        sorted_planes = sort_aeroplanes_by_speed(aeroplanes, reverse=True)
        assert sorted_planes[0].icao24 == "4b1814"  # 200 м/с
        assert sorted_planes[1].icao24 == "4b1812"  # 189.7 м/с
        assert sorted_planes[2].icao24 == "4b1813"  # 150 м/с
        assert sorted_planes[3].icao24 == "4b1815"  # 0 м/с

        sorted_planes = sort_aeroplanes_by_speed(aeroplanes, reverse=False)
        assert sorted_planes[0].icao24 == "4b1815"  # 0 м/с
        assert sorted_planes[1].icao24 == "4b1813"  # 150 м/с

    def test_parse_altitude_range(self):
        """Тест парсинга диапазона высот."""
        min_val, max_val = parse_altitude_range("1000-5000")
        assert min_val == 1000.0
        assert max_val == 5000.0

        min_val, max_val = parse_altitude_range("5000")
        assert min_val == 0.0
        assert max_val == 5000.0

        min_val, max_val = parse_altitude_range("1000-")
        assert min_val == 1000.0
        assert max_val is None

        min_val, max_val = parse_altitude_range("-5000")
        assert min_val is None
        assert max_val == 5000.0

        min_val, max_val = parse_altitude_range("")
        assert min_val is None
        assert max_val is None

        min_val, max_val = parse_altitude_range("invalid")
        assert min_val is None
        assert max_val is None

        min_val, max_val = parse_altitude_range("1000-invalid")
        assert min_val is None
        assert max_val is None

    @patch('src.user_interaction.JSONStorage')
    @patch('src.user_interaction.AeroplanesAPI')
    def test_user_interaction_quit(self, mock_api, mock_storage):
        """Тест выхода из программы."""
        with patch('builtins.input', return_value='0'):
            from src.user_interaction import user_interaction
            user_interaction()
            # Просто проверяем, что функция завершилась без ошибок

    @patch('src.user_interaction.JSONStorage')
    @patch('src.user_interaction.AeroplanesAPI')
    def test_user_interaction_invalid_choice(self, mock_api, mock_storage):
        """Тест неверного выбора команды."""
        with patch('builtins.input', side_effect=['99', '0']):
            from src.user_interaction import user_interaction
            user_interaction()
            # Проверяем, что функция обработала неверный ввод

    @patch('src.user_interaction.JSONStorage')
    @patch('src.user_interaction.AeroplanesAPI')
    def test_user_interaction_get_country_empty(self, mock_api, mock_storage):
        """Тест ввода пустого названия страны."""
        with patch('builtins.input', side_effect=['1', '', '0']):
            from src.user_interaction import user_interaction
            user_interaction()

    @patch('src.user_interaction.JSONStorage')
    @patch('src.user_interaction.AeroplanesAPI')
    def test_user_interaction_top_n_invalid(self, mock_api, mock_storage):
        """Тест ввода неверного N для топа."""
        with patch('builtins.input', side_effect=['2', 'abc', '0']):
            from src.user_interaction import user_interaction
            user_interaction()

    @patch('src.user_interaction.JSONStorage')
    @patch('src.user_interaction.AeroplanesAPI')
    def test_user_interaction_filter_country_empty(self, mock_api, mock_storage):
        """Тест фильтрации с пустым списком стран."""
        with patch('builtins.input', side_effect=['3', '', '0']):
            from src.user_interaction import user_interaction
            user_interaction()
