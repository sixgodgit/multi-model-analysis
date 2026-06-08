#!/usr/bin/env python3
"""Multi-model collaborator: call N models via OpenRouter with the same prompt."""
import json, urllib.request, os, sys, time

# API key resolution
api_key = os.environ.get('OPENROUTER_API_KEY', '').strip()
if not api_key:
    env_path = os.path.expanduser('~/.hermes/.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith('OPENROUTER_API_KEY='):
                    api_key = line.split('=', 1)[1].strip().strip('"\'')
                    break

if not api_key:
    print("ERROR: No OPENROUTER_API_KEY found")
    sys.exit(1)

# Diverse model lineup
MODELS = {
    'deepseek_r1': 'deepseek/deepseek-r1',
    'deepseek_v3': 'deepseek/deepseek-chat',
    'deepseek_v32': 'deepseek/deepseek-v3.2',
    'qwen235b': 'qwen/qwen3-235b-a22b',
    'qwen_thinking': 'qwen/qwen3-235b-a22b-thinking-2507',
}

OUT_DIR = '/tmp/multi_model_responses'
os.makedirs(OUT_DIR, exist_ok=True)

if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        PROMPT = f.read()
else:
    PROMPT = sys.stdin.read()

if not PROMPT.strip():
    print("ERROR: No prompt provided")
    sys.exit(1)

results = {}
for name, model in MODELS.items():
    print("-- Calling " + model + " (" + name + ") --", flush=True)
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": 2000,
        "temperature": 0.7
    }).encode('utf-8')

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        if 'choices' in data and data['choices']:
            content = data['choices'][0]['message']['content']
        else:
            content = json.dumps(data, ensure_ascii=False)
        outpath = os.path.join(OUT_DIR, name + '_response.txt')
        with open(outpath, 'w') as f:
            f.write(content)
        results[name] = {'status': 'ok', 'chars': len(content), 'model': model}
        print("  OK: " + str(len(content)) + " chars", flush=True)
    except Exception as e:
        body = str(getattr(e, 'read', lambda: str(e))()) if hasattr(e, 'read') else str(e)
        results[name] = {'status': 'error', 'detail': body[:200], 'model': model}
        print("  ERROR: " + body[:200], flush=True)
    time.sleep(0.5)

# Summary
summary = {
    'models_called': len(MODELS),
    'succeeded': sum(1 for r in results.values() if r['status'] == 'ok'),
    'results': results
}
with open(os.path.join(OUT_DIR, '_summary.json'), 'w') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

oks = [n for n, r in results.items() if r['status'] == 'ok']
if oks:
    print("\n" + str(len(oks)) + "/" + str(len(MODELS)) + " succeeded. Outputs:")
    for n in oks:
        print("  /tmp/multi_model_responses/" + n + "_response.txt (" + str(results[n]['chars']) + " chars)")
    print("\nRead each file with read_file, then synthesize.")
else:
    print("\nAll " + str(len(MODELS)) + " models failed. Try different model IDs.")