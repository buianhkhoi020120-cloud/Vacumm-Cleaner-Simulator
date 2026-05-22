import random
import copy
import heapq

# CẤU TRÚC NODE CHO UCS (Cần hỗ trợ so sánh __lt__)
class UCS_Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state          # Định dạng: ((rx, ry), tuple_các_vị_trí_rác)
        self.parent = parent
        self.action = action
        self.path_cost = path_cost  # Tổng chi phí g(n) từ ban đầu đến node này

    # Định nghĩa toán tử so sánh < để hàng đợi ưu tiên heapq biết cách sắp xếp theo path_cost
    def __lt__(self, other):
        return self.path_cost < other.path_cost

# THUẬT TOÁN UNIFORM-COST SEARCH (UCS)
class UCS_Vaccum:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.start_robot_pos = (0, 0)
        self.grid = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                if (i, j) == self.start_robot_pos:
                    row.append(0)
                else:
                    # 65% ô sạch (0), 20% ô rác (1), 15% ô tường (3)
                    cell_type = random.choices([0, 1, 3], weights=[65, 20, 15])[0]
                    row.append(cell_type)
            self.grid.append(row)
        
        # Thuật toán loang cô lập các ô rác kẹt trong tường
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
        # Bản đồ mặc định ban đầu để UI vẽ đồ họa khi khởi động
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
        initial_state = (self.start_robot_pos, self.initial_dirt_tuple)
        root_node = UCS_Node(initial_state, parent=None, action="START", path_cost=0)
        # Khởi tạo frontier dưới dạng một Heap mã hóa Priority Queue
        frontier = []
        heapq.heappush(frontier, root_node)
        # Dictionary quản lý chi phí tối ưu nhất để đến được một trạng thái (chống lặp và tối ưu hóa đường đi)
        frontier_costs = {root_node.state: 0}
        explored = set()
        while frontier:
            # Lấy nút có path_cost g(n) nhỏ nhất 
            node = heapq.heappop(frontier)
            # Kiểm tra xem trạng thái này có còn nằm trong frontier_costs với đúng chi phí tối ưu không
            if node.state in frontier_costs and frontier_costs[node.state] < node.path_cost:
                continue   
            if node.state in frontier_costs:
                del frontier_costs[node.state]
            # Đưa vào tập khám phá
            explored.add(node.state)
            # GOAL-TEST: Kiểm tra khi lấy nút ra khỏi frontier
            if len(node.state[1]) == 0:
                self._reconstruct_path(node)
                return node
            rx, ry = node.state[0]
            dirt_tuple = node.state[1]
            # Xác định các hành động khả thi và chi phí từng hành động
            actions = []  # Định dạng: (tên_hành_động, chi_phí_hành_động)
            if (rx, ry) in dirt_tuple:
                actions.append(("SUCK", 1)) # Hút rác tốn 1 chi phí   
            for move_name, (dx, dy) in [("Up", (-1, 0)), ("Down", (1, 0)), ("Left", (0, -1)), ("Right", (0, 1))]:
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                    actions.append((move_name, 1)) # Di chuyển tốn 1 chi phí
            for action_name, step_cost in actions:
                child_rx, child_ry = rx, ry
                child_dirt = dirt_tuple
                if action_name == "SUCK":
                    child_dirt = tuple(d for d in dirt_tuple if d != (rx, ry))
                elif action_name == "Up": child_rx -= 1
                elif action_name == "Down": child_rx += 1
                elif action_name == "Left": child_ry -= 1
                elif action_name == "Right": child_ry += 1
                child_state = ((child_rx, child_ry), child_dirt)
                new_path_cost = node.path_cost + step_cost
                child_node = UCS_Node(child_state, parent=node, action=action_name, path_cost=new_path_cost)
                # Điều kiện kiểm tra của UCS: Nếu chưa khám phá và chưa có trong frontier, hoặc tìm thấy đường đi rẻ hơn
                if child_state not in explored:
                    if child_state not in frontier_costs or new_path_cost < frontier_costs[child_state]:
                        frontier_costs[child_state] = new_path_cost
                        heapq.heappush(frontier, child_node)   
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
            rx, ry = n.state[0]
            dirt_tuple = n.state[1]
            matrix = [[3 if self.grid[i][j] == 3 else 0 for j in range(self.cols)] for i in range(self.rows)]
            for (dx, dy) in dirt_tuple: matrix[dx][dy] = 1
            for (ux, uy) in self.unreachable_dirt: matrix[ux][uy] = 1
            matrix[rx][ry] = 2
            # Đính kèm chi phí tích lũy vào log hiển thị cho UI sinh động
            action_display = f"{n.action} (g={n.path_cost})" if n.action != "START" else "START"
            self.path.append((matrix, action_display))

    def get_path(self, node):
        return self.path