import random
from collections import deque

class AdvancedRuleAgent:
    def __init__(self, tools):
        self.tools = tools
        self.map = {}
        self.visited = set()
        self.collected_positions = set()
        self.last_pos = None
        self.stuck_count = 0
        self.goal_pos = None
        self.path_stack = []          # DFS 回溯栈
        self.explore_target = None     # 全局探索目标
        self.steps_since_global_plan = 0
        self.step_count = 0            # 记录总步数，用于无进展检测

    def update_map(self, view, pos):
        view_size = len(view)
        half = view_size // 2
        for dr in range(view_size):
            for dc in range(view_size):
                cell = view[dr, dc]
                if cell != '?':
                    world_r = pos[0] + (dr - half)
                    world_c = pos[1] + (dc - half)
                    self.map[(world_r, world_c)] = cell
                    if cell == 'G':
                        self.goal_pos = (world_r, world_c)
        self.visited.add(pos)

    def bfs_to_target(self, start, target):
        """在已知地图中 BFS 寻找路径，只考虑已知且可通行的格子"""
        if start == target:
            return [start]
        queue = deque()
        queue.append(start)
        visited = {start}
        parent = {start: None}
        directions = [(0,1), (0,-1), (1,0), (-1,0)]
        while queue:
            current = queue.popleft()
            for dr, dc in directions:
                nr, nc = current[0] + dr, current[1] + dc
                neighbor = (nr, nc)
                cell = self.map.get(neighbor)
                if cell is not None and cell != 'W' and neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    if neighbor == target:
                        path = []
                        node = neighbor
                        while node is not None:
                            path.append(node)
                            node = parent[node]
                        return path[::-1]
                    queue.append(neighbor)
        return None

    def find_furthest_unvisited(self, start):
        """在已知地图中寻找距离 start 最远且可达的未访问格子"""
        max_dist = -1
        best_target = None
        queue = deque()
        queue.append((start, 0))
        visited_bfs = {start}
        directions = [(0,1), (0,-1), (1,0), (-1,0)]
        while queue:
            current, dist = queue.popleft()
            # 检查当前格子是否为未访问且已知且不是墙
            cell = self.map.get(current)
            if cell is not None and cell != 'W' and current not in self.visited:
                if dist > max_dist:
                    max_dist = dist
                    best_target = current
            for dr, dc in directions:
                nr, nc = current[0] + dr, current[1] + dc
                neighbor = (nr, nc)
                if neighbor not in visited_bfs:
                    cell = self.map.get(neighbor)
                    if cell is not None and cell != 'W':
                        visited_bfs.add(neighbor)
                        queue.append((neighbor, dist+1))
        return best_target

    def act(self):
        self.step_count += 1
        pos = self.tools.get_position()
        view = self.tools.get_local_view()
        collected_count = self.tools.get_collected_count()
        total_items = self.tools.get_total_items()

        self.update_map(view, pos)

        # 卡住检测
        if pos == self.last_pos:
            self.stuck_count += 1
        else:
            self.stuck_count = 0
        self.last_pos = pos

        # 如果卡住超过 10 步，强制随机移动并重置目标
        if self.stuck_count > 10:
            self.explore_target = None
            self.path_stack = []
            dirs = ['up','down','left','right']
            random.shuffle(dirs)
            for d in dirs:
                if self.tools.move(d):
                    return d
            return 'collect'

        # 收集脚下物品
        if view[2,2] == 'I' and pos not in self.collected_positions:
            if self.tools.collect():
                self.collected_positions.add(pos)
                self.map[pos] = '.'
            return 'collect'

        # 收集完毕前往目标
        if collected_count == total_items and self.goal_pos is not None:
            if pos == self.goal_pos:
                return 'collect'
            path = self.bfs_to_target(pos, self.goal_pos)
            if path and len(path) > 1:
                next_step = path[1]
                dr = next_step[0] - pos[0]
                dc = next_step[1] - pos[1]
                if dr == 1 and self.tools.move('down'): return 'down'
                if dr == -1 and self.tools.move('up'): return 'up'
                if dc == 1 and self.tools.move('right'): return 'right'
                if dc == -1 and self.tools.move('left'): return 'left'
            dirs = ['up','down','left','right']
            random.shuffle(dirs)
            for d in dirs:
                if self.tools.move(d): return d
            return 'collect'

        # 视野中有可见物品
        item_positions_in_view = []
        view_size = len(view)
        half = view_size // 2
        for dr in range(view_size):
            for dc in range(view_size):
                if view[dr, dc] == 'I':
                    world_r = pos[0] + (dr - half)
                    world_c = pos[1] + (dc - half)
                    if (world_r, world_c) not in self.collected_positions:
                        item_positions_in_view.append((world_r, world_c))
        if item_positions_in_view:
            target = min(item_positions_in_view, key=lambda p: abs(p[0]-pos[0]) + abs(p[1]-pos[1]))
            dr = target[0] - pos[0]
            dc = target[1] - pos[1]
            if abs(dr) > abs(dc):
                if dr > 0 and self.tools.move('down'): return 'down'
                if dr < 0 and self.tools.move('up'): return 'up'
            else:
                if dc > 0 and self.tools.move('right'): return 'right'
                if dc < 0 and self.tools.move('left'): return 'left'
            dirs = ['up','down','left','right']
            random.shuffle(dirs)
            for d in dirs:
                if self.tools.move(d): return d
            return 'collect'

        # ===== 混合探索 =====
        # 每隔 20 步重新规划一个全局探索目标
        self.steps_since_global_plan += 1
        if self.explore_target is None or self.steps_since_global_plan >= 20:
            self.explore_target = self.find_furthest_unvisited(pos)
            self.steps_since_global_plan = 0

        if self.explore_target is not None:
            path = self.bfs_to_target(pos, self.explore_target)
            if path and len(path) > 1:
                next_step = path[1]
                dr = next_step[0] - pos[0]
                dc = next_step[1] - pos[1]
                if dr == 1 and self.tools.move('down'): return 'down'
                if dr == -1 and self.tools.move('up'): return 'up'
                if dc == 1 and self.tools.move('right'): return 'right'
                if dc == -1 and self.tools.move('left'): return 'left'

        # DFS 探索（带回溯）
        if not self.path_stack or self.path_stack[-1] != pos:
            self.path_stack.append(pos)

        directions = [(0,1,'right'), (0,-1,'left'), (1,0,'down'), (-1,0,'up')]
        random.shuffle(directions)
        for dr, dc, d_name in directions:
            nr, nc = pos[0] + dr, pos[1] + dc
            cell = self.map.get((nr, nc))
            if cell is not None and cell != 'W':   # 只考虑已知可通行格子
                if (nr, nc) not in self.visited:
                    if self.tools.move(d_name):
                        return d_name

        # 无未访问邻居，回溯
        if len(self.path_stack) > 1:
            self.path_stack.pop()
            prev_pos = self.path_stack[-1]
            dr = prev_pos[0] - pos[0]
            dc = prev_pos[1] - pos[1]
            if dr == 1 and self.tools.move('down'): return 'down'
            if dr == -1 and self.tools.move('up'): return 'up'
            if dc == 1 and self.tools.move('right'): return 'right'
            if dc == -1 and self.tools.move('left'): return 'left'

        # 实在不行，随机移动
        dirs = ['up','down','left','right']
        random.shuffle(dirs)
        for d in dirs:
            if self.tools.move(d):
                return d
        return 'collect'