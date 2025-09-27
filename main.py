#!/usr/bin/env python3
"""
Main entry point for the Fintech Radar Bot.

This script starts the bot and runs the scheduler for daily updates.
Also supports CLI commands for Product Hunt integration.
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fintech_radar_bot.utils import setup_logging, ensure_directories, load_env_file, validate_environment
from fintech_radar_bot.config import config
from fintech_radar_bot.scheduler import BotScheduler
from fintech_radar_bot.bot import send_test_message, FintechRadarBot
from fintech_radar_bot.ph_client import create_ph_client


async def handle_slug_command(slug: str, dry_run: bool = False):
    """Handle --slug command to fetch and send a product by slug."""
    try:
        # Setup
        ensure_directories()
        setup_logging(config.LOG_LEVEL, config.LOG_FILE)
        load_env_file()
        
        # Create Product Hunt client
        ph_client = create_ph_client()
        
        # Fetch post by slug
        print(f"🔍 Fetching product by slug: {slug}")
        post = ph_client.get_post_by_slug(slug)
        
        if not post:
            print(f"❌ Post not found for slug: {slug}")
            return False
        
        print(f"✅ Found product: {post.get('name', 'Unknown')}")
        
        # Create bot and send article
        bot = FintechRadarBot()
        success = await bot.send_article_to_telegram(post, dry_run=dry_run)
        
        if success:
            print("✅ Article sent successfully!" if not dry_run else "✅ Article preview generated!")
        else:
            print("❌ Failed to send article")
        
        return success
        
    except ValueError as e:
        if "PRODUCTHUNT_TOKEN" in str(e):
            print("❌ Product Hunt token error. Please check your PRODUCTHUNT_TOKEN in .env file.")
        else:
            print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def handle_query_command(query: str, dry_run: bool = False):
    """Handle --query command to search and send top hit product."""
    try:
        # Setup
        ensure_directories()
        setup_logging(config.LOG_LEVEL, config.LOG_FILE)
        load_env_file()
        
        # Create Product Hunt client
        ph_client = create_ph_client()
        
        # Search for product
        print(f"🔍 Searching for: {query}")
        post = ph_client.search_post_tophit(query)
        
        if not post:
            print(f"❌ Post not found for query: {query}")
            return False
        
        print(f"✅ Found product: {post.get('name', 'Unknown')}")
        
        # Create bot and send article
        bot = FintechRadarBot()
        success = await bot.send_article_to_telegram(post, dry_run=dry_run)
        
        if success:
            print("✅ Article sent successfully!" if not dry_run else "✅ Article preview generated!")
        else:
            print("❌ Failed to send article")
        
        return success
        
    except ValueError as e:
        if "PRODUCTHUNT_TOKEN" in str(e):
            print("❌ Product Hunt token error. Please check your PRODUCTHUNT_TOKEN in .env file.")
        else:
            print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def run_bot():
    """Run the main bot scheduler."""
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


def print_usage():
    """Print usage information."""
    print("""
🧭 Fintech Radar Bot - Product Hunt Integration

Usage:
  python main.py                    # Run the bot scheduler
  python main.py --slug <slug>      # Fetch product by slug and send to Telegram
  python main.py --query <query>    # Search for product and send top hit to Telegram
  python main.py --dry-run          # Preview article without sending to Telegram

Examples:
  python main.py --slug gusto
  python main.py --query "fintech app"
  python main.py --slug gusto --dry-run

Environment Variables Required:
  TELEGRAM_BOT_TOKEN    - Your Telegram bot token
  TELEGRAM_CHAT_ID      - Your Telegram channel ID
  PRODUCTHUNT_TOKEN     - Your Product Hunt API token (for --slug/--query commands)
""")


async def main():
    """Main function to handle CLI arguments and run appropriate command."""
    parser = argparse.ArgumentParser(description="Fintech Radar Bot")
    parser.add_argument("--slug", help="Fetch product by slug and send to Telegram")
    parser.add_argument("--query", help="Search for product and send top hit to Telegram")
    parser.add_argument("--dry-run", action="store_true", help="Preview article without sending to Telegram")
    
    args = parser.parse_args()
    
    # Handle CLI commands
    if args.slug:
        success = await handle_slug_command(args.slug, args.dry_run)
        sys.exit(0 if success else 1)
    elif args.query:
        success = await handle_query_command(args.query, args.dry_run)
        sys.exit(0 if success else 1)
    elif args.dry_run:
        print("❌ --dry-run must be used with --slug or --query")
        print_usage()
        sys.exit(1)
    else:
        # No arguments provided, run the main bot
        await run_bot()


if __name__ == "__main__":
    asyncio.run(main())
