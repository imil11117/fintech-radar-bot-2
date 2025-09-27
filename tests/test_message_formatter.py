"""
Tests for the message formatter module.
"""

import pytest
from datetime import datetime
from fintech_radar_bot.message_formatter import MessageFormatter


class TestMessageFormatter:
    """Test cases for MessageFormatter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = MessageFormatter()
        self.sample_data = {
            'timestamp': datetime.now().isoformat(),
            'news': [
                {
                    'title': 'Test News Article',
                    'summary': 'This is a test summary for the news article.',
                    'source': 'Test Source',
                    'url': 'https://example.com/news1',
                    'published_at': datetime.now().isoformat()
                }
            ],
            'market_updates': [
                {
                    'type': 'stock',
                    'symbol': 'TEST',
                    'name': 'Test Company',
                    'price': 100.50,
                    'change': 5.25,
                    'change_percent': 5.5
                }
            ],
            'funding_rounds': [
                {
                    'company': 'Test Startup',
                    'amount': 10000000,
                    'currency': 'USD',
                    'round_type': 'Series A',
                    'date': datetime.now().isoformat(),
                    'investors': ['Test VC']
                }
            ],
            'regulatory_updates': [
                {
                    'title': 'Test Regulation',
                    'authority': 'Test Authority',
                    'summary': 'This is a test regulatory update.',
                    'date': datetime.now().isoformat(),
                    'url': 'https://example.com/regulation1'
                }
            ]
        }
    
    def test_format_daily_update(self):
        """Test formatting of daily update message."""
        message = self.formatter.format_daily_update(self.sample_data)
        
        assert isinstance(message, str)
        assert len(message) > 0
        assert "Daily Fintech Radar" in message
        assert "Test News Article" in message
        assert "Test Company" in message
        assert "Test Startup" in message
        assert "Test Regulation" in message
    
    def test_format_news_only(self):
        """Test formatting of news-only message."""
        news = self.sample_data['news']
        message = self.formatter.format_news_only(news)
        
        assert isinstance(message, str)
        assert "Fintech News Update" in message
        assert "Test News Article" in message
        assert "https://example.com/news1" in message
    
    def test_format_news_only_empty(self):
        """Test formatting of news-only message with empty data."""
        message = self.formatter.format_news_only([])
        
        assert isinstance(message, str)
        assert "No news updates available" in message
    
    def test_format_market_summary(self):
        """Test formatting of market summary message."""
        market_data = self.sample_data['market_updates']
        message = self.formatter.format_market_summary(market_data)
        
        assert isinstance(message, str)
        assert "Market Summary" in message
        assert "Test Company" in message
        assert "100.50" in message
        assert "5.5" in message
    
    def test_format_market_summary_empty(self):
        """Test formatting of market summary with empty data."""
        message = self.formatter.format_market_summary([])
        
        assert isinstance(message, str)
        assert "No market data available" in message
    
    def test_format_currency(self):
        """Test currency formatting utility."""
        # Test billions
        assert self.formatter._format_currency(1500000000, "USD") == "$1.5B USD"
        
        # Test millions
        assert self.formatter._format_currency(50000000, "USD") == "$50.0M USD"
        
        # Test thousands
        assert self.formatter._format_currency(15000, "USD") == "$15.0K USD"
        
        # Test small amounts
        assert self.formatter._format_currency(500, "USD") == "$500 USD"
