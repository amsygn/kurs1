from abc import ABC, abstractmethod
from typing import List, Optional
from src.planes_models import Aeroplane


class BaseStorage(ABC):
    """Абстрактный базовый класс для работы с хранилищем."""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавление информации о самолете в хранилище."""
        pass

    @abstractmethod
    def add_aeroplanes(self, aeroplanes: List[Aeroplane]) -> None:
        """Добавление информации о нескольких самолетах в хранилище."""
        pass

    @abstractmethod
    def get_aeroplane(self, icao24: str) -> Optional[Aeroplane]:
        """Получение информации о самолете по ICAO24."""
        pass

    @abstractmethod
    def get_aeroplanes_by_country(self, country: str) -> List[Aeroplane]:
        """Получение всех самолетов по стране регистрации."""
        pass

    @abstractmethod
    def get_all_aeroplanes(self) -> List[Aeroplane]:
        """Получение всех самолетов из хранилища."""
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удаление информации о самолете из хранилища."""
        pass

    @abstractmethod
    def delete_aeroplanes_by_country(self, country: str) -> int:
        """Удаление всех самолетов по стране регистрации."""
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Очистка хранилища."""
        pass
