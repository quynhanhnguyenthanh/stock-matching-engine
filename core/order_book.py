import heapq
from core.order import Order

class OrderBook:
    """
    Quản lý sổ lệnh (Order Book) bằng Heap và Hash Map.
    Cấu trúc này đảm bảo khớp lệnh siêu tốc và hủy lệnh O(1).
    """

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.buy_heap = []  
        self.sell_heap = [] 
        self.orders_map = {}

    def add_order(self, order: Order) -> None:
        """
        Thêm lệnh mới vào Sổ lệnh.
        
        Args:
            order (Order): Đối tượng lệnh giao dịch.
            
        Time Complexity: 
            O(log N) - Do thao tác đẩy vào Heap (heappush).
            O(1) - Lưu vào Hash Map.
        """
        # lưu vào Hash Map
        self.orders_map[order.order_id] = order
        
        # đẩy vào Heap tương ứng
        if order.side == 'BUY':
            # -> giá tốt nhất lên đầu. Nếu giá bằng nhau, timestamp nhỏ hơn lên đầu.
            heapq.heappush(self.buy_heap, [-order.price, order.timestamp, order.order_id])
        elif order.side == 'SELL':
            # bán thì dùng Min-Heap bình thường: Giá càng rẻ càng nằm trên đỉnh.
            heapq.heappush(self.sell_heap, [order.price, order.timestamp, order.order_id])

    def cancel_order(self, order_id: str) -> bool:
        """
        Hủy lệnh bằng phương pháp Lazy Deletion.
        
        Time Complexity: 
            O(1) - Chỉ cần tìm trong Hash Map và đổi cờ trạng thái.
        """
        if order_id in self.orders_map:
            order = self.orders_map[order_id]
            # kích hoạt cờ Lazy Deletion từ class Order
            order.cancel()
            return True
        return False

    def _clean_buy_heap(self) -> None:
        """
        [Hàm nội bộ] Dọn dẹp các lệnh đã hủy trên đỉnh Buy Heap.
        Đẩy các lệnh "rác" ra ngoài cho đến khi đỉnh Heap là một lệnh hợp lệ.
        
        Time Complexity:
            O(log N) cho mỗi lệnh bị hủy được pop ra.
        """
        while self.buy_heap:
            best_buy_id = self.buy_heap[0][2] # lấy order_id ở đỉnh Heap
            order = self.orders_map.get(best_buy_id)
            
            if order is None or order.is_canceled or order.quantity == 0:
                heapq.heappop(self.buy_heap)
                if order and order.quantity == 0:
                     self.orders_map.pop(best_buy_id, None)
            else:
                break

    def _clean_sell_heap(self) -> None:
        """
        [Hàm nội bộ] Dọn dẹp các lệnh đã hủy trên đỉnh Sell Heap.
        """
        while self.sell_heap:
            best_sell_id = self.sell_heap[0][2]
            order = self.orders_map.get(best_sell_id)
            
            if order is None or order.is_canceled or order.quantity == 0:
                heapq.heappop(self.sell_heap)
                if order and order.quantity == 0:
                    self.orders_map.pop(best_sell_id, None)
            else:
                break

    def get_best_bid(self) -> Order:
        """
        Lấy lệnh Mua có giá cao nhất (Best Bid).
        
        Time Complexity: 
            O(1) - Amortized (Trung bình) do chỉ nhìn vào đỉnh Heap.
        """
        self._clean_buy_heap()
        if self.buy_heap:
            best_buy_id = self.buy_heap[0][2]
            return self.orders_map[best_buy_id]
        return None

    def get_best_ask(self) -> Order:
        """
        Lấy lệnh Bán có giá thấp nhất (Best Ask).
        
        Time Complexity: 
            O(1) - Amortized (Trung bình) do chỉ nhìn vào đỉnh Heap.
        """
        self._clean_sell_heap()
        if self.sell_heap:
            best_sell_id = self.sell_heap[0][2]
            return self.orders_map[best_sell_id]
        return None
