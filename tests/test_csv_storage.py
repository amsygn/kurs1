import pytest
import os
import tempfile
from src.planes_models import Aeroplane
from src.storage.csv_storage import CSVStorage


class TestCSVStorage:
    """Тесты для класса CSVStorage."""

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

    def test_csv_storage_creation(self):
        """Тест создания CSV хранилища."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)
            assert os.path.exists(file_path)

            # Проверяем, что файл создан с заголовками
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'icao24' in content
                assert 'callsign' in content
                assert 'country' in content

    def test_csv_storage_add_aeroplane(self):
        """Тест добавления самолета в CSV хранилище."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

            aeroplane = self.create_test_aeroplane()
            storage.add_aeroplane(aeroplane)

            stored = storage.get_aeroplane("4b1812")
            assert stored is not None
            assert stored.icao24 == "4b1812"
            assert stored.callsign == "SWR438A"

    def test_csv_storage_add_aeroplane_with_none_values(self):
        """Тест добавления самолета с None значениями."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

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
            storage.add_aeroplane(aeroplane)

            stored = storage.get_aeroplane("4b1812")
            assert stored is not None
            assert stored.callsign is None
            assert stored.longitude is None
            assert stored.on_ground is True

    def test_csv_storage_update_existing(self):
        """Тест обновления существующей записи в CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

            aeroplane = self.create_test_aeroplane()
            storage.add_aeroplane(aeroplane)

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

    def test_csv_storage_get_aeroplane_not_found(self):
        """Тест получения несуществующего самолета."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

            result = storage.get_aeroplane("nonexistent")
            assert result is None

    def test_csv_storage_add_aeroplanes_empty_list(self):
        """Тест добавления пустого списка самолетов."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

            storage.add_aeroplanes([])
            all_planes = storage.get_all_aeroplanes()
            assert len(all_planes) == 0

    def test_csv_storage_load_empty_file(self):
        """Тест загрузки из пустого файла."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "empty.csv")
            # Создаем пустой файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('')

            storage = CSVStorage(file_path)
            data = storage._load_data()
            assert data == []

    def test_csv_storage_load_corrupted_file(self):
        """Тест загрузки поврежденного файла."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "corrupted.csv")
            # Создаем поврежденный файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('invalid,csv,data\n')

            storage = CSVStorage(file_path)
            data = storage._load_data()
            # Должен вернуть пустой список при ошибке
            assert data == []

    def test_csv_storage_delete_aeroplane_not_found(self):
        """Тест удаления несуществующего самолета."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

            aeroplane = self.create_test_aeroplane()
            storage.delete_aeroplane(aeroplane)  # Не должно вызвать ошибку

            assert len(storage.get_all_aeroplanes()) == 0

    def test_csv_storage_delete_aeroplanes_by_country(self):
        """Тест удаления самолетов по стране."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

            a1 = self.create_test_aeroplane("4b1812", "SWR438A", "Switzerland")
            a2 = self.create_test_aeroplane("4b1813", "LUFTHANSA", "Germany", 1766166619)

            storage.add_aeroplanes([a1, a2])

            deleted = storage.delete_aeroplanes_by_country("Switzerland")
            assert deleted == 1

            all_planes = storage.get_all_aeroplanes()
            assert len(all_planes) == 1
            assert all_planes[0].icao24 == "4b1813"

    def test_csv_storage_delete_aeroplanes_by_country_not_found(self):
        """Тест удаления самолетов по несуществующей стране."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

            aeroplane = self.create_test_aeroplane()
            storage.add_aeroplane(aeroplane)

            deleted = storage.delete_aeroplanes_by_country("NonExistent")
            assert deleted == 0

            all_planes = storage.get_all_aeroplanes()
            assert len(all_planes) == 1

    def test_csv_storage_clear_all(self):
        """Тест очистки CSV хранилища."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

            aeroplane = self.create_test_aeroplane()
            storage.add_aeroplane(aeroplane)

            assert len(storage.get_all_aeroplanes()) == 1

            storage.clear_all()
            assert len(storage.get_all_aeroplanes()) == 0

    def test_csv_storage_get_aeroplanes_by_country_case_insensitive(self):
        """Тест получения самолетов по стране (регистронезависимо)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.csv")
            storage = CSVStorage(file_path)

            aeroplane = self.create_test_aeroplane("4b1812", "SWR438A", "Switzerland")
            storage.add_aeroplane(aeroplane)

            # Разные варианты написания
            result1 = storage.get_aeroplanes_by_country("switzerland")
            result2 = storage.get_aeroplanes_by_country("SWITZERLAND")

            assert len(result1) == 1
            assert len(result2) == 1
