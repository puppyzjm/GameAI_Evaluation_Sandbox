import numpy as np
import json

class GridEnv:
    def __init__(self, grid_map, max_steps=200):
        """
        grid_map: 二维列表，元素为字符：'W'墙，'S'起点，'G'目标，'I'物品，'.'空地
        max_steps: 每回合最大步数
        """
        self.grid = np.array(grid_map)
        self.height, self.width = self.grid.shape
        self.max_steps = max_steps
        self.start_pos = self._find_start()
        self.goal_pos = self._find_goal()
        self.item_positions = self._find_items()
        self.reset()

    def _find_start(self):
        pos = np.argwhere(self.grid == 'S')
        return tuple(pos[0]) if len(pos) > 0 else (0, 0)

    def _find_goal(self):
        pos = np.argwhere(self.grid == 'G')
        return tuple(pos[0]) if len(pos) > 0 else (self.height-1, self.width-1)

    def _find_items(self):
        pos = np.argwhere(self.grid == 'I')
        return [tuple(p) for p in pos]

    def reset(self):
        self.agent_pos = self.start_pos
        self.collected = set()
        self.steps = 0
        self.done = False
        return self._get_obs()

    def _get_obs(self):
        """返回局部视野（5x5）和全局状态（位置、已收集数量）"""
        view_size = 5
        half = view_size // 2
        view = np.full((view_size, view_size), '?', dtype=str)  # 默认未知
        for dr in range(-half, half+1):
            for dc in range(-half, half+1):
                r = self.agent_pos[0] + dr
                c = self.agent_pos[1] + dc
                if 0 <= r < self.height and 0 <= c < self.width:
                    view[dr+half, dc+half] = self.grid[r, c]
        return {
            'view': view,
            'position': self.agent_pos,
            'collected_count': len(self.collected),
            'total_items': len(self.item_positions)
        }

    def step(self, action):
        """
        action: 0上,1下,2左,3右,4收集
        返回 (obs, reward, done, info)
        """
        self.steps += 1
        reward = -0.01  # 每步微小惩罚，鼓励尽快完成任务
        info = {}

        # 移动
        if action in [0,1,2,3]:
            new_pos = list(self.agent_pos)
            if action == 0: new_pos[0] -= 1  # 上
            elif action == 1: new_pos[0] += 1  # 下
            elif action == 2: new_pos[1] -= 1  # 左
            elif action == 3: new_pos[1] += 1  # 右
            new_pos = tuple(new_pos)

            # 检查是否撞墙或出界
            if (0 <= new_pos[0] < self.height and 0 <= new_pos[1] < self.width 
                and self.grid[new_pos] != 'W'):
                self.agent_pos = new_pos
                info['move_success'] = True
            else:
                info['move_success'] = False
                reward -= 0.1  # 撞墙惩罚

        # 收集
        elif action == 4:
            if self.agent_pos in self.item_positions and self.agent_pos not in self.collected:
                self.collected.add(self.agent_pos)
                reward += 1.0  # 收集奖励
                info['collected'] = True
            else:
                info['collected'] = False
                reward -= 0.2  # 无效收集惩罚

        # 检查任务完成：所有物品收集完且到达目标
        if len(self.collected) == len(self.item_positions) and self.agent_pos == self.goal_pos:
            self.done = True
            reward += 10.0  # 完成大奖

        # 检查步数超限
        if self.steps >= self.max_steps:
            self.done = True

        info['steps'] = self.steps
        return self._get_obs(), reward, self.done, info