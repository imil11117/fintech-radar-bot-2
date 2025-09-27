# API Documentation

## Overview

The Fintech Radar Bot is designed with a modular architecture that makes it easy to extend and customize. This document describes the main components and their APIs.

## Core Components

### Bot Class (`bot.py`)

The main bot class that handles Telegram interactions and coordinates other components.

#### Methods

- `__init__()`: Initialize the bot with configuration
- `post_daily_update()`: Collect data and post daily update to channel
- `test_connection()`: Test bot connection and channel access
- `send_test_message()`: Send a test message to verify functionality

### Data Collector (`data_collector.py`)

Responsible for collecting fintech-related data from various sources.

#### Methods

- `collect_daily_data()`: Main method to collect all daily data
- `_collect_news()`: Collect news articles
- `_collect_market_updates()`: Collect market data
- `_collect_funding_rounds()`: Collect funding information
- `_collect_regulatory_updates()`: Collect regulatory news

### Message Formatter (`message_formatter.py`)

Formats collected data into Telegram-friendly messages.

#### Methods

- `format_daily_update(data)`: Format complete daily update
- `format_news_only(news)`: Format news-only message
- `format_market_summary(market_data)`: Format market data
- `_format_currency(amount, currency)`: Format currency amounts

### Scheduler (`scheduler.py`)

Handles task scheduling and bot lifecycle management.

#### Methods

- `start()`: Start the scheduler and bot tasks
- `stop()`: Stop the scheduler
- `run_forever()`: Run the scheduler indefinitely
- `get_next_run_time()`: Get next scheduled run time
- `get_job_status()`: Get status of scheduled jobs

### Configuration (`config.py`)

Manages application configuration and environment variables.

#### Properties

- `BOT_TOKEN`: Telegram bot token
- `CHANNEL_ID`: Target channel ID
- `POST_TIME`: Daily post time
- `TIMEZONE`: Timezone for scheduling
- `LOG_LEVEL`: Logging level
- `MAX_ARTICLES_PER_UPDATE`: Maximum articles per update

#### Methods

- `validate()`: Validate required configuration

### Utilities (`utils.py`)

Common utility functions for the application.

#### Functions

- `setup_logging(log_level, log_file)`: Configure logging
- `ensure_directories()`: Create required directories
- `load_env_file(env_file)`: Load environment variables
- `validate_environment()`: Validate environment setup
- `format_number(num, precision)`: Format numbers with suffixes
- `truncate_text(text, max_length, suffix)`: Truncate text

## Data Structures

### News Article

```python
{
    'title': str,           # Article title
    'summary': str,         # Article summary
    'source': str,          # News source
    'url': str,             # Article URL
    'published_at': str     # ISO timestamp
}
```

### Market Update

```python
{
    'type': str,            # 'stock', 'crypto', etc.
    'symbol': str,          # Trading symbol
    'name': str,            # Company/asset name
    'price': float,         # Current price
    'change': float,        # Price change
    'change_percent': float # Percentage change
}
```

### Funding Round

```python
{
    'company': str,         # Company name
    'amount': float,        # Funding amount
    'currency': str,        # Currency code
    'round_type': str,      # Series A, B, etc.
    'date': str,            # ISO timestamp
    'investors': List[str]  # List of investors
}
```

### Regulatory Update

```python
{
    'title': str,           # Update title
    'authority': str,       # Regulatory authority
    'summary': str,         # Update summary
    'date': str,            # ISO timestamp
    'url': str              # Reference URL
}
```

## Extending the Bot

### Adding New Data Sources

1. Create a new collection method in `DataCollector`
2. Add the method to `collect_daily_data()`
3. Update the data structure if needed
4. Add formatting logic in `MessageFormatter`

### Adding New Message Types

1. Create a new formatter method in `MessageFormatter`
2. Add corresponding collection logic
3. Update the main formatting method
4. Test with the test script

### Custom Scheduling

1. Modify the scheduler configuration in `scheduler.py`
2. Add new job methods
3. Update the job registration
4. Test scheduling behavior

## Error Handling

The bot includes comprehensive error handling:

- **Telegram Errors**: Caught and logged, don't crash the bot
- **Data Collection Errors**: Logged, bot continues with available data
- **Configuration Errors**: Validated at startup, bot won't start if invalid
- **Network Errors**: Retried automatically where possible

## Logging

All components use structured logging with:

- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Format**: Timestamp, level, component, message
- **Output**: Console (colored) and file (rotating)
- **Context**: Function names, line numbers, error details

## Testing

The bot includes a comprehensive test suite:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end functionality
- **Test Script**: Manual testing and verification
- **Mock Data**: Sample data for testing

Run tests with:

```bash
python -m pytest tests/
python test_bot.py
```
