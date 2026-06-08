---
name: multi-model-routing
description: "Intelligent multi-model scheduling strategy — dispatch tasks between MiMo (main brain) and DeepSeek (auxiliary) based on complexity, modality, and cost. Balances reasoning depth vs. operational economy."
version: 1.0.0
author: Agent (user-defined strategy)
tags: [hermes, routing, model-selection, cost-optimization, miMo, deepseek, scheduling]
---

# Multi-Model Routing Strategy

用户定义的模型调度策略，在复杂任务处理能力和日常运行经济性之间找到平衡。

## Core Principle

> ⚠️ **用户已重新定义路由策略（2026-06）**：复杂任务走 DeepSeek，简单任务走 MiMo。
> 详见 `core-task-routing` 技能。以下为旧策略，保留供参考。

**旧策略（已被覆盖）：**
- **主模型（MiMo V2.5 / V2.5 Pro / Omni）** — 负责所有核心逻辑推理、复杂工具调用、跨会话记忆管理
- **辅助模型（DeepSeek V4 Flash）** — 仅用于轻量级、高频次、低复杂度任务

严禁将复杂逻辑推理或视觉任务分配给辅助模型。

## Routing Decision Tree

```
收到任务
│
├─ 有图片/视频/音频 → MiMo-V2-Omni (原生视觉，直连国内)
├─ 长文本/几十万字文档 → MiMo-V2.5 (100B+参数，1M上下文)
├─ 复杂推理/深度思考 → MiMo-V2.5-Pro (全球前三推理)
├─ 跨会话记忆/系统配置 → MiMo（主模型）
│
├─ 日常闲聊/简短问答 → DeepSeek V4 Flash（轻量级，省钱）
├─ 网页内容摘要/上下文压缩 → DeepSeek V4 Flash
├─ 简单翻译/格式转换 → DeepSeek V4 Flash
│
└─ 需要搜索/工具调用 → Hermes Agent（本地免费）
```

## Provider Configurations

### MiMo Token Plan (中国区) — 主模型

| 项目 | 值 |
|------|-----|
| Endpoint | `https://token-plan-cn.xiaomimimo.com/v1/chat/completions` |
| Key env | `MIMO_API_KEY` / `XIAOMI_API_KEY` |
| Models | `mimo-v2.5` (文本), `mimo-v2-omni` (全模态), `mimo-v2.5-pro` (推理) |
| Cost | 缓存命中 ¥0.02-0.025/百万token；Token Plan ¥39/月 |
| Notes | 默认带 `reasoning_content`（思考链），max_tokens 需设足够大 |

### DeepSeek V4 Flash — 辅助模型

| 项目 | 值 |
|------|-----|
| Endpoint | `https://api.deepseek.com/v1/chat/completions` |
| Key env | `DEEPSEEK_API_KEY` |
| Models | `deepseek-chat` (V4 Flash) |
| Cost | 输入 ¥1/百万token，输出 ¥2/百万token |
| Notes | 纯文本模型，不支持图片/视频输入 |

### Hermes Agent — 工具模型

| 项目 | 值 |
|------|-----|
| Endpoint | `http://127.0.0.1:8642/v1` |
| Key env | `API_SERVER_KEY` |
| Models | `hermes-agent` |
| Cost | 免费（本地运行） |
| Notes | 带 web_search + web_extract 等工具 |

## Hermes Agent Config

设置 MiMo 为默认主模型：

```bash
hermes config set model.provider xiaomi
hermes config set model.default mimo-v2.5
hermes config set model.base_url https://token-plan-cn.xiaomimimo.com/v1
```

确保 `.env` 中有 `XIAOMI_API_KEY=...`（与 `MIMO_API_KEY=...` 相同值）。

## Webchat Smart Router (Frontend)

```javascript
function pickModel(text, file) {
  // Image → MiMo (native vision, direct connect)
  if (file && file.type.startsWith('image/'))
    return 'mimo-v2-omni';
  // Document / large file → DeepSeek V4 (1M context)
  if (file && !file.type.startsWith('image/'))
    return 'deepseek-chat';
  // Complex reasoning → MiMo (main brain)
  if (text && (text.length > 800 || /^(解释|分析|对比|比较|推理|计算|推导|证明|实现|如何|为什么|区别|优缺点|设计方案|架构|性能|优化|调试|错误|bug|修复|翻译|总结|概述)/.test(text)))
    return 'mimo-v2.5';
  // Text processing / translation → DeepSeek V4 (lightweight)
  if (text && /^(翻译|改写|润色|缩写|扩写|转述|format|rewrite|summarize)/i.test(text))
    return 'deepseek-chat';
  // Search / knowledge / chat → Hermes (free, with tools)
  return 'hermes-agent';
}
```

## Reasoning Content Behavior

MiMo 模型（`mimo-v2.5`）默认输出 `reasoning_content` 字段——模型在生成回复前会进行内部思考链。表现：

- 简单问答也会产生一段 reasoning（通常几十到几百 tokens）
- `max_tokens` 设置过小时，思考链会吃掉所有分配 tokens，导致 `finish_reason: "length"` 且 `content: ""`
- **修复**：至少设 `max_tokens >= 100`，复杂任务设 2000+

API 响应示例：
```json
{
  "choices": [{
    "message": {
      "content": "你好！我是小米MiMo...",
      "reasoning_content": "用户要求介绍自己，这是一个直接的身份确认查询..."
    }
  }]
}
```

## OpenRouter 备用模型（中国区限制）

OpenRouter 可作为备用提供商，但有区域限制：

| 模型 | 中国区可用 | 说明 |
|------|-----------|------|
| **GPT-4o / GPT-4o-mini** | ❌ 不可用 | 403 Forbidden |
| **Claude 系列** | ❌ 不可用 | 403 Forbidden |
| **Llama 3.1** | ✅ 可用 | $0.02/$0.03 每百万token |
| **Qwen3** | ✅ 可用 | 按 OpenRouter 定价 |
| **Gemma 2** | ✅ 可用 | 按 OpenRouter 定价 |
| **Mistral** | ✅ 可用 | 按 OpenRouter 定价 |

**配置**：`.env` 中设置 `OPENROUTER_API_KEY`，config.yaml 中 `auxiliary.vision.provider: openrouter` 已配置。

**用途**：
- MiMo 故障时自动切换到 Llama 3.1 作为备用
- 辅助任务（vision、compression）使用 OpenRouter 的便宜模型
- 不建议作为主力（中国区不可用 GPT/Claude，性价比不如 MiMo）

## Pitfalls

- **Token Plan Key 的端点不同**
- **Token Plan Key 的端点不同**。标准 MiMo Key（`sk-...`）走 `api.xiaomimimo.com`，Token Plan Key（`tp-cn...`）必须走 `token-plan-cn.xiaomimimo.com`。端点用错返回 401 Invalid API Key（即使 Key 本身有效）。
- **max_tokens 不足导致 MiMo 返回空 content**。MiMo 有 reasoning_content 机制，max_tokens 设太小（< 50）经常只输出 reasoning 不输出 content。设 100+ 可解决。
- **主模型切换需要新会话生效**。`hermes config set` 修改的 model.provider/default/base_url 等配置在当前会话不生效，需要 `/reset` 或重启 CLI/Gateway。
- **不混用路由层级**。Webchat 的智能路由是前端逻辑，只在用户通过 webchat 发消息时自动选择模型。Hermes Agent 自己的主模型是单独的配置（`config.yaml`），两者互不干扰。
