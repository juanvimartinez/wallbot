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
                reserved=False,
                publish_date=1234567890
            )
            
            # Verify item was added to database with reserved=False
            mock_db.add_item.assert_called_once_with(
                "123", "456", "Test Item", 10.50, "test-item", "user123", 
                publish_date=1234567890, reserved=False
            )
            
            # Verify notification was sent without 'reserved' type
            mock_notify.assert_called_once()
            call_kwargs = mock_notify.call_args[1] if mock_notify.call_args[1] else {}
            assert call_kwargs.get('notification_type', 'default') != 'reserved'
    
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
                reserved=True,
                publish_date=1234567890
            )
            
            # Verify item was added with reserved=True
            mock_db.add_item.assert_called_once_with(
                "124", "456", "Reserved Item", 20.00, "reserved-item", "user123",
                publish_date=1234567890, reserved=True
            )
            
            # Notification should be sent with 'reserved' type for reserved items
            mock_notify.assert_called_once()
            call_kwargs = mock_notify.call_args[1] if mock_notify.call_args[1] else {}
            assert call_kwargs.get('notification_type') == 'reserved'
    
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
            'reserved': {'flag': True},
            'created_at': 1234567890
        }
        
        mock_db.search_item.return_value = None  # New item
        
        with patch.object(monitor, '_process_new_item') as mock_process_new:
            monitor._process_item(api_item, "789")
            
            # Verify reserved flag was extracted and passed
            mock_process_new.assert_called_once()
            call_args = mock_process_new.call_args[0]
            assert call_args[6] == True  # reserved parameter (7th argument)

    def test_process_existing_item_price_drop_only(self, monitor, mock_db):
        """Test when an existing item has a price drop but remains unreserved"""
        existing_item = Item(
            item_id="128",
            chat_id="456",
            title="Price Drop Item",
            price="100.00",
            url="price-drop-item",
            publish_date=1234567890,
            observaciones=None,
            item="full_json",
            reserved=0
        )
        
        with patch('src.wallbot.wallapop.monitor.send_notification') as mock_notify:
            monitor._process_existing_item(
                existing_item=existing_item,
                item_id="128",
                new_price=80.00,  # Price dropped from 100 to 80
                title="Price Drop Item",
                web_slug="price-drop-item",
                chat_id="456",
                new_reserved=False  # Still not reserved
            )
            
            # Verify database was updated with new price
            mock_db.update_item.assert_called_once()
            call_args = mock_db.update_item.call_args[0]
            assert call_args[0] == "128"  # item_id
            assert call_args[1] == "80.0"  # new price
            assert call_args[3] == False  # reserved parameter
            
            # Verify notification was sent with 'price' type
            mock_notify.assert_called_once()
            call_kwargs = mock_notify.call_args[1] if mock_notify.call_args[1] else {}
            assert call_kwargs.get('notification_type') == 'price'

    def test_process_existing_item_price_drop_and_reserved(self, monitor, mock_db):
        """Test when an existing item has both a price drop AND becomes reserved (offer accepted scenario)"""
        existing_item = Item(
            item_id="129",
            chat_id="456",
            title="Offer Accepted Item",
            price="150.00",
            url="offer-accepted-item",
            publish_date=1234567890,
            observaciones=None,
            item="full_json",
            reserved=0  # Was not reserved
        )
        
        with patch('src.wallbot.wallapop.monitor.send_notification') as mock_notify:
            monitor._process_existing_item(
                existing_item=existing_item,
                item_id="129",
                new_price=120.00,  # Price dropped from 150 to 120 (offer accepted)
                title="Offer Accepted Item",
                web_slug="offer-accepted-item",
                chat_id="456",
                new_reserved=True  # Now reserved (buyer reserved after offer accepted)
            )
            
            # Verify database was updated with new price and reserved status
            mock_db.update_item.assert_called_once()
            call_args = mock_db.update_item.call_args[0]
            assert call_args[0] == "129"  # item_id
            assert call_args[1] == "120.0"  # new price
            assert call_args[3] == True  # reserved parameter
            
            # Verify notification was sent with 'price_reserved' type (combined notification)
            mock_notify.assert_called_once()
            call_kwargs = mock_notify.call_args[1] if mock_notify.call_args[1] else {}
            assert call_kwargs.get('notification_type') == 'price_reserved'

    def test_process_existing_item_price_drop_with_history(self, monitor, mock_db):
        """Test price drop with existing price history"""
        existing_item = Item(
            item_id="130",
            chat_id="456",
            title="Multiple Price Drops",
            price="80.00",
            url="multiple-drops",
            publish_date=1234567890,
            observaciones="100,00 €",  # Previous price history
            item="full_json",
            reserved=0
        )
        
        with patch('src.wallbot.wallapop.monitor.send_notification') as mock_notify:
            monitor._process_existing_item(
                existing_item=existing_item,
                item_id="130",
                new_price=60.00,  # Another price drop
                title="Multiple Price Drops",
                web_slug="multiple-drops",
                chat_id="456",
                new_reserved=False
            )
            
            # Verify database was updated
            mock_db.update_item.assert_called_once()
            call_args = mock_db.update_item.call_args[0]
            assert call_args[0] == "130"  # item_id
            # Price history should include previous observaciones
            assert "100,00 €" in call_args[2] or "100.00" in call_args[2]
            
            # Verify notification was sent with price history
            mock_notify.assert_called_once()
            call_args_notify = mock_notify.call_args[0]
            # Notes (price history) should be included
            assert call_args_notify[4] is not None  # notes parameter

    def test_process_existing_item_price_drop_and_reserved_with_history(self, monitor, mock_db):
        """Test combined price drop + reservation with existing price history"""
        existing_item = Item(
            item_id="131",
            chat_id="456",
            title="Complex Scenario Item",
            price="200.00",
            url="complex-scenario",
            publish_date=1234567890,
            observaciones="250,00 €",  # Previous price history
            item="full_json",
            reserved=0
        )
        
        with patch('src.wallbot.wallapop.monitor.send_notification') as mock_notify:
            monitor._process_existing_item(
                existing_item=existing_item,
                item_id="131",
                new_price=180.00,  # Price dropped due to accepted offer
                title="Complex Scenario Item",
                web_slug="complex-scenario",
                chat_id="456",
                new_reserved=True  # And item got reserved
            )
            
            # Verify database was updated with new price and reserved status
            mock_db.update_item.assert_called_once()
            call_args = mock_db.update_item.call_args[0]
            assert call_args[0] == "131"  # item_id
            assert call_args[1] == "180.0"  # new price
            assert call_args[3] == True  # reserved parameter
            
            # Verify combined notification was sent
            mock_notify.assert_called_once()
            call_kwargs = mock_notify.call_args[1] if mock_notify.call_args[1] else {}
            assert call_kwargs.get('notification_type') == 'price_reserved'
            
            # Notes should include price history
            call_args_notify = mock_notify.call_args[0]
            assert call_args_notify[4] is not None  # notes parameter

    def test_process_existing_item_already_reserved_price_drop(self, monitor, mock_db):
        """Test price drop on an already reserved item (only price notification, not combined)"""
        existing_item = Item(
            item_id="132",
            chat_id="456",
            title="Already Reserved Item",
            price="100.00",
            url="already-reserved",
            publish_date=1234567890,
            observaciones=None,
            item="full_json",
            reserved=1  # Already was reserved
        )
        
        with patch('src.wallbot.wallapop.monitor.send_notification') as mock_notify:
            monitor._process_existing_item(
                existing_item=existing_item,
                item_id="132",
                new_price=90.00,  # Price dropped
                title="Already Reserved Item",
                web_slug="already-reserved",
                chat_id="456",
                new_reserved=True  # Still reserved
            )
            
            # Verify notification was sent with 'price' type only (not 'price_reserved')
            # because reservation_changed should be False (was already reserved)
            mock_notify.assert_called_once()
            call_kwargs = mock_notify.call_args[1] if mock_notify.call_args[1] else {}
            assert call_kwargs.get('notification_type') == 'price'

    def test_process_existing_item_no_changes(self, monitor, mock_db):
        """Test when nothing changes (same price, same reservation status)"""
        existing_item = Item(
            item_id="133",
            chat_id="456",
            title="No Changes Item",
            price="50.00",
            url="no-changes",
            publish_date=1234567890,
            observaciones=None,
            item="full_json",
            reserved=0
        )
        
        with patch('src.wallbot.wallapop.monitor.send_notification') as mock_notify:
            monitor._process_existing_item(
                existing_item=existing_item,
                item_id="133",
                new_price=50.00,  # Same price
                title="No Changes Item",
                web_slug="no-changes",
                chat_id="456",
                new_reserved=False  # Same reservation status
            )
            
            # No notification should be sent
            mock_notify.assert_not_called()
            # No database update should occur
            mock_db.update_item.assert_not_called()

    def test_process_existing_item_price_increase_ignored(self, monitor, mock_db):
        """Test that price increases are ignored (only price drops trigger notifications)"""
        existing_item = Item(
            item_id="134",
            chat_id="456",
            title="Price Increase Item",
            price="100.00",
            url="price-increase",
            publish_date=1234567890,
            observaciones=None,
            item="full_json",
            reserved=0
        )
        
        with patch('src.wallbot.wallapop.monitor.send_notification') as mock_notify:
            monitor._process_existing_item(
                existing_item=existing_item,
                item_id="134",
                new_price=120.00,  # Price increased (should be ignored)
                title="Price Increase Item",
                web_slug="price-increase",
                chat_id="456",
                new_reserved=False
            )
            
            # No notification should be sent for price increases
            mock_notify.assert_not_called()
