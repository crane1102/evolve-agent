---
name: evolve-agent
description: Use when 想让 agent 自我进化。3 个脚本：强制规划、失败学习、自动改进 skill。零配置下载即用。
triggers:
  - "任务执行前"
  - "失败复盘"
  - "skill 优化"
  - "提示词瘦身"
---

# EvolveAgent — 让你的 Agent 越用越聪明

## 30 秒看懂

你的 agent 是不是这样：
- 同样的错犯 N 次，昨天纠正的今天又踩
- 写了 300 个 skill，真正在执行的没几个
- 提示词越来越胖，每轮烧钱还变笨

**这个包用 3 个脚本解决：把「不用思考的行为」固化进代码（必然执行），把「失败的经验」自动写回 skill（不再犯）。**

## 3 个脚本 = 3 个超能力

| 脚本 | 超能力 | 用法 |
|------|--------|------|
| `planner.py` | 任务前强制五步规划，**目标没写清直接拦下开工**（exit 2） | `python3 planner.py "任务"` |
| `learn.py` | 扫日志负面反馈 → AI 裁判判定 → **教训自动入库** | `python3 learn.py --hours 24` |
| `upgrade.py` | 教训 → **自动改进对应 skill**（幂等、只追加、不覆盖） | `python3 upgrade.py --apply` |

## 安装（10 秒，零配置）

```bash
cp -r evolve-agent ~/.hermes/skills/
# 重启 gateway，搞定
# 可选：挂 cron 每天自动学习进化
#   0 1 * * *  → learn.py --hours 24 && upgrade.py --apply
```

## 30 秒验证有效

```bash
cd evolve-agent/scripts
python3 planner.py "随便什么任务"   # 不填目标会被 exit 2 拦截
```

被拦住 = 生效。就是这么简单。

## 为什么有效（三句话）

1. **系统一/系统二**（《思考，快与慢》）：本能行为代码化，真正要思考的才用 LLM
2. **关键路径移出 LLM**：可靠性来自代码执行，不是模型自觉
3. **失败是金子**：失败轨迹的反事实信号，比成功更值钱（ReasoningBank, ICLR 2026）

## 避坑（替你先踩过了）

- AI 裁判 70% 准确率就够，别追求完美
- 教训要写「这类任务该怎么想」，不是「这次做了什么」
- 幂等必须有，否则 skill 被同一教训反复污染
- 只追加不覆盖——净化是叠加改进，不是重写

## 环境变量（全部可选，默认零配置）

| 变量 | 默认 | 说明 |
|------|------|------|
| `HERMES_HOME` | `~/.hermes` | Hermes 数据目录 |
| `LLM_BASE_URL` | `http://localhost:8080/v1` | OpenAI 兼容端点（Ollama/Gemma/DeepSeek/OpenAI/通义都行） |
| `LLM_API_KEY` | 空 | 本地免认证 |
| `LLM_MODEL` | `qwen2.5:7b` | 裁判模型 |
