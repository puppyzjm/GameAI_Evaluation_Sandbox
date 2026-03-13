import json
import csv
import os
from environment.grid_env import GridEnv
from environment.tools import AgentTools
from agents.random_agent import RandomAgent
from agents.rule_agent import RuleAgent
from agents.advanced_rule_agent import AdvancedRuleAgent

# 获取项目根目录（当前脚本所在目录的上一级）
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_scenario(filename):
    with open(filename, 'r') as f:
        grid = json.load(f)
    return grid

def run_episode(env, agent, max_steps, episode_id, scenario_name, agent_name):
    """运行一局，返回日志记录列表"""
    env.reset()
    tools = AgentTools(env)
    agent.tools = tools  # 将 tools 绑定到 agent

    logs = []
    for step in range(max_steps):
        action = agent.act()
        pos = env.agent_pos
        collected = len(env.collected)
        done = env.done

        log_entry = {
            'episode': episode_id,
            'scenario': scenario_name,
            'agent': agent_name,
            'step': step,
            'pos_x': pos[0],
            'pos_y': pos[1],
            'action': action,
            'collected': collected,
            'done': done
        }
        logs.append(log_entry)

        if done:
            break
    return logs

def main():
    scenarios = {
        'scenario1': os.path.join(base_dir, 'scenarios', 'scenario1.json'),
        'scenario2': os.path.join(base_dir, 'scenarios', 'scenario2.json'),
        'scenario3': os.path.join(base_dir, 'scenarios', 'scenario3.json')
    }
    agents = {
        'RandomAgent': RandomAgent,
        'RuleAgent': RuleAgent,
        'AdvancedRuleAgent': AdvancedRuleAgent
    }
    num_episodes = 30
    max_steps = 200

    all_logs = []

    for scene_name, scene_file in scenarios.items():
        grid = load_scenario(scene_file)
        for agent_name, agent_class in agents.items():
            for ep in range(num_episodes):
                env = GridEnv(grid, max_steps=max_steps)
                tools = AgentTools(env)
                agent = agent_class(tools)
                logs = run_episode(env, agent, max_steps, ep, scene_name, agent_name)
                all_logs.extend(logs)
                print(f"Completed {agent_name} on {scene_name} episode {ep}")

    # 日志文件路径（使用绝对路径）
    log_file = os.path.join(base_dir, 'logs', 'evaluation_logs.csv')
    # 确保 logs 目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, 'w', newline='') as f:
        fieldnames = ['episode', 'scenario', 'agent', 'step', 'pos_x', 'pos_y', 'action', 'collected', 'done']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_logs)

    print("Evaluation finished. Logs saved to logs/evaluation_logs.csv")

if __name__ == '__main__':
    main()