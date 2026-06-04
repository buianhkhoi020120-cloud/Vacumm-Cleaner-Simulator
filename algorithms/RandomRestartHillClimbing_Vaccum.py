import random
import copy

class RandomRestart_Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state  
        self.parent = parent
        self.action = action
        self.value = 0      

class RandomRestartHillClimbing_Vaccum:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.start_robot_pos = (0, 0)
        self.grid = [
            [0, 1, 0, 0, 3],
            [3, 0, 0, 3, 1],
            [0, 3, 0, 0, 0],
            [1, 0, 3, 1, 0],
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

    def _calculate_value(self, pos, dirt_tuple):
        if not dirt_tuple: return 0
        rx, ry = pos
        dirt_penalty = len(dirt_tuple) * 1000
        # Dùng min() để tìm rác gần nhất, chống kẹt trên bình nguyên
        min_manhattan = min(abs(rx - dx) + abs(ry - dy) for dx, dy in dirt_tuple)
        return -(dirt_penalty + min_manhattan)

    def solve(self):
        MAX_RESTART = 5 # Số lần chạy lại tối đa
        nodes_journey = []
        
        # 2. CHO i = 1 đến MAX_RESTART:
        for i in range(1, MAX_RESTART + 1):
            # Khởi tạo lại Start ngẫu nhiên (Trừ lần đầu tiên)
            if i == 1:
                start_pos = self.start_robot_pos
                action_name = "START"
            else:
                valid_positions = [(r, c) for r in range(self.rows) for c in range(self.cols) if self.grid[r][c] != 3]
                start_pos = random.choice(valid_positions)
                action_name = f"♻️ RESTART LẦN {i}"
            # Current_State = Start
            current_state = (start_pos, self.initial_dirt_tuple)
            current_node = RandomRestart_Node(current_state, parent=None, action=action_name)
            current_node.value = self._calculate_value(current_node.state[0], current_node.state[1])
            nodes_journey.append(current_node)
            # TRONG KHI (đúng):
            while True:
                # NẾU Current_State == Goal: TRẢ VỀ Current_State
                if len(current_node.state[1]) == 0:
                    self._reconstruct_path(nodes_journey)
                    return current_node
                rx, ry = current_node.state[0]
                dirt_tuple = current_node.state[1]
                # Sinh tất cả trạng thái lân cận
                actions = []
                if (rx, ry) in dirt_tuple:
                    actions.append("SUCK")
                for move_name, (dx, dy) in [("Up", (-1, 0)), ("Down", (1, 0)), ("Left", (0, -1)), ("Right", (0, 1))]:
                    nx, ny = rx + dx, ry + dy
                    if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                        actions.append(move_name)
                # Lọc ra tập Better_Neighbors
                better_neighbors = []
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
                    child_node = RandomRestart_Node(child_state, parent=current_node, action=action)
                    child_node.value = self._calculate_value(child_node.state[0], child_node.state[1])
                    if child_node.value > current_node.value:
                        better_neighbors.append(child_node)
                # NẾU Better_Neighbors RỖNG:
                if not better_neighbors:
                    break # Thoát vòng lặp TRONG KHI (Lượt này bị kẹt, nhảy sang lượt i tiếp theo)
                # NGƯỢC LẠI: Chọn trạng thái TỐT NHẤT từ tập Better_Neighbors
                best_neighbor = max(better_neighbors, key=lambda n: n.value)
                current_node = best_neighbor
                nodes_journey.append(current_node)
        # 3. TRẢ VỀ "Thất bại"
        self._reconstruct_path(nodes_journey)
        return current_node # Trả về điểm kẹt cuối cùng để giao diện hiển thị

    def _reconstruct_path(self, nodes_journey):
        self.path = []
        for n in nodes_journey:
            rx, ry = n.state[0]
            dirt_tuple = n.state[1]
            matrix = [[3 if self.grid[i][j] == 3 else 0 for j in range(self.cols)] for i in range(self.rows)]
            for (dx, dy) in dirt_tuple: matrix[dx][dy] = 1
            for (ux, uy) in self.unreachable_dirt: matrix[ux][uy] = 1
            matrix[rx][ry] = 2
            action_display = f"{n.action} (v={n.value})" if "START" not in n.action and "RESTART" not in n.action else n.action
            self.path.append((matrix, action_display))

    def get_path(self, node=None):
        return self.path