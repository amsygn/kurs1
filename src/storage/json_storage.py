import json
import os
from typing import List, Optional, Dict, Any
from src.planes_models import Aeroplane
from src.storage.base_storage import BaseStorage


class JSONStorage(BaseStorage):
    """Класс для работы с JSON-файлом."""

    def __init__(self, file_path: str = 'data/aeroplanes.json'):
        self.file_path = file_path
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def _load_data(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _dict_to_aeroplane(self, data: Dict[str, Any]) -> Aeroplane:
        """Преобразование словаря в объект Aeroplane."""
        return Aeroplane(
            icao24=data['icao24'],
            callsign=data.get('callsign'),
            country=data['country'],
            time_position=data['time_position'],
            last_contact=data['last_contact'],
            longitude=data.get('longitude'),
            latitude=data.get('latitude'),
            baro_altitude=data.get('baro_altitude'),
            on_ground=data['on_ground'],
            velocity=data.get('velocity'),
            true_track=data.get('true_track'),
            vertical_rate=data.get('vertical_rate'),
            geo_altitude=data.get('geo_altitude'),
            squawk=data.get('squawk')
        )

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавление самолета в JSON-файл."""
        data = self._load_data()

        # Проверка, существует ли уже такой самолет
        for i, item in enumerate(data):
            if item['icao24'] == aeroplane.icao24 and item['time_position'] == aeroplane.time_position:
                data[i] = aeroplane.to_dict()
                self._save_data(data)
                return

        data.append(aeroplane.to_dict())
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
                        item['time_position'] == aeroplane.time_position)]
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
