"""
Finance subcategories whitelist and matching logic for Product Hunt posts.
"""

FINANCE_SUBCATS = [
    "Accounting software",
    "Budgeting apps",
    "Credit score tools",
    "Financial planning",
    "Fundraising resources",
    "Investing",
    "Invoicing tools",
    "Money transfer",
    "Neobanks",
    "Online banking",
    "Payroll software",
    "Remote workforce tools",
    "Retirement planning",
    "Savings apps",
    "Startup financial planning",
    "Startup incorporation",
    "Stock trading platforms",
    "Tax preparation",
    "Treasury management platforms",
]

# Pre-normalized for matching against post topics
FINANCE_SUBCATS_NORM = {s.lower() for s in FINANCE_SUBCATS}


def topic_hits_finance_subcat(topics: list[str]) -> tuple[bool, list[str]]:
    """
    Return (hit, matched_subcats) where matched_subcats are the (case-insensitive) items
    from FINANCE_SUBCATS that appear in topics.
    
    Args:
        topics: List of topic strings from Product Hunt post
        
    Returns:
        Tuple of (bool, list[str]): (has_match, list_of_matched_subcategories)
    """
    if not topics:
        return (False, [])
    
    tset = {t.lower() for t in topics}
    matched = [s for s in FINANCE_SUBCATS if s.lower() in tset]
    return (len(matched) > 0, matched)
