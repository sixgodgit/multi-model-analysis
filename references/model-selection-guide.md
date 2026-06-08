# 多模型协作：模型选择指南

## 选择原则

选择模型时，要确保它们在以下方面有足够的差异：

1. **训练范式**：RLHF (ChatGPT)、Constitutional AI (Claude)、系统指令对齐 (Gemini)、后训练优化 (DeepSeek)、思考链 (Qwen Thinking)
2. **架构规模**：70B vs 235B vs MoE vs Dense
3. **文化对齐**：西方安全对齐 (Anthropic)、中文对齐 (Qwen/DeepSeek)、工具型 (GPT-4o)

## 推荐阵容（通过 OpenRouter）

| 简称 | 模型 ID | 哲学流派 | 特点 |
|:---|:---|:---|:---|
| DeepSeek R1 | deepseek/deepseek-r1 | 推理派 | 元认知强，长链推理，适合逻辑分析 |
| DeepSeek V3 | deepseek/deepseek-chat | 实用派 | 简洁直接，文学感强，批判有锐度 |
| DeepSeek V3.2 | deepseek/deepseek-v3.2 | 系统派 | 结构化输出，论证严谨，句子长但完整 |
| Qwen3 235B | qwen/qwen3-235b-a22b | 学院派 | 体系化思维，学术感，分章节论证 |
| Qwen Thinking | qwen/qwen3-235b-a22b-thinking-2507 | 思辨派 | 命题式批判，分层论证，有冲击力 |
| Claude Sonnet 4 | anthropic/claude-sonnet-4 | 安全派 | 非常谨慎，注重伦理边界，视角偏西方 |
| Gemini 2.5 Pro | google/gemini-2.5-pro | 系统派 | 系统工程思维，注重上下文和整体性 |
| GPT-4o | openai/gpt-4o | 通用派 | 均衡，但可能过于安全过滤 |

## 地区限制（HK 服务器实测）

- ✅ 可用：DeepSeek 全系、Qwen 全系
- ❌ 403：Claude Sonnet 4、Gemini 2.5 Pro、GPT-4o（region-locked）
- 备选策略：如果主要目标模型不可用，选择同流派但更旧的版本

## 读取输出时的注意事项

- DeepSeek R1 的输出可能包含 `[thinking]` 标签包起来的推理过程——需要区分"推理内容"和"最终回答"
- Qwen Thinking 版本也可能有类似的结构
- Claude 和 GPT-4o 的 403 错误通常意味着需要切换 VPN 节点或使用中转 API
