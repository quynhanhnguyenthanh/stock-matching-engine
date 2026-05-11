from core.order import Order
from core.order_book import OrderBook

class MatchingEngine:
    """
    Bộ máy khớp lệnh trung tâm.
    Quản lý nhiều sổ lệnh (OrderBook) cho nhiều mã cổ phiếu khác nhau và
    thực thi thuật toán đối khớp liên tục.
    """

    def __init__(self):
        # hash Map lưu trữ OrderBook theo từng mã cổ phiếu (Ví dụ: 'FPT' -> OrderBook('FPT'))
        self.order_books = {}
        
        # mảng lưu trữ lịch sử các giao dịch đã khớp thành công
        self.trades = []

    def process_order(self, order: Order) -> None:
        """
        Tiếp nhận lệnh mới, phân loại vào sổ lệnh tương ứng và kích hoạt thuật toán khớp lệnh.
        
        Quy tắc xử lý Market Order (Lệnh thị trường):
            - Nếu là BUY Market: Gán price = float('inf') (Mua bằng mọi giá).
            - Nếu là SELL Market: Gán price = 0.0 (Bán bằng mọi giá).
               
        Time Complexity: 
            O(log N) cho việc thêm lệnh + O(K * log N) cho việc khớp lệnh (K là số lượng lệnh đối ứng bị khớp).
        """
        # 1. nếu mã cổ phiếu này chưa có sổ lệnh, tạo mới
        if order.symbol not in self.order_books:
            self.order_books[order.symbol] = OrderBook(order.symbol)
            
        book = self.order_books[order.symbol]
        
        # 2. xử lý logic ép giá cho Market Order
        if order.order_type == 'MARKET':
            order.price = float('inf') if order.side == 'BUY' else 0.0

        # 3. đẩy lệnh vào sổ
        book.add_order(order)
        
        # 4. kích hoạt động cơ đối khớp
        self._match(book)

    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """
        Gọi hàm hủy lệnh (Lazy Deletion) trên sổ lệnh tương ứng.
        """
        if symbol in self.order_books:
            return self.order_books[symbol].cancel_order(order_id)
        return False

    def _match(self, book: OrderBook) -> None:
        """
        Vòng lặp đối khớp lệnh.
        Tuân thủ quy tắc: Giá mua >= Giá bán.
        """
        # vòng lặp chạy liên tục cho đến khi 2 bên không thể khớp được nữa
        while True:
            # lấy 2 lệnh tốt nhất ở đỉnh 2 Heap
            best_bid = book.get_best_bid()
            best_ask = book.get_best_ask()

            # dừng nếu 1 trong 2 bên trống
            if not best_bid or not best_ask:
                break

            # điều kiện tiên quyết: lệnh mua sẵn sàng trả mức giá lớn hơn hoặc bằng giá người bán đưa ra
            if best_bid.price >= best_ask.price:
                
                # 1. xác định giá khớp (Match Price):
                # theo luật chứng khoán, lệnh nào vào hệ thống trước (nằm chờ sẵn) sẽ được ưu tiên quyết định giá khớp.
                if best_bid.timestamp < best_ask.timestamp:
                    match_price = best_bid.price  # lệnh mua chờ sẵn, khách bán chủ động khớp
                else:
                    match_price = best_ask.price  # lệnh bán chờ sẵn, khách mua chủ động khớp
                
                # xử lý ngoại lệ cho Market Order (không lấy giá vô cực hoặc giá 0 làm giá khớp)
                if best_bid.order_type == 'MARKET': match_price = best_ask.price
                if best_ask.order_type == 'MARKET': match_price = best_bid.price

                # 2. xác định khối lượng khớp (Match Quantity):
                # là mức tối thiểu giữa số lượng muốn mua và số lượng muốn bán
                match_qty = min(best_bid.quantity, best_ask.quantity)

                # 3. thực thi trừ khối lượng trong object Order (O(1) do truyền tham chiếu)
                best_bid.quantity -= match_qty
                best_ask.quantity -= match_qty

                # 4. ghi nhận giao dịch thành công
                trade_record = {
                    'symbol': book.symbol,
                    'price': match_price,
                    'quantity': match_qty,
                    'buyer_id': best_bid.order_id,
                    'seller_id': best_ask.order_id
                }
                self.trades.append(trade_record)

                # tại đây KHÔNG gọi hàm xóa (pop) phần tử nào cả.
                # nếu best_bid hoặc best_ask đã bị trừ quantity về 0, 
                # ở vòng lặp while tiếp theo, khi gọi book.get_best_bid() hoặc get_best_ask(),
                # hàm _clean_heap của OrderBook sẽ tự động phát hiện quantity == 0 và xóa nó khỏi đỉnh Heap.
                
            else:
                # giá người mua trả đang thấp hơn giá người bán đòi -> không thể khớp, ngắt vòng lặp.
                break
