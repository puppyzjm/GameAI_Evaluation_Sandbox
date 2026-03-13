class RuleAgent:
    def __init__(self, tools):
        self.tools = tools
        self.last_pos = None
        self.stuck_count = 0

    def act(self):
        # 获取视野
        view = self.tools.get_local_view()
        pos = self.tools.get_position()

        # 检查是否卡住（连续两回合位置没变）
        if pos == self.last_pos:
            self.stuck_count += 1
        else:
            self.stuck_count = 0
        self.last_pos = pos

        # 策略1：如果脚下有物品且未收集，优先收集
        center = view[2,2]  # 5x5视野中心就是自己所在格子
        if center == 'I' and self.tools.get_collected_count() < self.tools.get_total_items():
            self.tools.collect()
            return 'collect'

        # 策略2：如果附近有可见的物品，尝试走向它（简单启发：找最近的可见物品）
        # 为了简化，这里用随机移动+简单避障
        # 实际可以改进为BFS，但作为演示，我们用随机+不撞墙
        import random
        directions = ['up','down','left','right']
        random.shuffle(directions)
        for d in directions:
            # 检查对应方向是否可行（粗略检查视野边缘）
            # 这里简化：如果视野边界不是墙，就尝试移动
            # 注意：视野边界可能对应地图外，但move会处理
            if self.tools.move(d):
                return d

        # 如果所有方向都撞墙，那就随便移动（但可能继续撞）
        self.tools.move(random.choice(['up','down','left','right']))
        return 'random_move'