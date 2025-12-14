#!/usr/bin/env python3
"""
Ticker Lookup Tool
Allows users to input a company name and find the corresponding ticker symbol.
Searches both the main ticker database and custom ticker definitions.
"""

import os
import sys
import json

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Get project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# File paths
TICKER_FILE = os.path.join(PROJECT_ROOT, "data", "stock_tickers_clean.json")
TICKER_DEFINITIONS_FILE = os.path.join(PROJECT_ROOT, "data", "ticker_definitions.json")


def load_ticker_database():
    """Load ticker to company name mappings from stock_tickers_clean.json.
    
    Returns:
        dict: Mapping of ticker -> company name
    """
    ticker_map = {}
    
    if not os.path.exists(TICKER_FILE):
        return ticker_map
    
    try:
        with open(TICKER_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            for company in data.get('companies', []):
                ticker = company.get('ticker', '').strip().upper()
                name = company.get('name', '').strip()
                
                if ticker and name:
                    ticker_map[ticker] = name
    except Exception as e:
        print(f"Warning: Could not load ticker database: {e}")
    
    return ticker_map


def load_ticker_definitions():
    """Load custom ticker definitions from ticker_definitions.json.
    
    Returns:
        dict: Mapping of ticker -> company name
    """
    definitions = {}
    
    if not os.path.exists(TICKER_DEFINITIONS_FILE):
        return definitions
    
    try:
        with open(TICKER_DEFINITIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            definitions = data.get('definitions', {})
    except Exception as e:
        print(f"Warning: Could not load ticker definitions: {e}")
    
    return definitions


def create_reverse_lookup(ticker_map):
    """Create a reverse lookup mapping company name -> list of tickers.
    
    Args:
        ticker_map: dict mapping ticker -> company name
        
    Returns:
        dict: Mapping of company name (normalized) -> list of (ticker, original_name) tuples
    """
    reverse_map = {}
    
    for ticker, company_name in ticker_map.items():
        # Normalize company name for matching (lowercase, remove common suffixes)
        normalized = normalize_company_name(company_name)
        
        if normalized not in reverse_map:
            reverse_map[normalized] = []
        
        reverse_map[normalized].append((ticker, company_name))
    
    return reverse_map


def normalize_company_name(name):
    """Normalize company name for matching.
    
    Args:
        name: Company name string
        
    Returns:
        str: Normalized company name (lowercase, trimmed)
    """
    return name.lower().strip()


def search_company_name(query, ticker_db, ticker_defs):
    """Search for tickers matching a company name query.
    
    Args:
        query: Company name to search for
        ticker_db: dict mapping ticker -> company name from main database
        ticker_defs: dict mapping ticker -> company name from definitions
        
    Returns:
        list: List of (ticker, company_name, source) tuples where source is 'database' or 'definitions'
    """
    query_normalized = normalize_company_name(query)
    results = []
    
    # Combine both sources (definitions take precedence if same ticker)
    all_tickers = {**ticker_db, **ticker_defs}
    
    # Create reverse lookup
    reverse_map = create_reverse_lookup(all_tickers)
    
    # Exact match
    if query_normalized in reverse_map:
        for ticker, company_name in reverse_map[query_normalized]:
            source = 'definitions' if ticker in ticker_defs else 'database'
            results.append((ticker, company_name, source))
    
    # Partial match (company name contains query or query contains company name)
    if not results:
        for normalized_name, ticker_list in reverse_map.items():
            if query_normalized in normalized_name or normalized_name in query_normalized:
                for ticker, company_name in ticker_list:
                    source = 'definitions' if ticker in ticker_defs else 'database'
                    results.append((ticker, company_name, source))
    
    # Word-based matching (check if query words appear in company name)
    if not results:
        query_words = set(query_normalized.split())
        query_words = {w for w in query_words if len(w) > 2}  # Ignore short words
        
        for normalized_name, ticker_list in reverse_map.items():
            name_words = set(normalized_name.split())
            if query_words and query_words.issubset(name_words):
                for ticker, company_name in ticker_list:
                    source = 'definitions' if ticker in ticker_defs else 'database'
                    results.append((ticker, company_name, source))
    
    # Remove duplicates (same ticker)
    seen_tickers = set()
    unique_results = []
    for ticker, company_name, source in results:
        if ticker not in seen_tickers:
            seen_tickers.add(ticker)
            unique_results.append((ticker, company_name, source))
    
    return unique_results


def display_results(query, results):
    """Display search results.
    
    Args:
        query: Original search query
        results: List of (ticker, company_name, source) tuples
    """
    if not results:
        print(f"\nNo ticker found for '{query}'")
        print("\nTips:")
        print("  - Try using a partial company name")
        print("  - Check spelling")
        print("  - The company might not be in the database")
        return
    
    print(f"\nFound {len(results)} match(es) for '{query}':")
    print("-" * 80)
    print(f"{'Ticker':<10} {'Company Name':<50} {'Source':<15}")
    print("-" * 80)
    
    for ticker, company_name, source in results:
        source_label = 'Custom Def' if source == 'definitions' else 'Database'
        print(f"{ticker:<10} {company_name:<50} {source_label:<15}")
    
    print("-" * 80)
    
    if len(results) == 1:
        ticker, company_name, _ = results[0]
        print(f"\n✓ Ticker: {ticker}")
        print(f"  Company: {company_name}")


def main():
    """Main function."""
    print("=" * 80)
    print("Ticker Lookup Tool")
    print("=" * 80)
    print("\nEnter a company name to find its ticker symbol.")
    print("Searches both the main ticker database and custom definitions.")
    print("Type 'exit' to quit.")
    print()
    
    # Load data once at startup
    print("Loading ticker data...")
    ticker_db = load_ticker_database()
    ticker_defs = load_ticker_definitions()
    
    db_count = len(ticker_db)
    def_count = len(ticker_defs)
    print(f"Loaded {db_count:,} tickers from database")
    print(f"Loaded {def_count:,} tickers from custom definitions")
    print()
    
    while True:
        try:
            query = input("Enter company name: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            # Search for matches
            results = search_company_name(query, ticker_db, ticker_defs)
            
            # Display results
            display_results(query, results)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
