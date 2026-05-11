class SegmentTree:
    """
    cấu trúc dữ liệu segment tree dùng để phân tích kỹ thuật (Technical Analysis).
    xử lý các truy vấn khoảng (Range Queries) cho: Max Price, Min Price, Total Volume.
    """
    def __init__(self, data: list):
        """
        khởi tạo segment tree từ mảng dữ liệu lịch sử nến (candles).
        data là danh sách các dict chứa: {'high': float, 'low': float, 'volume': int}
        """
        self.n = len(data)
        # mảng 4N là kích thước an toàn tối đa cho segment tree
        self.tree = [{'high': 0.0, 'low': float('inf'), 'volume': 0} for _ in range(4 * self.n)]
        if self.n > 0:
            self._build(data, 0, 0, self.n - 1)

    def _build(self, data: list, node: int, start: int, end: int) -> None:
        """
        [hàm nội bộ] đệ quy xây dựng cây từ dưới lên.
        
        Time Complexity: O(N) - chỉ tốn thời gian ở bước khởi tạo ban đầu.
        """
        if start == end:
            # lá của cây chứa dữ liệu của 1 thời điểm cụ thể
            self.tree[node] = {
                'high': data[start]['high'],
                'low': data[start]['low'],
                'volume': data[start]['volume']
            }
            return

        mid = (start + end) // 2
        left_child = 2 * node + 1
        right_child = 2 * node + 2

        # đệ quy xây 2 nhánh
        self._build(data, left_child, start, mid)
        self._build(data, right_child, mid + 1, end)

        # tổng hợp dữ liệu từ 2 nhánh con lên node cha
        self.tree[node]['high'] = max(self.tree[left_child]['high'], self.tree[right_child]['high'])
        self.tree[node]['low'] = min(self.tree[left_child]['low'], self.tree[right_child]['low'])
        self.tree[node]['volume'] = self.tree[left_child]['volume'] + self.tree[right_child]['volume']

    def _query(self, node: int, start: int, end: int, l: int, r: int) -> dict:
        """
        [hàm nội bộ] đệ quy truy vấn dữ liệu.
        """
        # trường hợp nằm hoàn toàn ngoài khoảng truy vấn
        if r < start or end < l:
            return {'high': 0.0, 'low': float('inf'), 'volume': 0}
            
        # trường hợp nằm hoàn toàn trong khoảng truy vấn
        if l <= start and end <= r:
            return self.tree[node]

        # trường hợp giao nhau, tiếp tục chia đôi để tìm
        mid = (start + end) // 2
        left_res = self._query(2 * node + 1, start, mid, l, r)
        right_res = self._query(2 * node + 2, mid + 1, end, l, r)

        return {
            'high': max(left_res['high'], right_res['high']),
            'low': min(left_res['low'], right_res['low']),
            'volume': left_res['volume'] + right_res['volume']
        }

    def query_range(self, l: int, r: int) -> dict:
        """
        truy vấn khoảng: lấy giá cao nhất, thấp nhất và tổng khối lượng từ thời điểm L đến R.
        
        Args:
            l: index bắt đầu.
            r: index kết thúc.
            
        Time Complexity: O(log N) - cực kỳ nhanh, đáp ứng realtime cho biểu đồ.
        """
        if l < 0 or r >= self.n or l > r:
            raise ValueError("khoảng truy vấn không hợp lệ")
        return self._query(0, 0, self.n - 1, l, r)
