import random
import copy

class StochasticHill_Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state  # Định dạng: ((rx, ry), tuple_các_vị_trí_rác)
        self.parent = parent
        self.action = action
        self.value = 0      # Value = -(phạt_rác + manhattan)


class StochasticHillClimbing_Vaccum:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.start_robot_pos = (0, 0)
        self.grid = [
            [0, 1, 0, 0, 3],
            [3, 0, 1, 3, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 3, 0, 0],
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
        if not dirt_tuple:
            return 0
        rx, ry = pos
        dirt_penalty = len(dirt_tuple) * 1000
        min_manhattan = min(abs(rx - dx) + abs(ry - dy) for dx, dy in dirt_tuple)
        return -(dirt_penalty + min_manhattan)

    def solve(self):
        # Current_State = Start
        initial_state = (self.start_robot_pos, self.initial_dirt_tuple)
        current_node = StochasticHill_Node(initial_state, parent=None, action="START")
        current_node.value = self._calculate_value(current_node.state[0], current_node.state[1])
        nodes_journey = [current_node]
        while True:
            # Nếu Current_State == Goal: TRẢ VỀ Current_State
            if len(current_node.state[1]) == 0:
                self._reconstruct_path(nodes_journey)
                return current_node
            rx, ry = current_node.state[0]
            dirt_tuple = current_node.state[1]
            # Sinh tất cả các trạng thái lân cận của Current_State
            actions = []
            if (rx, ry) in dirt_tuple:
                actions.append("SUCK")
            for move_name, (dx, dy) in [("Up", (-1, 0)), ("Down", (1, 0)), ("Left", (0, -1)), ("Right", (0, 1))]:
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                    actions.append(move_name)
            # Lọc ra tập Better_Neighbors = {Neighbor | Value(Neighbor) > Value(Current_State)}
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
                child_node = StochasticHill_Node(child_state, parent=current_node, action=action)
                child_node.value = self._calculate_value(child_node.state[0], child_node.state[1])
                # Điều kiện lọc: Value tốt hơn hẳn Current_State
                if child_node.value > current_node.value:
                    better_neighbors.append(child_node)
            # NẾU Better_Neighbors RỖNG:
            if not better_neighbors:
                # TRẢ VỀ Current_State (Dừng vì đã đạt cực đại cục bộ)
                self._reconstruct_path(nodes_journey)
                return current_node
            # NGƯỢC LẠI: Next_State = Chọn ngẫu nhiên một trạng thái từ tập Better_Neighbors
            next_state = random.choice(better_neighbors)
            # Current_State = Next_State (Quay lại đầu vòng lặp với trạng thái mới)
            current_node = next_state
            nodes_journey.append(current_node)

    def _reconstruct_path(self, nodes_journey):
        self.path = []
        for n in nodes_journey:
            rx, ry = n.state[0]
            dirt_tuple = n.state[1]
            matrix = [[3 if self.grid[i][j] == 3 else 0 for j in range(self.cols)] for i in range(self.rows)]
            for (dx, dy) in dirt_tuple: matrix[dx][dy] = 1
            for (ux, uy) in self.unreachable_dirt: matrix[ux][uy] = 1
            matrix[rx][ry] = 2
            action_display = f"{n.action} (v={n.value})" if n.action != "START" else "START"
            self.path.append((matrix, action_display))

    def get_path(self, node=None):
        return self.path