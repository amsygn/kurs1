import pytest
from abc import ABC
from src.api.base_api import BaseAPI


class TestBaseAPI:
    """Тесты для абстрактного класса BaseAPI."""

    def test_base_api_is_abstract(self):
        """Тест, что BaseAPI является абстрактным классом."""
        assert issubclass(BaseAPI, ABC)

    def test_base_api_has_abstract_methods(self):
        """Тест, что BaseAPI имеет абстрактные методы."""
        abstract_methods = BaseAPI.__abstractmethods__
        assert 'get_data' in abstract_methods
        assert 'get_country_coordinates' in abstract_methods
        assert 'get_aeroplanes_by_country' in abstract_methods

    def test_base_api_cannot_be_instantiated(self):
        """Тест, что BaseAPI нельзя инстанцировать."""
        with pytest.raises(TypeError):
            BaseAPI()

    def test_concrete_class_implements_base_api(self):
        """Тест, что конкретный класс реализует BaseAPI."""
        from src.api.aeroplanes_api import AeroplanesAPI
        api = AeroplanesAPI()
        assert isinstance(api, BaseAPI)
        assert hasattr(api, 'get_data')
        assert hasattr(api, 'get_country_coordinates')
        assert hasattr(api, 'get_aeroplanes_by_country')
