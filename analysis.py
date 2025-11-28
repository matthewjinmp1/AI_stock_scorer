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
    
    # Store statistics for each metric to calculate overall averages
    all_averages = []
    all_medians = []
    all_mins = []
    all_maxes = []
    all_stdevs = []
    
    # For each metric, collect all values across all tickers
    for metric in metrics:
        values = []
        for ticker, company_data in companies.items():
            # Get the value and handle markdown formatting (e.g., "**2**" -> "2")
            value_str = str(company_data[metric]).strip()
            # Remove markdown formatting (asterisks)
            value_str = value_str.replace('*', '')
            # Convert to int, skip if invalid
            try:
                value = int(value_str)
                values.append(value)
            except (ValueError, TypeError):
                # Skip invalid values
                continue
        
        # Skip if no valid values found
        if len(values) == 0:
            print(f"{metric}:")
            print(f"  No valid values found")
            print()
            continue
        
        # Calculate statistics
        avg = statistics.mean(values)
        median = statistics.median(values)
        min_val = min(values)
        max_val = max(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Store statistics for overall averages
        all_averages.append(avg)
        all_medians.append(median)
        all_mins.append(min_val)
        all_maxes.append(max_val)
        all_stdevs.append(stdev)
        
        # Print results
        print(f"{metric}:")
        print(f"  Average: {avg:.2f}")
        print(f"  Median: {median:.2f}")
        print(f"  Min: {min_val}")
        print(f"  Max: {max_val}")
        print(f"  Std Dev: {stdev:.2f}")
        print()
    
    # Calculate and print overall averages across all metrics
    print("=" * 50)
    print("Overall Averages Across All Metrics:")
    print("=" * 50)
    print(f"  Average of Averages: {statistics.mean(all_averages):.2f}")
    print(f"  Average of Medians: {statistics.mean(all_medians):.2f}")
    print(f"  Average of Mins: {statistics.mean(all_mins):.2f}")
    print(f"  Average of Maxes: {statistics.mean(all_maxes):.2f}")
    print(f"  Average of Std Devs: {statistics.mean(all_stdevs):.2f}")
    print()

