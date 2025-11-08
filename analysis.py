import json
import statistics

# Load the stricter_scores.json file
with open('stricter_scores.json', 'r') as f:
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
            # Convert string to int
            value = int(company_data[metric])
            values.append(value)
        
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

