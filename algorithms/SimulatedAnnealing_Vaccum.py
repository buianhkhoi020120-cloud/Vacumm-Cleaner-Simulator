import random
import copy
import math

class SA_Node:
    def __init__(self, state, parent=None, action=None, temp=0):
        self.state = state  
        self.parent = parent
        self.action = action
        self.h = 0          
        self.temperature = temp  # Lưu lại nhiệt độ T để hiển thị ra UI

class SimulatedAnnealing_Vaccum:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.start_robot_pos = (0, 0)
        self.grid = [
            [0, 1, 0, 0, 3],
            [1, 0, 1, 0, 0],
            [0, 3, 0, 3, 1],
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
        """Hàm đánh giá h(n): Càng thấp càng tốt."""
        if not dirt_tuple: return 0
        rx, ry = pos
        dirt_penalty = len(dirt_tuple) * 1000
        min_manhattan = min(abs(rx - dx) + abs(ry - dy) for dx, dy in dirt_tuple)
        return dirt_penalty + min_manhattan

    def solve(self):
        # T = T0
        T = 1000.0  
        Tmin = 0.01 
        alpha = 0.95 # Hệ số làm lạnh
        # current state = start
        initial_state = (self.start_robot_pos, self.initial_dirt_tuple)
        current_node = SA_Node(initial_state, parent=None, action="START", temp=T)
        current_node.h = self._calculate_h(current_node.state[0], current_node.state[1])
        nodes_journey = [current_node]
        # while T > Tmin:
        while T > Tmin:
            # if current state == goal: return current state
            if len(current_node.state[1]) == 0:
                self._reconstruct_path(nodes_journey)
                return current_node
            rx, ry = current_node.state[0]
            dirt_tuple = current_node.state[1]
            # Khởi tạo tập hợp lân cận hợp lệ
            actions = []
            if (rx, ry) in dirt_tuple:
                actions.append("SUCK")
            for move_name, (dx, dy) in [("Up", (-1, 0)), ("Down", (1, 0)), ("Left", (0, -1)), ("Right", (0, 1))]:
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                    actions.append(move_name)
            if not actions: 
                break
            # next state = RandomNeighbor(current state)
            action = random.choice(actions)
            child_rx, child_ry = rx, ry
            child_dirt = dirt_tuple
            if action == "SUCK":
                child_dirt = tuple(d for d in dirt_tuple if d != (rx, ry))
            elif action == "Up": child_rx -= 1
            elif action == "Down": child_rx += 1
            elif action == "Left": child_ry -= 1
            elif action == "Right": child_ry += 1
            child_state = ((child_rx, child_ry), child_dirt)
            next_node = SA_Node(child_state, parent=current_node, action=action, temp=T)
            next_node.h = self._calculate_h(next_node.state[0], next_node.state[1])
            # Δ = h(next state) - h(current state)
            delta = next_node.h - current_node.h
            # if Δ < 0:
            if delta < 0:
                # current state = next state
                current_node = next_node
                nodes_journey.append(current_node)
            # else:
            else:
                # p = exp(-Δ / T)
                p = math.exp(-delta / T)
                # if Random(0,1) < p:
                if random.random() < p:
                    # current state = next state (Chấp nhận hướng đi tệ hơn để thoát cực đại cục bộ)
                    current_node = next_node
                    nodes_journey.append(current_node)
            # T = α * T
            T = alpha * T
        # return current state
        self._reconstruct_path(nodes_journey)
        return current_node

    def _reconstruct_path(self, nodes_journey):
        """Lưu lại toàn bộ quá trình đi lang thang để thấy rõ nhiệt độ ảnh hưởng thế nào"""
        self.path = []
        for n in nodes_journey:
            rx, ry = n.state[0]
            dirt_tuple = n.state[1]
            matrix = [[3 if self.grid[i][j] == 3 else 0 for j in range(self.cols)] for i in range(self.rows)]
            for (dx, dy) in dirt_tuple: matrix[dx][dy] = 1
            for (ux, uy) in self.unreachable_dirt: matrix[ux][uy] = 1
            matrix[rx][ry] = 2
            # Hiển thị T ra log để thấy nhiệt độ giảm dần
            action_display = f"{n.action} (T={n.temperature:.1f})" if n.action != "START" else "START"
            self.path.append((matrix, action_display))

    def get_path(self, node=None):
        return self.path