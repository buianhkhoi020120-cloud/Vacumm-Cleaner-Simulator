import copy
import heapq

class AStar_Node:
    def __init__(self, state, parent=None, action=None, g=0, h=0):
        self.state = state  # ((rx, ry), tuple_các_vị_trí_rác)
        self.parent = parent
        self.action = action
        self.g = g          # Chi phí thực tế g(n) từ gốc đến nút hiện tại
        self.h = h          # Chi phí ước lượng h(n) từ nút hiện tại đến đích
        self.f = g + h      # f(n) = g(n) + h(n)
    def __lt__(self, other):
        return self.f < other.f

class AStar_Vaccum:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.start_robot_pos = (0, 0)
        self.grid = [
            [0, 0, 1, 0, 3],
            [3, 0, 0, 1, 0],
            [0, 1, 3, 0, 0],
            [0, 3, 0, 3, 1],
            [1, 0, 1, 1, 0]
        ]
         # Tìm các ô robot có thể đi tới
        self.unreachable_dirt = set()
        self.reachable_tiles = self._get_reachable_tiles(self.start_robot_pos)
        # Lấy các vị trí rác có thể hút được
        initial_dirt = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 1:
                    if (i, j) in self.reachable_tiles:
                        initial_dirt.append((i, j))
                    else:
                        self.unreachable_dirt.add((i, j))
        self.initial_dirt_tuple = tuple(sorted(initial_dirt))
         # Map ban đầu để hiển thị
        self.start = copy.deepcopy(self.grid)
        self.start[self.start_robot_pos[0]][self.start_robot_pos[1]] = 2
        self.path = []
    # tìm các ô có thể đi tới
    def _get_reachable_tiles(self, start):
        queue = [start]
        reachable = set([start])
        while queue:
            x, y = queue.pop(0)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                # kiểm tra có vượt khỏi sàn hoặc đi vào vật cản không
                if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                    if (nx, ny) not in reachable:
                        reachable.add((nx, ny))
                        queue.append((nx, ny))
        return reachable
    
    # Tính H(n)
    def _calculate_heuristic(self, pos, dirt_tuple):
        if not dirt_tuple:
            return 0
        rx, ry = pos
        return sum(abs(rx - dx) + abs(ry - dy) for dx, dy in dirt_tuple)
    
    # Thuật toán A*
    def solve(self):
        # Trạng thái ban đầu
        initial_state = (self.start_robot_pos, self.initial_dirt_tuple) 
        init_h = self._calculate_heuristic(initial_state[0], initial_state[1])
        root_node = AStar_Node(initial_state, parent=None, action="START", g=0, h=init_h)
        frontier = []
        heapq.heappush(frontier, root_node)
        # lưu g min của mỗi state
        frontier_g_costs = {root_node.state: 0}
        explored = set()
        while frontier:
            # Lấy node có f nhỏ nhất
            node = heapq.heappop(frontier)
            # Đã xét -> bỏ qua
            if node.state in explored:
                continue
            explored.add(node.state)
            # GOAL-TEST khi lấy ra khỏi frontier
            if len(node.state[1]) == 0:
                self._reconstruct_path(node)
                return node
            rx, ry = node.state[0]
            dirt_tuple = node.state[1]
            actions = []
            # Nếu đang đứng trên rác -> hút
            if (rx, ry) in dirt_tuple:
                actions.append("SUCK")
            for move_name, (dx, dy) in [("Up", (-1, 0)), ("Down", (1, 0)), ("Left", (0, -1)), ("Right", (0, 1))]:
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                    actions.append(move_name)
            # Sinh node con
            for action in actions:
                child_rx, child_ry = rx, ry
                child_dirt = dirt_tuple
                # Xử lý hành động
                if action == "SUCK":
                    child_dirt = tuple(d for d in dirt_tuple if d != (rx, ry))
                elif action == "Up": child_rx -= 1
                elif action == "Down": child_rx += 1
                elif action == "Left": child_ry -= 1
                elif action == "Right": child_ry += 1
                 # State mới
                child_state = ((child_rx, child_ry), child_dirt)
                new_g = node.g + 1 # Mỗi bước đi hoặc hút bụi tốn 1 đơn vị chi phí g
                # Nếu state chưa xét
                if child_state not in explored:
                    # Nếu trạng thái chưa được sờ tới hoặc tìm được đường đi ngắn (ít tốn g) hơn
                    if child_state not in frontier_g_costs or new_g < frontier_g_costs[child_state]:
                        frontier_g_costs[child_state] = new_g
                        child_h = self._calculate_heuristic(child_state[0], child_state[1])
                        child_node = AStar_Node(child_state, parent=node, action=action, g=new_g, h=child_h)
                        heapq.heappush(frontier, child_node)        
        return None
    
    # Khôi phục đường đi từ goal về start
    def _reconstruct_path(self, goal_node):
        nodes_path = []
        curr = goal_node
        while curr is not None:
            nodes_path.append(curr)
            curr = curr.parent
        nodes_path.reverse()
        self.path = []
        # Tạo lại từng bước để hiển thị
        for n in nodes_path:
            rx, ry = n.state[0]
            dirt_tuple = n.state[1]
            # Tạo map hiển thị
            matrix = [[3 if self.grid[i][j] == 3 else 0 for j in range(self.cols)] for i in range(self.rows)]
            for (dx, dy) in dirt_tuple: matrix[dx][dy] = 1
            for (ux, uy) in self.unreachable_dirt: matrix[ux][uy] = 1
            matrix[rx][ry] = 2
            action_display = f"{n.action} (f={n.f},g={n.g},h={n.h})" if n.action != "START" else "START"
            self.path.append((matrix, action_display))
            
    # Trả về đường đi
    def get_path(self, node):
        return self.path
