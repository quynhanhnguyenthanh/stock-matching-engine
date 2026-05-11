# Stock Matching Engine

A stock matching engine focusing on Data Structures and Algorithms (DSA) optimizations. The system not only handles ultra-fast order execution but also integrates technical analysis tools and arbitrage opportunity detection.

Final Project for **IT003.Q21.TTNT**.

## Core Features & Algorithmic Architecture

The system is designed to overcome the limitations of standard linear data structures (Lists/Arrays) by implementing advanced memory and processing optimizations:

*   **Ultra-fast Order Book**: 
    *   Utilizes **Min/Max-Heap** to maintain the best market prices (Best Bid/Ask) with $O(1)$ peak retrieval and $O(\log N)$ updates.
    *   Integrates a **Hash Map** combined with **Lazy Deletion** for instantaneous $O(1)$ order localization and cancellation without breaking the tree structure.
    *   Optimizes RAM usage via Python's `__slots__` mechanism for large-scale data objects.
*   **Matching Engine**: Strictly adheres to the **Price-Time Priority** matching logic for both Limit and Market orders.
*   **Ticker Search (Autocomplete)**: Implements a **Trie (Prefix Tree)** for instant stock ticker suggestions. Response time depends strictly on the input string length rather than the total number of listed symbols.
*   **Technical Analysis**: Deploys a **Segment Tree** to handle Range Queries, efficiently extracting High/Low prices and Total Volume within any arbitrary timeframe with a time complexity of $O(\log N)$.
*   **Arbitrage Detection**: Models the market as a Directed Graph, converts exchange rates using logarithmic functions, and applies the **Bellman-Ford algorithm** to detect negative cycles (profitable arbitrage opportunities).
*   **Stress-test Bot**: Automatically simulates 100,000+ diverse trading orders to benchmark Latency and Throughput, proving performance superiority over naive $O(N)$ arrays.

## Installation & Usage

**Clone the repository**
```bash
git clone https://github.com/quynhanhnguyenthanh/stock-matching-engine.git
cd stock-matching-engine
