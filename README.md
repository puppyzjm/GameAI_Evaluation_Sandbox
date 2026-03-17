# GameAI Evaluation Sandbox

本项目是一个用于游戏 AI 行为评估的原型系统，包含自定义网格环境、MCP 风格工具接口、多场景测试框架以及三个迭代进化的 AI Agent。

## 核心特性
- 环境设计：2D 网格世界，支持墙壁、物品、目标点，提供 5x5 局部视野。
- 工具接口：类似 MCP 的 Agent 工具集（`move`、`collect`、`get_local_view` 等）。
- 评估体系：三个难度递增的测试场景（简单、障碍、迷宫），量化指标包括成功率、平均收集物品数、平均步数。
- Agent 迭代：
  - `RandomAgent`：随机策略，基线对比。
  - `RuleAgent`：基于局部视野的简单规则。
  - `AdvancedRuleAgent`：集成内部地图、记忆已收集物品、DFS 回溯、边界探索，并支持收集后 BFS 寻路至目标点。

## 实验结果

| 场景 | Agent | 成功率 | 平均收集物品数 |
|------|-------|--------|----------------|
| 场景1 | RandomAgent | 83.3% | 0.87 |
|       | RuleAgent | 96.7% | 1.00 |
|       | AdvancedRuleAgent | **100%** | 1.00 |
| 场景2 | RandomAgent | 53.3% | 2.77 |
|       | RuleAgent | 0% | 1.00 |
|       | AdvancedRuleAgent | **96.7%** | 2.97 |
| 场景3 | RandomAgent | 26.7% | 2.07 |
|       | RuleAgent | 0% | 1.00 |
|       | AdvancedRuleAgent | **20.0%** | 1.80 |

## 项目结构
GameAI_Evaluation_Sandbox/
├── agents/ # Agent 实现（Random, Rule, AdvancedRule）
├── environment/ # 环境核心（GridEnv, Tools）
├── scenarios/ # 测试场景 JSON 文件
├── evaluation/ # 评估脚本与 Jupyter 分析
├── logs/ # 运行日志（git ignored）
├── docs/ # 报告与协作模拟文档
└── README.md


## 快速开始
1. 克隆本仓库
2. 创建虚拟环境并安装依赖：`pip install numpy pandas matplotlib jupyter`
3. 运行评估：`python -m evaluation.run_evaluation`
4. 分析结果：`jupyter notebook` 打开 `evaluation/analyze.ipynb`

## 文档
- [行为分析报告](docs/behavior_analysis_report.md)
- [跨团队协作模拟](docs/collaboration_simulation.md)

## 未来改进
- 引入强化学习训练更智能的 Agent
- 接入 Unity/Unreal 引擎进行可视化测试
- 优化边界探索策略，进一步提升迷宫场景成功率