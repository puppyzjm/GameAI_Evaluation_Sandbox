class AgentTools:
    def __init__(self, env):
        self.env = env

    def get_position(self):
        return self.env.agent_pos

    def get_local_view(self):
        """返回5x5视野，每个格子是字符：'W','I','G','S','.'"""
        return self.env._get_obs()['view']

    def get_collected_count(self):
        return len(self.env.collected)

    def get_total_items(self):
        return len(self.env.item_positions)

    def is_task_complete(self):
        return (len(self.env.collected) == len(self.env.item_positions) 
                and self.env.agent_pos == self.env.goal_pos)

    def move(self, direction):
        """direction: 'up','down','left','right'"""
        dir_map = {'up':0, 'down':1, 'left':2, 'right':3}
        if direction not in dir_map:
            return False
        obs, reward, done, info = self.env.step(dir_map[direction])
        return info.get('move_success', False)

    def collect(self):
        obs, reward, done, info = self.env.step(4)
        return info.get('collected', False)