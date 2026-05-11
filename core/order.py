import time

class Order:
    """
    Đại diện cho một lệnh giao dịch trên hệ thống Stock Matching Engine.
    
    Tối ưu hóa:
        Sử dụng cơ chế `__slots__` để vô hiệu hóa `__dict__` mặc định của class trong Python.
        Việc này giúp cố định cấu trúc bộ nhớ, giảm khoảng 40-50% dung lượng RAM tiêu thụ 
        trên mỗi object và tăng tốc độ truy xuất thuộc tính. Đây là kỹ thuật 
        quan trọng trong các hệ thống khớp lệnh khi phải nạp hàng triệu lệnh vào RAM.
    """
    
    __slots__ = [
        'order_id',    # mã định danh duy nhất của lệnh (str)
        'symbol',      # mã cổ phiếu (ví dụ: 'VNM', 'FPT') (str)
        'side',        # hướng giao dịch: 'BUY' (Mua) hoặc 'SELL' (Bán) (str)
        'order_type',  # loại lệnh: 'LIMIT' (Giới hạn) hoặc 'MARKET' (Thị trường) (str)
        'price',       # giá đặt lệnh (float)
        'quantity',    # khối lượng đặt lệnh (int)
        'timestamp',   # dấu thời gian để xét ưu tiên (Time Priority) (float)
        'is_canceled'  # cờ đánh dấu lệnh đã bị hủy cho thuật toán Lazy Deletion (bool)
    ]

    def __init__(self, order_id: str, symbol: str, side: str, order_type: str, price: float, quantity: int, timestamp: float = None):
        """
        Khởi tạo một đối tượng lệnh giao dịch mới.
        
        Args:
            order_id: Mã định danh của lệnh.
            symbol: Tên mã chứng khoán.
            side: 'BUY' hoặc 'SELL'.
            order_type: 'LIMIT' hoặc 'MARKET'.
            price: Giá của lệnh. Với Market Order, giá có thể để mặc định là 0 hoặc cực lớn/nhỏ.
            quantity: Số lượng cổ phiếu.
            timestamp: Thời gian đặt lệnh. Nếu không truyền sẽ lấy thời gian hệ thống.
            
        Time Complexity: 
            O(1) - Khởi tạo các thuộc tính trực tiếp.
        Space Complexity: 
            O(1) - Kích thước object được cố định bởi __slots__.
        """
        self.order_id = order_id
        self.symbol = symbol.upper()
        self.side = side.upper()
        self.order_type = order_type.upper()
        self.price = float(price)
        self.quantity = int(quantity)
        
        # nếu được bơm từ data csv (bot) thì dùng timestamp của data, 
        # nếu tạo trực tiếp (live) thì lấy thời gian hiện tại của máy
        self.timestamp = timestamp if timestamp is not None else time.time()
        
        # mặc định lệnh sinh ra là chưa bị hủy
        self.is_canceled = False

    def cancel(self) -> None:
        """
        Thực hiện hủy lệnh bằng kỹ thuật Lazy Deletion.
        
        Thay vì phải duyệt qua cấu trúc cây/mảng để xóa phần tử (tốn O(N)), 
        hàm này chỉ cần bật cờ trạng thái. Khi thuật toán Matching Engine 
        lấy lệnh này ra khỏi đỉnh Heap, nó sẽ kiểm tra cờ này và bỏ qua nếu True.
        
        Time Complexity: 
            O(1) - Chỉ thay đổi giá trị một biến boolean.
        """
        self.is_canceled = True

    def __repr__(self) -> str:
        """
        Định dạng chuỗi in ra terminal để dễ dàng Debug và log hệ thống.
        
        Time Complexity: 
            O(1)
        """
        status = "CANCELED" if self.is_canceled else "ACTIVE"
        return f"<Order {self.order_id} | {self.side} {self.quantity} {self.symbol} @ {self.price} | {self.order_type} | {status}>"
