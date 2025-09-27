"""
State management for tracking posted Product Hunt IDs to avoid duplicates.
"""

import json
import os
from pathlib import Path
from typing import Set
from loguru import logger


def load_posted_ids(path: str = ".state/posted_ids.json") -> Set[str]:
    """
    Load previously posted Product Hunt IDs from disk.
    
    Args:
        path: Path to the JSON file containing posted IDs
        
    Returns:
        Set of posted Product Hunt IDs
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        if not os.path.exists(path):
            logger.info(f"State file {path} doesn't exist, starting with empty set")
            return set()
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Handle both list and set formats for backward compatibility
        if isinstance(data, list):
            posted_ids = set(data)
        elif isinstance(data, dict) and 'posted_ids' in data:
            posted_ids = set(data['posted_ids'])
        else:
            posted_ids = set(data) if isinstance(data, (list, set)) else set()
            
        logger.info(f"Loaded {len(posted_ids)} posted IDs from {path}")
        return posted_ids
        
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Error loading posted IDs from {path}: {e}. Starting with empty set.")
        return set()


def save_posted_ids(ids: Set[str], path: str = ".state/posted_ids.json"):
    """
    Save posted IDs back to disk.
    
    Args:
        ids: Set of Product Hunt IDs to save
        path: Path to the JSON file to save to
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Convert set to list for JSON serialization
        data = {
            'posted_ids': list(ids),
            'last_updated': str(Path().cwd())  # Add timestamp for debugging
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved {len(ids)} posted IDs to {path}")
        
    except IOError as e:
        logger.error(f"Error saving posted IDs to {path}: {e}")
        raise


def add_posted_id(post_id: str, path: str = ".state/posted_ids.json"):
    """
    Add a new posted ID to the state file.
    
    Args:
        post_id: Product Hunt ID to add
        path: Path to the JSON file
    """
    posted_ids = load_posted_ids(path)
    posted_ids.add(post_id)
    save_posted_ids(posted_ids, path)
    logger.info(f"Added posted ID: {post_id}")


def is_posted(post_id: str, path: str = ".state/posted_ids.json") -> bool:
    """
    Check if a Product Hunt ID has already been posted.
    
    Args:
        post_id: Product Hunt ID to check
        path: Path to the JSON file
        
    Returns:
        True if the ID has been posted before, False otherwise
    """
    posted_ids = load_posted_ids(path)
    return post_id in posted_ids
