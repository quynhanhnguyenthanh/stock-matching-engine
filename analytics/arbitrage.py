import math

class ArbitrageDetector:
    """
    công cụ phát hiện cơ hội kinh doanh chênh lệch giá (Arbitrage) 
    dựa trên đồ thị có hướng và thuật toán Bellman-Ford.
    """
    def __init__(self, symbols: list):
        """
        khởi tạo đồ thị với danh sách các loại tài sản/tiền tệ (đỉnh).
        """
        self.symbols = symbols
        # lưu trữ tỷ giá gốc: graph[u][v] = rate
        self.graph = {symbol: {} for symbol in symbols}

    def add_exchange_rate(self, base: str, quote: str, rate: float) -> None:
        """
        cập nhật tỷ giá hối đoái. ví dụ: base='USD', quote='VND', rate=25000
        """
        if rate <= 0:
            return
        self.graph[base][quote] = rate

    def detect_arbitrage(self) -> list:
        """
        thuật toán Bellman-Ford để tìm chu trình âm (Negative Cycle).
        
        toán học đằng sau:
            ta muốn tìm chu trình sao cho: R1 * R2 * ... * Rn > 1 (lời).
            logarit 2 vế: log(R1) + log(R2) + ... + log(Rn) > 0.
            nhân với -1: -log(R1) - log(R2) - ... - log(Rn) < 0.
            => bài toán biến thành tìm "chu trình có tổng trọng số âm" trên đồ thị.
            
        Time Complexity: 
            O(V * E) - V là số đỉnh (tài sản), E là số cạnh (cặp tỷ giá).
        """
        # khởi tạo mảng khoảng cách và mảng truy vết 
        dist = {node: float('inf') for node in self.symbols}
        parent = {node: None for node in self.symbols}
        
        # chọn node đầu tiên làm điểm bắt đầu
        source = self.symbols[0]
        dist[source] = 0

        # chuẩn bị danh sách các cạnh (u, v, weight)
        edges = []
        for u in self.graph:
            for v, rate in self.graph[u].items():
                # trọng số cạnh = -log(rate)
                weight = -math.log(rate)
                edges.append((u, v, weight))

        # bước 1: nới lỏng các cạnh V - 1 lần
        v_count = len(self.symbols)
        for _ in range(v_count - 1):
            for u, v, weight in edges:
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    parent[v] = u

        # bước 2: kiểm tra chu trình âm ở lần lặp thứ V
        arbitrage_cycle = []
        for u, v, weight in edges:
            if dist[u] + weight < dist[v]:
                # phát hiện chu trình âm bắt đầu truy vết ngược để lấy đường đi
                cycle_node = v
                # đi ngược v_count lần để chắc chắn rớt vào bên trong cái vòng lặp 
                for _ in range(v_count):
                    cycle_node = parent[cycle_node]
                
                # gom các node trong chu trình lại
                start_node = cycle_node
                arbitrage_cycle.append(start_node)
                curr = parent[start_node]
                while curr != start_node:
                    arbitrage_cycle.append(curr)
                    curr = parent[curr]
                arbitrage_cycle.append(start_node)
                
                # đảo ngược danh sách để ra thứ tự đi đúng
                arbitrage_cycle.reverse()
                return arbitrage_cycle # trả về cơ hội đầu tiên tìm thấy

        # không có cơ hội arbitrage nào
        return []
