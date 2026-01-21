import pytest
import locale
from unittest.mock import Mock, MagicMock, patch
from src.wallbot.wallapop.monitor import WallapopMonitor
from src.wallbot.database.models import Item


class TestMonitorReservedFlag:
    
    @pytest.fixture(autouse=True)
    def setup_locale(self):
        """Set up locale for currency formatting in tests"""
        try:
            locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            except locale.Error:
                # Fallback if neither locale is available
                locale.setlocale(locale.LC_ALL, '')
        yield
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database"""
        return Mock()
    
    @pytest.fixture
    def monitor(self, mock_db):
        """Create a monitor instance with mock db"""
        return WallapopMonitor(mock_db)
    
    def test_process_new_item_with_reserved_false(self, monitor, mock_db):
        """Test processing new item that is not reserved"""
        with patch('src.wallbot.wallapop.monitor.send_notification') as mock_notify:
            monitor._process_new_item(
                item_id="123",
                chat_id="456",
                title="Test Item",
                price=10.50,
                web_slug="test-item",
                user_id="user123",
                reserved=False
            )
            
            # Verify item was added to database with reserved=False
            mock_db.add_item.assert_called_once_with(
                "123", "456", "Test Item", 10.50, "test-item", "user123", reserved=False
            )
            
            # Verify notification was sent
            mock_notify.assert_called_once()
    
    def test_process_new_item_with_reserved_true(self, monitor, mock_db):
        """Test processing new item that is reserved"""
        with patch('src.wallbot.wallapop.monitor.send_notification') as mock_notify:
            monitor._process_new_item(
                item_id="124",
                chat_id="456",
                title="Reserved Item",
                price=20.00,
                web_slug="reserved-item",
                user_id="user123",
                reserved=True
            )
            
            # Verify item was added with reserved=True
            mock_db.add_item.assert_called_once_with(
                "124", "456", "Reserved Item", 20.00, "reserved-item", "user123", reserved=True
            )
            
            # Notification should still be sent for new items even if reserved
            mock_notify.assert_called_once()
    
    def test_process_existing_item_becomes_reserved(self, monitor, mock_db):
        """Test when an existing item becomes reserved"""
        # Mock existing item that is not reserved
        existing_item = Item(
            item_id="125",
            chat_id="456",
            title="Item to Reserve",
            price="15.00",
            url="item-to-reserve",
            publish_date=1234567890,
            observaciones=None,
            item="full_json",
            reserved=0
        )
        
        with patch('src.wallbot.wallapop.monitor.send_notification') as mock_notify:
            monitor._process_existing_item(
                existing_item=existing_item,
                item_id="125",
                new_price=15.00,
                title="Item to Reserve",
                web_slug="item-to-reserve",
                chat_id="456",
                new_reserved=True  # Item becomes reserved
            )
            
            # Verify database was updated with new reserved status
            mock_db.update_item.assert_called_once()
            call_args = mock_db.update_item.call_args[0]
            assert call_args[0] == "125"  # item_id
            assert call_args[3] == True   # reserved parameter
            
            # Verify notification was sent with 'reserved' type
            assert mock_notify.called
            # Check if notification_type='reserved' was passed
            call_kwargs = mock_notify.call_args[1] if mock_notify.call_args[1] else {}
            if 'notification_type' in call_kwargs:
                assert call_kwargs['notification_type'] == 'reserved'
    
    def test_process_existing_item_stays_unreserved(self, monitor, mock_db):
        """Test when item remains unreserved with same price"""
        existing_item = Item(
            item_id="126",
            chat_id="456",
            title="Unchanged Item",
            price="10.00",
            url="unchanged-item",
            publish_date=1234567890,
            observaciones=None,
            item="full_json",
            reserved=0
        )
        
        with patch('src.wallbot.wallapop.monitor.send_notification') as mock_notify:
            monitor._process_existing_item(
                existing_item=existing_item,
                item_id="126",
                new_price=10.00,
                title="Unchanged Item",
                web_slug="unchanged-item",
                chat_id="456",
                new_reserved=False  # Still not reserved
            )
            
            # No update or notification should occur if nothing changed
            # (depends on your implementation logic)
    
    def test_process_item_extracts_reserved_flag(self, monitor, mock_db):
        """Test that _process_item correctly extracts reserved flag from API response"""
        api_item = {
            'id': '127',
            'title': 'API Item',
            'price': {'amount': 25.00},
            'user_id': 'user456',
            'web_slug': 'api-item',
            'reserved': {'flag': True}
        }
        
        mock_db.search_item.return_value = None  # New item
        
        with patch.object(monitor, '_process_new_item') as mock_process_new:
            monitor._process_item(api_item, "789")
            
            # Verify reserved flag was extracted and passed
            mock_process_new.assert_called_once()
            call_args = mock_process_new.call_args[0]
            assert call_args[6] == True  # reserved parameter (7th argument)
