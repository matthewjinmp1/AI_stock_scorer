import json
import statistics

# Load the scores.json file
with open('scores.json', 'r') as f:
    data = json.load(f)

# Get all companies
companies = data['companies']

# Get all metric names from the first company (assuming all have the same metrics)
if companies:
    first_ticker = list(companies.keys())[0]
    metrics = list(companies[first_ticker].keys())
    
    # For each metric, collect all values across all tickers
    for metric in metrics:
        values = []
        for ticker, company_data in companies.items():
            # Convert string to int
            value = int(company_data[metric])
            values.append(value)
        
        # Calculate statistics
        avg = statistics.mean(values)
        median = statistics.median(values)
        min_val = min(values)
        max_val = max(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Print results
        print(f"{metric}:")
        print(f"  Average: {avg:.2f}")
        print(f"  Median: {median:.2f}")
        print(f"  Min: {min_val}")
        print(f"  Max: {max_val}")
        print(f"  Std Dev: {stdev:.2f}")
        print()

