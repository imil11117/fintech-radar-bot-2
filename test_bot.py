#!/usr/bin/env python3
"""
Test script for the Fintech Radar Bot.

This script can be used to test the bot functionality without running the scheduler.
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fintech_radar_bot.utils import setup_logging, ensure_directories, load_env_file, validate_environment
from fintech_radar_bot.config import config
from fintech_radar_bot.bot import FintechRadarBot


async def test_bot():
    """Test the bot functionality."""
    try:
        # Setup
        ensure_directories()
        setup_logging("DEBUG")
        
        # Load environment variables
        load_env_file()
        
        # Validate configuration
        if not validate_environment():
            print("❌ Configuration validation failed. Please check your environment variables.")
            return False
        
        print("🧪 Testing Fintech Radar Bot...")
        
        # Create bot instance
        bot = FintechRadarBot()
        
        # Test connection
        print("🔗 Testing bot connection...")
        if not await bot.test_connection():
            print("❌ Bot connection test failed")
            return False
        print("✅ Bot connection test passed")
        
        # Test data collection
        print("📊 Testing data collection...")
        data = await bot.data_collector.collect_daily_data()
        if not data:
            print("❌ Data collection test failed")
            return False
        print(f"✅ Data collection test passed - collected {len(data.get('news', []))} news items")
        
        # Test message formatting
        print("📝 Testing message formatting...")
        message = bot.message_formatter.format_daily_update(data)
        if not message:
            print("❌ Message formatting test failed")
            return False
        print("✅ Message formatting test passed")
        
        # Test sending message (optional)
        send_test = input("🤔 Do you want to send a test message to the channel? (y/N): ").lower().strip()
        if send_test == 'y':
            print("📤 Sending test message...")
            if await bot.send_test_message():
                print("✅ Test message sent successfully")
            else:
                print("❌ Failed to send test message")
        
        print("🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_bot())
    sys.exit(0 if success else 1)
