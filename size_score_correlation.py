#!/usr/bin/env python3
"""
Calculate correlation between total score (with size score weighted 0, others weighted 1) 
and the size/well-known score itself.
"""

import json
import os

# Score definitions (copied from scorer.py to avoid dependency on grok_client)
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


def load_excluded_tickers():
    """Load tickers from ticker_definitions.json that should be excluded.
    
    Returns:
        set: Set of ticker symbols (uppercase) to exclude
    """
    ticker_def_file = "ticker_definitions.json"
    if not os.path.exists(ticker_def_file):
        return set()
    
    try:
        with open(ticker_def_file, 'r') as f:
            data = json.load(f)
            definitions = data.get("definitions", {})
            # Return set of uppercase ticker symbols
            return {ticker.upper() for ticker in definitions.keys()}
    except Exception as e:
        print(f"Warning: Could not load {ticker_def_file}: {e}")
        return set()


def calculate_total_score(scores_dict):
    """Calculate total score from a dictionary of scores.
    
    Uses weight 0 for size_well_known_score, weight 1 for all others.
    
    Args:
        scores_dict: Dictionary with score keys and their string values
        
    Returns:
        float: The total weighted score (handling reverse scores appropriately)
    """
    total = 0
    for score_key in SCORE_DEFINITIONS:
        score_def = SCORE_DEFINITIONS[score_key]
        # Size score has weight 0, all others have weight 1
        weight = 0 if score_key == 'size_well_known_score' else 1
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


def calculate_pearson_correlation(x, y):
    """Calculate Pearson correlation coefficient.
    
    Args:
        x: List of x values
        y: List of y values
        
    Returns:
        tuple: (correlation, p_value_approximation)
    """
    n = len(x)
    if n != len(y) or n < 2:
        return None, None
    
    # Calculate means
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    # Calculate numerator (covariance)
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    
    # Calculate denominators (standard deviations)
    sum_sq_diff_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    sum_sq_diff_y = sum((y[i] - mean_y) ** 2 for i in range(n))
    
    # Avoid division by zero
    if sum_sq_diff_x == 0 or sum_sq_diff_y == 0:
        return None, None
    
    denominator = (sum_sq_diff_x * sum_sq_diff_y) ** 0.5
    
    correlation = numerator / denominator if denominator != 0 else None
    
    return correlation, None


