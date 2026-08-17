---
name: evolve-agent
description: Use when 想让 agent 自我进化。4 个脚本：强制规划、失败学习、教训→guardrail 代码、执行前强制检查。
triggers:
  - "任务执行前"
  - "失败复盘"
  - "workflow 代码化"
  - "提示词瘦身"
---

# EvolveAgent — 让你的 Agent 越用越聪明

## 30 秒看懂

你的 agent 是不是这样：
- 同样的错犯 N 次，昨天纠正的今天又踩
- 写了 300 个 skill，真正在执行的没几个
- 提示词越来越胖，每轮烧钱还变笨

**这个包的核心哲学：把「规则」从文档变成代码。**
skill 文档靠模型「读到并自觉遵守」——不可靠。代码规则**必然执行**，违反就拦截。教训不再写进 md，而是编译成 guardrail 代码，任务执行前强制检查。

## 4 个脚本 = 4 个环节

| 脚本 | 环节 | 用法 |
|------|------|------|
| `planner.py` | 任务前强制五步规划，**目标没写清直接拦下开工**（exit 2） | `python3 planner.py "任务"` |
| `learn.py` | 扫日志负面反馈 → AI 裁判判定 → **教训自动入库**（lessons/） | `python3 learn.py --hours 24` |
| `upgrade.py` | 教训 → **编译成 guardrail 代码**（guardrails/<类型>.py，含规则数据 + 检查函数） | `python3 upgrade.py --apply` |
| `guardrail.py` | **执行前强制检查**：加载规则代码，违规 exit 2 拦截，教训清单输出给 agent 对照 | `python3 guardrail.py <类型> "任务"` |

```
失败日志 → learn.py → lessons/<类型>.md → upgrade.py → guardrails/<类型>.py（代码）
                                              ↓
        执行前：guardrail.py <类型> "任务" → 违规 exit 2 拦截 / 通过继续
```

## 安装（10 秒，零配置）

```bash
cp -r evolve-agent ~/.hermes/skills/
# 重启 gateway，搞定
# 可选：cron 每天自动学习进化
#   0 1 * * *  learn.py --hours 24 && upgrade.py --apply
# 任务前强制检查（建议写进你的 agent 工作流第一步）
#   python3 guardrail.py <类型> "<任务描述>"
```

## 30 秒验证有效

```bash
cd evolve-agent/scripts
python3 planner.py "随便什么任务"      # 目标留空 → exit 2 拦截
python3 guardrail.py ppt "做PPT"       # 描述过短 → exit 2 拦截
```

被拦住 = 生效。就这么简单。

## 为什么有效（三句话）

1. **系统一/系统二**（《思考，快与慢》）：本能行为代码化，真正要思考的才用 LLM
2. **关键路径移出 LLM**：可靠性来自代码执行，不是模型自觉——guardrail 是代码，违反必拦截
3. **失败是金子**：失败教训编译成代码规则，下次执行前强制检查（ReasoningBank, ICLR 2026）

## 避坑（替你先踩过了）

- AI 裁判 70% 准确率就够，别追求完美
- 教训要写「这类任务该怎么想」，不是「这次做了什么」
- upgrade 生成的是**代码规则**，不是往 md 文档追加文字——文档靠自觉，代码才必然执行
- 任务类型用通用词（ppt/pdf/research/code/image/data/chat），不绑定任何特定 skill 名

## 环境变量（全部可选，默认零配置）

| 变量 | 默认 | 说明 |
|------|------|------|
| `HERMES_HOME` | `~/.hermes` | Hermes 数据目录 |
| `LLM_BASE_URL` | `http://localhost:8080/v1` | OpenAI 兼容端点（Ollama/Gemma/DeepSeek/OpenAI/通义都行） |
| `LLM_API_KEY` | 空 | 本地免认证 |
| `LLM_MODEL` | `qwen2.5:7b` | 裁判模型 |
