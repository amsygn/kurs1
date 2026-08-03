from typing import Any, Dict, Optional
from requests import get, RequestException
import logging
from .base_api import BaseAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AeroplanesAPI(BaseAPI):
    """Класс для работы с API OpenStreetMap и OpenSky Network."""

    def __init__(self) -> None:
        self.openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
        self.opensky_url = 'https://opensky-network.org/api/states/all'
        self.headers_nominatim = {
            'User-Agent': 'aeroplane-tracker/1.0'
        }

    def get_data(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Общий метод для получения данных из API."""
        try:
            response = get(
                url=self.openstreetmap_url,
                params=params,
                headers=self.headers_nominatim,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Ошибка при получении данных из OpenStreetMap: {e}")
            return None

    def get_country_coordinates(self, country: str) -> Optional[Dict[str, Any]]:
        """Получение координат страны из OpenStreetMap."""
        params = {
            'country': country,
            'format': 'json',
            'limit': 1
        }

        try:
            response = get(
                url=self.openstreetmap_url,
                params=params,
                headers=self.headers_nominatim,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                logger.warning(f"Страна '{country}' не найдена")
                return None

            return {
                'name': data[0].get('name'),
                'display_name': data[0].get('display_name'),
                'boundingbox': data[0].get('boundingbox'),
                'lat': data[0].get('lat'),
                'lon': data[0].get('lon')
            }
        except (RequestException, IndexError, KeyError) as e:
            logger.error(f"Ошибка при получении координат для '{country}': {e}")
            return None

    def get_aeroplanes_by_country(self, country: str) -> Optional[Dict[str, Any]]:
        """Получение информации о самолетах по стране."""
        country_coords = self.get_country_coordinates(country)

        if not country_coords:
            logger.warning(f"Не удалось получить координаты для страны '{country}'")
            return None

        boundingbox = country_coords.get('boundingbox', [])
        if len(boundingbox) < 4:
            logger.warning(f"Некорректные координаты для страны '{country}'")
            return None

        try:
            params = {
                'lamin': float(boundingbox[0]),  # южная
                'lamax': float(boundingbox[1]),  # северная
                'lomin': float(boundingbox[2]),  # западная
                'lomax': float(boundingbox[3]),  # восточная
                'time': 0,  # текущее время
            }

            response = get(
                url=self.opensky_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            data['country'] = country
            data['country_coords'] = country_coords

            return data
        except RequestException as e:
            logger.error(f"Ошибка при получении данных о самолетах: {e}")
            return None
