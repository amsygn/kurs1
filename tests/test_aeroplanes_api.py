from unittest.mock import patch, MagicMock
from requests import RequestException
from src.api.aeroplanes_api import AeroplanesAPI


class TestAeroplanesAPI:
    """Тесты для класса AeroplanesAPI."""

    @patch('src.api.aeroplanes_api.get')
    def test_get_country_coordinates_success(self, mock_get):
        """Тест успешного получения координат страны."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "name": "Canada",
                "display_name": "Canada",
                "boundingbox": ["41.6765597", "83.3362128", "-141.0027500", "-52.3237664"],
                "lat": "61.0666922",
                "lon": "-107.9917070"
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api.get_country_coordinates("Canada")

        assert result is not None
        assert result["name"] == "Canada"
        assert result["display_name"] == "Canada"
        assert len(result["boundingbox"]) == 4
        assert result["boundingbox"][0] == "41.6765597"
        assert result["lat"] == "61.0666922"

    @patch('src.api.aeroplanes_api.get')
    def test_get_country_coordinates_not_found(self, mock_get):
        """Тест получения координат несуществующей страны."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api.get_country_coordinates("NonExistentCountry")

        assert result is None

    @patch('src.api.aeroplanes_api.get')
    def test_get_country_coordinates_request_error(self, mock_get):
        """Тест ошибки запроса при получении координат."""
        # Используем RequestException вместо Exception
        mock_get.side_effect = RequestException("Network error")

        api = AeroplanesAPI()
        result = api.get_country_coordinates("Canada")

        assert result is None

    @patch('src.api.aeroplanes_api.get')
    def test_get_aeroplanes_by_country_success(self, mock_get):
        """Тест успешного получения самолетов по стране."""
        # Мок для координат страны
        coords_response = MagicMock()
        coords_response.json.return_value = [
            {
                "name": "Canada",
                "display_name": "Canada",
                "boundingbox": ["41.6765597", "83.3362128", "-141.0027500", "-52.3237664"]
            }
        ]
        coords_response.raise_for_status.return_value = None

        # Мок для данных о самолетах
        planes_response = MagicMock()
        planes_response.json.return_value = {
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
        planes_response.raise_for_status.return_value = None

        mock_get.side_effect = [coords_response, planes_response]

        api = AeroplanesAPI()
        result = api.get_aeroplanes_by_country("Canada")

        assert result is not None
        assert "states" in result
        assert result["country"] == "Canada"
        assert "country_coords" in result

    @patch('src.api.aeroplanes_api.get')
    def test_get_aeroplanes_by_country_no_coordinates(self, mock_get):
        """Тест получения самолетов при отсутствии координат."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api.get_aeroplanes_by_country("NonExistentCountry")

        assert result is None

    @patch('src.api.aeroplanes_api.get')
    def test_get_aeroplanes_by_country_invalid_coordinates(self, mock_get):
        """Тест получения самолетов с некорректными координатами."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "name": "Canada",
                "boundingbox": []  # Пустой boundingbox
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api.get_aeroplanes_by_country("Canada")

        assert result is None

    @patch('src.api.aeroplanes_api.get')
    def test_get_aeroplanes_by_country_api_error(self, mock_get):
        """Тест ошибки API OpenSky."""
        # Мок для координат
        coords_response = MagicMock()
        coords_response.json.return_value = [
            {
                "name": "Canada",
                "boundingbox": ["41.6765597", "83.3362128", "-141.0027500", "-52.3237664"]
            }
        ]
        coords_response.raise_for_status.return_value = None

        # Мок для ошибки OpenSky - используем RequestException
        mock_get.side_effect = [coords_response, RequestException("OpenSky API error")]

        api = AeroplanesAPI()
        result = api.get_aeroplanes_by_country("Canada")

        assert result is None

    @patch('src.api.aeroplanes_api.get')
    def test_get_data_success(self, mock_get):
        """Тест общего метода получения данных."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api.get_data({"param": "value"})

        assert result == {"test": "data"}

    @patch('src.api.aeroplanes_api.get')
    def test_get_data_error(self, mock_get):
        """Тест ошибки в общем методе получения данных."""
        # Используем RequestException вместо Exception
        mock_get.side_effect = RequestException("Request failed")

        api = AeroplanesAPI()
        result = api.get_data({"param": "value"})

        assert result is None

    @patch('src.api.aeroplanes_api.get')
    def test_get_aeroplanes_by_country_coords_api_error(self, mock_get):
        """Тест ошибки при получении координат через API."""
        mock_get.side_effect = RequestException("Coordinates API error")

        api = AeroplanesAPI()
        result = api.get_aeroplanes_by_country("Canada")

        assert result is None

    @patch('src.api.aeroplanes_api.get')
    def test_get_country_coordinates_http_error(self, mock_get):
        """Тест HTTP ошибки при получении координат."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = RequestException("HTTP 404")
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api.get_country_coordinates("Canada")

        assert result is None
