"""
B2B/SMB/Fintech discovery module for finding relevant posts.
"""

import math
from datetime import datetime, timezone
from dateutil import parser
from typing import List, Dict


# B2B/SMB/Fintech focused constants
B2B_TOPICS = {
    "Fintech", "Payments", "B2B", "Banking", "Finance", "Accounting", 
    "HR", "Payroll", "DevTools", "APIs", "SaaS", "Small Business", "SMB"
}

B2B_KEYWORDS = [
    "b2b", "smb", "small business", "merchant", "pos", "erp", "saas", "api", "platform",
    "fintech", "payments", "invoice", "invoicing", "billing", "payroll", "benefits",
    "accounting", "tax", "kyc", "aml", "compliance", "lending", "credit", "issuing", "reconciliation"
]


def relevance_score(post: Dict) -> float:
    """
    Calculate relevance score for a B2B/SMB/Fintech post.
    
    Args:
        post: Product Hunt post dictionary
        
    Returns:
        float: Relevance score (higher = more relevant)
    """
    text = (post.get("name", "") + " " + post.get("tagline", "") + " " + post.get("description", "")).lower()
    topics = {t.lower() for t in (post.get("topics") or [])}
    votes = post.get("votesCount") or 0
    comments = post.get("commentsCount") or 0
    
    # Age penalty
    try:
        age_days = max(0.0, (datetime.now(timezone.utc) - parser.isoparse(post["createdAt"])).total_seconds() / 86400.0)
    except (ValueError, TypeError):
        age_days = 0.0
    
    # Score components
    score = 0.0
    
    # Topic matching (30 points)
    if topics & {t.lower() for t in B2B_TOPICS}:
        score += 30
    
    # Keyword matching (25 points)
    if any(k in text for k in B2B_KEYWORDS):
        score += 25
    
    # Engagement bonus
    score += 0.04 * votes + 0.1 * comments
    
    # Freshness decay (tau ≈ 5 days)
    score *= math.exp(-age_days / 5.0)
    
    return score


def pick_top_b2b(candidates: List[Dict], k: int = 1) -> List[Dict]:
    """
    Pick the top k B2B/SMB/Fintech posts from candidates.
    
    Args:
        candidates: List of Product Hunt post dictionaries
        k: Number of top posts to return (default: 1)
        
    Returns:
        List of top k relevant posts (empty if no relevant posts found)
    """
    if not candidates:
        return []
    
    # Score all candidates
    scored = [(relevance_score(p), p) for p in candidates]
    
    # Filter out posts with score <= 0
    scored = [x for x in scored if x[0] > 0]
    
    if not scored:
        return []
    
    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Return top k posts
    return [p for s, p in scored[:k]]


def deduplicate_posts(posts: List[Dict]) -> List[Dict]:
    """
    Remove duplicate posts by ID.
    
    Args:
        posts: List of Product Hunt post dictionaries
        
    Returns:
        List of unique posts (first occurrence kept)
    """
    seen_ids = set()
    unique_posts = []
    
    for post in posts:
        post_id = post.get("id")
        if post_id and post_id not in seen_ids:
            seen_ids.add(post_id)
            unique_posts.append(post)
    
    return unique_posts
