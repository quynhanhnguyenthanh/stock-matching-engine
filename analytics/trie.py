class TrieNode:
    """
    nút của cây tiền tố.
    áp dụng __slots__ để tiết kiệm RAM nếu nạp hàng chục nghìn mã chứng khoán.
    """
    __slots__ = ['children', 'is_end_of_word']

    def __init__(self):
        # lưu các node con dưới dạng hash map (dict)
        self.children = {}
        # cờ đánh dấu kết thúc một mã hợp lệ (ví dụ: gõ tới 'VNM' là kết thúc)
        self.is_end_of_word = False

class Trie:
    """
    cấu trúc dữ liệu trie (cây tiền tố) để gợi ý mã cổ phiếu (autocomplete).
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """
        chèn một mã cổ phiếu mới vào cây.
        
        Time Complexity: 
            O(L) - L là độ dài của từ khóa.
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def _dfs(self, node: TrieNode, prefix: str, results: list, limit: int) -> None:
        """
        thuật toán tìm kiếm theo chiều sâu (DFS) để gom các kết quả gợi ý.
        """
        if len(results) >= limit:
            return
        if node.is_end_of_word:
            results.append(prefix)
            
        for char, child_node in node.children.items():
            self._dfs(child_node, prefix + char, results, limit)

    def autocomplete(self, prefix: str, limit: int = 10) -> list:
        """
        tìm và trả về danh sách các mã cổ phiếu bắt đầu bằng tiền tố (prefix).
        
        Args:
            prefix: chuỗi người dùng đang gõ (ví dụ: 'VC').
            limit: số lượng kết quả tối đa trả về.
            
        Time Complexity: 
            O(L + V) - L là độ dài tiền tố, V là số lượng node con trùng khớp.
            cực kỳ nhanh so với việc lặp mảng O(N).
        """
        node = self.root
        prefix = prefix.upper()
        
        # duyệt tới node cuối cùng của tiền tố
        for char in prefix:
            if char not in node.children:
                return [] # không tìm thấy mã nào
            node = node.children[char]
            
        # từ node đó, quét DFS để lấy các nhánh con
        results = []
        self._dfs(node, prefix, results, limit)
        return results
