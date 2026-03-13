import random

class RandomAgent:
    def __init__(self, tools):
        self.tools = tools
        self.actions = ['up', 'down', 'left', 'right', 'collect']

    def act(self):
        # 随机选择一个动作
        action = random.choice(self.actions)
        # 如果是移动，就调用move；如果是收集，就调用collect
        if action == 'collect':
            self.tools.collect()
        else:
            self.tools.move(action)
        return action