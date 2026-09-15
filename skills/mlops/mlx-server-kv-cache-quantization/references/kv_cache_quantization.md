# KV Cache Quantization for MLX-LLM Server

## Why It Matters
In long conversations or coding-agent workflows, the KV cache (key-value cache) grows linearly with the number of tokens processed. By default, `mlx_lm server` stores the KV cache in 16-bit floating point (fp16), which can consume tens of gigabytes for models like Qwen-3.6-35B-A3B-4bit when the context reaches tens of thousands of tokens.

Enabling KV-cache quantization reduces the precision of the cached keys and values from 16 bits to a lower bit-width (e.g., 4 bits), dramatically cutting memory usage with minimal impact on generation quality.

## How It Works
The `mlx_lm` library (since v0.22) supports KV-cache quantization via the `generate` CLI (`--kv-bits`, `--kv-group-size`, `--quantized-kv-start`). The server now exposes the same flags (as of mlx-lm >=0.31) to apply quantization to the server's KV cache.

When `--kv-bits N` is set:
- Each element in the KV cache is stored using N bits instead of 16.
- The `--kv-group-size` parameter controls how many elements are grouped together for quantization (default 64 works well).
- `--quantized-kv-start M` allows keeping the first M tokens (e.g., system prompt, instructions) in full precision to preserve quality for the initial part of the conversation, while quantizing the rest.

## Memory Savings Example
For a model like Qwen-3.6-35B-A3B-4bit:
- Base model weight memory (4-bit quantized): ~3.4 GB
- KV cache for a 16 K-token context:
  - fp16 (16-bit): ~25 GB
  - 4-bit quantized: ~6.2 GB
  - Savings: ~19 GB (~75% reduction)

This makes it feasible to run long-context sessions on machines with 32‑48 GB unified memory.

## Performance Impact
- Generation speed: Little to no impact; the quantization/dequantization overhead is minimal on Apple Silicon.
- Quality: With `--quantized-kv-start` set to a reasonable value (e.g., 2048), the impact on output quality is negligible for most tasks. Fully quantizing the entire cache (setting `--quantized-kv-start 0`) may cause slight degradation in very long or precise reasoning tasks, but is often acceptable for coding agents.

## Usage in Server
Add the following flags to your `mlx_lm server` command:

```bash
export HF_HUB_OFFLINE=1
python -m mlx_lm server \
  --model /path/to/your/mlx-model \
  --host 127.0.0.1 \
  --port 9000 \
  --max-tokens 4096 \
  --kv-bits 4 \
  --kv-group-size 64 \
  --quantized-kv-start 2048 \
  --log-level INFO
```

**Note**: When `--kv-bits` is set, batching is disabled in the current server implementation. For low‑concurrency use (single user or coding assistant) this is acceptable.

## Verification
After starting the server with these flags, you can verify memory usage via:
- `ps aux | grep mlx_lm` and look at the RSS column.
- Activity Monitor → Memory tab for the Python process.

You should observe a significantly lower RSS compared to running the same model without KV-cache quantization.

## References
- mlx-lm PR adding KV-cache quantization to server: https://github.com/ml-explore/mlx-lm/pull/1353
- Discussion on KV-cache quantization benefits: https://github.com/ml-explore/mlx-lm/issues/1043