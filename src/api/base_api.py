from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAPI(ABC):
    """Абстрактный базовый класс для работы с API."""

    @abstractmethod
    def get_data(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Получение данных из API по заданным параметрам."""
        pass

    @abstractmethod
    def get_country_coordinates(self, country: str) -> Optional[Dict[str, Any]]:
        """Получение географических координат страны."""
        pass

    @abstractmethod
    def get_aeroplanes_by_country(self, country: str) -> Optional[Dict[str, Any]]:
        """Получение информации о самолетах по стране."""
        pass
