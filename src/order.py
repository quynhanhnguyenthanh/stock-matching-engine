import time

class Order:
    __slots__ = ['order_id', 'is_buy', 'price', 'quantity', 'timestamp', 'is_canceled']

    def __init__(self, order_id: str, is_buy: bool, price: float, quantity: int):
        """
        Khởi tạo đối tượng lệnh giao dịch (Order).

        Args:
            order_id (str): Mã định danh duy nhất của lệnh.
            is_buy (bool): True nếu là lệnh Mua (Bid), False nếu là lệnh Bán (Ask).
            price (float): Mức giá đặt lệnh.
            quantity (int): Khối lượng giao dịch.

        Time Complexity: O(1)
        Space Complexity: O(1) - Nhờ sử dụng __slots__.
        """
        self.order_id = order_id
        self.is_buy = is_buy
        self.price = price
        self.quantity = quantity
        self.timestamp = time.time() 
        self.is_canceled = False     
