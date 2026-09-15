---
name: offline-mlx-llm
type: skill
description: "Run local MLX quantized models offline for Hermes Agent."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [local-llm, mlx, offline, setup, model]
---

# Offline MLX LLM Setup for Hermes

This skill describes how to run a quantized MLX model (e.g., Qwen 3.6) entirely offline, without requiring internet access after initial model download, and integrate it with Hermes Agent via a local OpenAI-compatible API server.

## Prerequisites

- Apple Silicon Mac (MLX requires Metal)
- Hermes Agent installed
- Model files in Hugging Face format (e.g., `~/models/Qwen3.6-35B-A3B-4bit`)
- Python environment with `mlx-lm` (≥0.31 recommended)

## Steps

### 1. Prepare Python Environment

Create or activate a virtual environment with `mlx-lm` installed:

```bash
# Example using a dedicated env
python3 -m venv ~/env/mlx-llm
source ~/env/mlx-llm/bin/activate
pip install --upgrade mlx-lm  # ensures ≥0.31 for Qwen3_5Moe support
```

### 2. Convert Model to MLX Format (One‑time)

Convert the Hugging Face model to MLX format with 4‑bit quantization:

```bash
# Adjust paths as needed
MODEL_HF="~/models/Qwen3.6-35B-A3B-4bit"
MODEL_MLX="~/models/Qwen3.6-35B-A3B-4bit-mlx"

# If output directory exists, remove it or choose a new path
rm -rf "$MODEL_MLX"
python -m mlx_lm convert \
    --hf-path "$MODEL_HF" \
    --mlx-path "$MODEL_MLX" \
    --q-bits 4 \
    --q-group-size 64 \
    --q-mode affine
```

**Pitfall:** If you see `ValueError: Cannot save to the path ... as it already exists`, delete the directory or specify a different `--mlx-path`.

### 3. Start the Local API Server

Run the MLX HTTP server locally. To avoid any outbound calls, set `HF_HUB_OFFLINE=1`.

```bash
source ~/env/mlx-llm/bin/activate
HF_HUB_OFFLINE=1 python -m mlx_lm server \
    --model "$MODEL_MLX" \
    --host 127.0.0.1 \
    --port 9000 \
    --max-tokens 4096 \
    --log-level INFO   # optional, use DEBUG for troubleshooting
```

The server will listen on `http://127.0.0.1:9000/v1` and provide an OpenAI‑compatible `/v1/completions` endpoint.

**Tip:** Run the server in a background Hermes terminal task with `notify_on_complete=true` so you are alerted if it exits unexpectedly.

### 4. Configure Hermes to Use the Local Endpoint

Add a custom provider in Hermes pointing to the local server.

#### Option A: Via `hermes model` (interactive)

```bash
hermes model
# Choose "Custom endpoint"
# Set:
#   Model: Qwen3.6-35B-A3B-4bit   (any string; the server ignores it)
#   Provider: custom
#   Base URL: http://127.0.0.1:9000/v1
#   API Key: none   (can be empty)
```

#### Option B: Direct config edit

```bash
hermes config edit
# Add or modify under `model`:
#   default: custom/local
#   provider:
#     custom/local:
#       base_url: "http://127.0.0.1:9000/v1"
#       api_key: ""   # optional
#   provider: custom/local
```

### 5. Test the Setup

In a Hermes chat session, send a simple query:

```
Hello, who are you?
```

You should receive a response generated entirely offline by the MLX model.

### 6. Persistence & Reuse

- The MLX model directory (`MODEL_MLX`) can be copied to other machines with the same architecture.
- Keep the virtual environment or export its requirements (`pip freeze > requirements.txt`) for easy reproduction.
- To upgrade `mlx-lm`, repeat step 1 and restart the server; the converted model remains valid.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ValueError: Model type qwen3_5_moe not supported` | mlx‑lm version too old (<0.31) | Upgrade: `pip install --upgrade mlx-lm` |
| Server logs show `Repository Not Found` or HF API calls | `HF_HUB_OFFLINE` not set or model missing tokenizer/config | Ensure `HF_HUB_OFFLINE=1` and that the MLX model directory contains `config.json`, `tokenizer.json`, etc. |
| `curl` returns 401 or empty response | Server not running or wrong port | Check `lsof -i :9000` or `ps aux | grep mlx_lm`; restart server if needed |
| Slow first token generation | Model not fully loaded into RAM; first call includes compilation | Warm‑up with a dummy prompt; subsequent calls are faster |

## Notes

- The MLX server does **not** support chat‑template application by default; it expects raw prompts. If you need chat formatting, prepend the prompt with the appropriate tokens manually or configure the server with `--chat-template` (see `mlx_lm server --help`).
- For best offline experience, download the model and tokenizer once while online, then convert and run with `HF_HUB_OFFLINE=1`.
- This skill assumes a single‑user local setup. For multi‑user or production, consider authentication and rate limiting at the reverse‑proxy level.

---

## References

- MLX‑LM GitHub: https://github.com/ml-explore/mlx-lm
- OpenAI‑compatible server documentation: https://github.com/ml-explore/mlx-lm#http-api

## Related Skills

- `hermes-agent` – for general Hermes configuration and tool usage
- `mlops/llamacpp` – alternative local inference via llama.cpp (if CPU‑only)
