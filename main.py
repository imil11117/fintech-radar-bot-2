#!/usr/bin/env python3
"""
Main entry point for the Fintech Radar Bot.

This script starts the bot and runs the scheduler for daily updates.
Also supports CLI commands for Product Hunt integration.
"""

import asyncio
import sys
import argparse
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fintech_radar_bot.utils import setup_logging, ensure_directories, load_env_file, validate_environment
from fintech_radar_bot.config import config
from fintech_radar_bot.scheduler import BotScheduler
from fintech_radar_bot.bot import send_test_message, FintechRadarBot
from fintech_radar_bot.ph_client import create_ph_client
from fintech_radar_bot.data_collector import pick_best_fintech, score_candidate
from fintech_radar_bot.state import load_posted_ids, add_posted_id
from fintech_radar_bot.discovery import pick_top_b2b, relevance_score, deduplicate_posts, debug_candidate, filter_finance_subcats, pick_random, pick_round_robin
from fintech_radar_bot.finance_subcats import FINANCE_SUBCATS


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


async def handle_daily_command(dry_run: bool = False, since: str = None, limit: int = 30):
    """Handle --daily command to find and post best fintech product of the day."""
    try:
        from datetime import datetime, timedelta
        import pytz
        
        # Setup
        ensure_directories()
        setup_logging(config.LOG_LEVEL, config.LOG_FILE)
        load_env_file()
        
        # Get timezone from environment (default: America/Mexico_City)
        timezone_str = os.getenv("TIMEZONE", "America/Mexico_City")
        try:
            tz = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            print(f"❌ Unknown timezone: {timezone_str}. Using UTC.")
            tz = pytz.UTC
        
        # Compute posted_after_iso (local midnight in TIMEZONE -> convert to UTC ISO)
        if since:
            posted_after_iso = since
            print(f"🔍 Using custom since date: {since}")
        else:
            # Get local midnight today
            now_local = datetime.now(tz)
            midnight_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
            # Convert to UTC
            midnight_utc = midnight_local.astimezone(pytz.UTC)
            posted_after_iso = midnight_utc.isoformat().replace('+00:00', 'Z')
            print(f"🔍 Fetching posts since local midnight: {posted_after_iso}")
        
        # Create Product Hunt client
        ph_client = create_ph_client()
        
        # Fetch posts
        print(f"📡 Fetching up to {limit} posts...")
        posts = ph_client.get_recent_posts(posted_after_iso, limit)
        print(f"✅ Found {len(posts)} recent posts")
        
        if not posts:
            print("❌ No recent posts found")
            return False
        
        # Pick best fintech product
        print("🎯 Scoring and selecting best fintech product...")
        best = pick_best_fintech(posts)
        
        if not best:
            print("❌ No fintech-relevant products found in recent posts")
            return False
        
        product_id = best.get("id")
        if not product_id:
            print("❌ Product missing ID field")
            return False
        
        # Check if already posted
        posted_ids = load_posted_ids()
        if product_id in posted_ids:
            print(f"⏭️  Product {product_id} already posted, skipping")
            return False
        
        # Log selection details
        score = score_candidate(best)
        print(f"🏆 Selected: {best.get('name', 'Unknown')}")
        print(f"   Score: {score:.1f}")
        print(f"   Votes: {best.get('votesCount', 0)}")
        print(f"   Website: {best.get('website', 'N/A')}")
        
        # Create bot and send article
        bot = FintechRadarBot()
        success = await bot.send_article_to_telegram(best, dry_run=dry_run)
        
        if success and not dry_run:
            # Mark as posted
            add_posted_id(product_id)
            print(f"✅ Successfully posted and marked product {product_id} as posted")
        elif success and dry_run:
            print("✅ Dry run completed successfully")
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