def load_scores():
    """Load scores from scores.json."""
    scores_file = "scores.json"
    if not os.path.exists(scores_file):
        print(f"Error: {scores_file} not found")
        return None
    
    try:
        with open(scores_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {scores_file}: {e}")
        return None


def main():
    """Main function to calculate correlation between total score and size score."""
    print("=" * 80)
    print("Size/Well-Known Score vs Total Score Correlation Analysis")
    print("=" * 80)
    print("\nNote: Total score calculated with size score weighted 0, all others weighted 1")
    
    # Load scores
    print("\nLoading scores from scores.json...")
    scores_data = load_scores()
    if not scores_data:
        return
    
    # Load excluded tickers
    excluded_tickers = load_excluded_tickers()
    if excluded_tickers:
        print(f"Excluding {len(excluded_tickers)} tickers from ticker_definitions.json")
    
    companies = scores_data.get("companies", {})
    if not companies:
        print("No companies found in scores.json")
        return
    
    print(f"Found {len(companies)} companies")
    
    # Collect data for each company
    print("\nProcessing company scores...")
    
    company_data = []
    excluded_count = 0
    missing_size_score = []
    missing_total_score = []
    
    for i, (ticker_key, scores_dict) in enumerate(companies.items(), 1):
        # Normalize ticker (handle lowercase keys)
        ticker = ticker_key.upper()
        
        # Skip tickers in ticker_definitions.json (not real tickers)
        if ticker in excluded_tickers:
            excluded_count += 1
            continue
        
        # Get size score
        try:
            size_score = float(scores_dict.get('size_well_known_score', 0))
            if size_score == 0:
                # Check if it's actually missing or just zero
                if 'size_well_known_score' not in scores_dict:
                    missing_size_score.append(ticker)
                    continue
        except (ValueError, TypeError):
            missing_size_score.append(ticker)
            continue
        
        # Calculate total score (with size score weighted 0)
        total_score = calculate_total_score(scores_dict)
        
        # Only include if we have a valid total score
        if total_score > 0:
            company_data.append({
                'ticker': ticker,
                'total_score': total_score,
                'size_score': size_score
            })
        else:
            missing_total_score.append(ticker)
    
    if excluded_count > 0:
        print(f"\nExcluded {excluded_count} ticker(s) from ticker_definitions.json")
    
    if missing_size_score:
        print(f"\nWarning: {len(missing_size_score)} companies missing size_well_known_score:")
        print(f"  {', '.join(missing_size_score[:10])}" + ("..." if len(missing_size_score) > 10 else ""))
    
    if missing_total_score:
        print(f"\nWarning: {len(missing_total_score)} companies missing valid total score")
    
    if len(company_data) < 2:
        print(f"\nError: Need at least 2 companies with both total score and size score. Found {len(company_data)}")
        return
    
    print(f"\nSuccessfully processed {len(company_data)} companies")
    
    # Extract total scores and size scores for correlation
    total_scores = [d['total_score'] for d in company_data]
    size_scores = [d['size_score'] for d in company_data]
    
    # Calculate correlation
    correlation, _ = calculate_pearson_correlation(total_scores, size_scores)
    
    if correlation is None:
        print("\nError: Could not calculate correlation (insufficient data variance)")
        return
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"\nNumber of companies analyzed: {len(company_data)}")
    print(f"\nPearson Correlation Coefficient: {correlation:.4f}")
    
    # Interpret correlation
    abs_corr = abs(correlation)
    if abs_corr >= 0.9:
        strength = "very strong"
    elif abs_corr >= 0.7:
        strength = "strong"
    elif abs_corr >= 0.5:
        strength = "moderate"
    elif abs_corr >= 0.3:
        strength = "weak"
    else:
        strength = "very weak"
    
    direction = "positive" if correlation > 0 else "negative"
    print(f"Interpretation: {strength} {direction} correlation")
    
    if abs_corr > 0.3:
        if correlation > 0:
            print("\nThis suggests that companies with higher total scores (excluding size)")
            print("tend to also have higher size/well-known scores.")
        else:
            print("\nThis suggests that companies with higher total scores (excluding size)")
            print("tend to have lower size/well-known scores.")
    
    # Show some examples
    print("\n" + "=" * 80)
    print("Sample Data (Top 10 by Total Score)")
    print("=" * 80)
    
    # Sort by total score (descending)
    sorted_data = sorted(company_data, key=lambda x: x['total_score'], reverse=True)
    
    # Calculate max possible total score (all scores except size, each weighted 1, max value 10)
    max_score = sum(1 for key in SCORE_DEFINITIONS if key != 'size_well_known_score') * 10
    
    print(f"\n{'Rank':<6} {'Ticker':<8} {'Total Score %':>18} {'Size Score':>12}")
    print("-" * 50)
    
    for rank, data in enumerate(sorted_data[:10], 1):
        ticker = data['ticker']
        total_score = data['total_score']
        size_score = data['size_score']
        
        # Calculate percentage for total score
        score_pct = int((total_score / max_score) * 100) if max_score > 0 else 0
        
        print(f"{rank:<6} {ticker:<8} {score_pct:>16}% {size_score:>10.1f}/10")
    
    # Show bottom 10 for comparison
    print("\n" + "=" * 80)
    print("Sample Data (Bottom 10 by Total Score)")
    print("=" * 80)
    
    print(f"\n{'Rank':<6} {'Ticker':<8} {'Total Score %':>18} {'Size Score':>12}")
    print("-" * 50)
    
    for rank, data in enumerate(sorted_data[-10:], len(sorted_data) - 9):
        ticker = data['ticker']
        total_score = data['total_score']
        size_score = data['size_score']
        
        # Calculate percentage for total score
        score_pct = int((total_score / max_score) * 100) if max_score > 0 else 0
        
        print(f"{rank:<6} {ticker:<8} {score_pct:>16}% {size_score:>10.1f}/10")
    
    print("=" * 80)


if __name__ == "__main__":
    main()

