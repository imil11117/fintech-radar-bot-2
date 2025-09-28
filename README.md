# Fintech Radar Bot

A Telegram bot that posts daily fintech industry updates to a designated channel. The bot collects news, market updates, funding rounds, and regulatory changes to provide comprehensive daily summaries.

## Features

- 📰 **Daily News Updates**: Curated fintech news from multiple sources
- 📊 **Market Data**: Stock prices, cryptocurrency updates, and market trends
- 💰 **Funding Rounds**: Recent fintech funding announcements
- ⚖️ **Regulatory Updates**: Policy changes and regulatory news
- ⏰ **Automated Scheduling**: Configurable daily posting times
- 🔧 **Extensible Architecture**: Easy to add new data sources
- 🎯 **Product Hunt Integration**: Find and post fintech products from Product Hunt
- 💸 **Finance Subcategories**: Whitelisted finance topic filtering with round-robin selection

## Project Structure

```
fintech-radar-bot/
├── src/
│   └── fintech_radar_bot/
│       ├── __init__.py
│       ├── bot.py              # Main bot class
│       ├── config.py           # Configuration management
│       ├── data_collector.py   # Data collection logic
│       ├── message_formatter.py # Message formatting
│       ├── scheduler.py        # Task scheduling
│       ├── utils.py            # Utility functions
│       ├── ph_client.py        # Product Hunt API client
│       ├── discovery.py        # B2B/Fintech discovery logic
│       ├── finance_subcats.py  # Finance subcategories whitelist
│       └── state.py            # State management for deduplication
├── config/                     # Configuration files
├── tests/                      # Test files
├── docs/                       # Documentation
├── logs/                       # Log files
├── main.py                     # Main entry point
├── test_bot.py                 # Test script
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- A Telegram bot token (get one from [@BotFather](https://t.me/botfather))
- A Telegram channel where the bot will post updates
- A Product Hunt API token (optional, for Product Hunt integration)

### Setup

1. **Clone or create the project directory:**
   ```bash
   mkdir fintech-radar-bot
   cd fintech-radar-bot
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