async def handle_discovery_command(dry_run: bool = False, since: str = None, limit: int = 60, 
                                 top: int = 1, debug: bool = False):
    """Handle --discover command to find and post best B2B/SMB/Fintech posts."""
    try:
        from datetime import datetime, timedelta
        import pytz
        
        # Setup
        ensure_directories()
        setup_logging(config.LOG_LEVEL, config.LOG_FILE)
        load_env_file()
        
        # Get timezone from environment (default: America/Mexico_City)
        timezone_str = os.getenv("TIMEZONE", "America/Mexico_City")
        try:
            tz = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            print(f"❌ Unknown timezone: {timezone_str}. Using UTC.")
            tz = pytz.UTC
        
        # Compute posted_after_iso
        if since:
            posted_after_iso = since
            print(f"🔍 Using custom since date: {since}")
        else:
            # Local midnight minus 48h (two-day window)
            now_local = datetime.now(tz)
            midnight_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
            two_days_ago = midnight_local - timedelta(days=2)
            # Convert to UTC
            two_days_ago_utc = two_days_ago.astimezone(pytz.UTC)
            posted_after_iso = two_days_ago_utc.isoformat().replace('+00:00', 'Z')
            print(f"🔍 Fetching posts since 48h ago: {posted_after_iso}")
        
        # Create Product Hunt client
        ph_client = create_ph_client()
        
        # Fetch posts from time window using paginated method
        print(f"📡 Fetching up to {limit} posts from time window (paginated)...")
        posts = ph_client.get_posts_since_paginated(posted_after_iso, limit=limit, page_size=20)
        print(f"✅ Found {len(posts)} posts from time window")
        
        if not posts:
            print("❌ No posts found")
            return False
        
        # Score and filter for B2B relevance with strict filtering
        print("🎯 Scoring posts for B2B/SMB/Fintech relevance (strict filtering)...")
        scored_posts = [(relevance_score(p), p) for p in posts]
        relevant_posts = [p for score, p in scored_posts if score > 0]
        
        print(f"📊 {len(relevant_posts)} posts scored > 0 (relevant)")
        
        if debug:
            print("\n🔍 Debug - All candidates:")
            for post in posts:
                print(f"  {debug_candidate(post)}")
        
        # Strict filtering - if no relevant posts, exit without posting anything
        if not relevant_posts:
            print("❌ No B2B/fintech candidates today.")
            return True  # Exit 0 - DO NOT post anything
        
        # Pick top N posts
        top_posts = pick_top_b2b(posts, k=top)
        
        if not top_posts:
            print("❌ No suitable B2B/SMB/fintech posts found")
            return True
        
        print(f"🏆 Selected top {len(top_posts)} B2B/SMB/Fintech posts:")
        for i, post in enumerate(top_posts, 1):
            score = relevance_score(post)
            print(f"  {i}. {post.get('name', 'Unknown')} (score: {score:.1f}, votes: {post.get('votesCount', 0)})")
        
        # Log which one was picked
        if top_posts:
            picked_post = top_posts[0]
            print(f"📌 Picked: {picked_post.get('name', 'Unknown')} (score: {relevance_score(picked_post):.1f})")
        
        # Check posted IDs and send posts
        posted_ids = load_posted_ids()
        bot = FintechRadarBot()
        sent_count = 0
        
        for post in top_posts:
            product_id = post.get("id")
            if not product_id:
                print(f"⚠️  Post missing ID, skipping: {post.get('name', 'Unknown')}")
                continue
            
            if product_id in posted_ids:
                print(f"⏭️  Post {product_id} already posted, skipping")
                continue
            
            # Send post
            if dry_run:
                print(f"\n📄 DRY RUN - Article for: {post.get('name', 'Unknown')}")
                success = await bot.send_article_to_telegram(post, dry_run=True)
                if success:
                    print("✅ Dry run successful - article text printed above")
            else:
                print(f"\n📤 Sending: {post.get('name', 'Unknown')}")
                success = await bot.send_article_to_telegram(post, dry_run=False)
                if success:
                    add_posted_id(product_id)
                    sent_count += 1
                    print(f"✅ Successfully posted and marked {product_id} as posted")
                else:
                    print(f"❌ Failed to send post {product_id}")
        
        if not dry_run:
            print(f"\n🎉 Successfully sent {sent_count} posts")
        
        # Final summary
        print(f"\n📊 Summary:")
        print(f"  Fetched: {len(posts)} posts")
        print(f"  Matched (>0 score): {len(relevant_posts)} posts")
        if top_posts:
            picked_name = top_posts[0].get('name', 'Unknown')
            print(f"  Picked: {picked_name}")
        print(f"  Posted: {sent_count} posts")
        
        return True
        
    except ValueError as e:
        if "PRODUCTHUNT_TOKEN" in str(e):
            print("❌ Product Hunt token error. Please check your PRODUCTHUNT_TOKEN in .env file.")
        else:
            print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def handle_finance_subcats_command(dry_run: bool = False, since: str = None, limit: int = 60, 
                                       choose: str = "rr", debug: bool = False):
    """Handle --finance-subcats command to find and post finance subcategory posts."""
    try:
        from datetime import datetime, timedelta
        import pytz
        
        # Setup
        ensure_directories()
        setup_logging(config.LOG_LEVEL, config.LOG_FILE)
        load_env_file()
        
        # Get timezone from environment (default: America/Mexico_City)
        timezone_str = os.getenv("TIMEZONE", "America/Mexico_City")
        try:
            tz = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            print(f"❌ Unknown timezone: {timezone_str}. Using UTC.")
            tz = pytz.UTC
        
        # Compute posted_after_iso (if --since given, use it; else local midnight minus 48h in TIMEZONE → convert to UTC ISO)
        if since:
            posted_after_iso = since
            print(f"🔍 Using custom since date: {since}")
        else:
            # Local midnight minus 48h (two-day window)
            now_local = datetime.now(tz)
            midnight_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
            two_days_ago = midnight_local - timedelta(days=2)
            # Convert to UTC
            two_days_ago_utc = two_days_ago.astimezone(pytz.UTC)
            posted_after_iso = two_days_ago_utc.isoformat().replace('+00:00', 'Z')
            print(f"🔍 Fetching posts since 48h ago: {posted_after_iso}")
        
        # Create Product Hunt client
        ph_client = create_ph_client()
        
        # Fetch posts from time window using paginated method
        print(f"📡 Fetching up to {limit} posts from time window (paginated)...")
        posts = ph_client.get_posts_since_paginated(posted_after_iso, limit=limit, page_size=20)
        print(f"✅ Found {len(posts)} posts from time window")
        
        if not posts:
            print("❌ No posts found")
            return False
        
        # Filter for finance subcategories
        print("🎯 Filtering posts for finance subcategories...")
        filtered = filter_finance_subcats(posts)
        print(f"📊 {len(filtered)} posts match finance subcategories")
        
        if debug:
            print("\n🔍 Debug - Finance subcategory candidates:")
            for p in filtered:
                topics_str = ", ".join(p.get("topics", [])[:5])
                matched_str = ", ".join(p.get("_matched_subcats", []))
                print(f"  [DBG] {p['name']} | topics={topics_str} | matched={matched_str}")
        
        # De-dup with posted_ids
        posted_ids = load_posted_ids()
        filtered = [p for p in filtered if p.get("id") not in posted_ids]
        print(f"📊 {len(filtered)} posts after de-duplication")
        
        if not filtered:
            print("No candidates in Finance subcategories for this window.")
            return True
        
        # Pick using selection strategy
        if choose == "rr":
            pick = pick_round_robin(filtered, subcat_order=FINANCE_SUBCATS)
        else:
            pick = pick_random(filtered)
        
        if not pick:
            print("No candidates in Finance subcategories for this window.")
            return True
        
        print(f"🏆 Selected: {pick.get('name', 'Unknown')}")
        print(f"   Matched subcategories: {', '.join(pick.get('_matched_subcats', []))}")
        print(f"   Votes: {pick.get('votesCount', 0)}")
        print(f"   Website: {pick.get('website', 'N/A')}")
        
        # Create bot and send article
        bot = FintechRadarBot()
        success = await bot.send_article_to_telegram(pick, dry_run=dry_run, mode="finance-subcats")
        
        if success and not dry_run:
            # Mark as posted
            add_posted_id(pick["id"])
            print(f"✅ Successfully posted and marked product {pick['id']} as posted")
        elif success and dry_run:
            print("✅ Dry run completed successfully")
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
  python main.py --daily            # Find and post best fintech product from today
  python main.py --discover         # Discover B2B/SMB/Fintech posts (48h window)
  python main.py --finance-subcats  # Finance subcategories picker (whitelisted topics)
  python main.py --since <ISO>      # Override posted_after date (ISO format)
  python main.py --limit <N>        # Total candidates cap (default 60)
  python main.py --top <N>          # Number of posts to send (default 1)
  python main.py --choose {random,rr} # Selection strategy: random or round-robin (default: rr)
  python main.py --debug            # Show debug scoring information
  python main.py --dry-run          # Preview article without sending to Telegram

