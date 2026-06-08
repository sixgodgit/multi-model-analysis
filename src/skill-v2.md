---
name: multi-model-collaboration
description: "Orchestrate multiple different AI models to collaborate on complex reasoning tasks — select diverse models, craft unified prompts, collect independent responses, and synthesize findings."
version: 1.0.0
author: Hermes Agent
license: MIT
dependencies: [python3, curl]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [multi-model, collaboration, synthesis, philosophy, cross-model]
    related_skills: [subagent-driven-development, architecture-diagram]
---

# Multi-Model Collaboration

A systematic methodology for conducting deep multi-perspective analysis by calling multiple different AI models with the **same prompt**, collecting their independent responses, and synthesizing them into a coherent final answer.

> **注意:** 本技能已合并 root-level 的 `multi-model-analysis` — 后者为 2026-06-05 创建的粗版，功能完全被此版本覆盖。`multi-model-analysis` 已在生态评估中被标记为 `delete_candidate`。后续加载时应无视 `multi-model-analysis`，直接使用此版本。

## When to Use

Use this skill when the question has **no single right answer** and benefits from multiple independent perspectives:

- **Philosophical questions** — "What is X's relationship to Y in modern society?"
- **Meta-analysis** — "Is this design/idea good or bad, and why?"
- **Verification** — "Do all models agree on this premise, or is it model-specific?"
- **Multi-perspective evaluation** — "How would different schools of thought assess this?"
- **Bias detection** — "Is a particular viewpoint model-dependent or universally agreed?"

Do NOT use for: factual lookup, code generation, math problems, or any question with a single correct answer. Multi-model collaboration adds cost and latency — reserve it for genuinely ambiguous, subjective, or philosophical territory.

## Workflow

### 1. Select Models for Diversity

The key insight: choose models from **different families** (different training data, alignment strategies, architecture paradigms). Similar models will produce similar outputs — defeating the purpose.

**Best diversity set (via OpenRouter):**

| Model | Philosophy | Why Include |
|:---|:---|:---|
| `deepseek/deepseek-chat` (V3) | Literary-critical | Sharp, poetic, metaphorical |
| `deepseek/deepseek-v3.2` | Structural-analytical | Well-structured, rigorous argumentation |
| `deepseek/deepseek-r1` | Radical-critical | High tension, dramatic framing |
| `qwen/qwen3-235b-a22b` | Chinese-aligned | Systematic, academic, culturally distinct |
| `qwen/qwen3-235b-a22b-thinking-2507` | Speculative-critical | Propositional, incisive different angle |

**Backup tier** (region-restricted on some OpenRouter endpoints):
- `anthropic/claude-sonnet-4` — Safety-first, Western philosophical tradition
- `google/gemini-2.5-pro` — Systems-thinking, very different training paradigm
- `openai/gpt-4o` — Generally available, broad perspective
- `deepseek/deepseek-v3.2` — Newer than V3, different emphasis

**Minimum viable set:** 3 models from at least 2 different families.

### 2. Craft the Prompt

The prompt structure is critical. Each model needs the **exact same prompt** to produce comparable outputs.

Template:
```
## [Topic Name]

## Background
[3-5 sentences of context — what the system/idea is, how it works, the user's specific framing]

## Please analyze from these perspectives
### 1. Cognitive Level
[Specific question about the cognitive/epistemological dimension]

### 2. Social Level
[Specific question about the social/historical dimension]

### 3. Power Level
[Specific question about the power/political dimension]

## Format requirements
- Use Chinese (or the user's language)
- About 800-1000 characters
- [Tone/style requirements — e.g., "要有锐度，不要安全废话"]
```

**Critical:** Never include "what do you think" or "give me your perspective" in a way that implies the model should respond differently from others. Models naturally diverge — let them.

### 3. Call Models — Sequential or Batched

**Sequential (default):** Use `terminal()` with Python `urllib.request`. Each sequential call takes 10-20s.

Write a Python script:

```python
import json, urllib.request, os

API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
with open('/tmp/prompt.md') as f:
    PROMPT = f.read()

for name, model in [('model1', 'provider/model-id'), ...]:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": 1500,
        "temperature": 0.7
    }).encode('utf-8')

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=50) as resp:
        data = json.loads(resp.read())
    content = data['choices'][0]['message']['content']
    with open(f'/tmp/{name}_response.txt', 'w') as f:
        f.write(content)
```

**Batched (parallel):** Use `delegate_task` with multiple tasks, each calling a different model. Faster but more complex to aggregate results.

### 4. Handle Failures Gracefully

**Common failure modes:**

