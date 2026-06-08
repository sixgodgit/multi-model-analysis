# Multi-Model Analysis 架构设计

## 系统架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Model Analysis System               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Prompt 模板  │───>│ 多模型调用   │───>│ 合成引擎     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         v                    v                    v          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ 统一格式     │    │ OpenRouter   │    │ 共性/差异    │  │
│  │ 多维分析     │    │ API 调用     │    │ 缺席分析     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                            │                                │
│                            v                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   模型路由引擎                        │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐             │   │
│  │  │ MiMo    │  │DeepSeek │  │OpenRouter│             │   │
│  │  │ V2.5    │  │ V4      │  │ 341+    │             │   │
│  │  └─────────┘  └─────────┘  └─────────┘             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. Prompt 模板引擎

#### 模板结构
```python
class PromptTemplate:
    def __init__(self):
        self.structure = {
            "topic": "主题名称",
            "background": "背景说明（3-5句）",
            "perspectives": [
                "认知层面分析",
                "社会层面分析",
                "权力层面分析"
            ],
            "format": "输出格式要求"
        }
    
    def generate(self, topic, context):
        """生成统一 prompt"""
        prompt = f"""
## {topic}

## 背景
{context}

## 请从以下维度分析
### 1. 认知层面
{self.structure['perspectives'][0]}

### 2. 社会层面
{self.structure['perspectives'][1]}

### 3. 权力层面
{self.structure['perspectives'][2]}

## 格式要求
- 使用中文
- 约800-1000字
- 结构清晰，论点明确
"""
        return prompt
```

### 2. 多模型调用引擎

#### 调用流程
```python
class MultiModelCaller:
    def __init__(self, models, api_key):
        self.models = models
        self.api_key = api_key
    
    def call_all(self, prompt):
        """并行调用所有模型"""
        responses = []
        for model in self.models:
            try:
                response = self.call_model(model, prompt)
                responses.append({
                    "model": model,
                    "response": response,
                    "status": "success"
                })
            except Exception as e:
                responses.append({
                    "model": model,
                    "error": str(e),
                    "status": "failed"
                })
            time.sleep(0.5)  # 避免限流
        return responses
    
    def call_model(self, model, prompt):
        """调用单个模型"""
        # OpenRouter API 调用逻辑
        pass
```

### 3. 合成引擎

#### 合成方法
```python
class SynthesisEngine:
    def synthesize(self, responses):
        """合成多个模型的响应"""
        # 1. 找共性
        commonalities = self.find_commonalities(responses)
        
        # 2. 找差异
        differences = self.find_differences(responses)
        
        # 3. 找缺席
        absences = self.find_absences(responses)
        
        # 4. 生成合成报告
        report = self.generate_report(commonalities, differences, absences)
        
        return report
    
    def find_commonalities(self, responses):
        """找跨模型共识"""
        # 分析多个模型的共同观点
        pass
    
    def find_differences(self, responses):
        """找独特视角"""
        # 分析模型之间的差异
        pass
    
    def find_absences(self, responses):
        """找缺席视角"""
        # 分析哪些视角被忽略了
        pass
```

### 4. 模型路由引擎

#### 路由策略
```python
class ModelRouter:
    def __init__(self):
        self.routes = {
            "image": "mimo-v2-omni",
            "long_text": "mimo-v2.5",
            "complex_reasoning": "mimo-v2.5-pro",
            "daily_chat": "deepseek-chat",
            "simple_task": "deepseek-chat"
        }
    
    def route(self, task_type):
        """根据任务类型选择模型"""
        return self.routes.get(task_type, "mimo-v2.5")
```

## 数据流

### 分析流程
```
1. 接收问题
   ↓
2. 评估问题性质
   ├─ 事实查询 → 单模型
   └─ 多维分析 → 多模型
   ↓
3. 生成统一 Prompt
   ↓
4. 调用多个模型
   ├─ MiMo V2.5
   ├─ DeepSeek V3
   ├─ Qwen3-235B
   └─ ...
   ↓
5. 收集响应
   ↓
6. 合成分析
   ├─ 找共性
   ├─ 找差异
   └─ 找缺席
   ↓
7. 生成报告
   ↓
8. 输出结果
```

## 配置参数

### 模型配置
```yaml
models:
  primary:
    - deepseek/deepseek-chat
    - deepseek/deepseek-v3.2
    - deepseek/deepseek-r1
    - qwen/qwen3-235b-a22b
    - qwen/qwen3-235b-a22b-thinking-2507
  
  backup:
    - anthropic/claude-sonnet-4
    - google/gemini-2.5-pro
    - openai/gpt-4o
  
  minimum_viable: 3  # 最少模型数
```

### 调用配置
```yaml
api:
  provider: openrouter
  timeout: 30
  retry: 3
  delay: 0.5  # 模型间延迟（秒）
```

### 合成配置
```yaml
synthesis:
  method: "weighted"  # weighted | consensus | hybrid
  weights:
    deepseek-chat: 0.3
    qwen3-235b: 0.25
    deepseek-r1: 0.25
    # ...
  
  output:
    language: "chinese"
    length: 800  # 字数
```

## 扩展点

### 1. 添加新模型
```python
# 只需在配置中添加
models.primary.append("new-provider/new-model")
```

### 2. 自定义合成策略
```python
class CustomSynthesis(SynthesisEngine):
    def synthesize(self, responses):
        # 自定义合成逻辑
        pass
```

### 3. 信息图管道
```python
class InfographicPipeline:
    def generate(self, analysis_result):
        # 生成信息图
        pass
```

## 监控指标

### 性能指标
- **调用成功率** - >95%
- **平均响应时间** - <30秒
- **合成质量** - 用户评分 >4.0

### 成本指标
- **单次分析成本** - <¥0.05
- **月度总成本** - <¥15
- **成本效率** - 每元产出分析质量

## 参考资料

- `src/skill-v1.md` - v1.0 技能文档
- `src/skill-v2.md` - v2.0 技能文档
- `docs/feasibility-report.md` - 可行性报告
- `docs/evolution.md` - 演进历史
