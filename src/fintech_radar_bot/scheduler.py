"""
Scheduling module for the Fintech Radar Bot.
"""

import asyncio
from datetime import datetime, time
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from .config import config
from .bot import FintechRadarBot


class BotScheduler:
    """Handles scheduling of bot tasks."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.bot = FintechRadarBot()
        self._running = False
    
    async def start(self) -> None:
        """Start the scheduler and bot tasks."""
        try:
            # Validate configuration
            config.validate()
            
            # Test bot connection
            if not await self.bot.test_connection():
                raise Exception("Bot connection test failed")
            
            # Parse post time
            post_hour, post_minute = map(int, config.POST_TIME.split(':'))
            
            # Schedule daily post
            self.scheduler.add_job(
                func=self._daily_post_job,
                trigger=CronTrigger(
                    hour=post_hour,
                    minute=post_minute,
                    timezone=config.TIMEZONE
                ),
                id='daily_post',
                name='Daily Fintech Update',
                replace_existing=True
            )
            
            # Start scheduler
            self.scheduler.start()
            self._running = True
            
            logger.info(f"Scheduler started. Daily posts scheduled for {config.POST_TIME} {config.TIMEZONE}")
            
            # Send startup notification
            await self._send_startup_notification()
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        if self._running:
            self.scheduler.shutdown()
            self._running = False
            logger.info("Scheduler stopped")
    
    async def _daily_post_job(self) -> None:
        """Execute the daily post job."""
        logger.info("Executing daily post job...")
        
        try:
            success = await self.bot.post_daily_update()
            
            if success:
                logger.info("Daily post job completed successfully")
            else:
                logger.error("Daily post job failed")
                
        except Exception as e:
            logger.error(f"Error in daily post job: {e}")
    
    async def _send_startup_notification(self) -> None:
        """Send a notification when the bot starts up."""
        try:
            startup_message = (
                "🤖 <b>Fintech Radar Bot Started</b>\n\n"
                f"⏰ Daily updates scheduled for {config.POST_TIME} {config.TIMEZONE}\n"
                "📊 Monitoring fintech news, market updates, and regulatory changes\n\n"
                "✅ Bot is ready and running!"
            )
            
            await self.bot.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=startup_message,
                parse_mode='HTML'
            )
            
            logger.info("Startup notification sent")
            
        except Exception as e:
            logger.error(f"Failed to send startup notification: {e}")
    
    async def run_forever(self) -> None:
        """Run the scheduler indefinitely."""
        try:
            await self.start()
            
            # Keep the scheduler running
            while self._running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Unexpected error in scheduler: {e}")
        finally:
            await self.stop()
    
    def get_next_run_time(self) -> Optional[datetime]:
        """Get the next scheduled run time."""
        job = self.scheduler.get_job('daily_post')
        if job:
            return job.next_run_time
        return None
    
    def get_job_status(self) -> dict:
        """Get the status of scheduled jobs."""
        jobs = self.scheduler.get_jobs()
        return {
            'total_jobs': len(jobs),
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
                for job in jobs
            ]
        }
