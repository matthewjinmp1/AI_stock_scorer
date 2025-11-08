#!/usr/bin/env python3
"""
Simplified Company Scorer - For Testing Prompts
This is a simplified version that only scores one metric.
Once prompts are confirmed good, they can be integrated into scorer.py
"""

from grok_client import GrokClient
from config import XAI_API_KEY
import sys
import json
import os
import time

# JSON file to store scores (separate from main scorer)
SCORES_FILE = "scores_simple.json"

# Stock ticker lookup file
TICKER_FILE = "stock_tickers_clean.json"

# Cache for ticker lookups
_ticker_cache = None

# Single metric definition - modify this prompt for testing
METRIC = {
    'key': 'moat_score',
    'display_name': 'Competitive Moat',
    'prompt': """Rate the competitive moat strength of {company_name} on a scale of 0-10, where:
- 0 = Weak or minimal competitive advantage, easily replaceable, commodity-like business
- 5 = TYPICAL AVERAGE - This is the standard score for most companies. Average competitive advantages typical of most companies in the industry
- 10 = Very strong moat, companies with exceptional competitive advantages that are difficult to replicate

Consider factors like:
- Brand strength and customer loyalty
- Network effects
- Switching costs
- Economies of scale
- Patents/intellectual property
- Regulatory barriers
- Unique resources or capabilities

Respond with ONLY the numerical score (0-10), no explanation needed."""
}


def load_ticker_lookup():
    """Load ticker to company name lookup."""
    global _ticker_cache
    
    if _ticker_cache is not None:
        return _ticker_cache
    
    _ticker_cache = {}
    
    try:
        if os.path.exists(TICKER_FILE):
            with open(TICKER_FILE, 'r') as f:
                data = json.load(f)
                
                for company in data.get('companies', []):
                    ticker = company.get('ticker', '').strip().upper()
                    name = company.get('name', '').strip()
                    
                    if ticker:
                        _ticker_cache[ticker] = name
        else:
            print(f"Warning: {TICKER_FILE} not found. Ticker lookups will not work.")
    except Exception as e:
        print(f"Warning: Could not load ticker file: {e}")
    
    return _ticker_cache


def resolve_to_company_name(input_str):
    """
    Resolve input to a company name.
    Returns (company_name, ticker) tuple.
    """
    input_upper = input_str.strip().upper()
    
    # Check if it's a ticker symbol (uppercase, 1-5 chars)
    if len(input_upper) >= 1 and len(input_upper) <= 5 and input_upper.isalpha():
        ticker_lookup = load_ticker_lookup()
        
        if input_upper in ticker_lookup:
            company_name = ticker_lookup[input_upper]
            return (company_name, input_upper)
    
    # Otherwise treat as company name
    return (input_str.strip(), None)


def load_scores():
    """Load existing scores from JSON file."""
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"companies": {}}
    return {"companies": {}}


def save_scores(scores_data):
    """Save scores to JSON file."""
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores_data, f, indent=2)


def score_ticker(input_str):
    """Score a single ticker."""
    input_stripped = input_str.strip()
    input_upper = input_stripped.upper()
    
    ticker = None
    company_name = None
    
    ticker_lookup = load_ticker_lookup()
    if input_upper in ticker_lookup:
        ticker = input_upper
        company_name = ticker_lookup[ticker]
    else:
        print(f"\nError: '{input_upper}' is not a valid ticker symbol.")
        print("Please enter a valid NYSE or NASDAQ ticker symbol.")
        return False
    
    scores_data = load_scores()
    
    # Check if already scored
    if ticker in scores_data["companies"]:
        existing_data = scores_data["companies"][ticker]
        if METRIC['key'] in existing_data:
            score = existing_data[METRIC['key']]
            print(f"\n{ticker} ({company_name}) already scored: {score}/10")
            return True
    
    # Score the company
    print(f"\nScoring {ticker} ({company_name})...")
    print(f"Metric: {METRIC['display_name']}")
    
    grok = GrokClient(api_key=XAI_API_KEY)
    prompt = METRIC['prompt'].format(company_name=company_name)
    
    start_time = time.time()
    try:
        response, token_usage = grok.simple_query_with_tokens(prompt, model="grok-4-fast")
        elapsed_time = time.time() - start_time
        total_tokens = token_usage.get('total_tokens', 0)
        
        score = response.strip()
        print(f"  Time: {elapsed_time:.2f}s | Tokens: {total_tokens}")
        print(f"Score: {score}/10")
        
        # Save the score
        if ticker not in scores_data["companies"]:
            scores_data["companies"][ticker] = {}
        
        scores_data["companies"][ticker][METRIC['key']] = score
        scores_data["companies"][ticker]['company_name'] = company_name
        save_scores(scores_data)
        
        print(f"\nScore saved to {SCORES_FILE}")
        return True
        
    except Exception as e:
        print(f"Error scoring {ticker}: {e}")
        return False


def score_multiple_tickers(tickers_str):
    """Score multiple tickers."""
    tickers = tickers_str.strip().split()
    
    if not tickers:
        print("No tickers provided.")
        return
    
    print(f"\nScoring {len(tickers)} ticker(s)...")
    
    for ticker in tickers:
        score_ticker(ticker)
        print()  # Add blank line between tickers


def view_scores():
    """Display all stored scores."""
    scores_data = load_scores()
    
    if not scores_data["companies"]:
        print("No scores stored yet.")
        return
    
    print(f"\n{METRIC['display_name']} Scores:")
    print("=" * 60)
    
    # Sort by score (descending)
    companies_with_scores = []
    for ticker, data in scores_data["companies"].items():
        score = data.get(METRIC['key'])
        company_name = data.get('company_name', '')
        if score:
            try:
                score_float = float(score)
                companies_with_scores.append((ticker, company_name, score_float))
            except (ValueError, TypeError):
                pass
    
    if not companies_with_scores:
        print("No valid scores found.")
        return
    
    # Sort by score descending
    companies_with_scores.sort(key=lambda x: x[2], reverse=True)
    
    # Display
    max_ticker_len = max(len(ticker) for ticker, _, _ in companies_with_scores) if companies_with_scores else 0
    
    print(f"{'Ticker':<{max(8, max_ticker_len)}} {'Company Name':<30} {'Score':>8}")
    print("-" * 60)
    
    for ticker, company_name, score in companies_with_scores:
        score_str = f"{int(score)}" if score == int(score) else f"{score:.1f}"
        company_display = company_name[:28] if len(company_name) > 28 else company_name
        print(f"{ticker:<{max(8, max_ticker_len)}} {company_display:<30} {score_str:>8}")


def main():
    """Main function to run the simplified scorer."""
    print("Simplified Company Scorer - For Testing Prompts")
    print("=" * 50)
    print(f"Current Metric: {METRIC['display_name']}")
    print()
    print("Commands:")
    print("  Enter ticker symbol (e.g., AAPL) or multiple tickers (e.g., AAPL MSFT GOOGL) to score")
    print("  Type 'view' to see all scores")
    print("  Type 'quit' or 'exit' to stop")
    print()
    
    while True:
        try:
            user_input = input("Enter ticker(s) or command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'view':
                view_scores()
                print()
            elif user_input:
                # Check if input contains multiple space-separated tickers
                tickers = user_input.strip().split()
                if len(tickers) > 1:
                    # Multiple tickers
                    score_multiple_tickers(user_input)
                    print()
                else:
                    # Single ticker
                    score_ticker(user_input)
                    print()
            else:
                print("Please enter a ticker symbol or command.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()

