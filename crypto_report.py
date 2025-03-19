import requests
import json
import os
import time
import csv
import random
from datetime import datetime
from dotenv import load_dotenv

class CryptoReport:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency"
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        self.output_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'CMC report')
        self.rate_limit = int(os.getenv('API_RATE_LIMIT', 30))
        self.last_request_time = 0
        os.makedirs(self.output_dir, exist_ok=True)

    def _rate_limit_check(self):
        """Ensure we respect API rate limits"""
        current_time = time.time()
        if current_time - self.last_request_time < 60/self.rate_limit:
            time.sleep(60/self.rate_limit - (current_time - self.last_request_time))
        self.last_request_time = time.time()

    def _make_api_request(self, url, params):
        """Make API request with retry logic and exponential backoff"""
        max_retries = 5
        base_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                self._rate_limit_check()
                response = requests.get(url, headers=self.headers, params=params)
                
                # Check for specific API errors
                if response.status_code == 401:
                    error_msg = response.json().get('status', {}).get('error_message', 'Unauthorized')
                    print(f"API Error: {error_msg}")
                    if "Invalid API key" in error_msg:
                        raise ValueError("Invalid API key - please check your .env file")
                    return None
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"API request failed (attempt {attempt + 1}/{max_retries}), retrying in {delay:.1f} seconds...")
                time.sleep(delay)

    def get_token_data(self, symbols):
        """Get data for specific tokens by their symbols"""
        url = f"{self.base_url}/quotes/latest"
        params = {
            'symbol': ','.join(symbols),
            'convert': 'USD'
        }
        
        try:
            response = self._make_api_request(url, params)
            data = response.json()['data']
            return [{
                'symbol': token['symbol'],
                'name': token['name'],
                'rank': token['cmc_rank'],
                'price': token['quote']['USD']['price'],
                '7d_change': token['quote']['USD']['percent_change_7d'],
                '30d_change': token['quote']['USD']['percent_change_30d'],
                '90d_change': token['quote']['USD']['percent_change_90d'],
                '1y_change': token['quote']['USD'].get('percent_change_1y', None)
            } for token in data.values()]
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {str(e)}")
            return None
        except KeyError as e:
            print(f"Invalid API response format: {str(e)}")
            return None

    def get_top_performers(self, limit=100, top=5):
        """Get best and worst performing tokens in top 100"""
        url = f"{self.base_url}/listings/latest"
        params = {
            'start': 1,
            'limit': limit,
            'convert': 'USD',
            'sort': 'market_cap',
            'sort_dir': 'desc'
        }
        
        try:
            response = self._make_api_request(url, params)
            if response is None:
                return None
                
            data = response.json()['data']
            
            # Get top 100 by market cap
            top_100 = sorted(data[:100], key=lambda x: x['cmc_rank'])
            
            # Sort by 7d performance
            sorted_by_performance = sorted(
                top_100,
                key=lambda x: x['quote']['USD']['percent_change_7d'],
                reverse=True
            )
            
            # Get best performers
            best = [{
                'symbol': token['symbol'],
                'name': token['name'],
                'rank': token['cmc_rank'],
                'price': token['quote']['USD']['price'],
                '7d_change': token['quote']['USD']['percent_change_7d'],
                '30d_change': token['quote']['USD']['percent_change_30d'],
                '90d_change': token['quote']['USD']['percent_change_90d']
            } for token in sorted_by_performance[:top]]
            
            # Get worst performers
            worst = [{
                'symbol': token['symbol'],
                'name': token['name'],
                'rank': token['cmc_rank'],
                'price': token['quote']['USD']['price'],
                '7d_change': token['quote']['USD']['percent_change_7d'],
                '30d_change': token['quote']['USD']['percent_change_30d'],
                '90d_change': token['quote']['USD']['percent_change_90d']
            } for token in sorted_by_performance[-top:]]
            
            return {'best': best, 'worst': worst}
            
        except Exception as e:
            print(f"Error getting top performers: {str(e)}")
            return None

    def save_csv(self, data, filename):
        """Save data as CSV file"""
        report_path = os.path.join(self.output_dir, filename)
        try:
            with open(report_path, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['Symbol', 'Name', 'Rank', 'Price', '7d Change', '30d Change', '90d Change'])
                # Write data
                for token in data:
                    writer.writerow([
                        token['symbol'],
                        token['name'],
                        token['rank'],
                        token['price'],
                        token['7d_change'],
                        token['30d_change'],
                        token['90d_change']
                    ])
            return True
        except Exception as e:
            print(f"Failed to save CSV: {str(e)}")
            return False

    def save_report(self, data, filename):
        """Save report data to file"""
        report_path = os.path.join(self.output_dir, filename)
        try:
            with open(report_path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Failed to save report: {str(e)}")
            return False

    def generate_report(self):
        """Generate comprehensive weekly report"""
        # Define token lists
        top_tokens = ['BTC', 'ETH', 'XRP', 'BNB', 'SOL']
        meme_tokens = ['DOGE', 'PEPE', 'WIF', 'SPX', 'PNUT']
        solana_tokens = ['RENDER', 'JTO', 'PYTH', 'RAY', 'W']
        base_tokens = ['VIRTUAL', 'AERO', 'BRETT', 'AIXBT', 'WELL']

        # Get all data
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'top_tokens': self.get_token_data(top_tokens),
            'meme_tokens': self.get_token_data(meme_tokens),
            'solana_tokens': self.get_token_data(solana_tokens),
            'base_tokens': self.get_token_data(base_tokens),
            'performance': self.get_top_performers()
        }
        
        # Save JSON report
        json_filename = f"crypto_report_{datetime.now().strftime('%Y%m%d')}.json"
        if not self.save_report(report_data, json_filename):
            return None
            
        # Save CSV reports
        csv_filename = f"crypto_report_{datetime.now().strftime('%Y%m%d')}.csv"
        all_tokens = (report_data['top_tokens'] + report_data['meme_tokens'] + 
                     report_data['solana_tokens'] + report_data['base_tokens'])
        if not self.save_csv(all_tokens, csv_filename):
            return None
            
        # Save performance CSV
        perf_filename = f"crypto_performance_{datetime.now().strftime('%Y%m%d')}.csv"
        # Format performance data with type indicator
        performance_data = []
        for token in report_data['performance']['best']:
            token['type'] = 'best'
            performance_data.append(token)
        for token in report_data['performance']['worst']:
            token['type'] = 'worst'
            performance_data.append(token)
            
        if not self.save_csv(performance_data, perf_filename):
            return None
            
        return {
            'json': json_filename,
            'csv': csv_filename,
            'performance_csv': perf_filename
        }

if __name__ == "__main__":
    try:
        load_dotenv()
        api_key = os.getenv('CMC_API_KEY')
        if not api_key:
            raise ValueError("Please set CMC_API_KEY in .env file")
        
        reporter = CryptoReport(api_key)
        report_file = reporter.generate_report()
        if report_file:
            print(f"Report generated: {report_file}")
        else:
            print("Failed to generate report")
    except Exception as e:
        print(f"Script failed: {str(e)}")
