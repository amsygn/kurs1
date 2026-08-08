from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Aeroplane:
    """Класс для работы с информацией о самолете."""

    icao24: str
    callsign: Optional[str]
    country: str
    time_position: int
    last_contact: int
    longitude: Optional[float]
    latitude: Optional[float]
    baro_altitude: Optional[float]
    on_ground: bool
    velocity: Optional[float]
    true_track: Optional[float]
    vertical_rate: Optional[float]
    geo_altitude: Optional[float]
    squawk: Optional[str]

    def __post_init__(self):
        """Валидация данных после инициализации."""
        self._validate()

    def _validate(self):
        """Валидация атрибутов."""
        # ICAO24 должен быть строкой
        if not isinstance(self.icao24, str) or len(self.icao24) != 6:
            raise ValueError("ICAO24 должен быть 6-символьной строкой")

        # Страна должна быть строкой
        if not self.country or not isinstance(self.country, str):
            raise ValueError("Страна должна быть непустой строкой")

        # Валидация скорости (0-1000 м/с)
        if self.velocity is not None and (self.velocity < 0 or self.velocity > 1000):
            raise ValueError("Скорость должна быть в диапазоне 0-1000 м/с")

        # Валидация высоты (0-30000 м)
        if self.baro_altitude is not None and (self.baro_altitude < -500 or self.baro_altitude > 30000):
            raise ValueError("Высота должна быть в диапазоне -500-30000 м")

        # Валидация координат
        if self.latitude is not None and (self.latitude < -90 or self.latitude > 90):
            raise ValueError("Широта должна быть в диапазоне -90-90°")

        if self.longitude is not None and (self.longitude < -180 or self.longitude > 180):
            raise ValueError("Долгота должна быть в диапазоне -180-180°")

    @property
    def altitude_m(self) -> Optional[float]:
        """Возвращает барометрическую высоту в метрах."""
        return self.baro_altitude

    @property
    def altitude_ft(self) -> Optional[float]:
        """Возвращает барометрическую высоту в футах."""
        if self.baro_altitude is not None:
            return self.baro_altitude * 3.28084
        return None

    @property
    def speed_kmh(self) -> Optional[float]:
        """Возвращает скорость в км/ч."""
        if self.velocity is not None:
            return self.velocity * 3.6
        return None

    @property
    def speed_mph(self) -> Optional[float]:
        """Возвращает скорость в милях/ч."""
        if self.velocity is not None:
            return self.velocity * 2.23694
        return None

    @property
    def position_time(self) -> datetime:
        """Возвращает время позиции как datetime."""
        return datetime.fromtimestamp(self.time_position)

    @property
    def is_active(self) -> bool:
        """Проверяет, активен ли самолет (не на земле и имеет координаты)."""
        return not self.on_ground and self.latitude is not None and self.longitude is not None

    def compare_by_velocity(self, other: "Aeroplane") -> int:
        """
        Сравнение по скорости.
        -1 если self медленнее, 0 если равны, 1 если быстрее.
        None считаем меньше любого числа.
        """
        if self.velocity is None and other.velocity is None:
            return 0
        if self.velocity is None:
            return -1
        if other.velocity is None:
            return 1
        return (self.velocity > other.velocity) - (self.velocity < other.velocity)

    def compare_by_altitude(self, other: "Aeroplane") -> int:
        """
        Сравнение по высоте (baro_altitude).
        -1 если self ниже, 0 если равны, 1 если выше.
        None считаем меньше любого числа.
        """
        if self.baro_altitude is None and other.baro_altitude is None:
            return 0
        if self.baro_altitude is None:
            return -1
        if other.baro_altitude is None:
            return 1
        return (self.baro_altitude > other.baro_altitude) - (self.baro_altitude < other.baro_altitude)

    def __lt__(self, other: "Aeroplane") -> bool:
        """Сравнение по скорости (меньше). Использует compare_by_velocity."""
        return self.compare_by_velocity(other) < 0

    def __gt__(self, other: "Aeroplane") -> bool:
        """Сравнение по скорости (больше). Использует compare_by_velocity."""
        return self.compare_by_velocity(other) > 0

    def __le__(self, other: "Aeroplane") -> bool:
        """Сравнение по скорости (меньше или равно). Использует compare_by_velocity."""
        return self.compare_by_velocity(other) <= 0

    def __ge__(self, other: "Aeroplane") -> bool:
        """Сравнение по скорости (больше или равно). Использует compare_by_velocity."""
        return self.compare_by_velocity(other) >= 0

    def __eq__(self, other: "Aeroplane") -> bool:
        """Сравнение по ICAO24 и времени."""
        if not isinstance(other, Aeroplane):
            return False
        return self.icao24 == other.icao24 and self.time_position == other.time_position

    def __hash__(self) -> int:
        """Хэш для использования в множествах."""
        return hash((self.icao24, self.time_position))

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование объекта в словарь."""
        return {
            'icao24': self.icao24,
            'callsign': self.callsign,
            'country': self.country,
            'time_position': self.time_position,
            'last_contact': self.last_contact,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'baro_altitude': self.baro_altitude,
            'geo_altitude': self.geo_altitude,
            'on_ground': self.on_ground,
            'velocity': self.velocity,
            'true_track': self.true_track,
            'vertical_rate': self.vertical_rate,
            'squawk': self.squawk
        }

    @classmethod
    def from_state(cls, state: List[Any]) -> "Aeroplane":
        """Создание объекта из массива состояния OpenSky."""
        return cls(
            icao24=state[0],
            callsign=state[1].strip() if state[1] else None,
            country=state[2],
            time_position=state[3],
            last_contact=state[4],
            longitude=state[5],
            latitude=state[6],
            baro_altitude=state[7],
            on_ground=state[8],
            velocity=state[9],
            true_track=state[10],
            vertical_rate=state[11],
            geo_altitude=state[13],
            squawk=state[14]
        )

    @classmethod
    def cast_to_object_list(cls, data: Dict[str, Any]) -> List["Aeroplane"]:
        """Преобразование ответа API в список объектов Aeroplane."""
        if not data or 'states' not in data:
            return []

        aeroplanes = []
        for state in data['states']:
            try:
                aeroplane = cls.from_state(state)
                aeroplanes.append(aeroplane)
            except (ValueError, IndexError) as e:
                print(f"Ошибка при создании объекта Aeroplane: {e}")
                continue

        return aeroplanes
