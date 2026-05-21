import random
import copy

# ==========================================
# CẤU TRÚC NODE THEO LÝ THUYẾT AI
# ==========================================
class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state  # Định dạng: ((rx, ry), tuple_các_vị_trí_rác)
        self.parent = parent
        self.action = action


# ==========================================
# THUẬT TOÁN BREADTH-FIRST-SEARCH
# ==========================================
class BFS_Vaccum_1:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.start_robot_pos = (0, 0)
        
        # Sinh sàn ngẫu nhiên tương tự bản mẫu trước
        self.grid = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                if (i, j) == self.start_robot_pos:
                    row.append(0)
                else:
                    # 65% ô sạch (0), 20% ô rác (1), 15% ô tường/vật cản (3)
                    cell_type = random.choices([0, 1, 3], weights=[65, 20, 15])[0]
                    row.append(cell_type)
            self.grid.append(row)
        
        # Tìm tập hợp các ô robot thực sự có thể đi tới được (Loang BFS)
        self.unreachable_dirt = set()
        self.reachable_tiles = self._get_reachable_tiles(self.start_robot_pos)
        
        # Phân loại rác khả thi để nạp vào trạng thái BFS
        initial_dirt = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 1:
                    if (i, j) in self.reachable_tiles:
                        initial_dirt.append((i, j))
                    else:
                        self.unreachable_dirt.add((i, j))
                        
        self.initial_dirt_tuple = tuple(sorted(initial_dirt))
        
        # Bản đồ mặc định ban đầu để UI vẽ đồ họa khi khởi động
        self.start = copy.deepcopy(self.grid)
        self.start[self.start_robot_pos[0]][self.start_robot_pos[1]] = 2
        self.path = []

    def _get_reachable_tiles(self, start):
        """Hàm bổ trợ tìm các ô có thể đi tới để tránh kẹt rác trong tường"""
        queue = [start]
        reachable = set([start])
        while queue:
            x, y = queue.pop(0)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                    if (nx, ny) not in reachable:
                        reachable.add((nx, ny))
                        queue.append((nx, ny))
        return reachable

    def solve(self):
        """
        Khớp chuẩn xác 100% từng dòng mã giả BREADTH-FIRST-SEARCH trong ảnh slide
        """
        # node <- NODE(problem.INITIAL)
        initial_state = (self.start_robot_pos, self.initial_dirt_tuple)
        root_node = Node(initial_state, parent=None, action="START")
        
        # if problem.GOAL-TEST(node.STATE) then return SOLUTION(node)
        if len(root_node.state[1]) == 0:
            self.path = [(copy.deepcopy(self.start), "START")]
            return root_node
            
        # frontier <- FIFO-QUEUE()
        frontier = [root_node]
        frontier_states = {root_node.state} # Set bổ trợ kiểm tra nhanh: child ∉ frontier
        
        # reached <- ∅
        reached = set()
        
        # while not EMPTY?(frontier) do
        while frontier:
            # node <- frontier.REMOVE()
            node = frontier.pop(0)
            frontier_states.remove(node.state)
            
            # reached <- reached ∪ {node.STATE}
            reached.add(node.state)
            
            # if problem.GOAL-TEST(node.STATE) then return SOLUTION(node)
            if len(node.state[1]) == 0:
                self._reconstruct_path(node)
                return node  # Trả về đích thành công cho UI nhận diện
                
            # for each action in problem.ACTIONS(node.STATE) do
            rx, ry = node.state[0]
            dirt_tuple = node.state[1]
            
            actions = []
            # Nếu ô hiện tại có rác khả thi -> Thêm hành động hút
            if (rx, ry) in dirt_tuple:
                actions.append("SUCK")
            
            # Các hành động di chuyển hợp lệ xung quanh
            for move_name, (dx, dy) in [("Up", (-1, 0)), ("Down", (1, 0)), ("Left", (0, -1)), ("Right", (0, 1))]:
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                    actions.append(move_name)
                    
            for action in actions:
                # child <- CHILD-NODE(problem, node, action)
                child_rx, child_ry = rx, ry
                child_dirt = dirt_tuple
                
                if action == "SUCK":
                    child_dirt = tuple(d for d in dirt_tuple if d != (rx, ry))
                elif action == "Up": child_rx -= 1
                elif action == "Down": child_rx += 1
                elif action == "Left": child_ry -= 1
                elif action == "Right": child_ry += 1
                
                child_state = ((child_rx, child_ry), child_dirt)
                child_node = Node(child_state, parent=node, action=action)
                
                # if child.STATE ∉ reached ∧ child ∉ frontier then
                if child_state not in reached and child_state not in frontier_states:
                    # frontier.INSERT(child)
                    frontier.append(child_node)
                    frontier_states.add(child_state)
                    
        return None # return failure (Không tìm thấy lời giải)

    def _reconstruct_path(self, goal_node):
        """Truy vết ngược từ đích về root để tạo danh sách hành trình phục vụ vẽ UI animation"""
        nodes_path = []
        curr = goal_node
        while curr is not None:
            nodes_path.append(curr)
            curr = curr.parent
        nodes_path.reverse()
        
        self.path = []
        for n in nodes_path:
            rx, ry = n.state[0]
            dirt_tuple = n.state[1]
            
            # Khởi tạo ma trận rỗng dựa trên các ô tường cố định ban đầu
            matrix = []
            for i in range(self.rows):
                row = []
                for j in range(self.cols):
                    if self.grid[i][j] == 3:
                        row.append(3)
                    else:
                        row.append(0)
                matrix.append(row)
                
            # Vẽ lại các hạt rác khả thi chưa dọn tại bước này
            for (dx, dy) in dirt_tuple:
                matrix[dx][dy] = 1
                
            # Giữ nguyên hiển thị các hạt rác bất khả thi kẹt trong tường để nhìn trực quan
            for (ux, uy) in self.unreachable_dirt:
                matrix[ux][uy] = 1
                
            # Đặt robot vào vị trí hiện hành
            matrix[rx][ry] = 2
            
            self.path.append((matrix, n.action))

    def get_path(self, node):
        return self.path