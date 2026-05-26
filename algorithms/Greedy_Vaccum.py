import heapq

class Greedy_Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.h = 0
    def __lt__(self, other):
        return self.h < other.h

class Greedy_Vaccum:
    def __init__(self):
        self.rows = 5
        self.cols = 5
        self.start_robot_pos = (0, 0)
        # 0: sạch, 1: bẩn, 3:vật cản
        self.grid = [
            [0, 1, 0, 0, 3],
            [0, 3, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [1, 3, 0, 0, 0],
            [0, 0, 1, 3, 0]
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
        self.start = [row[:] for row in self.grid]
        self.start[self.start_robot_pos[0]][self.start_robot_pos[1]] = 2
        self.path = []

    def _get_reachable_tiles(self, start):
        queue = [start]
        reachable = set([start])
        while queue:
            x, y = queue.pop(0)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < self.rows
                    and 0 <= ny < self.cols
                    and self.grid[nx][ny] != 3
                ):
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
        root_node = Greedy_Node(
            initial_state,
            parent=None,
            action="START"
        )
        root_node.h = self._calculate_heuristic(
            root_node.state[0],
            root_node.state[1]
        )
        frontier = []
        heapq.heappush(frontier, root_node)
        explored = set()
        while frontier:
            node = heapq.heappop(frontier)
            if node.state in explored:
                continue
            explored.add(node.state)
            # GOAL TEST
            if len(node.state[1]) == 0:
                self._reconstruct_path(node)
                return node
            rx, ry = node.state[0]
            dirt_tuple = node.state[1]
            actions = []
            if (rx, ry) in dirt_tuple:
                actions.append("SUCK")
            for move_name, (dx, dy) in [
                ("Up", (-1, 0)),
                ("Down", (1, 0)),
                ("Left", (0, -1)),
                ("Right", (0, 1))
            ]:
                nx, ny = rx + dx, ry + dy
                if (
                    0 <= nx < self.rows
                    and 0 <= ny < self.cols
                    and self.grid[nx][ny] != 3
                ):
                    actions.append(move_name)
            for action in actions:
                child_rx, child_ry = rx, ry
                child_dirt = dirt_tuple
                if action == "SUCK":
                    child_dirt = tuple(
                        d for d in dirt_tuple if d != (rx, ry)
                    )
                elif action == "Up":
                    child_rx -= 1
                elif action == "Down":
                    child_rx += 1
                elif action == "Left":
                    child_ry -= 1
                elif action == "Right":
                    child_ry += 1
                child_state = (
                    (child_rx, child_ry),
                    child_dirt
                )
                if child_state not in explored:
                    child_node = Greedy_Node(
                        child_state,
                        parent=node,
                        action=action
                    )
                    child_node.h = self._calculate_heuristic(
                        child_node.state[0],
                        child_node.state[1]
                    )
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
            matrix = [
                [
                    3 if self.grid[i][j] == 3 else 0
                    for j in range(self.cols)
                ]
                for i in range(self.rows)
            ]
            for (dx, dy) in dirt_tuple:
                matrix[dx][dy] = 1
            for (ux, uy) in self.unreachable_dirt:
                matrix[ux][uy] = 1
            matrix[rx][ry] = 2
            action_display = (
                f"{n.action} (h={n.h})"
                if n.action != "START"
                else "START"
            )
            self.path.append((matrix, action_display))
            
    def get_path(self, node=None):
        return self.path