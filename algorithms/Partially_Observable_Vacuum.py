import copy
from collections import deque

class PO_Node():
    def __init__(self, state, parent, act, cost_path):
        self.state = state          
        self.parent = parent        
        self.act = act              
        self.cost_path = cost_path  

class Partially_Observable_Vacuum:
    def __init__(self):
        self.rows = 4
        self.cols = 4
        # Không cần định nghĩa self.goals cố định, chúng ta sẽ kiểm tra động xem rác đã sạch chưa
        
        # 8 Trạng thái Bắt đầu Khả thi
        s1_clean = ((2, 0, 1, 1), (0, 0, -1, 0), (0, -1, 0, 0), (0, 0, 0, 0))
        s1_dirty = ((2, 0, 1, 1), (0, 0, -1, 0), (0, -1, 0, 0), (1, 0, 0, 0))
        
        s2_clean = ((0, 2, 1, 1), (0, 0, -1, 0), (0, -1, 0, 0), (0, 0, 0, 0))
        s2_dirty = ((0, 2, 1, 1), (0, 0, -1, 0), (0, -1, 0, 0), (1, 0, 0, 0))
        
        s3_clean = ((0, 0, 1, 1), (2, 0, -1, 0), (0, -1, 0, 0), (0, 0, 0, 0))
        s3_dirty = ((0, 0, 1, 1), (2, 0, -1, 0), (0, -1, 0, 0), (1, 0, 0, 0))
        
        s4_clean = ((0, 0, 1, 1), (0, 2, -1, 0), (0, -1, 0, 0), (0, 0, 0, 0))
        s4_dirty = ((0, 0, 1, 1), (0, 2, -1, 0), (0, -1, 0, 0), (1, 0, 0, 0))
        
        self.start_belief = (s1_clean, s1_dirty, s2_clean, s2_dirty, s3_clean, s3_dirty, s4_clean, s4_dirty)
        
        # Chuyển đổi thành ma trận gộp để vẽ lên màn hình UI lúc chưa bấm RUN
        self.start = self._make_ui_matrix(self.start_belief)
        self.path = []

    def _make_ui_matrix(self, belief_state):
        """Hàm gộp các vũ trụ song song thành 1 ma trận để vẽ lên Tkinter"""
        matrix = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for state in belief_state:
            for i in range(self.rows):
                for j in range(self.cols):
                    val = state[i][j]
                    if val == -1:
                        matrix[i][j] = 3 # Map -1 sang 3 (Màu tường của UI)
                    elif val == 1:
                        if matrix[i][j] != 3: matrix[i][j] = 1 # Rác
                    elif val == 2:
                        matrix[i][j] = 2 # Bóng ma robot
        return matrix

    def get_location(self, physical_state):
        for i in range(len(physical_state)):
            for j in range(len(physical_state[0])):
                if physical_state[i][j] == 2:
                    return i, j
        return None, None
                
    def possible_move(self, node):
        return ["Up", "Down", "Left", "Right"]
    
    def is_clean(self, state):
        for row in state:
            if 1 in row:
                return False
        return True

    def transition(self, state, move):
        x, y = self.get_location(state)
        if x is None or y is None: return state
        nx, ny = x, y
        if move == "Up": nx -= 1
        elif move == "Down": nx += 1
        elif move == "Left": ny -= 1
        elif move == "Right": ny += 1
        if 0 <= nx < 4 and 0 <= ny < 4 and state[nx][ny] != -1:
            matrix = [list(row) for row in state]
            tmp = matrix[x][y] # robot (2)
            matrix[x][y] = 0   # ô cũ trở thành sạch
            matrix[nx][ny] = tmp
            return tuple(tuple(row) for row in matrix)
        return state

    def act(self, node, move):
        next_states = []
        for state in node.state:
            next_states.append(self.transition(state, move))  
        # Lọc trùng lặp để giảm số lượng "bóng ma" và sort lại
        new_belief = tuple(sorted(list(set(next_states))))
        return PO_Node(new_belief, node, move, node.cost_path + 1)
    
    def is_goal(self, node):
        return all(self.is_clean(state) for state in node.state)
    
    def solve(self):
        start_node = PO_Node(self.start_belief, None, "START", 0)
        self.frontier = deque([start_node])
        self.reached = set([self.start_belief])
        if self.is_goal(start_node):
            self._reconstruct_path(start_node)
            return start_node
        while self.frontier:
            node = self.frontier.popleft()
            moves = self.possible_move(node)
            for m in moves:
                new_node = self.act(node, m)
                if self.is_goal(new_node):
                    self._reconstruct_path(new_node)
                    return new_node
                if new_node.state not in self.reached:
                    self.reached.add(new_node.state)
                    self.frontier.append(new_node)
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
            matrix = self._make_ui_matrix(n.state)
            belief_size = len(n.state)
            action_display = f"{n.act} (Bất định: {belief_size})" if n.act != "START" else f"START (Bất định: {belief_size})"
            self.path.append((matrix, action_display))

    def get_path(self, node=None):
        return self.path