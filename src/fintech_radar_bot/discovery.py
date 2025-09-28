"""
B2B/SMB/Fintech discovery module for finding relevant posts.
"""

import math
from datetime import datetime, timezone
from dateutil import parser
from typing import List, Dict


# Strict B2B/SMB/Fintech keyword families (lowercase match)
FIN_CORE = {
    "fintech", "payments", "payment", "payment processing", "banking", "treasury", "merchant", "pos", 
    "reconciliation", "open banking", "embedded finance", "issuing", "card issuing", "issuer processing", 
    "issuing processor", "settlement", "remittance", "accounts", "iban", "ach", "sepa", 
    "corporate card", "virtual card", "spend management", "expense management",
    "b2b", "smb", "sme", "small business"
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
BUSINESS_SIZE = {"b2b", "smb", "sme", "small business", "corporate"}

# Exclusion lists to avoid false positives
EXCLUDE_TOPICS = {"games", "gaming", "card games", "pokemon", "entertainment", "nft", "collectibles"}
EXCLUDE_WORDS = {"pokemon", "tcg", "trading card", "collectible", "gaming"}

# Finance phrases for co-occurrence gate
FINANCE_PHRASES = {
    "payments", "payment processing", "invoicing", "treasury", "open banking", "embedded finance",
    "issuing", "card issuing", "corporate card", "virtual card", "settlement", "remittance",
    "iban", "ach", "sepa", "invoice financing", "factoring", "payroll", "salary", "benefits",
    "accounting", "ledger", "tax"
}


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
    topics = [t.lower() for t in (post.get("topics") or [])]
    votes = post.get("votesCount") or 0
    comments = post.get("commentsCount") or 0
    
    # Age penalty
    try:
        age_days = max(0.0, (datetime.now(timezone.utc) - parser.isoparse(post["createdAt"])).total_seconds() / 86400.0)
    except (ValueError, TypeError):
        age_days = 0.0
    
    # EXCLUSION CHECKS - early return if excluded
    # Check for excluded words in name+tagline+description
    if any(excl in text for excl in EXCLUDE_WORDS):
        return 0.0
    
    # Check for excluded topics
    if any(t in EXCLUDE_TOPICS for t in topics):
        return 0.0
    
    # CO-OCCURRENCE FINANCE GATE
    # Require at least ONE of these conditions:
    # A) Contains a finance phrase
    # B) Has SMB/B2B context AND one of PAYROLL/LENDING/ACCOUNT hits
    all_text = text + " " + " ".join(topics)
    
    # Check A: Finance phrases
    has_finance_phrase = any(phrase in all_text for phrase in FINANCE_PHRASES)
    
    # Check B: SMB/B2B context + PAYROLL/LENDING/ACCOUNT
    has_business_context = any(k in all_text for k in BUSINESS_SIZE)
    has_payroll_lending_account = (
        any(k in all_text for k in PAYROLL) or
        any(k in all_text for k in LENDING) or
        any(k in all_text for k in ACCOUNT)
    )
    has_business_finance = has_business_context and has_payroll_lending_account
    
    # Finance gate: must have either A or B
    finance_gate = has_finance_phrase or has_business_finance
    
    if not finance_gate:
        return 0.0
    
    # Strict scoring - start with 0
    score = 0.0
    
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
    Generate debug string for a candidate post showing which rules fired.
    
    Args:
        post: Product Hunt post dictionary
        
    Returns:
        str: Debug string in format "[DBG] gate=... excl=... name=... topics=... score=..."
    """
    name = post.get("name", "Unknown")
    text = (post.get("name", "") + " " + post.get("tagline", "") + " " + post.get("description", "")).lower()
    topics = [t.lower() for t in (post.get("topics") or [])]
    all_text = text + " " + " ".join(topics)
    
    # Check exclusion
    excl_hit = any(excl in text for excl in EXCLUDE_WORDS) or any(t in EXCLUDE_TOPICS for t in topics)
    
    # Check finance gate
    has_finance_phrase = any(phrase in all_text for phrase in FINANCE_PHRASES)
    has_business_context = any(k in all_text for k in BUSINESS_SIZE)
    has_payroll_lending_account = (
        any(k in all_text for k in PAYROLL) or
        any(k in all_text for k in LENDING) or
        any(k in all_text for k in ACCOUNT)
    )
    has_business_finance = has_business_context and has_payroll_lending_account
    finance_gate = has_finance_phrase or has_business_finance
    
    score = relevance_score(post)
    topics_str = ", ".join(topics[:3]) if topics else "None"
    
    return f"[DBG] gate={finance_gate} excl={excl_hit} name={name} topics={topics_str} score={score:.2f}"


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
