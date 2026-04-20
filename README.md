# stock-matching-engine
A high-performance, algorithmic order matching engine for financial markets. This project simulates a real-world stock exchange backend, strictly enforcing the **Price-Time Priority** rule for Limit and Market orders. 

By leveraging advanced data structures like Min/Max-Heaps and Hash Maps, this engine is built for speed, memory efficiency, and scalability.

## Key Features

**Core Matching Engine**: Fully functional order book with precise matching algorithms for both Limit and Market orders following the Price-Time Priority rule.
**Highly Optimized Memory & Speed**: Utilizes 1D array Min/Max-Heaps and Python's `__slots__` mechanism to drastically reduce RAM footprint and ensure high-speed processing.
**Instant Order Cancellation**: Combines Hash Maps with **Lazy Deletion** (Logical Deletion) to locate and cancel orders in $O(1)$ time without disrupting the core data structure.
**Automated Trading Bot**: A built-in algorithmic bot that trades based on the order book spread to generate market liquidity and stress-test the system under heavy loads.
**Performance Benchmarking**: Includes simulation scripts for **100,000+ orders** to definitively prove the performance superiority of the Heap+Hash architecture over traditional $O(n)$ arrays.
**Real-time Terminal UI**: A sleek, interactive command-line interface to visualize the order book, recent trades, and system metrics in real-time.
**Production-Ready Code**: Codebase is fully documented using standard Docstrings, including strict **Big-O time complexity analysis** for all critical functions.
