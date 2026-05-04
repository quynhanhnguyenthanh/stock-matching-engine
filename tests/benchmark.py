import time
from src.orderbook import OrderBook
from src.bot import TradingBot

def run_benchmark(num_orders=100_000):
    book = OrderBook()
    bot = TradingBot(book, base_price=50000, spread=1000)
    
    start = time.time()
    bot.generate_random_orders(num_orders)
    elapsed = time.time() - start
    
    print("\n--- KẾT QUẢ BENCHMARK ---")
    print(f"Thời gian chạy : {elapsed:.4f} s")
    print(f"Throughput     : {int(num_orders / elapsed):,} req/s")
    print(f"Tổng số đã khớp: {len(book.trades):,} giao dịch")

if __name__ == "__main__":
    run_benchmark(100_000)
