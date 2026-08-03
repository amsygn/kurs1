import csv
import os
from typing import List, Optional, Dict, Any
from src.planes_models import Aeroplane
from src.storage.base_storage import BaseStorage


class CSVStorage(BaseStorage):
    """Класс для работы с CSV-файлом."""

    def __init__(self, file_path: str = 'data/aeroplanes.csv'):
        self.file_path = file_path
        self.fields = ['icao24', 'callsign', 'country', 'time_position', 'last_contact',
                       'longitude', 'latitude', 'baro_altitude', 'geo_altitude', 'on_ground',
                       'velocity', 'true_track', 'vertical_rate', 'squawk']
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def _load_data(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except (csv.Error, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        with open(self.file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(data)

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавление самолета в CSV-файл."""
        data = self._load_data()
        aeroplane_dict = aeroplane.to_dict()

        # Преобразуем булевы значения в строки
        aeroplane_dict['on_ground'] = str(aeroplane_dict['on_ground'])

        for i, item in enumerate(data):
            if item['icao24'] == aeroplane.icao24 and item['time_position'] == str(aeroplane.time_position):
                data[i] = aeroplane_dict
                self._save_data(data)
                return

        data.append(aeroplane_dict)
        self._save_data(data)

    def add_aeroplanes(self, aeroplanes: List[Aeroplane]) -> None:
        """Добавление нескольких самолетов."""
        for aeroplane in aeroplanes:
            self.add_aeroplane(aeroplane)

    def get_aeroplane(self, icao24: str) -> Optional[Aeroplane]:
        """Получение самолета по ICAO24."""
        data = self._load_data()
        for item in data:
            if item['icao24'] == icao24:
                return self._dict_to_aeroplane(item)
        return None

    def get_aeroplanes_by_country(self, country: str) -> List[Aeroplane]:
        """Получение самолетов по стране регистрации."""
        data = self._load_data()
        result = []
        for item in data:
            if item['country'].lower() == country.lower():
                result.append(self._dict_to_aeroplane(item))
        return result

    def get_all_aeroplanes(self) -> List[Aeroplane]:
        """Получение всех самолетов."""
        data = self._load_data()
        return [self._dict_to_aeroplane(item) for item in data]

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удаление самолета."""
        data = self._load_data()
        data = [item for item in data
                if not (item['icao24'] == aeroplane.icao24 and
                        item['time_position'] == str(aeroplane.time_position))]
        self._save_data(data)

    def delete_aeroplanes_by_country(self, country: str) -> int:
        """Удаление всех самолетов по стране."""
        data = self._load_data()
        initial_count = len(data)
        data = [item for item in data if item['country'].lower() != country.lower()]
        self._save_data(data)
        return initial_count - len(data)

    def clear_all(self) -> None:
        """Очистка хранилища."""
        self._save_data([])

    def _dict_to_aeroplane(self, data: Dict[str, Any]) -> Aeroplane:
        """Преобразование словаря в объект Aeroplane."""
        return Aeroplane(
            icao24=data['icao24'],
            callsign=data.get('callsign'),
            country=data['country'],
            time_position=int(data['time_position']),
            last_contact=int(data['last_contact']),
            longitude=float(data['longitude']) if data.get('longitude') else None,
            latitude=float(data['latitude']) if data.get('latitude') else None,
            baro_altitude=float(data['baro_altitude']) if data.get('baro_altitude') else None,
            on_ground=data['on_ground'].lower() == 'true',
            velocity=float(data['velocity']) if data.get('velocity') else None,
            true_track=float(data['true_track']) if data.get('true_track') else None,
            vertical_rate=float(data['vertical_rate']) if data.get('vertical_rate') else None,
            geo_altitude=float(data['geo_altitude']) if data.get('geo_altitude') else None,
            squawk=data.get('squawk')
        )
