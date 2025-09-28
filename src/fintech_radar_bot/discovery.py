"""
B2B/SMB/Fintech discovery module for finding relevant posts.
"""

import math
from datetime import datetime, timezone
from dateutil import parser
from typing import List, Dict


# Strict B2B/SMB/Fintech keyword families (lowercase match)
FIN_CORE = {
    "fintech", "payments", "payment", "banking", "treasury", "merchant", "pos", 
    "reconciliation", "open banking", "embedded finance", "issuing", "settlement", 
    "remittance", "accounts", "iban", "ach", "sepa", "b2b", "smb", "sme", "small business"
}

LENDING = {
    "lending", "credit", "bnpl", "invoice financing", "factoring", "working capital"
}

PAYROLL = {
    "payroll", "salary", "salaries", "benefits", "tax", "withholding", "w2", 
    "w-2", "1099", "hr", "employee", "employees", "compensation", "paystub"
}

ACCOUNT = {
    "accounting", "bookkeeping", "invoicing", "invoice", "billing", "ar", "ap", 
    "ledger", "erp", "reporting"
}

# Business size keywords for additional scoring
BUSINESS_SIZE = {"b2b", "smb", "sme", "small business"}


def relevance_score(post: Dict) -> float:
    """
    Calculate relevance score for a B2B/SMB/Fintech post with strict filtering.
    Returns 0 if no keyword families match (no fallback to non-fintech/B2B).
    
    Args:
        post: Product Hunt post dictionary
        
    Returns:
        float: Relevance score (0 if not fintech/B2B relevant)
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
    
    # Strict scoring - start with 0
    score = 0.0
    
    # Check keyword families (all text + topics)
    all_text = text + " " + " ".join(topics)
    
    # Core fintech keywords (30 points)
    if any(k in all_text for k in FIN_CORE):
        score += 30
    
    # Lending keywords (20 points)
    if any(k in all_text for k in LENDING):
        score += 20
    
    # Payroll keywords (20 points)
    if any(k in all_text for k in PAYROLL):
        score += 20
    
    # Accounting keywords (18 points)
    if any(k in all_text for k in ACCOUNT):
        score += 18
    
    # Business size bonus (10 points)
    if any(k in all_text for k in BUSINESS_SIZE):
        score += 10
    
    # If no keyword families match, return 0 (no fallback)
    if score == 0:
        return 0.0
    
    # Engagement bonus (only if already relevant)
    score += 0.04 * votes + 0.08 * comments
    
    # Freshness decay (tau ≈ 5 days)
    score *= math.exp(-age_days / 5.0)
    
    return score


def debug_candidate(post: Dict) -> str:
    """
    Generate debug string for a candidate post.
    
    Args:
        post: Product Hunt post dictionary
        
    Returns:
        str: Debug string in format "[DBG] name=... score=... votes=... topics=..."
    """
    name = post.get("name", "Unknown")
    score = relevance_score(post)
    votes = post.get("votesCount", 0)
    topics = post.get("topics", [])[:4]  # First 4 topics
    topics_str = ", ".join(topics) if topics else "None"
    
    return f"[DBG] name={name} score={score:.2f} votes={votes} topics={topics_str}"


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
