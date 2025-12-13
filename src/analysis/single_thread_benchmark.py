#!/usr/bin/env python3
"""
Single-threaded computation benchmark.
Runs at max capacity for 5 seconds and prints the total number of computations.
"""

import time


def compute():
    """Perform a simple computation (increment counter)."""
    return 1


def main():
    """Run computation at max capacity for 5 seconds."""
    print("Starting single-threaded computation benchmark...")
    print("Running for 5 seconds at max capacity...")
    
    start_time = time.time()
    end_time = start_time + 5.0  # Run for 5 seconds
    computation_count = 0
    
    # Run computations as fast as possible until 5 seconds have passed
    while time.time() < end_time:
        compute()
        computation_count += 1
    
    elapsed_time = time.time() - start_time
    
    print(f"\nBenchmark complete!")
    print(f"Total computations: {computation_count:,}")
    print(f"Elapsed time: {elapsed_time:.4f} seconds")
    print(f"Computations per second: {computation_count / elapsed_time:,.0f}")


if __name__ == "__main__":
    main()
