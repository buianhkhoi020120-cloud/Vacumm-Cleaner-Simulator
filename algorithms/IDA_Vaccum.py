import copy

class IDA_Node:
    def __init__(self, state, parent=None, action=None, g=0, h=0):
        self.state = state  # ((rx, ry), tuple_các_vị_trí_rác)
        self.parent = parent
        self.action = action
        self.g = g          # Chi phí thực tế đi từ gốc g(n)
        self.h = h          # Heuristic h(n)
        self.f = g + h      # f(n) = g(n) + h(n)


class IDA_Vaccum:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.start_robot_pos = (0, 0)
        self.grid = [
            [0, 1, 0, 0, 3],
            [0, 3, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [1, 0, 3, 0, 0],
            [3, 1, 1, 3, 0]
        ]
        # Loang cô lập rác kẹt trong tường
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

    def _calculate_heuristic(self, pos, dirt_tuple):
        if not dirt_tuple:
            return 0
        rx, ry = pos
        return sum(abs(rx - dx) + abs(ry - dy) for dx, dy in dirt_tuple)

    def solve(self):
        initial_state = (self.start_robot_pos, self.initial_dirt_tuple)
        init_h = self._calculate_heuristic(initial_state[0], initial_state[1])
        root_node = IDA_Node(initial_state, parent=None, action="START", g=0, h=init_h)
        # Khởi tạo ngưỡng ban đầu bằng f(root)
        threshold = root_node.f
        while True:
            #  tránh lặp trạng thái TRÊN CÙNG MỘT NHÁNH DUYỆT 
            path_set = set([root_node.state])
            # Gọi hàm duyệt DFS đệ quy
            result, next_threshold = self._search(root_node, threshold, path_set)
            if isinstance(result, IDA_Node): # Nếu tìm thấy Node đích
                self._reconstruct_path(result)
                return result
            if next_threshold == float('inf'): # Duyệt hết toàn bộ cây mà không có lời giải
                return None
            # Cập nhật ngưỡng lớn hơn cho vòng lặp tiếp theo
            threshold = next_threshold

    def _search(self, node, threshold, path_set):
        if node.f > threshold:
            return "CUTOFF", node.f # Bị chặt cụt và trả về giá trị f để làm ngưỡng tiếp theo
        if len(node.state[1]) == 0:
            return node, threshold # Đạt đích!
        min_cutoff = float('inf')
        rx, ry = node.state[0]
        dirt_tuple = node.state[1]
        actions = []
        if (rx, ry) in dirt_tuple:
            actions.append("SUCK")
        for move_name, (dx, dy) in [("Up", (-1, 0)), ("Down", (1, 0)), ("Left", (0, -1)), ("Right", (0, 1))]:
            nx, ny = rx + dx, ry + dy
            if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                actions.append(move_name)
        for action in actions:
            child_rx, child_ry = rx, ry
            child_dirt = dirt_tuple
            if action == "SUCK":
                child_dirt = tuple(d for d in dirt_tuple if d != (rx, ry))
            elif action == "Up": child_rx -= 1
            elif action == "Down": child_rx += 1
            elif action == "Left": child_ry -= 1
            elif action == "Right": child_ry += 1
            child_state = ((child_rx, child_ry), child_dirt)
            # Chỉ đi tiếp nếu trạng thái này chưa có ở tổ tiên của nhánh hiện tại
            if child_state not in path_set:
                child_g = node.g + 1
                child_h = self._calculate_heuristic(child_state[0], child_state[1])
                child_node = IDA_Node(child_state, parent=node, action=action, g=child_g, h=child_h)
                path_set.add(child_state)
                # Đệ quy đi sâu xuống tiếp
                result, next_t = self._search(child_node, threshold, path_set)
                if isinstance(result, IDA_Node):
                    return result, threshold      
                if next_t < min_cutoff:
                    min_cutoff = next_t     
                path_set.remove(child_state) # Backtrack giải phóng trạng thái khỏi nhánh   
        return "CUTOFF", min_cutoff

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
            matrix = [[3 if self.grid[i][j] == 3 else 0 for j in range(self.cols)] for i in range(self.rows)]
            for (dx, dy) in dirt_tuple: matrix[dx][dy] = 1
            for (ux, uy) in self.unreachable_dirt: matrix[ux][uy] = 1
            matrix[rx][ry] = 2
            action_display = f"{n.action} (f={n.f})" if n.action != "START" else "START"
            self.path.append((matrix, action_display))

    def get_path(self, node=None):
        return self.path