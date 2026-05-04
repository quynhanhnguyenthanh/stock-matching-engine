from .order import Order
from .heap import Heap, bid_compare, ask_compare

class OrderBook:
    def __init__(self):
        """
        Khởi tạo Sổ lệnh (OrderBook) và Matching Engine.
        """
        self.bids = Heap(bid_compare) 
        self.asks = Heap(ask_compare) 
        self.orders_map = {}          
        self.trades = []              

    def add_order(self, order_id: str, is_buy: bool, price: float, quantity: int):
        """
        Thêm lệnh mới vào sổ lệnh và tiến hành khớp lệnh tự động.

        Time Complexity: O(log n) cho việc thêm vào Heap, O(1) cho Hash Map.
        """
        order = Order(order_id, is_buy, price, quantity)
        self.orders_map[order_id] = order

        if is_buy:
            self.bids.push(order)
        else:
            self.asks.push(order)
            
        self._match()

    def cancel_order(self, order_id: str) -> bool:
        """
        Hủy lệnh bằng kỹ thuật Lazy Deletion.

        Time Complexity: O(1) - Chỉ cần đổi trạng thái cờ trên Hash Map.
        """
        if order_id in self.orders_map:
            order = self.orders_map[order_id]
            if not order.is_canceled and order.quantity > 0:
                order.is_canceled = True
                return True
        return False

    def _clean_top(self, heap: Heap):
        """
        Loại bỏ các lệnh đã bị hủy (Lazy Deletion) hoặc hết khối lượng ở đỉnh Heap.
        
        Time Complexity: Tương đương O(log n) mỗi lần pop.
        """
        while heap.peek() and (heap.peek().is_canceled or heap.peek().quantity == 0):
            heap.pop()

    def _match(self):
        """
        Thuật toán đối khớp lệnh liên tục.
        Duyệt đỉnh của 2 Heap, nếu Bid >= Ask thì khớp.

        Time Complexity: O(k log n) với k là số lệnh được khớp thành công.
        """
        self._clean_top(self.bids)
        self._clean_top(self.asks)

        while self.bids.peek() and self.asks.peek():
            best_bid = self.bids.peek()
            best_ask = self.asks.peek()

            if best_bid.price >= best_ask.price:
                match_qty = min(best_bid.quantity, best_ask.quantity)
                match_price = best_bid.price if best_bid.timestamp < best_ask.timestamp else best_ask.price

                best_bid.quantity -= match_qty
                best_ask.quantity -= match_qty

                self.trades.append({
                    "buyer_id": best_bid.order_id,
                    "seller_id": best_ask.order_id,
                    "price": match_price,
                    "quantity": match_qty
                })

                self._clean_top(self.bids)
                self._clean_top(self.asks)
            else:
                break 
