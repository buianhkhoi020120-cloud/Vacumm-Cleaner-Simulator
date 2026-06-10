import copy
from collections import deque

# Node lưu CẢ MỘT TẬP HỢP các trạng thái có thể xảy ra
class BeliefState_Node:
    def __init__(self, belief_state, parent=None, action=None):
        self.state = belief_state  # Định dạng: tuple( ((rx, ry), tuple_rac), ... )
        self.parent = parent
        self.action = action

class BeliefState_BFS_Vaccum:
    def __init__(self, rows=4, cols=4):
        self.rows = rows
        self.cols = cols
        self.grid = [
            [0, 1, 0, 3],
            [3, 0, 1, 0],
            [0, 0, 0, 3],
            [0, 1, 0, 0]
        ]
        initial_dirt = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 1:
                    initial_dirt.append((i, j))
        self.initial_dirt_tuple = tuple(sorted(initial_dirt))
        # ==========================================================
        # 1. TẠO TẬP NIỀM TIN BAN ĐẦU (INITIAL BELIEF STATE)
        # Giả định robot không biết mình ở đâu, nhưng nó đoán nó ở 
        # 1 trong 2 vị trí bắt đầu khả thi.
        # ==========================================================
        possible_starts = [(0, 0), (2, 0)]
        initial_belief = []
        for pos in possible_starts:
            initial_belief.append((pos, self.initial_dirt_tuple))
        # Ép kiểu về tuple đã sắp xếp để có thể so sánh và băm (hash)
        self.initial_belief_state = tuple(sorted(initial_belief))
        # Khởi tạo bản đồ ảo cho UI
        self.start = self._make_ui_matrix(self.initial_belief_state)
        self.path = []

    def _make_ui_matrix(self, belief_state):
        """Vẽ hiển thị: Rác thực tế và các 'Bóng ma' robot có thể tồn tại"""
        matrix = [[3 if self.grid[i][j] == 3 else 0 for j in range(self.cols)] for i in range(self.rows)]
        # Vẽ rác (Nếu rác tồn tại ở bất kỳ vũ trụ nào, cứ vẽ ra)
        for phys in belief_state:
            for dx, dy in phys[1]:
                if matrix[dx][dy] != 3: 
                    matrix[dx][dy] = 1
        # Vẽ các "Bóng ma" Robot tại mọi vị trí có thể
        for phys in belief_state:
            matrix[phys[0][0]][phys[0][1]] = 2
        return matrix

    def apply_action(self, belief_state, action):
        """
        Áp dụng 1 hành động lên TẤT CẢ các trạng thái trong Belief State.
        """
        new_belief = set()
        for phys in belief_state:
            rx, ry = phys[0]
            dirt = phys[1]
            if action == "SUCK":
                # Nếu hút, rác tại vị trí đó biến mất
                new_dirt = tuple(d for d in dirt if d != (rx, ry))
                new_belief.add(((rx, ry), new_dirt))
            else:
                dx, dy = 0, 0
                if action == "Up": dx = -1
                elif action == "Down": dx = 1
                elif action == "Left": dy = -1
                elif action == "Right": dy = 1
                nx, ny = rx + dx, ry + dy
                # Nếu đi hợp lệ -> Tọa độ mới. Nếu đụng tường -> Tọa độ cũ (Đứng im)
                if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                    new_belief.add(((nx, ny), dirt))
                else:
                    new_belief.add(((rx, ry), dirt))   
        # Sắp xếp và trả về Tuple mới
        return tuple(sorted(list(new_belief)))

    def solve(self):
        """
        Dùng thuật toán cũ (BFS) duyệt trên không gian Belief State
        """
        root_node = BeliefState_Node(self.initial_belief_state, parent=None, action="START")
        # Điều kiện đích: TẤT CẢ các vũ trụ song song đều phải sạch bóng rác
        if all(len(phys[1]) == 0 for phys in root_node.state):
            self._reconstruct_path(root_node)
            return root_node   
        frontier = deque([root_node])
        explored = set([root_node.state])
        while frontier:
            node = frontier.popleft()
            for action in ["Up", "Down", "Left", "Right", "SUCK"]:
                # 2. CHẠY ĐỂ TÌM KẾT QUẢ: Sinh tập niềm tin mới sau khi hành động
                child_state = self.apply_action(node.state, action)
                if child_state not in explored:
                    child_node = BeliefState_Node(child_state, parent=node, action=action)
                    explored.add(child_state)
                    # Kiểm tra đích: Liệu tập niềm tin này có chắc chắn 100% sạch rác chưa?
                    if all(len(phys[1]) == 0 for phys in child_state):
                        self._reconstruct_path(child_node)
                        return child_node
                    frontier.append(child_node)   
        return None

    def _reconstruct_path(self, goal_node):
        nodes_path = []
        curr = goal_node
        while curr is not None:
            nodes_path.append(curr)
            curr = curr.parent
        nodes_path.reverse()
        self.path = []
        for n in nodes_path:
            matrix = self._make_ui_matrix(n.state)
            # Log ra số lượng "bóng ma" để thấy sự hội tụ niềm tin
            belief_size = len(n.state)
            action_display = f"{n.action} (Tin vào {belief_size} vị trí)" if n.action != "START" else f"START ({belief_size} vị trí)"
            self.path.append((matrix, action_display))

    def get_path(self, node=None):
        return self.path