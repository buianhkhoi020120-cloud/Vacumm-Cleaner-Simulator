import random
import copy

class LocalBeam_Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state  
        self.parent = parent
        self.action = action
        self.h = 0          # Hàm chi phí h(n) (Càng nhỏ càng tốt)


class LocalBeamSearch_Vaccum:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.start_robot_pos = (0, 0)
        self.grid = [
            [0, 1, 3, 0, 3],
            [1, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [1, 0, 3, 0, 0],
            [3, 0, 1, 0, 3]
        ]
        
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

    def _calculate_h(self, pos, dirt_tuple):
        """Hàm chi phí mục tiêu: Càng ít rác và càng gần rác thì h càng nhỏ (tốt)"""
        if not dirt_tuple: return 0
        rx, ry = pos
        dirt_penalty = len(dirt_tuple) * 1000
        min_manhattan = min(abs(rx - dx) + abs(ry - dy) for dx, dy in dirt_tuple)
        return dirt_penalty + min_manhattan

    def solve(self):
        k = 3  # Giới hạn số lượng trạng thái trong chùm
        initial_state = (self.start_robot_pos, self.initial_dirt_tuple)
        root_node = LocalBeam_Node(initial_state, parent=None, action="START")
        root_node.h = self._calculate_h(root_node.state[0], root_node.state[1])
        Current_State_set = [root_node]
        # 2. TRONG KHI (đúng):
        while True:
            Neighbor_States = []
            # 2.1. SINH TRẠNG THÁI LÂN CẬN
            # VỚI MỖI State trong Current_State_set:
            for node in Current_State_set:
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
                    child_node = LocalBeam_Node(child_state, parent=node, action=action)
                    child_node.h = self._calculate_h(child_node.state[0], child_node.state[1])
                    # Thêm các trạng thái lân cận này vào Neighbor_States
                    Neighbor_States.append(child_node)
            if not Neighbor_States:
                self._reconstruct_path(Current_State_set[0])
                return Current_State_set[0]
            # 2.2. KIỂM TRA ĐÍCH
            # VỚI MỖI Neighbor trong Neighbor_States:
            for neighbor in Neighbor_States:
                # NẾU Neighbor == Goal: TRẢ VỀ Neighbor
                if len(neighbor.state[1]) == 0:
                    self._reconstruct_path(neighbor)
                    return neighbor
            # 2.3. LỰA CHỌN CHÙM (NẾU CHƯA TÌM THẤY ĐÍCH)
            # Sắp xếp Neighbor_States theo thứ tự giá trị hàm mục tiêu h tốt dần (nhỏ dần)
            Neighbor_States.sort(key=lambda n: n.h)
            
            # Current_State_set = Lấy k trạng thái tốt nhất từ Neighbor_States đã sắp xếp
            Current_State_set = Neighbor_States[:k]

    def _reconstruct_path(self, goal_node):
        """Truy vết lại nhánh của Robot từ đích về điểm xuất phát"""
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
            action_display = f"{n.action} (h={n.h})" if n.action != "START" else "START"
            self.path.append((matrix, action_display))

    def get_path(self, node=None):
        return self.path