5. **Set up your Telegram bot:**
   - Create a bot with [@BotFather](https://t.me/botfather)
   - Add the bot to your channel as an administrator
   - Get the channel ID (you can use [@userinfobot](https://t.me/userinfobot))

## Configuration

Create a `.env` file with the following variables:

```env
# Required
BOT_TOKEN=your_bot_token_here
CHANNEL_ID=@your_channel_username_or_channel_id

# Optional
POST_TIME=09:00
TIMEZONE=America/Mexico_City
LOG_LEVEL=INFO
MAX_ARTICLES_PER_UPDATE=5
PRODUCTHUNT_TOKEN=your_producthunt_token_here
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | Yes | - | Telegram bot token from @BotFather |
| `CHANNEL_ID` | Yes | - | Channel username or ID where bot posts |
| `POST_TIME` | No | 09:00 | Daily post time (24h format) |
| `TIMEZONE` | No | America/Mexico_City | Timezone for scheduling |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `API_BASE_URL` | No | - | Base URL for external APIs |
| `API_KEY` | No | - | API key for external services |
| `MAX_ARTICLES_PER_UPDATE` | No | 5 | Maximum articles per daily update |
| `PRODUCTHUNT_TOKEN` | No | - | Product Hunt API token for product discovery |

## Usage

### Running the Bot

1. **Test the bot first:**
   ```bash
   python test_bot.py
   ```

2. **Start the bot:**
   ```bash
   python main.py
   ```

The bot will:
- Start the scheduler
- Send a startup notification to the channel
- Post daily updates at the configured time
- Log all activities to the console and log files

### Testing

Run the test script to verify everything is working:

```bash
python test_bot.py
```

This will:
- Test bot connection
- Test data collection
- Test message formatting
- Optionally send a test message

### Product Hunt Integration

The bot supports several Product Hunt integration commands:

#### Basic Commands

1. **Fetch a specific product by slug:**
   ```bash
   python main.py --slug gusto
   ```

2. **Search for a product:**
   ```bash
   python main.py --query "fintech app"
   ```

3. **Find best fintech product from today:**
   ```bash
   python main.py --daily
   ```

#### Discovery Commands

4. **Discover B2B/SMB/Fintech posts (48h window):**
   ```bash
   python main.py --discover
   python main.py --discover --dry-run
   python main.py --discover --top 3
   python main.py --discover --since "2025-09-25T00:00:00Z" --limit 50 --debug
   ```

5. **Finance Subcategories Picker (NEW):**
   ```bash
   # Dry run for last 48h
   python main.py --finance-subcats --dry-run --debug
   
   # Wider time window
   python main.py --finance-subcats --since "2025-09-24T00:00:00Z" --limit 60 --dry-run --debug
   
   # Real post with round-robin selection
   python main.py --finance-subcats --choose rr
   
   # Random selection
   python main.py --finance-subcats --choose random
   ```

#### Command Options

- `--dry-run`: Preview article without sending to Telegram
- `--since ISO`: Override posted_after date (ISO format)
- `--limit N`: Total candidates cap (default 30/60)
- `--top N`: Number of posts to send (default 1)
- `--choose {random,rr}`: Selection strategy (default: rr)
- `--debug`: Show debug scoring information

#### Finance Subcategories

The finance subcategories picker uses a whitelist of 19 finance-related topics:

- Accounting software
- Budgeting apps
- Credit score tools
- Financial planning
- Fundraising resources
- Investing
- Invoicing tools
- Money transfer
- Neobanks
- Online banking
- Payroll software
- Remote workforce tools
- Retirement planning
- Savings apps
- Startup financial planning
- Startup incorporation
- Stock trading platforms
- Tax preparation
- Treasury management platforms

The picker supports two selection strategies:
- **Round-robin (default)**: Rotates through subcategories to ensure variety
- **Random**: Randomly selects from matching posts

## Development

### Adding New Data Sources

1. **Extend the DataCollector class:**
   ```python
   # In data_collector.py
   async def _collect_custom_data(self) -> List[Dict]:
       # Your custom data collection logic
       pass
   ```

2. **Update the message formatter:**
   ```python
   # In message_formatter.py
   def format_custom_section(self, data: List[Dict]) -> str:
       # Your custom formatting logic
       pass
   ```

### Adding New Message Types

1. **Create new formatter methods in MessageFormatter**
2. **Add corresponding collection methods in DataCollector**
3. **Update the main format_daily_update method**

### Customizing the Schedule

Modify the scheduler configuration in `scheduler.py`:

```python
# For multiple daily posts
self.scheduler.add_job(
    func=self._morning_update,
    trigger=CronTrigger(hour=9, minute=0),
    id='morning_update'
)

self.scheduler.add_job(
    func=self._evening_update,
    trigger=CronTrigger(hour=18, minute=0),
    id='evening_update'
)
```

## Logging

The bot uses structured logging with the following features:

- **Console output**: Colored, formatted logs
- **File logging**: Rotating log files with compression
- **Log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log retention**: 30 days with daily rotation

Log files are stored in the `logs/` directory.

## Troubleshooting

### Common Issues

1. **Bot token invalid:**
   - Verify the token with @BotFather
   - Ensure no extra spaces or characters

2. **Channel access denied:**
   - Add the bot to the channel as an administrator
   - Use the correct channel ID or username

3. **No data collected:**
   - Check internet connection
   - Verify API keys if using external services
   - Check log files for specific errors

4. **Scheduling issues:**
   - Verify timezone configuration
   - Check system time and date
   - Review scheduler logs

### Debug Mode

Run with debug logging to see detailed information:

```bash
LOG_LEVEL=DEBUG python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review log files
- Create an issue in the repository

## Roadmap

- [ ] Integration with real news APIs
- [ ] Web dashboard for configuration
- [ ] Multiple channel support
- [ ] Custom message templates
- [ ] Analytics and metrics
- [ ] Docker deployment
- [ ] CI/CD pipeline
