import random
import copy

# ==========================================
# 1. LOGIC CỦA BẠN (Sửa vật cản thành 3)
# ==========================================
class ModelBasedAgent:
    def __init__(self, n, m):
        self.name = "Model-Based Agent"
        self.N = n
        self.M = m

    def update_internal_model(self, pos, internal_model):
        if "visited" not in internal_model:
            internal_model["visited"] = {}
            
        if pos not in internal_model["visited"]:
            internal_model["visited"][pos] = 1
        else:
            internal_model["visited"][pos] += 1

    def interpret_input(self, percept, environment, internal_model):
        x, y = percept
        state_value = environment[(x, y)]
        possible_moves = []
        
        directions = [("Up", (x-1, y)), ("Down", (x+1, y)), 
                      ("Left", (x, y-1)), ("Right", (x, y+1))]
        
        for move_name, (nx, ny) in directions:
            if 0 <= nx < self.N and 0 <= ny < self.M and environment[(nx, ny)] != 3:
                visit_count = internal_model["visited"].get((nx, ny), 0)
                possible_moves.append((move_name, visit_count))    
                
        return (percept, state_value, possible_moves)

    def decide(self, position, environment, internal_model):
        state = self.interpret_input(position, environment, internal_model)
        pos, val, moves = state
        
        if val == 1:
            return "SUCK"
            
        if not moves:
            return "STAY"
            
        moves.sort(key=lambda x: x[1])
        min_visits = moves[0][1]
        best_moves = [m[0] for m in moves if m[1] == min_visits]
        
        return random.choice(best_moves)

# ==========================================
# 2. LỚP WRAPPER ĐỂ TƯƠNG THÍCH VỚI UI
# ==========================================
class ModelBased_Wrapper:
    def __init__(self):
        # 0: Sạch, 1: Rác, 3: Vật cản (Tường)
        self.grid = [
            [0, 1, 0, 3, 1],
            [0, 0, 0, 0, 0],
            [3, 3, 0, 1, 0],
            [1, 0, 0, 3, 0],
            [0, 1, 0, 0, 1]
        ]
        self.start_robot_pos = (0, 0)
        
        self.start = copy.deepcopy(self.grid)
        self.start[self.start_robot_pos[0]][self.start_robot_pos[1]] = 2
        self.path = []

    def solve(self):
        rows, cols = len(self.grid), len(self.grid[0])
        agent = ModelBasedAgent(rows, cols)
        
        current_grid = copy.deepcopy(self.grid)
        rx, ry = self.start_robot_pos
        internal_model = {"visited": {}}
        
        self.path = [(copy.deepcopy(self.start), "START")]
        agent.update_internal_model((rx, ry), internal_model)
        
        max_steps = 150 
        step = 0
        
        while step < max_steps:
            dirt_count = sum(row.count(1) for row in current_grid)
            if dirt_count == 0:
                break
                
            env = {}
            for i in range(rows):
                for j in range(cols):
                    env[(i, j)] = current_grid[i][j]
                    
            action = agent.decide((rx, ry), env, internal_model)
            
            if action == "SUCK":
                current_grid[rx][ry] = 0
            elif action == "Up":
                rx -= 1
            elif action == "Down":
                rx += 1
            elif action == "Left":
                ry -= 1
            elif action == "Right":
                ry += 1
                
            agent.update_internal_model((rx, ry), internal_model)
            
            ui_matrix = copy.deepcopy(current_grid)
            ui_matrix[rx][ry] = 2
            
            self.path.append((ui_matrix, action))
            step += 1
            
        return "Model_Based_Done" 

    def get_path(self, node):
        return self.path