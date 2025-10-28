#!/usr/bin/env python3
"""
Migrate moat_scores.json from company names to ticker symbols
"""

import json
import sys
sys.path.insert(0, '.')
from moat_scorer import load_scores, save_scores, get_ticker_from_company_name, load_ticker_lookup, SCORE_DEFINITIONS

def migrate_to_tickers():
    """Migrate scores to use tickers as keys."""
    print("=" * 60)
    print("Migrating moat_scores.json to use tickers")
    print("=" * 60)
    
    scores_data = load_scores()
    
    if not scores_data["companies"]:
        print("No scores to migrate.")
        return
    
    print(f"\nFound {len(scores_data['companies'])} companies in existing scores")
    
    ticker_lookup = load_ticker_lookup()
    new_companies = {}
    ticker_mappings = {}
    
    for key, data in scores_data["companies"].items():
        # Skip if already a ticker (uppercase, short)
        if len(key) <= 5 and key.upper() == key:
            new_companies[key.upper()] = data
            continue
        
        # Try to find ticker for this company
        ticker = get_ticker_from_company_name(key)
        
        if ticker:
            # Update with ticker
            new_companies[ticker] = data
            ticker_mappings[key] = ticker
            print(f"  {key} → {ticker}")
        else:
            # Keep as is if we can't find a ticker
            new_companies[key] = data
            print(f"  {key} → (no ticker found, keeping as is)")
    
    scores_data["companies"] = new_companies
    save_scores(scores_data)
    
    print(f"\n{'=' * 60}")
    print(f"Migration complete!")
    print(f"Total companies: {len(new_companies)}")
    if ticker_mappings:
        print(f"Mapped to tickers: {len(ticker_mappings)}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    migrate_to_tickers()
