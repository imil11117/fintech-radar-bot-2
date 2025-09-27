"""
Message formatting module for the Fintech Radar Bot.
"""

from typing import Dict, List
from datetime import datetime


class MessageFormatter:
    """Formats collected data into Telegram messages."""
    
    def format_daily_update(self, data: Dict) -> str:
        """
        Format daily data into a comprehensive Telegram message.
        
        Args:
            data: Collected data dictionary
            
        Returns:
            str: Formatted message for Telegram
        """
        message_parts = []
        
        # Header
        message_parts.append("🚀 <b>Daily Fintech Radar</b>")
        message_parts.append(f"📅 {datetime.now().strftime('%B %d, %Y')}")
        message_parts.append("")
        
        # News section
        if data.get('news'):
            message_parts.append("📰 <b>Top Fintech News</b>")
            for i, article in enumerate(data['news'][:3], 1):
                message_parts.append(
                    f"{i}. <b>{article['title']}</b>\n"
                    f"   {article['summary'][:100]}...\n"
                    f"   📖 <a href='{article['url']}'>Read more</a>"
                )
            message_parts.append("")
        
        # Market updates section
        if data.get('market_updates'):
            message_parts.append("📊 <b>Market Updates</b>")
            for update in data['market_updates'][:3]:
                change_emoji = "📈" if update['change'] >= 0 else "📉"
                message_parts.append(
                    f"{change_emoji} <b>{update['name']} ({update['symbol']})</b>\n"
                    f"   ${update['price']:.2f} ({update['change_percent']:+.1f}%)"
                )
            message_parts.append("")
        
        # Funding rounds section
        if data.get('funding_rounds'):
            message_parts.append("💰 <b>Recent Funding</b>")
            for funding in data['funding_rounds'][:2]:
                amount_str = self._format_currency(funding['amount'], funding['currency'])
                message_parts.append(
                    f"🏢 <b>{funding['company']}</b>\n"
                    f"   {funding['round_type']}: {amount_str}"
                )
            message_parts.append("")
        
        # Regulatory updates section
        if data.get('regulatory_updates'):
            message_parts.append("⚖️ <b>Regulatory Updates</b>")
            for update in data['regulatory_updates'][:2]:
                message_parts.append(
                    f"📋 <b>{update['title']}</b>\n"
                    f"   {update['authority']}\n"
                    f"   {update['summary'][:80]}..."
                )
            message_parts.append("")
        
        # Footer
        message_parts.append("━━━━━━━━━━━━━━━━━━━━")
        message_parts.append("🤖 Powered by Fintech Radar Bot")
        message_parts.append("📱 Stay updated with the latest in fintech!")
        
        return "\n".join(message_parts)
    
    def format_news_only(self, news: List[Dict]) -> str:
        """
        Format only news articles into a message.
        
        Args:
            news: List of news articles
            
        Returns:
            str: Formatted news message
        """
        if not news:
            return "📰 No news updates available at this time."
        
        message_parts = ["📰 <b>Fintech News Update</b>", ""]
        
        for i, article in enumerate(news, 1):
            message_parts.append(
                f"{i}. <b>{article['title']}</b>\n"
                f"   {article['summary']}\n"
                f"   📖 <a href='{article['url']}'>Read more</a>\n"
            )
        
        return "\n".join(message_parts)
    
    def format_market_summary(self, market_data: List[Dict]) -> str:
        """
        Format market data into a summary message.
        
        Args:
            market_data: List of market updates
            
        Returns:
            str: Formatted market summary
        """
        if not market_data:
            return "📊 No market data available at this time."
        
        message_parts = ["📊 <b>Market Summary</b>", ""]
        
        for update in market_data:
            change_emoji = "📈" if update['change'] >= 0 else "📉"
            message_parts.append(
                f"{change_emoji} <b>{update['name']} ({update['symbol']})</b>\n"
                f"   ${update['price']:.2f} ({update['change_percent']:+.1f}%)"
            )
        
        return "\n".join(message_parts)
    
    def _format_currency(self, amount: float, currency: str) -> str:
        """
        Format currency amount for display.
        
        Args:
            amount: Amount to format
            currency: Currency code
            
        Returns:
            str: Formatted currency string
        """
        if amount >= 1_000_000_000:
            return f"${amount / 1_000_000_000:.1f}B {currency}"
        elif amount >= 1_000_000:
            return f"${amount / 1_000_000:.1f}M {currency}"
        elif amount >= 1_000:
            return f"${amount / 1_000:.1f}K {currency}"
        else:
            return f"${amount:.0f} {currency}"
