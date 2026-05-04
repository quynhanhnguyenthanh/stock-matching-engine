import time
import random
import uuid
from src.orderbook import OrderBook
from src.naive_orderbook import NaiveOrderBook

def generate_test_data(num_orders):
    data = []
    for _ in range(num_orders):
        data.append({
            "id": str(uuid.uuid4())[:8],
            "is_buy": random.choice([True, False]),
            "price": round(50000 + random.uniform(-1000, 1000), 2),
            "qty": random.randint(1, 50) * 100
        })
    return data

def run_benchmark(num_orders=100_000):
    test_data = generate_test_data(num_orders)
    
    print(f"\n[1] TEST MẢNG THUẦN O(N) VỚI {num_orders:,} LỆNH")
    naive_book = NaiveOrderBook()
    start_naive = time.time()
    for o in test_data:
        naive_book.add_order(o['id'], o['is_buy'], o['price'], o['qty'])
    time_naive = time.time() - start_naive
    print(f"-> Chạy mất: {time_naive:.4f} s")
    print(f"-> Khớp được: {len(naive_book.trades):,} giao dịch")

    print("\n[2] TEST KIẾN TRÚC HEAP + HASH")
    heap_book = OrderBook() 
    start_heap = time.time()
    for o in test_data:
        heap_book.add_order(o['id'], o['is_buy'], o['price'], o['qty'])
    time_heap = time.time() - start_heap
    print(f"-> Chạy mất: {time_heap:.4f} s")
    print(f"-> Khớp được: {len(heap_book.trades):,} giao dịch")

        speedup = time_naive / time_heap
        print(f"Heap xử lý nhanh gấp {speedup:.1f} lần")

if __name__ == "__main__":
    run_benchmark(100_000)
