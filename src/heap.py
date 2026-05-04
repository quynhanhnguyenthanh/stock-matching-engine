class Heap:
    def __init__(self, compare_func):
        """
        Khởi tạo Cấu trúc dữ liệu Heap trên mảng 1 chiều.

        Args:
            compare_func (Callable): Hàm xác định độ ưu tiên giữa 2 node. 
                                     Trả về True nếu node 1 ưu tiên hơn node 2.
        """
        self.data = []
        self.compare = compare_func

    def push(self, order):
        """
        Thêm một lệnh mới vào Heap.

        Time Complexity: O(log n) - do quá trình sift_up.
        Space Complexity: O(1) - thao tác trên mảng hiện tại.
        """
        self.data.append(order)
        self._sift_up(len(self.data) - 1)

    def pop(self):
        """
        Lấy và xóa phần tử ưu tiên nhất ra khỏi đỉnh Heap.

        Returns:
            Order: Lệnh ưu tiên nhất. Trả về None nếu Heap rỗng.

        Time Complexity: O(log n) - do quá trình sift_down.
        """
        if not self.data:
            return None
        if len(self.data) == 1:
            return self.data.pop()
        
        top = self.data[0]
        self.data[0] = self.data.pop() 
        self._sift_down(0)
        return top

    def peek(self):
        """
        Xem phần tử ở đỉnh Heap mà không xóa.

        Time Complexity: O(1)
        """
        return self.data[0] if self.data else None

    def _sift_up(self, idx):
        parent = (idx - 1) // 2
        while idx > 0 and self.compare(self.data[idx], self.data[parent]):
            self.data[idx], self.data[parent] = self.data[parent], self.data[idx]
            idx = parent
            parent = (idx - 1) // 2

    def _sift_down(self, idx):
        n = len(self.data)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            largest_or_smallest = idx

            if left < n and self.compare(self.data[left], self.data[largest_or_smallest]):
                largest_or_smallest = left
            if right < n and self.compare(self.data[right], self.data[largest_or_smallest]):
                largest_or_smallest = right

            if largest_or_smallest != idx:
                self.data[idx], self.data[largest_or_smallest] = self.data[largest_or_smallest], self.data[idx]
                idx = largest_or_smallest
            else:
                break

def bid_compare(o1, o2):
    if o1.price != o2.price:
        return o1.price > o2.price
    return o1.timestamp < o2.timestamp

def ask_compare(o1, o2):
    if o1.price != o2.price:
        return o1.price < o2.price
    return o1.timestamp < o2.timestamp
