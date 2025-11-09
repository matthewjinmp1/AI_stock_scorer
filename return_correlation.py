#!/usr/bin/env python3
"""
Calculate correlation between total scores and stock returns
Loads returns from returns.json and scores from scores.json
"""

import json
import os
from scipy.stats import pearsonr
import numpy as np

SCORES_FILE = "scores.json"
RETURNS_FILE = "returns.json"
TICKER_DEFINITIONS_FILE = "ticker_definitions.json"

# Score weightings - must match scorer.py
SCORE_WEIGHTS = {
    'moat_score': 10,
    'barriers_score': 10,
    'disruption_risk': 10,
    'switching_cost': 10,
    'brand_strength': 10, 
    'competition_intensity': 10,
    'network_effect': 10,
    'product_differentiation': 10,
    'innovativeness_score': 10,
    'growth_opportunity': 10,
    'riskiness_score': 10,
    'pricing_power': 10,
    'ambition_score': 10,
    'bargaining_power_of_customers': 10,
    'bargaining_power_of_suppliers': 10,
    'product_quality_score': 10,
    'culture_employee_satisfaction_score': 10,
    'trailblazer_score': 10,
    'size_well_known_score': 0,
}

# Score definitions - must match scorer.py (only need is_reverse flag)
SCORE_DEFINITIONS = {
    'moat_score': {'is_reverse': False},
    'barriers_score': {'is_reverse': False},
    'disruption_risk': {'is_reverse': True},
    'switching_cost': {'is_reverse': False},
    'brand_strength': {'is_reverse': False},
    'competition_intensity': {'is_reverse': True},
    'network_effect': {'is_reverse': False},
    'product_differentiation': {'is_reverse': False},
    'innovativeness_score': {'is_reverse': False},
    'growth_opportunity': {'is_reverse': False},
    'riskiness_score': {'is_reverse': True},
    'pricing_power': {'is_reverse': False},
    'ambition_score': {'is_reverse': False},
    'bargaining_power_of_customers': {'is_reverse': True},
    'bargaining_power_of_suppliers': {'is_reverse': True},
    'product_quality_score': {'is_reverse': False},
    'culture_employee_satisfaction_score': {'is_reverse': False},
    'trailblazer_score': {'is_reverse': False},
    'size_well_known_score': {'is_reverse': False},
}


def calculate_total_score(scores_dict):
    """Calculate total score from a dictionary of scores.
    
    Args:
        scores_dict: Dictionary with score keys and their string values
        
    Returns:
        float: The total weighted score (handling reverse scores appropriately)
    """
    total = 0
    for score_key in SCORE_DEFINITIONS:
        score_def = SCORE_DEFINITIONS[score_key]
        weight = SCORE_WEIGHTS.get(score_key, 1.0)  # Default to 1.0 if weight not found
        try:
            score_value = float(scores_dict.get(score_key, 0))
            # For reverse scores, invert to get "goodness" value
            if score_def['is_reverse']:
                total += (10 - score_value) * weight
            else:
                total += score_value * weight
        except (ValueError, TypeError):
            pass
    return total


def load_scores():
    """Load scores from scores.json."""
    if not os.path.exists(SCORES_FILE):
        print(f"Error: {SCORES_FILE} not found.")
        return None
    
    try:
        with open(SCORES_FILE, 'r') as f:
            data = json.load(f)
        return data.get("companies", {})
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {SCORES_FILE}: {e}")
        return None


def load_returns():
    """Load returns from returns.json."""
    if not os.path.exists(RETURNS_FILE):
        print(f"Error: {RETURNS_FILE} not found.")
        print("Please run returns.py first to generate returns data.")
        return None
    
    try:
        with open(RETURNS_FILE, 'r') as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {RETURNS_FILE}: {e}")
        return None


def load_excluded_tickers():
    """Load tickers to exclude from ticker_definitions.json."""
    excluded = set()
    if os.path.exists(TICKER_DEFINITIONS_FILE):
        try:
            with open(TICKER_DEFINITIONS_FILE, 'r') as f:
                data = json.load(f)
            definitions = data.get("definitions", {})
            # Extract all ticker symbols and convert to uppercase
            excluded = {ticker.upper() for ticker in definitions.keys()}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load {TICKER_DEFINITIONS_FILE}: {e}")
    return excluded


