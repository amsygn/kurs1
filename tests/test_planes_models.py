import pytest
from datetime import datetime
from src.planes_models import Aeroplane


class TestAeroplane:
    """Тесты для класса Aeroplane."""

    def test_aeroplane_creation(self):
        """Тест создания объекта Aeroplane."""
        aeroplane = Aeroplane(
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
        )

        assert aeroplane.icao24 == "4b1812"
        assert aeroplane.callsign == "SWR438A"
        assert aeroplane.country == "Switzerland"
        assert aeroplane.velocity == 189.7
        assert aeroplane.baro_altitude == 4267.2
        assert not aeroplane.on_ground
        assert aeroplane.squawk == "2061"

    def test_aeroplane_creation_with_none_values(self):
        """Тест создания объекта с None значениями."""
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

        assert aeroplane.callsign is None
        assert aeroplane.longitude is None
        assert aeroplane.latitude is None
        assert aeroplane.baro_altitude is None
        assert aeroplane.velocity is None
        assert aeroplane.on_ground is True

    def test_aeroplane_validation_icao24(self):
        """Тест валидации ICAO24."""
        with pytest.raises(ValueError, match="ICAO24 должен быть 6-символьной строкой"):
            Aeroplane(
                icao24="invalid",
                callsign="TEST",
                country="Test",
                time_position=123,
                last_contact=123,
                longitude=0,
                latitude=0,
                baro_altitude=1000,
                on_ground=False,
                velocity=100,
                true_track=0,
                vertical_rate=0,
                geo_altitude=1000,
                squawk="0000"
            )

    def test_aeroplane_validation_country(self):
        """Тест валидации страны."""
        with pytest.raises(ValueError, match="Страна должна быть непустой строкой"):
            Aeroplane(
                icao24="123abc",
                callsign="TEST",
                country="",
                time_position=123,
                last_contact=123,
                longitude=0,
                latitude=0,
                baro_altitude=1000,
                on_ground=False,
                velocity=100,
                true_track=0,
                vertical_rate=0,
                geo_altitude=1000,
                squawk="0000"
            )

    def test_aeroplane_validation_velocity(self):
        """Тест валидации скорости."""
        with pytest.raises(ValueError, match="Скорость должна быть в диапазоне 0-1000 м/с"):
            Aeroplane(
                icao24="123abc",
                callsign="TEST",
                country="Test",
                time_position=123,
                last_contact=123,
                longitude=0,
                latitude=0,
                baro_altitude=1000,
                on_ground=False,
                velocity=2000,
                true_track=0,
                vertical_rate=0,
                geo_altitude=1000,
                squawk="0000"
            )

    def test_aeroplane_validation_altitude(self):
        """Тест валидации высоты."""
        with pytest.raises(ValueError, match="Высота должна быть в диапазоне -500-30000 м"):
            Aeroplane(
                icao24="123abc",
                callsign="TEST",
                country="Test",
                time_position=123,
                last_contact=123,
                longitude=0,
                latitude=0,
                baro_altitude=40000,
                on_ground=False,
                velocity=100,
                true_track=0,
                vertical_rate=0,
                geo_altitude=1000,
                squawk="0000"
            )

    def test_aeroplane_validation_latitude(self):
        """Тест валидации широты."""
        with pytest.raises(ValueError, match="Широта должна быть в диапазоне -90-90°"):
            Aeroplane(
                icao24="123abc",
                callsign="TEST",
                country="Test",
                time_position=123,
                last_contact=123,
                longitude=0,
                latitude=100,
                baro_altitude=1000,
                on_ground=False,
                velocity=100,
                true_track=0,
                vertical_rate=0,
                geo_altitude=1000,
                squawk="0000"
            )

    def test_aeroplane_validation_longitude(self):
        """Тест валидации долготы."""
        with pytest.raises(ValueError, match="Долгота должна быть в диапазоне -180-180°"):
            Aeroplane(
                icao24="123abc",
                callsign="TEST",
                country="Test",
                time_position=123,
                last_contact=123,
                longitude=200,
                latitude=0,
                baro_altitude=1000,
                on_ground=False,
                velocity=100,
                true_track=0,
                vertical_rate=0,
                geo_altitude=1000,
                squawk="0000"
            )

    def test_aeroplane_properties(self):
        """Тест свойств объекта Aeroplane."""
        aeroplane = Aeroplane(
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
        )

        assert aeroplane.altitude_m == 4267.2
        assert aeroplane.altitude_ft is not None
        assert aeroplane.altitude_ft > 0
        assert aeroplane.speed_kmh > 0
        assert aeroplane.speed_mph > 0
        assert aeroplane.is_active is True
        assert isinstance(aeroplane.position_time, datetime)

    def test_aeroplane_properties_with_none(self):
        """Тест свойств с None значениями."""
        aeroplane = Aeroplane(
            icao24="4b1812",
            callsign="SWR438A",
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

        assert aeroplane.altitude_ft is None
        assert aeroplane.speed_kmh is None
        assert aeroplane.speed_mph is None
        assert aeroplane.is_active is False

    def test_aeroplane_comparison_by_speed(self):
        """Тест сравнения самолетов по скорости."""
        a1 = Aeroplane(
            icao24="4b1812",
            callsign="TEST1",
            country="Switzerland",
            time_position=1766166618,
            last_contact=1766166618,
            longitude=0,
            latitude=0,
            baro_altitude=5000,
            on_ground=False,
            velocity=200,
            true_track=0,
            vertical_rate=0,
            geo_altitude=5000,
            squawk="0000"
        )

        a2 = Aeroplane(
            icao24="4b1813",
            callsign="TEST2",
            country="Germany",
            time_position=1766166619,
            last_contact=1766166619,
            longitude=0,
            latitude=0,
            baro_altitude=3000,
            on_ground=False,
            velocity=150,
            true_track=0,
            vertical_rate=0,
            geo_altitude=3000,
            squawk="0001"
        )

        assert a1 > a2
        assert a2 < a1
        assert a1 >= a2
        assert a2 <= a1

    def test_aeroplane_comparison_with_none_speed(self):
        """Тест сравнения с None скоростью."""
        a1 = Aeroplane(
            icao24="4b1812",
            callsign="TEST1",
            country="Switzerland",
            time_position=1766166618,
            last_contact=1766166618,
            longitude=0,
            latitude=0,
            baro_altitude=5000,
            on_ground=False,
            velocity=None,
            true_track=0,
            vertical_rate=0,
            geo_altitude=5000,
            squawk="0000"
        )

        a2 = Aeroplane(
            icao24="4b1813",
            callsign="TEST2",
            country="Germany",
            time_position=1766166619,
            last_contact=1766166619,
            longitude=0,
            latitude=0,
            baro_altitude=3000,
            on_ground=False,
            velocity=150,
            true_track=0,
            vertical_rate=0,
            geo_altitude=3000,
            squawk="0001"
        )

        # None считается меньше любого числа
        assert a1.compare_by_velocity(a2) == -1
        assert a2.compare_by_velocity(a1) == 1
        # Операторы сравнения должны работать корректно
        assert not (a1 > a2)
        assert a1 < a2

    def test_compare_by_altitude_and_velocity(self):
        """Тест сравнения по высоте и скорости."""
        low = Aeroplane(
            icao24="aaaaaa",
            callsign="A",
            country="Test",
            time_position=1,
            last_contact=1,
            longitude=0,
            latitude=0,
            baro_altitude=1000,
            on_ground=False,
            velocity=100,
            true_track=0,
            vertical_rate=0,
            geo_altitude=1000,
            squawk="0000",
        )
        high = Aeroplane(
            icao24="bbbbbb",
            callsign="B",
            country="Test",
            time_position=2,
            last_contact=2,
            longitude=0,
            latitude=0,
            baro_altitude=5000,
            on_ground=False,
            velocity=200,
            true_track=0,
            vertical_rate=0,
            geo_altitude=5000,
            squawk="0001",
        )

        # Проверка сравнения по высоте
        assert low.compare_by_altitude(high) == -1
        assert high.compare_by_altitude(low) == 1
        assert low.compare_by_altitude(low) == 0
        assert high.compare_by_altitude(high) == 0

        # Проверка сравнения по скорости
        assert low.compare_by_velocity(high) == -1
        assert high.compare_by_velocity(low) == 1
        assert low.compare_by_velocity(low) == 0
        assert high.compare_by_velocity(high) == 0

    def test_compare_by_altitude_with_none(self):
        """Тест сравнения по высоте с None значениями."""
        a1 = Aeroplane(
            icao24="aaaaaa",
            callsign="A",
            country="Test",
            time_position=1,
            last_contact=1,
            longitude=0,
            latitude=0,
            baro_altitude=None,
            on_ground=False,
            velocity=100,
            true_track=0,
            vertical_rate=0,
            geo_altitude=None,
            squawk="0000"
        )
        a2 = Aeroplane(
            icao24="bbbbbb",
            callsign="B",
            country="Test",
            time_position=2,
            last_contact=2,
            longitude=0,
            latitude=0,
            baro_altitude=5000,
            on_ground=False,
            velocity=200,
            true_track=0,
            vertical_rate=0,
            geo_altitude=5000,
            squawk="0001"
        )

        # None считается меньше любого числа
        assert a1.compare_by_altitude(a2) == -1
        assert a2.compare_by_altitude(a1) == 1

        # Оба None - равны
        a3 = Aeroplane(
            icao24="cccccc",
            callsign="C",
            country="Test",
            time_position=3,
            last_contact=3,
            longitude=0,
            latitude=0,
            baro_altitude=None,
            on_ground=False,
            velocity=150,
            true_track=0,
            vertical_rate=0,
            geo_altitude=None,
            squawk="0002"
        )
        assert a1.compare_by_altitude(a3) == 0

    def test_compare_by_velocity_with_none(self):
        """Тест сравнения по скорости с None значениями."""
        a1 = Aeroplane(
            icao24="aaaaaa",
            callsign="A",
            country="Test",
            time_position=1,
            last_contact=1,
            longitude=0,
            latitude=0,
            baro_altitude=1000,
            on_ground=False,
            velocity=None,
            true_track=0,
            vertical_rate=0,
            geo_altitude=1000,
            squawk="0000"
        )
        a2 = Aeroplane(
            icao24="bbbbbb",
            callsign="B",
            country="Test",
            time_position=2,
            last_contact=2,
            longitude=0,
            latitude=0,
            baro_altitude=5000,
            on_ground=False,
            velocity=200,
            true_track=0,
            vertical_rate=0,
            geo_altitude=5000,
            squawk="0001"
        )

        # None считается меньше любого числа
        assert a1.compare_by_velocity(a2) == -1
        assert a2.compare_by_velocity(a1) == 1

        # Оба None - равны
        a3 = Aeroplane(
            icao24="cccccc",
            callsign="C",
            country="Test",
            time_position=3,
            last_contact=3,
            longitude=0,
            latitude=0,
            baro_altitude=3000,
            on_ground=False,
            velocity=None,
            true_track=0,
            vertical_rate=0,
            geo_altitude=3000,
            squawk="0002"
        )
        assert a1.compare_by_velocity(a3) == 0

    def test_aeroplane_equality(self):
        """Тест равенства самолетов."""
        a1 = Aeroplane(
            icao24="4b1812",
            callsign="TEST1",
            country="Switzerland",
            time_position=1766166618,
            last_contact=1766166618,
            longitude=0,
            latitude=0,
            baro_altitude=5000,
            on_ground=False,
            velocity=200,
            true_track=0,
            vertical_rate=0,
            geo_altitude=5000,
            squawk="0000"
        )

        a2 = Aeroplane(
            icao24="4b1812",
            callsign="TEST1",
            country="Switzerland",
            time_position=1766166618,
            last_contact=1766166618,
            longitude=0,
            latitude=0,
            baro_altitude=5000,
            on_ground=False,
            velocity=200,
            true_track=0,
            vertical_rate=0,
            geo_altitude=5000,
            squawk="0000"
        )

        a3 = Aeroplane(
            icao24="4b1813",
            callsign="TEST2",
            country="Germany",
            time_position=1766166619,
            last_contact=1766166619,
            longitude=0,
            latitude=0,
            baro_altitude=3000,
            on_ground=False,
            velocity=150,
            true_track=0,
            vertical_rate=0,
            geo_altitude=3000,
            squawk="0001"
        )

        assert a1 == a2
        assert a1 != a3
        assert hash(a1) == hash(a2)
        assert hash(a1) != hash(a3)

    def test_aeroplane_to_dict(self):
        """Тест преобразования в словарь."""
        aeroplane = Aeroplane(
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
        )

        data = aeroplane.to_dict()
        assert data['icao24'] == "4b1812"
        assert data['callsign'] == "SWR438A"
        assert data['country'] == "Switzerland"
        assert data['velocity'] == 189.7
        assert data['baro_altitude'] == 4267.2

    def test_aeroplane_from_state(self):
        """Тест создания из состояния OpenSky."""
        state = [
            "4b1812",
            "SWR438A ",
            "Switzerland",
            1766166618,
            1766166618,
            -0.0168,
            51.0888,
            4267.2,
            False,
            189.7,
            129.39,
            14.63,
            None,
            4282.44,
            "2061",
            False,
            0
        ]

        aeroplane = Aeroplane.from_state(state)
        assert aeroplane.icao24 == "4b1812"
        assert aeroplane.callsign == "SWR438A"
        assert aeroplane.country == "Switzerland"
        assert aeroplane.velocity == 189.7
        assert aeroplane.baro_altitude == 4267.2

    def test_aeroplane_cast_to_object_list(self):
        """Тест преобразования данных API в список объектов."""
        test_data = {
            "time": 1766142246,
            "states": [
                [
                    "4b1812",
                    "SWR438A ",
                    "Switzerland",
                    1766166618,
                    1766166618,
                    -0.0168,
                    51.0888,
                    4267.2,
                    False,
                    189.7,
                    129.39,
                    14.63,
                    None,
                    4282.44,
                    "2061",
                    False,
                    0
                ]
            ]
        }

        aeroplanes = Aeroplane.cast_to_object_list(test_data)
        assert len(aeroplanes) == 1
        assert aeroplanes[0].icao24 == "4b1812"
        assert aeroplanes[0].callsign == "SWR438A"
        assert aeroplanes[0].country == "Switzerland"

    def test_aeroplane_cast_to_object_list_empty(self):
        """Тест преобразования пустых данных."""
        assert Aeroplane.cast_to_object_list(None) == []
        assert Aeroplane.cast_to_object_list({}) == []
        assert Aeroplane.cast_to_object_list({"states": []}) == []

    def test_aeroplane_cast_to_object_list_invalid(self):
        """Тест преобразования с невалидными данными."""
        test_data = {
            "states": [
                ["invalid"]  # Недостаточно данных
            ]
        }
        aeroplanes = Aeroplane.cast_to_object_list(test_data)
        assert len(aeroplanes) == 0
