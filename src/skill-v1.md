---
name: multi-model-analysis
category: research
description: |
  多模型深度分析工作流。当需要多角度、多流派视角来审视一个复杂问题时，
  通过 API 平行调用多个不同模型，分别读取各自输出，再合成统一分析结论。
triggers:
  - 用户要求"深度思考"、"用不同模型协作"、"多角度分析"
  - 哲学、伦理、技术评估等需要多维视角的问题
  - 需要验证"多个模型是否达成共识"的命题
steps:
  1. 评估问题性质：是否需要多模型协作。
     哲学/伦理/技术设计争议 → 适合。事实查询/编码 → 单模型足矣。
  2. 选择模型阵容：确保训练范式、架构、对齐策略足够多样。
     推荐组合（OpenRouter）：deepseek/deepseek-r1, qwen/qwen3-235b-a22b,
     qwen/qwen3-235b-a22b-thinking-2507, deepseek/deepseek-chat,
     deepseek/deepseek-v3.2. 备选：anthropic/claude-sonnet-4, google/gemini-2.5-pro
     （可能受地区限制）。
  3. 创建统一 prompt 文件（写入 /tmp/），包含背景说明和格式要求。
  4. 运行 scripts/call_models.py 脚本，输出到 /tmp/multi_model_responses/。
  5. 逐一读取各模型响应，然后合成分析。
  6. 合成方法：找共性（跨模型共识）→ 找差异（独特视角）→ 找缺席（你可以补充的）。
  7. 输出最终合成报告。
pitfalls:
  - 模型名称在 OpenRouter 上会变。先用 API 查可用列表再选。
  - 某些模型在 HK 服务器被 region-restrict。优雅降级。
  - 不要用 terminal background 做顺序 API 调用。正确做法：一个 Python 脚本里顺序循环，加 0.5s delay。
  - 不要在 prompt 里写"不要安全废话"——安全 filter 会拒绝。
  - 输出质量不等：短而有锐度 > 长而空洞。
scripts:
  - scripts/call_models.py: 多模型调用脚本
references:
  - references/deep-question-template.md: 深度分析 prompt 模板
  - references/model-selection-guide.md: 各模型哲学流派对比
---
# Multi-Model Deep Analysis

> ⚠️ **已废弃** — 本技能已被 `research/multi-model-collaboration` 完全覆盖。
> 所有内容已冻结，保留仅作为生态评估的历史记录。
> 如需执行多模型分析，请加载 `research/multi-model-collaboration`，其中包含更完整的文档、脚本和引用文件。

该技能在 2026-06-05 生态评估中被标记为 duplicated，与 research/multi-model-collaboration 功能完全重复且内容更少。后续加载时应无视此版本。

进行深度分析时，调用多个不同模型获取独立视角，再合成统一结论。

## 原理

不同训练范式、架构、对齐策略的模型，在面对同一问题时会产出不同风格的思考。
通过"分别提问 → 分别读取 → 统一合成"的方式，可以获得比单模型更丰富的分析维度。

## 典型流程

1. 写好跨模型共享的 prompt
2. 用脚本平行调用 3-5 个不同模型
3. 读取各自输出
4. 找共识、找差异、找缺席
5. 输出合成报告

## 成功案例

本技能来自 DeepSeek V4 Flash 分析"Skills Judgment 熵减系统是否符合 AI 的现代定位"
的实际工作流。调用了 5 个模型（DeepSeek V3/V3.2/R1 + Qwen3 235B/Thinking），
所有模型 100% 一致批判该系统，形成有说服力的多模型共识结论。

## 脚本依赖

- Python 3.11+
- urllib（标准库）
- 可用的 API key（Hermes 主配置文件中的 OPENROUTER_API_KEY）
