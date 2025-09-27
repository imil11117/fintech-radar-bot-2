"""
Data collection module for fintech news and updates.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from loguru import logger

from .config import config


class DataCollector:
    """Collects fintech-related data from various sources."""
    
    def __init__(self):
        """Initialize the data collector."""
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def collect_daily_data(self) -> Dict:
        """
        Collect daily fintech data from various sources.
        
        Returns:
            Dict: Collected data including news, market updates, etc.
        """
        data = {
            'timestamp': datetime.now().isoformat(),
            'news': [],
            'market_updates': [],
            'funding_rounds': [],
            'regulatory_updates': []
        }
        
        try:
            # Collect news articles
            data['news'] = await self._collect_news()
            
            # Collect market updates
            data['market_updates'] = await self._collect_market_updates()
            
            # Collect funding information
            data['funding_rounds'] = await self._collect_funding_rounds()
            
            # Collect regulatory updates
            data['regulatory_updates'] = await self._collect_regulatory_updates()
            
            logger.info(f"Collected {len(data['news'])} news articles, "
                       f"{len(data['market_updates'])} market updates, "
                       f"{len(data['funding_rounds'])} funding rounds, "
                       f"{len(data['regulatory_updates'])} regulatory updates")
            
        except Exception as e:
            logger.error(f"Error collecting daily data: {e}")
        
        return data
    
    async def _collect_news(self) -> List[Dict]:
        """
        Collect fintech news articles.
        
        Returns:
            List[Dict]: List of news articles
        """
        # This is a placeholder implementation
        # In a real implementation, you would integrate with news APIs
        # like NewsAPI, RSS feeds, or web scraping
        
        news = [
            {
                'title': 'Fintech Innovation Drives Digital Banking Growth',
                'summary': 'Latest trends in digital banking and fintech adoption...',
                'source': 'Fintech News',
                'url': 'https://example.com/news1',
                'published_at': datetime.now().isoformat()
            },
            {
                'title': 'Cryptocurrency Regulations Update',
                'summary': 'New regulatory framework for digital assets...',
                'source': 'Crypto Weekly',
                'url': 'https://example.com/news2',
                'published_at': datetime.now().isoformat()
            }
        ]
        
        return news[:config.MAX_ARTICLES_PER_UPDATE]
    
    async def _collect_market_updates(self) -> List[Dict]:
        """
        Collect market updates and financial data.
        
        Returns:
            List[Dict]: List of market updates
        """
        # Placeholder for market data collection
        # In a real implementation, you would integrate with financial APIs
        # like Alpha Vantage, Yahoo Finance, or cryptocurrency APIs
        
        market_updates = [
            {
                'type': 'stock',
                'symbol': 'SQ',
                'name': 'Square Inc.',
                'price': 45.67,
                'change': 2.34,
                'change_percent': 5.4
            },
            {
                'type': 'crypto',
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'price': 43250.00,
                'change': -1250.00,
                'change_percent': -2.8
            }
        ]
        
        return market_updates
    
    async def _collect_funding_rounds(self) -> List[Dict]:
        """
        Collect recent fintech funding rounds.
        
        Returns:
            List[Dict]: List of funding rounds
        """
        # Placeholder for funding data collection
        # In a real implementation, you would integrate with APIs like
        # Crunchbase, PitchBook, or web scraping
        
        funding_rounds = [
            {
                'company': 'Fintech Startup A',
                'amount': 50000000,
                'currency': 'USD',
                'round_type': 'Series B',
                'date': (datetime.now() - timedelta(days=1)).isoformat(),
                'investors': ['VC Fund 1', 'VC Fund 2']
            }
        ]
        
        return funding_rounds
    
    async def _collect_regulatory_updates(self) -> List[Dict]:
        """
        Collect regulatory updates and policy changes.
        
        Returns:
            List[Dict]: List of regulatory updates
        """
        # Placeholder for regulatory data collection
        # In a real implementation, you would monitor government websites,
        # regulatory body announcements, or specialized APIs
        
        regulatory_updates = [
            {
                'title': 'New Digital Asset Framework Released',
                'authority': 'Financial Services Authority',
                'summary': 'Updated guidelines for digital asset management...',
                'date': datetime.now().isoformat(),
                'url': 'https://example.com/regulation1'
            }
        ]
        
        return regulatory_updates


# Fintech/B2B/SMB scoring constants
FIN_TOPICS = {
    "Fintech", "Payments", "B2B", "Banking", "Finance", "Accounting", 
    "HR", "Payroll", "SMB", "Small Business"
}

FIN_KEYWORDS = [
    "fintech", "payments", "b2b", "banking", "card", "cards", "issuing", 
    "payroll", "benefits", "invoice", "invoicing", "payout", "kyc", "aml", 
    "compliance", "tax", "erp", "lending", "smb", "small business", 
    "merchant", "pos", "accounting", "finance", "api"
]


def score_candidate(post: dict) -> float:
    """
    Score a Product Hunt post for fintech/B2B/SMB relevance.
    
    Args:
        post: Product Hunt post dictionary
        
    Returns:
        float: Score indicating relevance (higher = more relevant)
    """
    text = f"{post.get('name','')} {post.get('tagline','')} {post.get('description','')}".lower()
    topics = {t.lower() for t in (post.get('topics') or [])}
    score = 0.0
    
    # Topic matching (30 points)
    if topics & {t.lower() for t in FIN_TOPICS}:
        score += 30
    
    # Keyword matching (20 points)
    if any(k in text for k in FIN_KEYWORDS):
        score += 20
    
    # Vote count bonus (0.05 per vote)
    score += 0.05 * (post.get('votesCount') or 0)
    
    return score


def pick_best_fintech(candidates: list[dict]) -> Optional[dict]:
    """
    Pick the best fintech/B2B/SMB product from candidates.
    
    Args:
        candidates: List of Product Hunt post dictionaries
        
    Returns:
        dict: Best fintech product or None if no relevant products found
    """
    scored = [(score_candidate(p), p) for p in candidates]
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[0][1] if scored and scored[0][0] > 0 else None
    return top


def score_product(product: dict) -> int:
    """
    Returns a score indicating how relevant this product is for fintech/B2B audience.
    Higher score = more relevant.
    
    Args:
        product: Product Hunt post data dictionary
        
    Returns:
        int: Score from 0 to N (0 means not relevant)
    """
    # Keywords to look for in product data
    fintech_keywords = [
        "fintech", "payments", "banking", "b2b", "smb", "finance", "api", 
        "payroll", "invoicing", "accounting", "business", "card", "cards",
        "issuing", "benefits", "payout", "kyc", "aml", "compliance", "tax",
        "small business", "merchant", "pos", "p2p", "lending", "crypto",
        "blockchain", "trading", "investment", "wealth", "insurance"
    ]
    
    score = 0
    
    # Get text content to search in
    name = product.get('name', '').lower()
    tagline = product.get('tagline', '').lower()
    description = product.get('description', '').lower()
    topics = [topic.lower() for topic in product.get('topics', [])]
    
    # Combine all text for keyword search
    all_text = f"{name} {tagline} {description} {' '.join(topics)}"
    
    # Check for keywords
    for keyword in fintech_keywords:
        if keyword in all_text:
            score += 1
    
    return score


def pick_best_fintech(candidates: list[dict]) -> Optional[dict]:
    """
    Sort candidates by score descending and return the top one.
    Ignore candidates with score = 0.
    
    Args:
        candidates: List of Product Hunt post dictionaries
        
    Returns:
        dict: Best fintech product or None if no relevant products found
    """
    if not candidates:
        return None
    
    # Score all candidates
    scored_candidates = []
    for candidate in candidates:
        score = score_product(candidate)
        if score > 0:  # Only include products with positive scores
            scored_candidates.append((score, candidate))
    
    if not scored_candidates:
        return None
    
    # Sort by score descending, then by votes count as tiebreaker
    scored_candidates.sort(
        key=lambda x: (x[0], x[1].get('votesCount', 0)), 
        reverse=True
    )
    
    return scored_candidates[0][1]
