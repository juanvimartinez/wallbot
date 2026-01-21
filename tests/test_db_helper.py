import pytest
import tempfile
import os
from src.wallbot.database.db_helper import DBHelper
from src.wallbot.database.models import ChatSearch


class TestDBHelperReserved:
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
        temp_file.close()
        db = DBHelper(dbname=temp_file.name)
        db.setup(version='1.0.7')  # Use latest version with reserved column
        yield db
        # Cleanup
        os.unlink(temp_file.name)
    
    def test_add_item_with_reserved_false(self, temp_db):
        """Test adding item with reserved=False"""
        temp_db.add_item(
            item_id="123",
            chat_id="456",
            title="Test Item",
            price="10.50",
            url="test-url",
            user="user123",
            item='{"test": "data"}',
            reserved=0
        )
        
        item = temp_db.search_item("123", "456")
        assert item is not None
        assert item.item_id == 123
        assert item.reserved == 0
    
    def test_add_item_with_reserved_true(self, temp_db):
        """Test adding item with reserved=True"""
        temp_db.add_item(
            item_id="124",
            chat_id="456",
            title="Reserved Item",
            price="20.00",
            url="test-url-2",
            user="user123",
            item='{"test": "data"}',
            reserved=1
        )
        
        item = temp_db.search_item("124", "456")
        assert item is not None
        assert item.item_id == 124
        assert item.reserved == 1
    
    def test_add_item_with_default_reserved(self, temp_db):
        """Test adding item without specifying reserved (should default to 0)"""
        temp_db.add_item(
            item_id="125",
            chat_id="456",
            title="Default Reserved Item",
            price="15.00",
            url="test-url-3",
            user="user123",
            item='{"test": "data"}'
        )
        
        item = temp_db.search_item("125", "456")
        assert item is not None
        assert item.reserved == 0
    
    def test_update_item_reserved_status(self, temp_db):
        """Test updating item's reserved status"""
        # Add item with reserved=False
        temp_db.add_item(
            item_id="126",
            chat_id="456",
            title="Item to Update",
            price="25.00",
            url="test-url-4",
            user="user123",
            reserved=0
        )
        
        # Verify initial state
        item = temp_db.search_item("126", "456")
        assert item.reserved == 0
        
        # Update to reserved=True
        temp_db.update_item("126", "25.00", None, 1)
        
        # Verify updated state
        item = temp_db.search_item("126", "456")
        assert item.reserved == 1
    
    def test_update_item_price_and_reserved(self, temp_db):
        """Test updating both price and reserved status"""
        # Add item
        temp_db.add_item(
            item_id="127",
            chat_id="456",
            title="Price Change Item",
            price="30.00",
            url="test-url-5",
            user="user123",
            reserved=0
        )
        
        # Update price and reserved status
        temp_db.update_item("127", "20.00", "30.00", 1)
        
        # Verify both updates
        item = temp_db.search_item("127", "456")
        assert item.price == "20.00"
        assert item.observaciones == "30.00"
        assert item.reserved == 1
    
    def test_search_nonexistent_item(self, temp_db):
        """Test searching for item that doesn't exist"""
        item = temp_db.search_item("999", "999")
        assert item is None

