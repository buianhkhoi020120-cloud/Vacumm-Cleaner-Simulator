import copy

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state  # ((rx, ry), tuple_các_vị_trí_rác)
        self.parent = parent
        self.action = action
class DFS_Vaccum_1:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.start_robot_pos = (0, 0)       
        # Sinh sàn ngẫu nhiên
        self.grid = [
            [0, 1, 0, 3, 0],
            [0, 3, 0, 1, 0],
            [0, 0, 0, 0, 1],
            [3, 1, 0, 3, 0],
            [0, 0, 1, 0, 0]
        ] 

        # Loang trùng khớp để cô lập rác kẹt trong tường
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

    def solve(self):
        initial_state = (self.start_robot_pos, self.initial_dirt_tuple)
        root_node = Node(initial_state, parent=None, action="START")
        
        if len(root_node.state[1]) == 0:
            self.path = [(copy.deepcopy(self.start), "START")]
            return root_node
            
        # frontier lúc này hoạt động như một STACK (LIFO)
        frontier = [root_node]
        frontier_states = {root_node.state}
        reached = set()
        
        while frontier:
            # KHÁC BIỆT: Dùng .pop() để lấy phần tử cuối cùng vừa thêm vào (LIFO)
            node = frontier.pop()
            frontier_states.remove(node.state)    
            reached.add(node.state)
            
            # GOAL-TEST khi lấy node ra khỏi frontier
            if len(node.state[1]) == 0:
                self._reconstruct_path(node)
                return node
                
            rx, ry = node.state[0]
            dirt_tuple = node.state[1]
            actions = []
            for move_name, (dx, dy) in [("Up", (-1, 0)), ("Down", (1, 0)), ("Left", (0, -1)), ("Right", (0, 1))]:
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols and self.grid[nx][ny] != 3:
                    actions.append(move_name)
            if (rx, ry) in dirt_tuple:
                actions.append("SUCK")
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
                child_node = Node(child_state, parent=node, action=action)
                if child_state not in reached and child_state not in frontier_states:
                    frontier.append(child_node)
                    frontier_states.add(child_state)                
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
            self.path.append((matrix, n.action))
    def get_path(self, node):
        return self.path