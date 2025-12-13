#!/usr/bin/env python3
"""
Single-threaded and multithreaded computation benchmark.
Runs at max capacity for 5 seconds and prints the total number of computations.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor


def compute():
    """Perform a simple computation (increment counter)."""
    return 1


def single_thread_benchmark():
    """Run single-threaded computation at max capacity for 5 seconds."""
    print("=" * 80)
    print("SINGLE-THREADED BENCHMARK")
    print("=" * 80)
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
    return computation_count


def worker_thread(end_time, result_list, thread_id):
    """Worker thread that performs computations until end_time."""
    local_count = 0
    while time.time() < end_time:
        compute()
        local_count += 1
    result_list[thread_id] = local_count
    return local_count


def multithread_benchmark(num_threads=None):
    """Run multithreaded computation at max capacity for 5 seconds.
    
    Args:
        num_threads: Number of threads to use. If None, uses CPU count.
    """
    import os
    if num_threads is None:
        num_threads = os.cpu_count() or 4
    
    print("\n" + "=" * 80)
    print("MULTITHREADED BENCHMARK")
    print("=" * 80)
    print(f"Starting multithreaded computation benchmark with {num_threads} threads...")
    print("Running for 5 seconds at max capacity...")
    
    start_time = time.time()
    end_time = start_time + 5.0  # Run for 5 seconds
    
    # Use a list to store results from each thread
    result_list = [0] * num_threads
    
    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker_thread, args=(end_time, result_list, i))
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    elapsed_time = time.time() - start_time
    total_computations = sum(result_list)
    
    print(f"\nBenchmark complete!")
    print(f"Number of threads: {num_threads}")
    print(f"Total computations: {total_computations:,}")
    print(f"Elapsed time: {elapsed_time:.4f} seconds")
    print(f"Computations per second: {total_computations / elapsed_time:,.0f}")
    print(f"Computations per thread: {total_computations / num_threads:,.0f}")
    return total_computations


def main():
    """Run single-threaded or multithreaded benchmark based on user choice."""
    print("=" * 80)
    print("COMPUTATION BENCHMARK")
    print("=" * 80)
    print("\nChoose benchmark type:")
    print("  1 - Single-threaded")
    print("  2 - Multithreaded")
    
    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            single_thread_benchmark()
            break
        elif choice == "2":
            multithread_benchmark()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
