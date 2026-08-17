# EvolveAgent

**让你的 AI Agent 越用越聪明 —— 零配置，下载即用。**

中文 | [English](README.md)

## 问题

你的 agent 是不是这样：

- 同样的错犯 N 次——昨天纠正的，今天又踩
- 装了 300 个 skill，真正在执行的没几个——该呼叫的不呼叫，不该送的天天送
- 提示词越来越胖——每轮烧 token，还分散模型注意力

试过「记忆系统」？残酷的事实：**记忆解决「记不记得」，解决不了「遵不遵守」**——这是两个完全不同的题。

## 哲学：规则是代码，不是文档

skill 文件是**文档**——它只有被模型读到、且模型决定遵守时才生效。不可靠。

**EvolveAgent 把教训变成代码。** 一条教训被编译成 guardrail 规则，**在任务执行前运行**，违反就**拦截（exit 2）**。不需要模型自觉——规则要么通过，要么不通过。

## 4 个脚本 = 4 个环节

| 脚本 | 环节 | 用法 |
|------|------|------|
| `planner.py` | 任务前强制五步规划，**目标没写清直接拦下开工**（exit 2） | `python3 planner.py "任务"` |
| `learn.py` | 扫日志负面反馈 → AI 裁判判定 → **教训自动入库** | `python3 learn.py --hours 24` |
| `upgrade.py` | 教训 → **编译成 guardrail 代码**（规则数据 + 检查函数） | `python3 upgrade.py --apply` |
| `guardrail.py` | **执行前强制检查**：运行规则代码，违规 exit 2，教训清单输出给 agent 对照 | `python3 guardrail.py <类型> "任务"` |

```
失败日志 → learn.py → lessons/<类型>.md → upgrade.py → guardrails/<类型>.py（代码）
                                                          ↓
             任务执行前：guardrail.py <类型> "任务" → 违规 = exit 2 拦截
```

## 安装（10 秒，零配置）

```bash
cp -r evolve-agent ~/.hermes/skills/
# 重启 gateway，搞定

# 可选：cron 每天自动进化
#   0 1 * * *  learn.py --hours 24 && upgrade.py --apply
# 可选：任务前强制检查（建议写进你 agent 工作流的第一步）
#   python3 guardrail.py <类型> "<任务描述>"
```

## 30 秒验证有效

```bash
cd evolve-agent/scripts
python3 planner.py "随便什么任务"      # 目标留空 → exit 2
python3 guardrail.py ppt "做PPT"       # 描述过短 → exit 2
```

被拦住 = 生效。就这么简单。

## 为什么有效（三句话）

1. **系统一/系统二**（《思考，快与慢》）：本能行为代码化，真正要思考的才用 LLM
2. **关键路径移出 LLM**：可靠性来自代码执行，不是模型自觉——guardrail 是代码，违反必拦截
3. **失败是金子**：失败教训编译成代码规则，下次执行前强制检查（ReasoningBank, ICLR 2026）

## 避坑（替你先踩过了）

- AI 裁判 **70% 准确率就够**——别追求完美，追求迭代
- 教训必须**可迁移**（「这类任务该怎么想」），不是「这次我做了什么」
- **upgrade.py 写的是代码，不是文档**——往 md 文档追加教训，恰恰是这个包不做的事
- 任务类型用**通用词**（ppt/pdf/research/code/image/data/chat），不绑定任何特定 skill 名

## 框架支持 — 先读这个

**✅ Hermes：下载即用，零配置。** 这是唯一的零二次开发承诺范围。

**⚠️ 其他 agent 框架：机制能用，但你必须自己适配**（两处小改）：

| 脚本 | Hermes 默认（零配置） | 其他框架：你要改什么 |
|------|----------------------|---------------------|
| `learn.py` | 解析 `inbound message: text=...` 日志行 | 重写 `extract_user_message()` 正则为你的日志格式 |
| `upgrade.py` | 读 `~/.hermes/skills/lessons/` | 把 `LESSONS_DIR` 指向你的教训目录 |
| `planner.py` / `guardrail.py` | 无 | 无——天生框架无关 |

全部通过 `HERMES_HOME` / `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` 环境变量配置。

## License

MIT
