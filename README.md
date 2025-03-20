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
1. After cloning, create a `.env` file in the project root with your API key:
```bash
echo "CMC_API_KEY=your_api_key_here" > .env
echo "API_RATE_LIMIT=30" >> .env
```

2. Install dependencies:
```bash
# First ensure pip is installed
python3 -m ensurepip --upgrade

# Then install requirements
python3 -m pip install -r requirements.txt
```

3. Run the script:
```bash
python3 crypto_report.py
```

Reports will be saved to `~/Desktop/CMC_report/`

## Troubleshooting
- If no reports are generated:
  - Verify your API key is correct in `.env`
  - Check that the output directory exists:
    ```bash
    ls ~/Desktop/CMC_report
    ```
  - Run with debug output:
    ```bash
    python3 crypto_report.py --debug
    ```

## Requirements
- Python 3.8+
- CoinMarketCap API key
- Required packages in requirements.txt