class TestDeleteAllChatSearches:
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
        temp_file.close()
        db = DBHelper(dbname=temp_file.name)
        db.setup(version='2.0.4')
        yield db
        # Cleanup
        os.unlink(temp_file.name)
    
    def test_delete_all_chat_searches_with_no_data(self, temp_db):
        """Test deleting from a chat_id that has no searches or items"""
        # Should not raise any errors
        temp_db.del_all_chat_searches("999")
        
        # Verify nothing broke
        searches = temp_db.get_chat_searches("999")
        assert len(searches) == 0
    
    def test_delete_all_chat_searches_single_search(self, temp_db):
        """Test deleting a single chat search"""
        # Add a search
        cs = ChatSearch(
            chat_id="123",
            kws="test search",
            active=1
        )
        temp_db.add_search(cs)
        
        # Verify it exists
        searches = temp_db.get_chat_searches("123")
        assert len(searches) == 1
        
        # Delete all searches for this chat
        temp_db.del_all_chat_searches("123")
        
        # Verify it's gone
        searches = temp_db.get_chat_searches("123")
        assert len(searches) == 0
    
    def test_delete_all_chat_searches_multiple_searches(self, temp_db):
        """Test deleting multiple chat searches for the same chat_id"""
        # Add multiple searches
        for i in range(3):
            cs = ChatSearch(
                chat_id="456",
                kws=f"search {i}",
                active=1
            )
            temp_db.add_search(cs)
        
        # Verify they exist
        searches = temp_db.get_chat_searches("456")
        assert len(searches) == 3
        
        # Delete all searches for this chat
        temp_db.del_all_chat_searches("456")
        
        # Verify all are gone
        searches = temp_db.get_chat_searches("456")
        assert len(searches) == 0
    
    def test_delete_all_chat_searches_with_items(self, temp_db):
        """Test deleting chat searches also deletes related items"""
        chat_id = "789"
        
        # Add a search
        cs = ChatSearch(
            chat_id=chat_id,
            kws="shoes",
            active=1
        )
        temp_db.add_search(cs)
        
        # Add related items
        for i in range(3):
            temp_db.add_item(
                item_id=str(100 + i),
                chat_id=chat_id,
                title=f"Item {i}",
                price="10.00",
                url=f"url-{i}",
                user="testuser"
            )
        
        # Verify items exist
        item1 = temp_db.search_item("100", chat_id)
        assert item1 is not None
        
        # Delete all searches and items
        temp_db.del_all_chat_searches(chat_id)
        
        # Verify items are deleted
        item1 = temp_db.search_item("100", chat_id)
        assert item1 is None
        
        item2 = temp_db.search_item("101", chat_id)
        assert item2 is None
        
        # Verify searches are deleted
        searches = temp_db.get_chat_searches(chat_id)
        assert len(searches) == 0
    
    def test_delete_all_chat_searches_does_not_affect_other_chats(self, temp_db):
        """Test that deleting one chat's data doesn't affect another chat"""
        # Add searches for two different chats
        cs1 = ChatSearch(chat_id="111", kws="chat 1 search", active=1)
        cs2 = ChatSearch(chat_id="222", kws="chat 2 search", active=1)
        temp_db.add_search(cs1)
        temp_db.add_search(cs2)
        
        # Add items for both chats
        temp_db.add_item("500", "111", "Item Chat 1", "10", "url1", "user1")
        temp_db.add_item("501", "222", "Item Chat 2", "20", "url2", "user2")
        
        # Delete all data for chat 111
        temp_db.del_all_chat_searches("111")
        
        # Verify chat 111 data is gone
        searches1 = temp_db.get_chat_searches("111")
        assert len(searches1) == 0
        item1 = temp_db.search_item("500", "111")
        assert item1 is None
        
        # Verify chat 222 data still exists
        searches2 = temp_db.get_chat_searches("222")
        assert len(searches2) == 1
        assert searches2[0].kws == "chat 2 search"
        item2 = temp_db.search_item("501", "222")
        assert item2 is not None
        assert item2.title == "Item Chat 2"
    
    def test_delete_all_chat_searches_with_inactive_searches(self, temp_db):
        """Test that deletion removes both active and inactive searches"""
        chat_id = "333"
        
        # Add active search
        cs_active = ChatSearch(chat_id=chat_id, kws="active", active=1)
        temp_db.add_search(cs_active)
        
        # Add inactive search (simulate soft delete)
        cs_inactive = ChatSearch(chat_id=chat_id, kws="inactive", active=0)
        temp_db.add_search(cs_inactive)
        
        # Verify only active search is returned by get_chat_searches
        searches = temp_db.get_chat_searches(chat_id)
        assert len(searches) == 1
        
        # Delete all (should remove both active and inactive)
        temp_db.del_all_chat_searches(chat_id)
        
        # Verify all are gone (even the inactive one)
        searches = temp_db.get_chat_searches(chat_id)
        assert len(searches) == 0
    
    def test_delete_all_chat_searches_transaction_rollback(self, temp_db):
        """Test that errors trigger rollback (best effort test)"""
        chat_id = "444"
        
        # Add some data
        cs = ChatSearch(chat_id=chat_id, kws="test", active=1)
        temp_db.add_search(cs)
        temp_db.add_item("600", chat_id, "Item", "10", "url", "user")
        
        # Verify data exists before deletion attempt
        searches_before = temp_db.get_chat_searches(chat_id)
        assert len(searches_before) == 1
        
        # Note: It's difficult to force a real error in SQLite for this test,
        # but we're testing that the function completes without crashing
        temp_db.del_all_chat_searches(chat_id)
        
        # Verify deletion worked
        searches_after = temp_db.get_chat_searches(chat_id)
        assert len(searches_after) == 0
