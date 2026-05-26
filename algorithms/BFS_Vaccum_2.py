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
# THUẬT TOÁN BREADTH-FIRST-SEARCH (LOẠI 2)
# ==========================================
class BFS_Vaccum_2:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.start_robot_pos = (0, 0)
        
        self.grid = [
            [0, 0, 1, 0, 3],
            [1, 3, 0, 0, 0],
            [0, 0, 3, 1, 0],
            [0, 1, 0, 3, 0],
            [0, 0, 1, 0, 0]
        ]
        
        # Tìm tập hợp các ô robot có thể đi tới được (Loang để tránh kẹt rác trong tường)
        self.unreachable_dirt = set()
        self.reachable_tiles = self._get_reachable_tiles(self.start_robot_pos)
        
        initial_dirt = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 1:
                    if (i, j) in self.reachable_tiles:
                        initial_dirt.append((i, j))
                    else:
                        self.unreachable_dirt.add((i, j))
                        
        self.initial_dirt_tuple = tuple(sorted(initial_dirt))
        
        # Bản đồ mặc định ban đầu cho UI vẽ đồ họa khi khởi động
        self.start = copy.deepcopy(self.grid)
        self.start[self.start_robot_pos[0]][self.start_robot_pos[1]] = 2
        self.path = []

    def _get_reachable_tiles(self, start):
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
        Khớp chuẩn xác 100% từng dòng mã giả BFS LOẠI 2 trong ảnh slide mới
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
        frontier_states = {root_node.state} # Set bổ trợ kiểm tra nhanh trạng thái thuộc frontier
        
        # explored <- ∅
        explored = set()
        
        # while not EMPTY?(frontier) do
        while frontier:
            # node <- frontier.REMOVE()
            node = frontier.pop(0)
            frontier_states.remove(node.state)
            
            # explored <- explored ∪ {node.STATE}
            explored.add(node.state)
            
            # Lấy danh sách hành động khả thi tại node hiện tại
            rx, ry = node.state[0]
            dirt_tuple = node.state[1]
            
            actions = []
            if (rx, ry) in dirt_tuple:
                actions.append("SUCK")
            
            for move_name, (dx, dy) in [("Up", (-1, 0)), ("Down", (1, 0)), ("Left", (0, -1)), ("Right", (0, 1))]:
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                    actions.append(move_name)
            
            # for each action in problem.ACTIONS(node.STATE) do
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
                
                # if child.STATE ∉ explored ∧ child ∉ frontier then
                if child_state not in explored and child_state not in frontier_states:
                    
                    # if problem.GOAL-TEST(child.STATE) then return SOLUTION(child)
                    if len(child_state[1]) == 0:
                        self._reconstruct_path(child_node)
                        return child_node # Tìm thấy đích sớm ngay khi tạo node con!
                        
                    # frontier.INSERT(child)
                    frontier.append(child_node)
                    frontier_states.add(child_state)
                    
        return None # return failure

    def _reconstruct_path(self, goal_node):
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
            
            matrix = []
            for i in range(self.rows):
                row = []
                for j in range(self.cols):
                    if self.grid[i][j] == 3:
                        row.append(3)
                    else:
                        row.append(0)
                matrix.append(row)
                
            for (dx, dy) in dirt_tuple:
                matrix[dx][dy] = 1
            for (ux, uy) in self.unreachable_dirt:
                matrix[ux][uy] = 1
                
            matrix[rx][ry] = 2
            self.path.append((matrix, n.action))

    def get_path(self, node):
        return self.path