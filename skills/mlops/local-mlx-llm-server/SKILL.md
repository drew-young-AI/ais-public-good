---
name: local-mlx-llm-server
type: skill
description: "Set up and run a local MLX-LLM server for offline use with Hermes Agent."
version: 1.0.0
author: Hermes Agent
platforms: [macos, linux]
tags: [mlx, llm, offline, local server, hermes config, mlx-lm]
---
# Local MLX-LLM Server for Hermes

This skill describes how to convert a Hugging Face model to MLX format, run a local inference server without internet access, and configure Hermes Agent to use it as a custom provider.

## When to Use

- You want to run a large language model entirely offline on Apple Silicon (or Linux with MLX support).
- You have the model weights locally (e.g., downloaded from Hugging Face while online).
- You wish to integrate the model with Hermes Agent via its custom provider mechanism.

## Prerequisites

- A local copy of the model directory (contains `config.json`, `model-*.safetensors`, `tokenizer.json`, etc.).
- A Python virtual environment with `mlx-lm` installed (version >= 0.31 recommended).
- Sufficient RAM and Apple GPU (or compatible hardware) for the model size.
- Port 9000 (or your chosen port) free on the host.

## Procedure

### 1. Activate the MLX environment

```bash
source ~/ENV/localLLM/bin/activate   # adjust path to your venv
# Verify mlx-lm version
python -c "import mlx_lm; print(mlx_lm.__version__)"
```

### 2. Convert the model to MLX format (offline)

Choose an output directory that does **not** already exist.

```bash
export HF_HUB_OFFLINE=1   # prevent accidental online look‑ups
python -m mlx_lm convert \
    --hf-path /path/to/your/model \
    --mlx-path /path/to/output/mlx-model \
    --q-bits 4 \
    --q-group-size 64 \
    --q-mode affine
```

- `--q-bits 4` gives 4‑bit quantization (good balance of size/speed).  
- For higher fidelity, omit `--q-bits`/`--q-group-size`/`--q-mode` to keep bfloat16 weights.  
- If the output directory exists, delete it first or choose a new path.

### 3. Start the local inference server

```bash
export HF_HUB_OFFLINE=1   # crucial: disables any outbound HF hub calls
python -m mlx_lm server \
    --model /path/to/output/mlx-model \
    --host 127.0.0.1 \
    --port 9000 \
    --max-tokens 4096 \
    --log-level INFO   # optional, adjust as needed
```

The server will start and listen for OpenAI‑compatible requests at `http://127.0.0.1:9000/v1`.

### 4. Configure Hermes Agent to use the custom provider

1. Open Hermes configuration:
   ```bash
   hermes config edit
   ```
2. Under the `model` section, add or edit a provider entry, e.g.:

   ```yaml
   model:
     default: local-qwen
     providers:
       local-qwen:
         type: custom
         base_url: http://127.0.0.1:9000/v1
         api_key: "not-needed"   # any non‑empty string
         model: Qwen3.6-35B-A3B-4bit   # must match the model name expected by the server
   ```

3. Save the file and restart your Hermes session (`/reset` in chat or exit and relaunch).

### 5. Verify the integration

From within Hermes, ask a simple question or use the `/usage` slash command to see token counts.  
You can also test directly with `curl`:

```bash
curl -s -X POST http://127.0.0.1:9000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen3.6-35B-A3B-4bit","prompt":"Hello","max_tokens":10}'
```

A successful response will contain a `choices` array with generated text.

## Pitfalls & Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ValueError: Model type qwen3_5_moe not supported.` | Using an outdated `mlx-lm` version that lacks support for the model architecture. | Upgrade `mlx-lm` (`pip install -U mlx-lm`) to >=0.31. |
| `OSError: [Errno 48] Address already in use` | Another process is bound to the chosen port. | Kill the existing process (`lsof -ti:9000 \| xargs kill -9`) or choose a different port. |
| `Cannot find an appropriate cached snapshot folder...` | Server attempted to reach Hugging Face Hub despite `HF_HUB_OFFLINE=1` not being set, or the model was not fully converted. | Ensure `HF_HUB_OFFLINE=1` is exported before starting the server; verify the MLX model directory contains the safetensor shards and index file. |
| Server starts but returns 401/404 on `/v1/completions` | Wrong `base_url` or model name mismatch in Hermes config. | Confirm the `base_url` matches the server’s host:port and that the `model` field in Hermes config equals the model identifier the server expects (usually the directory name or whatever you passed via `--model`). |
| Slow generation or high memory usage | Using unquantized (bfloat16) model on limited RAM. | Re‑convert with quantization (`--q-bits 4 --q-group-size 64`). |

## Reference Commands

Exact commands used in this session are stored in `references/commands.txt`.

> **Tip**: Treat the MLX model directory as immutable once created; moving or renaming it requires updating the `--model` path and the Hermes provider config.

See `references/commands.txt` for the exact command lines used in this session.