| Error | Cause | Fix |
|:---|:---|:---|
| `Not Found` | Wrong model ID | Run `curl -H "Authorization: Bearer $KEY" https://openrouter.ai/api/v1/models \| python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data'] if 'claude' in m['id']]"` to list valid IDs |
| `not available in your region` | Geo-restriction | Try backup tier models from the list above |
| Timeout (50s+) | Model is slow | Increase timeout, or skip this model entirely |
| Empty response / truncated | Token limit hit | Increase `max_tokens` to 2000+ |

**Rule:** Always check `data['choices'][0]['message']['content']` exists before writing. On failure, log the raw response for debugging.

### 5. Synthesize Responses

After collecting all model outputs:

1. **Read all responses** — look for themes, not individual arguments
2. **Find consensus** — what do ALL models agree on? This is the strongest signal
3. **Find unique insights** — what did ONE model say that others missed?
4. **Find contradictions** — where do models disagree? This is often the most interesting finding
5. **Meta-observation** — the fact that N/N models all agreed (or all disagreed) is itself a finding

**Synthesis structure:**
```
## Layer 1: Meta-Discovery
[The fact that X/Y/Z models all converged/divered]

## Layer 2: Consensus Analysis
[Across 3 dimensions — cognitive, social, power]

## Layer 3: Unique Contributions
[What each model uniquely contributed]

## Layer 4: My Own Take
[Your own synthesis + added value beyond what any single model provided]
```

### 6. (Optional) Visualize Results

For particularly rich analyses, create an HTML infographic:

1. Write a dark-themed HTML page with the analysis (see `references/infographic-pipeline.md`)
2. Convert to PNG using weasyprint + pdftoppm for delivery
3. Send via MEDIA: path on the messaging platform

## Pitfalls

- **❗DO NOT** put multiple `&` background processes in a single foreground `terminal()` call — use `background=true` or sequential calls instead
- **❗DO NOT** use shell `$()` for variable expansion in `write_file` content — the tool processes it. Use Python to construct the file content.
- **❗Model IDs can differ** between OpenRouter API doc and actual usable IDs. Always verify with the models endpoint.
- **❗Always query OpenRouter models endpoint first** to find exact model IDs before writing the API script. Region blocks change frequently — a model that worked yesterday may be blocked today. Call `curl -H "Authorization: Bearer $KEY" https://openrouter.ai/api/v1/models | python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data'] if 'claude' in m['id'] or 'gemini' in m['id']]"` to discover available alternatives.
- **❗Temperature matters** — 0.7 is the sweet spot for creative divergence while maintaining coherence. Lower = more similar outputs, higher = risk of incoherence.
- **❗Check response size** — some models return <200 chars which likely means an error response, not actual content.
- **❗Region blocks** on OpenRouter are per-model, not per-provider. A model blocked in your region can sometimes be reached via a different provider. For HK-based servers, Claude Sonnet 4, GPT-4o, and Gemini models are often blocked — fall through to DeepSeek V3/V3.2/R1 and Qwen3 235B series.
- **❗Always list models first before writing the call script** — don't hardcode model IDs from last session. OpenRouter changes availability frequently. Always run the models endpoint query at the start of the task to discover what's actually available.
- **❗Negative prompt framing can trigger safety filters** — writing "不要安全废话" or similar demands in the shared prompt can cause the model to refuse or hedge. Phrase positively: "用中文回答，约800-1000字，要有锐度" without mentioning what you don't want.
- **❗100% consensus across diverse models IS the finding** — when all models from different families agree on a controversial topic, the consensus itself is more significant than any individual argument. Highlight it as a meta-observation before presenting individual quotes.
- **❗`write_file` tool corrupts `${}` patterns in Python API scripts** — when writing API-call Python scripts that contain `${OPENROUTER_API_KEY}` or similar shell-style expansions, the `write_file` tool evaluates them as shell variables and corrupts the string. Fix: use `terminal()` to write the file via heredoc, or construct the API key string using Python-only patterns (`.split()` on a file read, not env-var expansion in the source string). Symptom: script passes lint but at runtime the key evaluates to empty or garbage.
- **❗Cost management** — calling 5+ models can consume significant API quota. Consider limiting to 3 models for routine use and 5 for deep analysis.
- **❗Synthesis time** — reading and synthesizing 5 model outputs of ~1000+ chars each is cognitively expensive. Use session_search to persist partial findings if you need to continue across turns.
- **❗API key in execute_code sandbox** — the sandbox doesn't inherit `~/.hermes/.env`. Use `from dotenv import load_dotenv; load_dotenv(os.path.expanduser("~/.hermes/.env"))` or read the key from env var with a fallback to file.

## When NOT to use this skill

- Questions with factual answers ("what is the capital of France")
- Code generation or debugging
- Simple preference questions ("which color is better")
- When the user explicitly wants a single model's opinion

## Related Skills

- `subagent-driven-development` — for delegating coding tasks to subagents (different: those subagents run the same model, not different models)
- `architecture-diagram` — for creating visual diagrams of technical systems (the infographic pipeline here is adapted from its approach)
