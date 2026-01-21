import pytest
from src.wallbot.database.models import Item


class TestItemModel:
    
    def test_item_creation_with_reserved_default(self):
        """Test Item creation with default reserved value"""
        item = Item(
            item_id="123",
            chat_id="456",
            title="Test Item",
            price="10.50",
            url="test-url",
            publish_date=1234567890,
            observaciones=None,
            item="full_json"
        )
        assert item.reserved == 0
    
    def test_item_creation_with_reserved_true(self):
        """Test Item creation with reserved=True"""
        item = Item(
            item_id="123",
            chat_id="456",
            title="Test Item",
            price="10.50",
            url="test-url",
            publish_date=1234567890,
            observaciones=None,
            item="full_json",
            reserved=1
        )
        assert item.reserved == 1
    
    def test_item_creation_with_reserved_false(self):
        """Test Item creation with reserved=False"""
        item = Item(
            item_id="123",
            chat_id="456",
            title="Test Item",
            price="10.50",
            url="test-url",
            publish_date=1234567890,
            observaciones=None,
            item="full_json",
            reserved=0
        )
        assert item.reserved == 0
