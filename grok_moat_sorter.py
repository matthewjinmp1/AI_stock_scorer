#!/usr/bin/env python3
"""
Efficient Moat Score Sorter using Grok API
Uses merge sort (O(n log n)) to rank companies by moat strength.
Each comparison is done by asking Grok which company has a stronger moat.
Expected API calls: ~n*log2(n) = ~33 calls for 10 companies
"""

from grok_client import GrokClient
from config import XAI_API_KEY
import time

# 10 well-known companies to rank
COMPANIES = [
    ("AAPL", "Apple Inc"),
    ("MSFT", "Microsoft Corporation"),
    ("GOOGL", "Alphabet Inc"),
    ("AMZN", "Amazon.com Inc"),
    ("NVDA", "NVIDIA Corporation"),
    ("META", "Meta Platforms Inc"),
    ("TSLA", "Tesla Inc"),
    ("JPM", "JPMorgan Chase & Co"),
    ("V", "Visa Inc"),
    ("JNJ", "Johnson & Johnson"),
]

# Track API calls
api_call_count = 0

def compare_companies_grok(grok, company1, company2):
    """
    Ask Grok which company has a stronger competitive moat.
    
    Args:
        grok: GrokClient instance
        company1: Tuple of (ticker, company_name)
        company2: Tuple of (ticker, company_name)
        
    Returns:
        -1 if company1 has stronger moat (company1 < company2 in sort order)
         1 if company2 has stronger moat (company2 < company1 in sort order)
         0 if equal (shouldn't happen, but handle gracefully)
    """
    global api_call_count
    
    ticker1, name1 = company1
    ticker2, name2 = company2
    
    prompt = f"""Compare the competitive moat strength of these two companies:

Company 1: {name1} ({ticker1})
Company 2: {name2} ({ticker2})

Which company has a STRONGER competitive moat? Consider factors like:
- Brand strength and customer loyalty
- Network effects
- Switching costs
- Economies of scale
- Patents/intellectual property
- Regulatory barriers
- Unique resources or capabilities

Respond with ONLY:
- "1" if {name1} ({ticker1}) has a stronger moat
- "2" if {name2} ({ticker2}) has a stronger moat
- "equal" if they have equally strong moats (very rare)

Just respond with the number or "equal", nothing else."""

    api_call_count += 1
    print(f"  [Call #{api_call_count}] Comparing {ticker1} vs {ticker2}...", end=" ", flush=True)
    
    try:
        response, _ = grok.simple_query_with_tokens(prompt, model="grok-4-fast")
        response = response.strip().lower()
        
        if "1" in response or ticker1.lower() in response:
            print(f"→ {ticker1} stronger")
            return -1  # company1 has stronger moat (should come first)
        elif "2" in response or ticker2.lower() in response:
            print(f"→ {ticker2} stronger")
            return 1   # company2 has stronger moat (should come first)
        else:
            # Default to company1 if unclear (shouldn't happen often)
            print(f"→ unclear, defaulting to {ticker1}")
            return -1
    except Exception as e:
        print(f"→ Error: {e}, defaulting to {ticker1}")
        return -1


def merge_sort_companies(grok, companies):
    """
    Merge sort implementation using Grok comparisons.
    
    Args:
        grok: GrokClient instance
        companies: List of (ticker, company_name) tuples
        
    Returns:
        Sorted list of companies (strongest moat first)
    """
    if len(companies) <= 1:
        return companies
    
    # Split the list in half
    mid = len(companies) // 2
    left = merge_sort_companies(grok, companies[:mid])
    right = merge_sort_companies(grok, companies[mid:])
    
    # Merge the two sorted halves
    return merge(grok, left, right)


def merge(grok, left, right):
    """
    Merge two sorted lists using Grok comparisons.
    
    Args:
        grok: GrokClient instance
        left: Sorted list of companies
        right: Sorted list of companies
        
    Returns:
        Merged sorted list
    """
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        # Compare using Grok
        comparison = compare_companies_grok(grok, left[i], right[j])
        
        if comparison <= 0:  # left[i] has stronger or equal moat
            result.append(left[i])
            i += 1
        else:  # right[j] has stronger moat
            result.append(right[j])
            j += 1
    
    # Add remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result


def main():
    """Main function to sort companies by moat strength."""
    global api_call_count
    
    print("=" * 80)
    print("Grok-Powered Moat Score Sorter")
    print("=" * 80)
    print(f"\nRanking {len(COMPANIES)} companies by competitive moat strength...")
    print("Using merge sort (O(n log n)) with Grok API comparisons")
    print(f"Expected API calls: ~{len(COMPANIES)} * log2({len(COMPANIES)}) ≈ {int(len(COMPANIES) * __import__('math').log2(len(COMPANIES)))}")
    print()
    
    # Initialize Grok client
    try:
        grok = GrokClient(api_key=XAI_API_KEY)
    except Exception as e:
        print(f"Error initializing Grok client: {e}")
        print("\nTo fix this:")
        print("1. Get an API key from https://console.x.ai/")
        print("2. Set the XAI_API_KEY environment variable:")
        print("   export XAI_API_KEY='your_api_key_here'")
        return
    
    # Reset API call counter
    api_call_count = 0
    
    # Start timing
    start_time = time.time()
    
    # Sort companies using merge sort
    print("Starting merge sort with Grok comparisons...\n")
    sorted_companies = merge_sort_companies(grok, COMPANIES.copy())
    
    # End timing
    elapsed_time = time.time() - start_time
    
    # Display results
    print("\n" + "=" * 80)
    print("Ranking Results (Strongest Moat First)")
    print("=" * 80)
    print()
    
    for rank, (ticker, company_name) in enumerate(sorted_companies, 1):
        print(f"{rank:2}. {ticker:6} - {company_name}")
    
    print()
    print("=" * 80)
    print(f"Total Grok API calls: {api_call_count}")
    print(f"Expected calls (n*log2(n)): {int(len(COMPANIES) * __import__('math').log2(len(COMPANIES)))}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print("=" * 80)


if __name__ == "__main__":
    main()

