---
name: mlx-server-kv-cache-quantization
type: skill
category: mlops
description: "Optimize MLX-LLM server memory via KV-cache quantization."
version: 1.0.0
author: Hermes Agent
platforms: [macos, linux]
tags: [mlx, llm, server, kv-cache, quantization, memory-optimization]
---
# MLX-LLM Server KV Cache Quantization

This skill describes how to reduce the memory footprint of the `mlx_lm server` by enabling KV-cache quantization, which is especially beneficial for large models (e.g., 72B) during long conversations or coding-agent workloads.

## When to Use

- You are running a large MLX model (e.g., 7B+) and notice high memory usage during extended interactions.
- You want to keep the model offline and accessible via an OpenAI‑compatible API.
- You are using the server for a single user or low‑concurrency scenario (batching is disabled when KV‑cache quantization is active).

## Prerequisites

- A locally available MLX model directory (converted via `mlx_lm convert`).
- Python virtual environment with `mlx-lm` (≥0.31), `mlx`, and `mlx-metal` installed.
- Port 9000 (or your chosen port) free.
- Optional: `jq` for pretty‑printing JSON responses.

## Procedure

### 1. Prepare the Environment

```bash
# Create a dedicated venv if desired
python3 -m venv ~/env/mlx-server
source ~/env/mlx-server/bin/activate
pip install --upgrade pip
pip install --break-system-packages mlx mlx-metal mlx-lm
# Verify installation
python -c "import mlx, mlx_lm; print('mlx:', mlx.__version__, 'mlx_lm:', mlx_lm.__version__)"
```

### 2. Start the Server with KV‑Cache Quantization

Use the following flags to enable quantization:

- `--kv-bits 4` – Quantize KV cache to 4 bits per element (default: 16‑bit fp16).
- `--kv-group-size 64` – Group size for quantization (keep at 64 unless experimenting).
- `--quantized-kv-start 2048` – Keep the first N tokens in full precision (useful for preserving system prompt quality).

```bash
export HF_HUB_OFFLINE=1   # Prevent any outbound Hugging Face calls
python -m mlx_lm server \\
    --model /path/to/your/mlx-model \\
    --host 127.0.0.1 \\
    --port 9000 \\
    --max-tokens 4096 \\
    --kv-bits 4 \\
    --kv-group-size 64 \\
    --quantized-kv-start 2048 \\
    --log-level INFO
```

**Note**: When `--kv-bits` is set, the server disables batching because the batched quantized KV cache implementation is not yet available. For low‑concurrency use (e.g., a single developer or coding assistant) this is acceptable.

### 3. Verify the Endpoint

```bash
# List models
curl -s http://127.0.0.1:9000/v1/models | jq .

# Test completion
curl -s -X POST http://127.0.0.1:9000/v1/completions \\
  -H "Content-Type: application/json" \\
  -d '{"model":"/path/to/your/mlx-model","prompt":"Hello, how are you?","max_tokens":10,"temperature":0.0}' | jq .
```

A successful response includes a `choices` array with generated text.

## Memory Impact

Enabling KV‑cache quantization reduces the per‑token KV cache size from 16 bits to 4 bits, cutting the KV cache memory by ~75%. For a model like Qwen‑3.6‑35B‑A3B‑4bit, the base model weight memory stays ~3.4 GB, but the KV cache for a 16 K‑token context drops from ~25 GB (fp16) to ~6 GB (4‑bit), making long conversations feasible on machines with 32‑48 GB unified memory.

See `references/kv_cache_quantization.md` for detailed measurements from a real‑world session.

## Pitfalls & Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: No module named 'mlx_lm'` | `mlx-lm` not installed in the active Python environment. | Ensure you have activated the venv and run `pip install mlx-lm`. |
| `Address already in use` | Another process bound to the chosen port. | Kill the existing process (`lsof -ti:9000 \\| xargs kill -9`) or change `--port`. |
| Server starts but returns 404/401 on `/v1/completions` | Wrong `base_url` or model name mismatch in client configuration. | Verify the `model` argument to the server matches what the client expects (often the directory name). |
| `ValueError: Cannot save to the path ... as it already exists` | Output directory exists during model conversion. | Remove the directory or pick a new `--mlx-path`. |
| Slow first token generation | Model not fully loaded into RAM; first call includes compilation. | Warm‑up with a dummy prompt; subsequent calls are faster. |

## Reference Commands

Exact commands used in the session that discovered this optimization are stored in `references/commands.txt`.

## Related Skills

- `local-mlx-llm-server` – Base skill for setting up and running a local MLX‑LLM server.
- `offline-mlx-llm` – Running quantized MLX models offline for Hermes.
- `huggingface-hub` – Managing model downloads from the Hub.

> **Tip**: Treat the MLX model directory as immutable once created; moving or renaming it requires updating the `--model` path and any Hermes provider config.

## References

See `references/kv_cache_quantization.md` for a concise write‑up of the KV‑cache quantization technique, including performance numbers from the user's sysdiagnose analysis and a step‑by‑step reproduction recipe.