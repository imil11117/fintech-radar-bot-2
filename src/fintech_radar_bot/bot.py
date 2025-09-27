"""
Main bot class for the Fintech Radar Bot.
"""

import asyncio
from typing import Optional, Dict, List, Tuple
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from loguru import logger

from .config import config
from .data_collector import DataCollector, score_product, pick_best_fintech
from .message_formatter import MessageFormatter, compose_article_ru
from .state import load_posted_ids, add_posted_id, is_posted
from .ph_client import create_ph_client


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
    
    async def send_article_to_telegram(self, post: Dict, dry_run: bool = False) -> bool:
        """
        Send a Product Hunt article to Telegram.
        
        Args:
            post: Product Hunt post data dictionary
            dry_run: If True, only print the article without sending to Telegram
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Compose the article
            article_text, buttons, photo_url = compose_article_ru(post)
            
            if dry_run:
                print("=" * 50)
                print("DRY RUN - Article Preview:")
                print("=" * 50)
                print(article_text)
                print("\n" + "=" * 50)
                print("Buttons:")
                for button_text, button_url in buttons:
                    print(f"  {button_text}: {button_url}")
                print("=" * 50)
                if photo_url:
                    print(f"Photo URL: {photo_url}")
                return True
            
            # Create inline keyboard if buttons exist
            keyboard = None
            if buttons:
                keyboard_buttons = []
                for button_text, button_url in buttons:
                    keyboard_buttons.append([InlineKeyboardButton(button_text, url=button_url)])
                keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            # Send message with or without photo
            if photo_url:
                await self.bot.send_photo(
                    chat_id=config.CHANNEL_ID,
                    photo=photo_url,
                    caption=article_text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await self.bot.send_message(
                    chat_id=config.CHANNEL_ID,
                    text=article_text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
            logger.info("Product Hunt article sent successfully")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error while sending article: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending article: {e}")
            return False
    
    async def post_daily_fintech_pick(self, dry_run: bool = False) -> bool:
        """
        Pick the best fintech/B2B product from Product Hunt for the last 24h and post to Telegram.
        Avoid duplicates using state file.
        
        Args:
            dry_run: If True, only print the article without sending to Telegram
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from datetime import datetime, timedelta
            
            logger.info("Starting daily fintech pick...")
            
            # Create Product Hunt client
            ph_client = create_ph_client()
            
            # Get posts from last 24 hours
            posted_after = (datetime.now() - timedelta(hours=24)).isoformat() + "Z"
            logger.info(f"Fetching posts posted after: {posted_after}")
            
            recent_posts = ph_client.get_recent_posts(posted_after, limit=30)
            logger.info(f"Found {len(recent_posts)} recent posts")
            
            if not recent_posts:
                logger.warning("No recent posts found")
                return False
            
            # Pick the best fintech product
            best_product = pick_best_fintech(recent_posts)
            
            if not best_product:
                logger.info("No fintech-relevant products found in recent posts")
                return False
            
            product_id = best_product.get('id')
            if not product_id:
                logger.error("Product missing ID field")
                return False
            
            # Check if already posted
            if is_posted(product_id):
                logger.info(f"Product {product_id} already posted, skipping")
                return False
            
            logger.info(f"Selected product: {best_product.get('name', 'Unknown')} (score: {score_product(best_product)})")
            
            # Send to Telegram
            success = await self.send_article_to_telegram(best_product, dry_run=dry_run)
            
            if success and not dry_run:
                # Mark as posted
                add_posted_id(product_id)
                logger.info(f"Successfully posted and marked product {product_id} as posted")
            elif success and dry_run:
                logger.info("Dry run completed successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in daily fintech pick: {e}")
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