Examples:
  python main.py --slug gusto
  python main.py --query "fintech app"
  python main.py --daily
  python main.py --discover
  python main.py --discover --dry-run
  python main.py --discover --top 3
  python main.py --discover --since "2025-09-25T00:00:00Z" --limit 50 --debug
  python main.py --daily --dry-run
  python main.py --finance-subcats --dry-run --debug
  python main.py --finance-subcats --since "2025-09-24T00:00:00Z" --limit 60 --dry-run --debug
  python main.py --finance-subcats --choose rr

Environment Variables Required:
  TELEGRAM_BOT_TOKEN    - Your Telegram bot token
  TELEGRAM_CHAT_ID      - Your Telegram channel ID
  PRODUCTHUNT_TOKEN     - Your Product Hunt API token
  TIMEZONE              - Your timezone (default: America/Mexico_City)
""")


async def main():
    """Main function to handle CLI arguments and run appropriate command."""
    parser = argparse.ArgumentParser(description="Fintech Radar Bot")
    parser.add_argument("--slug", help="Fetch product by slug and send to Telegram")
    parser.add_argument("--query", help="Search for product and send top hit to Telegram")
    parser.add_argument("--daily", action="store_true", help="Find and post best fintech product from today")
    parser.add_argument("--discover", action="store_true", help="Discover B2B/SMB/Fintech posts (48h window)")
    parser.add_argument("--finance-subcats", action="store_true", help="Finance subcategories picker (whitelisted topics)")
    parser.add_argument("--since", help="Override posted_after date (ISO format)")
    parser.add_argument("--limit", type=int, default=30, help="Override fetch limit (default 30/60)")
    parser.add_argument("--top", type=int, default=1, help="Number of posts to send (default 1)")
    parser.add_argument("--choose", choices=["random", "rr"], default="rr", help="Selection strategy: random or round-robin (default: rr)")
    parser.add_argument("--debug", action="store_true", help="Show debug scoring information")
    parser.add_argument("--dry-run", action="store_true", help="Preview article without sending to Telegram")
    
    args = parser.parse_args()
    
    # Handle CLI commands
    if args.slug:
        success = await handle_slug_command(args.slug, args.dry_run)
        sys.exit(0 if success else 1)
    elif args.query and not args.discover:
        success = await handle_query_command(args.query, args.dry_run)
        sys.exit(0 if success else 1)
    elif args.daily or (args.since and not args.discover):
        success = await handle_daily_command(args.dry_run, args.since, args.limit)
        sys.exit(0 if success else 1)
    elif args.discover:
        # For discovery mode, use higher default limit
        limit = args.limit if args.limit != 30 else 60
        success = await handle_discovery_command(
            dry_run=args.dry_run,
            since=args.since,
            limit=limit,
            top=args.top,
            debug=args.debug
        )
        sys.exit(0 if success else 1)
    elif args.finance_subcats:
        # For finance subcats mode, use higher default limit
        limit = args.limit if args.limit != 30 else 60
        success = await handle_finance_subcats_command(
            dry_run=args.dry_run,
            since=args.since,
            limit=limit,
            choose=args.choose,
            debug=args.debug
        )
        sys.exit(0 if success else 1)
    elif args.dry_run:
        print("❌ --dry-run must be used with --slug, --query, --daily, --discover, --finance-subcats, or --since")
        print_usage()
        sys.exit(1)
    else:
        # No arguments provided, run the main bot
        await run_bot()


if __name__ == "__main__":
    asyncio.run(main())
