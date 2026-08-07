# tests/test_storage.py
import pytest
import os
import json
import tempfile
from src.planes_models import Aeroplane
from src.storage.json_storage import JSONStorage
from src.storage.csv_storage import CSVStorage
from src.storage.txt_storage import TXTStorage


class TestStorage:
    """Тесты для классов хранилищ."""

    def create_test_aeroplane(self, icao24="4b1812", callsign="SWR438A",
                              country="Switzerland", time_position=1766166618):
        """Создание тестового самолета."""
        return Aeroplane(
            icao24=icao24,
            callsign=callsign,
            country=country,
            time_position=time_position,
            last_contact=time_position,
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

    def test_json_storage_creation(self):
        """Тест создания JSON хранилища."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")
            storage = JSONStorage(file_path)

            assert os.path.exists(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data == []

    def test_json_storage_add_aeroplane(self):
        """Тест добавления самолета в JSON хранилище."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")
            storage = JSONStorage(file_path)

            aeroplane = self.create_test_aeroplane()
            storage.add_aeroplane(aeroplane)

            stored = storage.get_aeroplane("4b1812")
            assert stored is not None
            assert stored.icao24 == "4b1812"
            assert stored.callsign == "SWR438A"
            assert stored.country == "Switzerland"

    def test_json_storage_add_aeroplanes(self):
        """Тест добавления нескольких самолетов в JSON хранилище."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")
            storage = JSONStorage(file_path)

            a1 = self.create_test_aeroplane("4b1812", "SWR438A", "Switzerland")
            a2 = self.create_test_aeroplane("4b1813", "LUFTHANSA", "Germany", 1766166619)

            storage.add_aeroplanes([a1, a2])

            all_aeroplanes = storage.get_all_aeroplanes()
            assert len(all_aeroplanes) == 2

    def test_json_storage_get_by_country(self):
        """Тест получения самолетов по стране."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")
            storage = JSONStorage(file_path)

            a1 = self.create_test_aeroplane("4b1812", "SWR438A", "Switzerland")
            a2 = self.create_test_aeroplane("4b1813", "LUFTHANSA", "Germany", 1766166619)

            storage.add_aeroplanes([a1, a2])

            swiss_planes = storage.get_aeroplanes_by_country("Switzerland")
            assert len(swiss_planes) == 1
            assert swiss_planes[0].icao24 == "4b1812"

            german_planes = storage.get_aeroplanes_by_country("Germany")
            assert len(german_planes) == 1
            assert german_planes[0].icao24 == "4b1813"

    def test_json_storage_delete_aeroplane(self):
        """Тест удаления самолета."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")
            storage = JSONStorage(file_path)

            aeroplane = self.create_test_aeroplane()
            storage.add_aeroplane(aeroplane)

            assert storage.get_aeroplane("4b1812") is not None

            storage.delete_aeroplane(aeroplane)
            assert storage.get_aeroplane("4b1812") is None

    def test_json_storage_delete_by_country(self):
        """Тест удаления самолетов по стране."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")
            storage = JSONStorage(file_path)

            a1 = self.create_test_aeroplane("4b1812", "SWR438A", "Switzerland")
            a2 = self.create_test_aeroplane("4b1813", "LUFTHANSA", "Germany", 1766166619)

            storage.add_aeroplanes([a1, a2])

            deleted = storage.delete_aeroplanes_by_country("Switzerland")
            assert deleted == 1

            all_planes = storage.get_all_aeroplanes()
            assert len(all_planes) == 1
            assert all_planes[0].icao24 == "4b1813"

    def test_json_storage_clear_all(self):
        """Тест очистки хранилища."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")
            storage = JSONStorage(file_path)

            aeroplane = self.create_test_aeroplane()
            storage.add_aeroplane(aeroplane)

            assert len(storage.get_all_aeroplanes()) == 1

            storage.clear_all()
            assert len(storage.get_all_aeroplanes()) == 0

    def test_json_storage_update_existing(self):
        """Тест обновления существующей записи."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.json")
            storage = JSONStorage(file_path)

            aeroplane = self.create_test_aeroplane()
            storage.add_aeroplane(aeroplane)

            # Создаем обновленный самолет с теми же ICAO24 и временем
            updated = Aeroplane(
                icao24="4b1812",
                callsign="UPDATED",
                country="Switzerland",
                time_position=1766166618,
                last_contact=1766166618,
                longitude=-1.0,
                latitude=52.0,
                baro_altitude=5000.0,
                on_ground=False,
                velocity=200.0,
                true_track=130.0,
                vertical_rate=15.0,
                geo_altitude=5000.0,
                squawk="2061"
            )
            storage.add_aeroplane(updated)

            stored = storage.get_aeroplane("4b1812")
            assert stored.callsign == "UPDATED"
            assert stored.longitude == -1.0
            assert stored.velocity == 200.0

    def test_csv_storage(self):
        """Тест CSV хранилища."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

            aeroplane = self.create_test_aeroplane()
            storage.add_aeroplane(aeroplane)

            stored = storage.get_aeroplane("4b1812")
            assert stored is not None
            assert stored.icao24 == "4b1812"

            all_planes = storage.get_all_aeroplanes()
            assert len(all_planes) == 1

            storage.delete_aeroplane(aeroplane)
            assert storage.get_aeroplane("4b1812") is None

    def test_txt_storage(self):
        """Тест TXT хранилища."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            storage = TXTStorage(file_path)

            aeroplane = self.create_test_aeroplane()
            storage.add_aeroplane(aeroplane)

            stored = storage.get_aeroplane("4b1812")
            assert stored is not None
            assert stored.icao24 == "4b1812"

            all_planes = storage.get_all_aeroplanes()
            assert len(all_planes) == 1

            storage.delete_aeroplane(aeroplane)
            assert storage.get_aeroplane("4b1812") is None

    def test_csv_storage_add_aeroplanes(self):
        """Тест добавления нескольких самолетов в CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

            a1 = self.create_test_aeroplane("4b1812", "SWR438A", "Switzerland")
            a2 = self.create_test_aeroplane("4b1813", "LUFTHANSA", "Germany", 1766166619)

            storage.add_aeroplanes([a1, a2])

            all_planes = storage.get_all_aeroplanes()
            assert len(all_planes) == 2

    def test_txt_storage_add_aeroplanes(self):
        """Тест добавления нескольких самолетов в TXT."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            storage = TXTStorage(file_path)

            a1 = self.create_test_aeroplane("4b1812", "SWR438A", "Switzerland")
            a2 = self.create_test_aeroplane("4b1813", "LUFTHANSA", "Germany", 1766166619)

            storage.add_aeroplanes([a1, a2])

            all_planes = storage.get_all_aeroplanes()
            assert len(all_planes) == 2
