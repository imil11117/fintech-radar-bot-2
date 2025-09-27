"""
Message formatting module for the Fintech Radar Bot.
"""

from typing import Dict, List, Tuple, Optional
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


def compose_article_ru(post: Dict) -> Tuple[str, List[Tuple[str, str]], Optional[str]]:
    """
    Compose a Russian article for a Product Hunt post.
    
    Args:
        post: Product Hunt post data dictionary
        
    Returns:
        Tuple of (article_text, buttons, photo_url)
        - article_text: Formatted Russian article
        - buttons: List of (text, url) tuples for inline keyboard
        - photo_url: URL of the thumbnail or first media image
    """
    # Extract basic information
    name = post.get("name", "Unknown Product")
    tagline = post.get("tagline", "")
    description = post.get("description", "")
    votes = post.get("votesCount", 0)
    comments = post.get("commentsCount", 0)
    website = post.get("website", "")
    url = post.get("url", "")
    created_at = post.get("createdAt", "")
    
    # Format creation date
    try:
        if created_at:
            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime("%Y-%m-%d")
        else:
            formatted_date = "Unknown"
    except:
        formatted_date = "Unknown"
    
    # Extract topics (flat list of strings)
    # Limit printed topics to 3-4
    topics = post.get("topics", [])
    if topics:
        topics_limited = topics[:4]  # Limit to 4 topics
        topics_joined = ", ".join(topics_limited)
    else:
        topics_joined = "Не указаны"
    
    # Extract makers (flat list of strings - maker names)
    makers = post.get("makers", [])
    makers_joined = ", ".join(makers) if makers else "Не указаны"
    
    # Create short description (first 200 characters)
    # If description is empty -> fallback to tagline
    if description:
        short_ru_description = description[:200] + "..." if len(description) > 200 else description
    elif tagline:
        short_ru_description = tagline
    else:
        short_ru_description = "Описание недоступно"
    
    # Extract features from description (simple approach - split by sentences)
    features = []
    if description:
        sentences = [s.strip() for s in description.split('.') if s.strip()]
        features = sentences[:3]  # Take first 3 sentences as features
    
    
    # Build the article
    article_parts = [
        "🧭 Fintech Radar — продукт дня",
        "",
        f"🏷️ {name} — {tagline}",
        f"Темы: {topics_joined}",
        "",
        "Что это:",
        short_ru_description,
        "",
        "Ключевые фичи:",
        f"1. {features[0] if len(features) > 0 else '-'}",
        f"2. {features[1] if len(features) > 1 else '-'}",
        f"3. {features[2] if len(features) > 2 else '-'}",
        "",
        "Почему важно:",
        "• (placeholder — will be generated by AI later)",
        "",
        "Соц. сигнал на Product Hunt:",
        f"👍 {votes:,}   💬 {comments:,}",
        f"🚀 Запуск: {formatted_date}",
        ""
    ]
    
    # If makers empty -> omit the makers line
    if makers:
        article_parts.append(f"Мейкеры: {makers_joined}")
    
    article_text = "\n".join(article_parts)
    
    # Build buttons
    buttons = []
    
    # Website button
    if website:
        buttons.append(("Website", website))
    
    # Product Hunt button
    if url:
        buttons.append(("Product Hunt", url))
    
    # Product links buttons (flat list of link objects)
    product_links = post.get("productLinks", [])
    for link in product_links:
        link_type = link.get("type", "")
        link_url = link.get("url", "")
        
        if link_type == "DOCS" and link_url:
            buttons.append(("Docs", link_url))
        elif link_type == "PRICING" and link_url:
            buttons.append(("Pricing", link_url))
    
    # Extract photo URL
    # Photo: prefer thumbnailUrl; else first media image; else send text only
    photo_url = None
    
    # Try thumbnail first (normalized as thumbnailUrl field)
    if post.get("thumbnailUrl"):
        photo_url = post["thumbnailUrl"]
    # Fallback to first media image (flat list of media objects)
    elif post.get("media"):
        for media in post["media"]:
            if media.get("type") == "image" and media.get("url"):
                photo_url = media["url"]
                break
    
    return article_text, buttons, photo_url
