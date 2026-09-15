# Hermes Configuration Files Explained

## config.yaml
The main configuration file for Hermes Agent located at `~/.hermes/config.yaml`. This file contains:

- **Model settings**: Default model, provider, API keys (referenced from .env)
- **Agent configuration**: Max turns, timeouts, tool usage enforcement
- **Terminal settings**: Backend type, working directory, timeouts
- **Compression settings**: Context compression thresholds and ratios
- **Display preferences**: Personality, skin, streaming options
- **Platform configurations**: Settings for Telegram, Discord, WhatsApp, etc.
- **Security settings**: Secret redaction, PII handling, approval modes
- **Tool configurations**: Individual settings for various auxiliary tools

The config.yaml is safe to share publicly as it doesn't contain actual API keys (those are in .env).

## .env file
The environment file located at `~/.hermes/.env` contains sensitive credentials:

- **LLM Provider API Keys**: OpenRouter, Google Gemini, DeepSeek, etc.
- **Tool API Keys**: Exa, Parallel, Firecrawl, FAL.ai, etc.
- **Platform Credentials**: Telegram bot token, Slack tokens, etc.
- **Service Accounts**: Home Assistant URL, etc.
- **Other Secrets**: Sudo password, Honcho API key, etc.

This file should NEVER be shared or committed to version control. It contains actual secrets that provide access to paid services and personal accounts.

## Security Considerations
When backing up these files:
1. Treat the backup as sensitive as the original files
2. Store backups in secure locations (encrypted drives, password managers)
3. Consider encrypting the zip file for additional protection
4. Delete temporary copies after backup creation
5. Verify backup integrity before relying on it for recovery

The .env file follows the format:
```
KEY_NAME=value
KEY_NAME_2=value_2
```

Lines starting with # are comments and are ignored.