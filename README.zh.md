# EvolveAgent

**让你的 AI Agent 越用越聪明 —— 零配置，下载即用。**

中文 | [English](README.md)

## 问题

你的 agent 是不是这样：

- 同样的错犯 N 次——昨天纠正的，今天又踩
- 装了 300 个 skill，真正在执行的没几个——该呼叫的不呼叫，不该送的天天送
- 提示词越来越胖——每轮烧 token，还分散模型注意力

试过「记忆系统」？残酷的事实：**记忆解决「记不记得」，解决不了「遵不遵守」**——这是两个完全不同的题。

## 解法

三个脚本，关上一个**自我进化闭环**：

| 脚本 | 超能力 | 用法 |
|------|--------|------|
| `planner.py` | 任务前强制五步规划，**目标没写清直接拦下开工**（exit 2）——干掉「绕四小时」的失败模式 | `python3 planner.py "任务"` |
| `learn.py` | 扫日志负面反馈 → AI 裁判判定成败 → **教训自动提炼入库** | `python3 learn.py --hours 24` |
| `upgrade.py` | 教训 → **自动改进对应 skill**（幂等、只追加、不覆盖） | `python3 upgrade.py --apply` |

```
失败日志 → LLM 裁判 → lessons/<类型>.md → upgrade.py 自动 patch skill
   → 下次任务读到净化的 skill → 不再犯同类错误 → 循环
```

## 安装（10 秒，零配置）

```bash
cp -r evolve-agent ~/.hermes/skills/
# 重启 gateway，搞定

# 可选：cron 每天自动进化
#   0 1 * * *  learn.py --hours 24 && upgrade.py --apply
```

## 30 秒验证有效

```bash
cd evolve-agent/scripts
python3 planner.py "随便什么任务"   # 目标留空 → 被 exit 2 拦截
```

被拦住 = 生效。就这么简单。

## 为什么有效（三句话）

1. **系统一/系统二**（《思考，快与慢》）：本能行为代码化，真正要思考的才用 LLM
2. **关键路径移出 LLM**：可靠性来自代码执行，不是模型自觉
3. **失败是金子**：失败轨迹的反事实信号，比成功更值钱（ReasoningBank, ICLR 2026）

## 配置（全部可选，默认零配置）

| 环境变量 | 默认 | 说明 |
|---------|------|------|
| `HERMES_HOME` | `~/.hermes` | Hermes 数据目录 |
| `LLM_BASE_URL` | `http://localhost:8080/v1` | 任意 OpenAI 兼容端点（Ollama/Gemma/DeepSeek/OpenAI/通义...） |
| `LLM_API_KEY` | 空 | 空 = 本地免认证 |
| `LLM_MODEL` | `qwen2.5:7b` | 裁判模型 |

## 避坑（替你先踩过了）

- AI 裁判 **70% 准确率就够**——别追求完美，追求迭代
- 教训必须**可迁移**（「这类任务该怎么想」），不是「这次我做了什么」
- **幂等必须有**——否则 skill 被同一教训反复污染
- **只追加不覆盖**——净化是叠加改进，不是重写用户的 skill

## 与 Hermes skill 模型的关系

`evolve-agent/` 就是一个普通 Hermes skill 目录：`SKILL.md`（路由+说明）+ `scripts/`（真正的逻辑）。丢进 skills 目录，索引自动收录。确定性部分（校验、去重、patch）全在脚本里——**关键路径上不经过模型采样**。

## 框架支持 — 先读这个

**✅ Hermes：下载即用，零配置。** 这是唯一的零二次开发承诺范围。

**⚠️ 其他 agent 框架：机制能用，但你必须自己适配**（两处小改）：

| 脚本 | Hermes 默认（零配置） | 其他框架：你要改什么 |
|------|----------------------|---------------------|
| `learn.py` | 解析 `inbound message: text=...` 日志行 | 重写 `extract_user_message()` 正则为你的日志格式 |
| `upgrade.py` | 找 `skills/<名字>/SKILL.md` | 重写 `find_skill()` 为你的 skill/知识目录结构 |
| `planner.py` | 无 | 无——天生框架无关 |

全部通过 `HERMES_HOME` / `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` 环境变量配置。

## License

MIT