def main():
    """Main function to calculate and display correlation."""
    print("=" * 60)
    print("Score-Return Correlation Analysis")
    print("=" * 60)
    print()
    
    # Load scores
    print("Loading scores from scores.json...")
    scores_data = load_scores()
    if scores_data is None:
        return
    
    print(f"Found {len(scores_data)} companies in scores.json")
    
    # Load returns
    print("Loading returns from returns.json...")
    returns_data = load_returns()
    if returns_data is None:
        return
    
    returns_dict = returns_data.get("returns", {})
    print(f"Found {len(returns_dict)} companies in returns.json")
    
    # Get date range from returns file
    start_date = returns_data.get("start_date", "Unknown")
    end_date = returns_data.get("end_date", "Unknown")
    print(f"Returns period: {start_date} to {end_date}")
    print()
    
    # Load excluded tickers
    excluded_tickers = load_excluded_tickers()
    if excluded_tickers:
        print(f"Excluding {len(excluded_tickers)} tickers from ticker_definitions.json")
    
    # Match companies and calculate total scores
    print("Calculating total scores and matching with returns...")
    matched_data = []
    excluded_count = 0
    
    for ticker, scores_dict in scores_data.items():
        ticker_upper = ticker.upper()
        
        # Skip if ticker is in excluded list
        if ticker_upper in excluded_tickers:
            excluded_count += 1
            continue
        
        # Check if this ticker has return data
        if ticker_upper in returns_dict:
            return_info = returns_dict[ticker_upper]
            
            # Only include successful returns
            if return_info.get("status") == "success" and return_info.get("return") is not None:
                total_score = calculate_total_score(scores_dict)
                return_pct = return_info.get("return")
                
                matched_data.append({
                    'ticker': ticker_upper,
                    'total_score': total_score,
                    'return': return_pct
                })
    
    if excluded_count > 0:
        print(f"Excluded {excluded_count} tickers from custom definitions")
    
    print(f"Found {len(matched_data)} companies with both scores and returns")
    print()
    
    if len(matched_data) < 2:
        print("Error: Need at least 2 companies with both scores and returns to calculate correlation.")
        return
    
    # Extract arrays for correlation calculation
    total_scores = [d['total_score'] for d in matched_data]
    returns = [d['return'] for d in matched_data]
    
    # Calculate correlation
    correlation, p_value = pearsonr(total_scores, returns)
    
    # Display results
    print("=" * 60)
    print("CORRELATION RESULTS")
    print("=" * 60)
    print(f"Pearson Correlation Coefficient: {correlation:.4f}")
    print(f"P-value: {p_value:.6f}")
    print()
    
    # Interpret correlation
    abs_corr = abs(correlation)
    if abs_corr < 0.1:
        strength = "negligible"
    elif abs_corr < 0.3:
        strength = "weak"
    elif abs_corr < 0.5:
        strength = "moderate"
    elif abs_corr < 0.7:
        strength = "strong"
    else:
        strength = "very strong"
    
    direction = "positive" if correlation > 0 else "negative"
    
    print(f"Interpretation: {strength.capitalize()} {direction} correlation")
    if p_value < 0.05:
        print(f"Statistically significant (p < 0.05)")
    else:
        print(f"Not statistically significant (p >= 0.05)")
    print()
    
    # Display statistics
    print("=" * 60)
    print("STATISTICS")
    print("=" * 60)
    print(f"Number of companies: {len(matched_data)}")
    print()
    print("Total Scores:")
    print(f"  Mean: {np.mean(total_scores):.2f}")
    print(f"  Median: {np.median(total_scores):.2f}")
    print(f"  Min: {min(total_scores):.2f}")
    print(f"  Max: {max(total_scores):.2f}")
    print(f"  Std Dev: {np.std(total_scores):.2f}")
    print()
    print("Returns (%):")
    print(f"  Mean: {np.mean(returns):+.2f}%")
    print(f"  Median: {np.median(returns):+.2f}%")
    print(f"  Min: {min(returns):+.2f}%")
    print(f"  Max: {max(returns):+.2f}%")
    print(f"  Std Dev: {np.std(returns):.2f}%")
    print()
    
    # Show top and bottom performers
    print("=" * 60)
    print("TOP 10 BY TOTAL SCORE")
    print("=" * 60)
    sorted_by_score = sorted(matched_data, key=lambda x: x['total_score'], reverse=True)
    print(f"{'Ticker':<10} {'Total Score':<15} {'Return %':<15}")
    print("-" * 60)
    for item in sorted_by_score[:10]:
        print(f"{item['ticker']:<10} {item['total_score']:>12.2f}    {item['return']:>+8.2f}%")
    print()
    
    print("=" * 60)
    print("TOP 10 BY RETURN")
    print("=" * 60)
    sorted_by_return = sorted(matched_data, key=lambda x: x['return'], reverse=True)
    print(f"{'Ticker':<10} {'Total Score':<15} {'Return %':<15}")
    print("-" * 60)
    for item in sorted_by_return[:10]:
        print(f"{item['ticker']:<10} {item['total_score']:>12.2f}    {item['return']:>+8.2f}%")
    print()
    
    # Show scatter plot data points (top and bottom)
    print("=" * 60)
    print("EXAMPLES: High Score, High Return")
    print("=" * 60)
    # Find companies with both high score and high return
    high_score_high_return = [d for d in matched_data if d['total_score'] > np.median(total_scores) and d['return'] > np.median(returns)]
    high_score_high_return.sort(key=lambda x: x['total_score'] + x['return'], reverse=True)
    print(f"{'Ticker':<10} {'Total Score':<15} {'Return %':<15}")
    print("-" * 60)
    for item in high_score_high_return[:5]:
        print(f"{item['ticker']:<10} {item['total_score']:>12.2f}    {item['return']:>+8.2f}%")
    print()
    
    print("=" * 60)
    print("EXAMPLES: Low Score, Low Return")
    print("=" * 60)
    # Find companies with both low score and low return
    low_score_low_return = [d for d in matched_data if d['total_score'] < np.median(total_scores) and d['return'] < np.median(returns)]
    low_score_low_return.sort(key=lambda x: x['total_score'] + x['return'])
    print(f"{'Ticker':<10} {'Total Score':<15} {'Return %':<15}")
    print("-" * 60)
    for item in low_score_low_return[:5]:
        print(f"{item['ticker']:<10} {item['total_score']:>12.2f}    {item['return']:>+8.2f}%")
    print()


if __name__ == "__main__":
    main()

