"""
Main bot class for the Fintech Radar Bot.
"""

import asyncio
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from loguru import logger

from .config import config
from .data_collector import DataCollector
from .message_formatter import MessageFormatter


class FintechRadarBot:
    """Main bot class for posting daily fintech updates."""
    
    def __init__(self):
        """Initialize the bot."""
        self.bot = Bot(token=config.BOT_TOKEN)
        self.data_collector = DataCollector()
        self.message_formatter = MessageFormatter()
        
    async def post_daily_update(self) -> bool:
        """
        Collect data and post daily update to the channel.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Starting daily update collection...")
            
            # Collect fintech data
            data = await self.data_collector.collect_daily_data()
            
            if not data:
                logger.warning("No data collected for daily update")
                return False
            
            # Format the message
            message = self.message_formatter.format_daily_update(data)
            
            # Post to channel
            await self.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info("Daily update posted successfully")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error while posting update: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while posting update: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Test the bot connection and channel access.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Test bot connection
            bot_info = await self.bot.get_me()
            logger.info(f"Bot connected successfully: @{bot_info.username}")
            
            # Test channel access
            chat_info = await self.bot.get_chat(config.CHANNEL_ID)
            logger.info(f"Channel access confirmed: {chat_info.title}")
            
            return True
            
        except TelegramError as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def send_test_message(self) -> bool:
        """
        Send a test message to verify everything is working.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            test_message = "Fintech Radar Bot is live 🚀"
            
            await self.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=test_message
            )
            
            logger.info("Test message sent successfully")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to send test message: {e}")
            return False


async def send_test_message():
    """
    Simple function to send a test message to the channel.
    This function can be called from main.py for testing.
    """
    try:
        bot = FintechRadarBot()
        success = await bot.send_test_message()
        if success:
            print("✅ Test message sent successfully!")
        else:
            print("❌ Failed to send test message")
        return success
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False
