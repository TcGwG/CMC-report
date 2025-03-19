# Cryptocurrency Report Generator

This Python script automatically scrapes cryptocurrency data from CoinMarketCap to generate weekly reports based on specific token price movements and rankings.

## Features
- Retrieves price data for predefined token lists
- Tracks 7-day, 30-day, 90-day, and 1-year percentage price changes
- Generates reports in JSON and CSV formats
- Identifies top 5 best/worst performing tokens in top 100

## Setup
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with your CoinMarketCap API key:
```
CMC_API_KEY=your_api_key_here
API_RATE_LIMIT=30
```

## Usage
Run the script:
```bash
python3 crypto_report.py
```

Reports will be saved to `~/Desktop/CMC_report/`

## Requirements
- Python 3.8+
- CoinMarketCap API key
- Required packages in requirements.txt
