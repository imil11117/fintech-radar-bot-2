#!/usr/bin/env python3
"""
Main entry point for the Fintech Radar Bot.

This script starts the bot and runs the scheduler for daily updates.
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fintech_radar_bot.utils import setup_logging, ensure_directories, load_env_file, validate_environment
from fintech_radar_bot.config import config
from fintech_radar_bot.scheduler import BotScheduler
from fintech_radar_bot.bot import send_test_message


async def main():
    """Main function to run the bot."""
    try:
        # Setup
        ensure_directories()
        setup_logging(config.LOG_LEVEL, config.LOG_FILE)
        
        # Load environment variables
        load_env_file()
        
        # Validate configuration
        if not validate_environment():
            print("❌ Configuration validation failed. Please check your environment variables.")
            sys.exit(1)
        
        print("🚀 Starting Fintech Radar Bot...")
        
        # Send test message to verify bot is working
        print("📤 Sending test message...")
        await send_test_message()
        
        # Create and start scheduler
        scheduler = BotScheduler()
        await scheduler.run_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
