"""
Utility functions for the Fintech Radar Bot.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from loguru import logger


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration for the bot.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True
    )
    
    # Add file logger if specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="1 day",
            retention="30 days",
            compression="zip"
        )


def ensure_directories() -> None:
    """Ensure all required directories exist."""
    directories = [
        "logs",
        "data",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def load_env_file(env_file: str = ".env") -> bool:
    """
    Load environment variables from a file.
    
    Args:
        env_file: Path to the environment file
        
    Returns:
        bool: True if file was loaded successfully, False otherwise
    """
    env_path = Path(env_file)
    
    if not env_path.exists():
        logger.warning(f"Environment file {env_file} not found")
        return False
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        
        logger.info(f"Environment variables loaded from {env_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error loading environment file {env_file}: {e}")
        return False


def validate_environment() -> bool:
    """
    Validate that all required environment variables are set.
    
    Returns:
        bool: True if all required variables are set, False otherwise
    """
    required_vars = [
        "BOT_TOKEN",
        "CHANNEL_ID"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path: Project root directory
    """
    return Path(__file__).parent.parent.parent


def format_number(num: float, precision: int = 2) -> str:
    """
    Format a number with appropriate suffixes (K, M, B).
    
    Args:
        num: Number to format
        precision: Decimal precision
        
    Returns:
        str: Formatted number string
    """
    if abs(num) >= 1_000_000_000:
        return f"{num / 1_000_000_000:.{precision}f}B"
    elif abs(num) >= 1_000_000:
        return f"{num / 1_000_000:.{precision}f}M"
    elif abs(num) >= 1_000:
        return f"{num / 1_000:.{precision}f}K"
    else:
        return f"{num:.{precision}f}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
