# Offline MLX LLM Commands

## Environment Setup
```bash
python3 -m venv ~/env/mlx-llm
source ~/env/mlx-llm/bin/activate
pip install --upgrade mlx-lm
```

## Model Conversion
```bash
MODEL_HF="~/models/Qwen3.6-35B-A3B-4bit"
MODEL_MLX="~/models/Qwen3.6-35B-A3B-4bit-mlx"
rm -rf "$MODEL_MLX"
python -m mlx_lm convert \
    --hf-path "$MODEL_HF" \
    --mlx-path "$MODEL_MLX" \
    --q-bits 4 \
    --q-group-size 64 \
    --q-mode affine
```

## Start Server (Offline)
```bash
source ~/env/mlx-llm/bin/activate
HF_HUB_OFFLINE=1 python -m mlx_lm server \
    --model "$MODEL_MLX" \
    --host 127.0.0.1 \
    --port 9000 \
    --max-tokens 4096 \
    --log-level INFO
```

## Hermes Config (Custom Provider)
```yaml
# ~/.hermes/config.yaml
model:
  default: custom/local
  provider:
    custom/local:
      base_url: "http://127.0.0.1:9000/v1"
      api_key: ""
  provider: custom/local
```

## Test Query
```bash
hermes chat -q "Hello, who are you?"
```