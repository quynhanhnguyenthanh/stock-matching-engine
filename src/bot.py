import random
import time
import uuid
from .orderbook import OrderBook

class TradingBot:
    def __init__(self, orderbook: OrderBook, base_price: float, spread: float = 500):
        self.orderbook = orderbook
        self.base_price = base_price
        self.spread = spread

    def generate_random_orders(self, num_orders: int):
        """Tạo test data để ép tải hệ thống."""
        for _ in range(num_orders):
            order_id = str(uuid.uuid4())[:8] 
            is_buy = random.choice([True, False]) 
            
            price = round(self.base_price + random.uniform(-self.spread, self.spread), 2)
            
            quantity = random.randint(1, 50) * 100 

            self.orderbook.add_order(order_id, is_buy, price, quantity)

    def run_continuous(self, interval: float = 0.5):
        print(">>> Bot started. Bấm Ctrl+C để dừng nha.")
        try:
            while True:
                self.generate_random_orders(1)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n>>> Bot stopped.")
