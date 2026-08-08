import pytest
from abc import ABC
from src.storage.base_storage import BaseStorage


class TestBaseStorage:
    """Тесты для абстрактного класса BaseStorage."""

    def test_base_storage_is_abstract(self):
        """Тест, что BaseStorage является абстрактным классом."""
        assert issubclass(BaseStorage, ABC)

    def test_base_storage_has_abstract_methods(self):
        """Тест, что BaseStorage имеет абстрактные методы."""
        abstract_methods = BaseStorage.__abstractmethods__
        assert 'add_aeroplane' in abstract_methods
        assert 'add_aeroplanes' in abstract_methods
        assert 'get_aeroplane' in abstract_methods
        assert 'get_aeroplanes_by_country' in abstract_methods
        assert 'get_all_aeroplanes' in abstract_methods
        assert 'delete_aeroplane' in abstract_methods
        assert 'delete_aeroplanes_by_country' in abstract_methods
        assert 'clear_all' in abstract_methods

    def test_base_storage_cannot_be_instantiated(self):
        """Тест, что BaseStorage нельзя инстанцировать."""
        with pytest.raises(TypeError):
            BaseStorage()

    def test_concrete_classes_implement_base_storage(self):
        """Тест, что конкретные классы реализуют BaseStorage."""
        from src.storage.json_storage import JSONStorage
        from src.storage.csv_storage import CSVStorage
        from src.storage.txt_storage import TXTStorage

        json_storage = JSONStorage()
        csv_storage = CSVStorage()
        txt_storage = TXTStorage()

        assert isinstance(json_storage, BaseStorage)
        assert isinstance(csv_storage, BaseStorage)
        assert isinstance(txt_storage, BaseStorage)
