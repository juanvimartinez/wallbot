import pytest
import sys
from pathlib import Path
from unittest.mock import patch

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestSearchIntervalValidation:
    """Test suite for SEARCH_INTERVAL minimum value validation"""
    
    def test_search_interval_below_minimum(self):
        """Test that SEARCH_INTERVAL below 180 seconds is clamped to 180"""
        with patch.dict('os.environ', {'SEARCH_INTERVAL': '100'}):
            # Re-import to get fresh settings with mocked env var
            import importlib
            from src.wallbot.config import settings
            importlib.reload(settings)
            
            assert settings.SEARCH_INTERVAL == 180, \
                f"Expected 180, got {settings.SEARCH_INTERVAL}. Values below 180 should be clamped to 180."
    
    def test_search_interval_at_minimum(self):
        """Test that SEARCH_INTERVAL at exactly 180 seconds is accepted"""
        with patch.dict('os.environ', {'SEARCH_INTERVAL': '180'}):
            import importlib
            from src.wallbot.config import settings
            importlib.reload(settings)
            
            assert settings.SEARCH_INTERVAL == 180, \
                f"Expected 180, got {settings.SEARCH_INTERVAL}"
    
    def test_search_interval_above_minimum(self):
        """Test that SEARCH_INTERVAL above 180 seconds is preserved"""
        with patch.dict('os.environ', {'SEARCH_INTERVAL': '300'}):
            import importlib
            from src.wallbot.config import settings
            importlib.reload(settings)
            
            assert settings.SEARCH_INTERVAL == 300, \
                f"Expected 300, got {settings.SEARCH_INTERVAL}. Values above 180 should be preserved."
    
    def test_search_interval_very_low_value(self):
        """Test that very low SEARCH_INTERVAL values are clamped to 180"""
        with patch.dict('os.environ', {'SEARCH_INTERVAL': '1'}):
            import importlib
            from src.wallbot.config import settings
            importlib.reload(settings)
            
            assert settings.SEARCH_INTERVAL == 180, \
                f"Expected 180, got {settings.SEARCH_INTERVAL}. Even very low values should be clamped to 180."
    
    def test_search_interval_zero(self):
        """Test that SEARCH_INTERVAL of 0 is clamped to 180"""
        with patch.dict('os.environ', {'SEARCH_INTERVAL': '0'}):
            import importlib
            from src.wallbot.config import settings
            importlib.reload(settings)
            
            assert settings.SEARCH_INTERVAL == 180, \
                f"Expected 180, got {settings.SEARCH_INTERVAL}. Zero should be clamped to 180."
    
    def test_search_interval_default_value(self):
        """Test that default SEARCH_INTERVAL (300) is used when env var is not set"""
        with patch.dict('os.environ', {}, clear=True):
            # Ensure SEARCH_INTERVAL is not in environment
            import importlib
            from src.wallbot.config import settings
            importlib.reload(settings)
            
            assert settings.SEARCH_INTERVAL == 300, \
                f"Expected default 300, got {settings.SEARCH_INTERVAL}"
    
    def test_search_interval_high_value(self):
        """Test that high SEARCH_INTERVAL values are preserved"""
        with patch.dict('os.environ', {'SEARCH_INTERVAL': '3600'}):
            import importlib
            from src.wallbot.config import settings
            importlib.reload(settings)
            
            assert settings.SEARCH_INTERVAL == 3600, \
                f"Expected 3600, got {settings.SEARCH_INTERVAL}. High values should be preserved."
    
    def test_search_interval_just_below_minimum(self):
        """Test that SEARCH_INTERVAL just below 180 (179) is clamped to 180"""
        with patch.dict('os.environ', {'SEARCH_INTERVAL': '179'}):
            import importlib
            from src.wallbot.config import settings
            importlib.reload(settings)
            
            assert settings.SEARCH_INTERVAL == 180, \
                f"Expected 180, got {settings.SEARCH_INTERVAL}. 179 should be clamped to 180."
    
    def test_search_interval_just_above_minimum(self):
        """Test that SEARCH_INTERVAL just above 180 (181) is preserved"""
        with patch.dict('os.environ', {'SEARCH_INTERVAL': '181'}):
            import importlib
            from src.wallbot.config import settings
            importlib.reload(settings)
            
            assert settings.SEARCH_INTERVAL == 181, \
                f"Expected 181, got {settings.SEARCH_INTERVAL}. 181 should be preserved."


class TestOtherSettings:
    """Test suite for other settings to ensure they still work correctly"""
    
    def test_bot_token_setting(self):
        """Test that BOT_TOKEN is read correctly from environment"""
        with patch.dict('os.environ', {'BOT_TOKEN': 'test_token_123'}):
            import importlib
            from src.wallbot.config import settings
            importlib.reload(settings)
            
            assert settings.TOKEN == 'test_token_123', \
                "BOT_TOKEN should be read from environment"
    
    def test_bot_token_default(self):
        """Test BOT_TOKEN default value when not set"""
        with patch.dict('os.environ', {}, clear=True):
            import importlib
            from src.wallbot.config import settings
            importlib.reload(settings)
            
            assert settings.TOKEN == "Bot Token does not exist", \
                "BOT_TOKEN should have default value when not set"
    
    def test_cleanup_interval_constant(self):
        """Test that CLEANUP_INTERVAL is set to expected value"""
        from src.wallbot.config import settings
        
        assert settings.CLEANUP_INTERVAL == 86400, \
            "CLEANUP_INTERVAL should be 86400 seconds (24 hours)"
    
    def test_cleanup_retention_hours_constant(self):
        """Test that CLEANUP_RETENTION_HOURS is set to expected value"""
        from src.wallbot.config import settings
        
        assert settings.CLEANUP_RETENTION_HOURS == 168, \
            "CLEANUP_RETENTION_HOURS should be 168 hours (7 days)"
