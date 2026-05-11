import time
import random
import uuid
from core.order import Order
from core.order_book import OrderBook
from core.engine import MatchingEngine

class NaiveOrderBook:
    """
    Sổ lệnh phiên bản dùng list (mảng thuần) để làm đối chứng.
    Mọi thao tác đều có độ phức tạp O(N), gây thắt cổ chai khi dữ liệu lớn.
    """
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.buy_orders = []
        self.sell_orders = []

    def add_order(self, order: Order) -> None:
        """Thêm lệnh vào mảng mất O(1)"""
        if order.side == 'BUY':
            self.buy_orders.append(order)
        else:
            self.sell_orders.append(order)

    def cancel_order(self, order_id: str) -> bool:
        """
        Hủy lệnh: Phải duyệt toàn bộ mảng để tìm và xóa O(N).
        Đây là điểm yếu chí mạng của mảng.
        """
        # duyệt qua cả 2 list mua và bán để tìm lệnh cần xóa
        for lst in (self.buy_orders, self.sell_orders):
            for i, o in enumerate(lst):
                if o.order_id == order_id:
                    lst.pop(i)
                    return True
        return False

    def get_best_bid(self) -> Order:
        """
        Tìm lệnh mua giá cao nhất: Duyệt toàn bộ mảng O(N).
        """
        if not self.buy_orders: return None
        # ưu tiên giá cao nhất, nếu giá bằng nhau thì thời gian nhỏ nhất
        return max(self.buy_orders, key=lambda o: (o.price, -o.timestamp))

class StressTestBot:
    """
    Bot giả lập ép tải hệ thống và đo lường Latency, Throughput.
    """
    def __init__(self, num_orders: int = 100000):
        self.num_orders = num_orders
        self.symbols = ['FPT', 'VNM', 'VIC', 'HPG', 'SSI']
        self.test_data = []
        
    def generate_data(self) -> None:
        """
        Sinh ra bộ dữ liệu test.
        Tạo sẵn dữ liệu để khi đo thời gian không bị dính thời gian random của python.
        """
        print(f"[*] Đang sinh {self.num_orders:,} lệnh giao dịch ngẫu nhiên...")
        active_ids = []
        
        for i in range(self.num_orders):
            action = random.choices(['ADD', 'CANCEL'], weights=[0.8, 0.2])[0]
            
            if action == 'CANCEL' and active_ids:
                # chọn một lệnh ngẫu nhiên đang tồn tại để hủy
                order_id_to_cancel = random.choice(active_ids)
                self.test_data.append(('CANCEL', order_id_to_cancel))
                active_ids.remove(order_id_to_cancel)
            else:
                # tạo lệnh đặt mới
                order_id = uuid.uuid4().hex[:8]
                symbol = random.choice(self.symbols)
                side = random.choice(['BUY', 'SELL'])
                order_type = random.choices(['LIMIT', 'MARKET'], weights=[0.9, 0.1])[0]
                price = round(random.uniform(20.0, 100.0), 2)
                quantity = random.randint(1, 100) * 100 # làm tròn theo lô 100 cổ phiếu
                
                order = Order(order_id, symbol, side, order_type, price, quantity)
                self.test_data.append(('ADD', order))
                active_ids.append(order_id)
                
        print("[*] Sinh dữ liệu hoàn tất.\n")

    def benchmark_naive(self) -> tuple:
        """
        Chạy thử nghiệm trên cấu trúc mảng thuần O(N).
        """
        print(f"[1] Đang chạy Benchmark trên Mảng thuần (Naive List) O(N)...")
        # chỉ dùng 1 sổ lệnh để test sự cồng kềnh của list
        naive_book = NaiveOrderBook("FPT")
        
        start_time = time.perf_counter()
        
        for action, payload in self.test_data:
            if action == 'ADD':
                naive_book.add_order(payload)
                # mô phỏng thao tác luôn phải dò tìm đỉnh như engine thật
                naive_book.get_best_bid()
            elif action == 'CANCEL':
                naive_book.cancel_order(payload)
                
        end_time = time.perf_counter()
        total_time = end_time - start_time
        return total_time

    def benchmark_optimized(self) -> tuple:
        """
        Chạy thử nghiệm trên kiến trúc Heap + Hash Map O(log N) của đồ án.
        """
        engine = MatchingEngine()
        
        start_time = time.perf_counter()
        
        for action, payload in self.test_data:
            if action == 'ADD':
                # đẩy thẳng vào engine để tự phân loại và khớp lệnh
                engine.process_order(payload)
            elif action == 'CANCEL':
                # quét các sổ để hủy lệnh
                for sym in engine.order_books:
                    if engine.cancel_order(sym, payload):
                        break
                        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        return total_time

    def run(self) -> None:
        """
        Thực thi toàn bộ bài test và in báo cáo ra màn hình.
        """
        self.generate_data()
        
        # chạy đồ án (với kiến trúc tối ưu)
        opt_time = self.benchmark_optimized()
        opt_throughput = self.num_orders / opt_time
        opt_latency_ms = (opt_time / self.num_orders) * 1000
        
        # chạy mảng thuần đối chứng
        naive_time = self.benchmark_naive()
        naive_throughput = self.num_orders / naive_time
        naive_latency_ms = (naive_time / self.num_orders) * 1000
        
        print("\n" + "="*50)
        print("KẾT QUẢ STRESS-TEST")
        print("="*50)
        
        print(f"Mảng thuần (Naive List O(N)):")
        print(f"   - Tổng thời gian : {naive_time:.4f} giây")
        print(f"   - Latency: {naive_latency_ms:.4f} ms/lệnh")
        print(f"   - Throughput: {naive_throughput:,.0f} lệnh/giây\n")
        
        print(f"Heap + Hash Map (Đồ án O(log N)):")
        print(f"   - Tổng thời gian : {opt_time:.4f} giây")
        print(f"   - Latency: {opt_latency_ms:.4f} ms/lệnh")
        print(f"   - Throughput: {opt_throughput:,.0f} lệnh/giây\n")
        
        speedup = naive_time / opt_time
        print(f"TỔNG KẾT: Kiến trúc mới nhanh gấp {speedup:.1f} lần so với mảng thuần")
        print("="*50)


if __name__ == "__main__":
    bot = StressTestBot(num_orders=50000)
    bot.run()
