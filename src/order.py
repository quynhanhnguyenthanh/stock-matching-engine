class Order:
    __slots__ = ['order_id', 'is_buy', 'price', 'quantity', 'timestamp', 'is_canceled']
    
    def __init__(self, order_id: str, is_buy: bool, price: float, quantity: int, timestamp: float):
        self.order_id = order_id
        self.is_buy = is_buy 
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp
        self.is_canceled = False 
