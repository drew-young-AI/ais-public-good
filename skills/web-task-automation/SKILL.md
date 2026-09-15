---
name: web-task-automation
type: skill
description: Automate web interactions and report via Telegram.
version: 1.0
---

# Web Task Automation

This skill outlines how to automate interactions with web-based platforms (like chat interfaces) and report results via Telegram.

## When to Use

Use this skill when you need to:
    - Navigate to a specific web page
    - Perform an action (e.g., click a button, send a message)
    - Capture evidence (e.g., screenshot)
    - Report the outcome via Telegram

## Prerequisites

- Ensure the required browser engine is available (Camoufox preferred, fallback to Chrome).
- Ensure API keys for vision tools (if needed) are valid.
- Ensure the Telegram bot token for the target bot is configured.

## Steps

1. **Check Browser Engine**
      - Verify if Camoufox is installed and available.
      - If not, fall back to Chrome (or other configured browser).
      - Log the engine being used.

  2. **Navigate to Target URL**
      - Use the browser tool to navigate to the URL.
      - Wait for the page to load (consider using a snapshot to check readiness).

  3. **Handle Authentication (if applicable)**
      - If the page requires login and you have credentials, attempt to log in.
      - If login is required and no credentials are available, note the failure and skip interaction steps.
      - If the page is accessible without login, proceed.

  4. **Perform Desired Action**
      - Use browser_snapshot to identify interactive elements.
      - Use browser_click to perform actions (e.g., click a send button).
      - If the action fails, log the error and consider alternative selectors.

  5. **Capture Evidence**
      - If a screenshot is required, use browser_vision (with a specific question) or browser_get_images.
      - Before using vision, verify that the vision API key is valid (check environment or config).
      - If vision fails, fall back to browser_snapshot for text-based evidence.

  6. **Report via Telegram**
      - Verify the Telegram bot token for the target bot is available in the environment.
      - Use the Telegram tool to send a message or photo.
      - If sending a photo, ensure the image was captured successfully.
      - If the Telegram bot token is missing, log an error and consider alternative notification methods.

  7. **Cleanup**
      - Close browser sessions if necessary.
      - Remove any temporary files created.

## Pitfalls

- **Login Walls**: Automated tasks may fail if the target page requires authentication and no credentials are provided.
- **API Key Validity**: Vision and Telegram tools will fail if the required API keys are missing or invalid.
- **Element Selectors**: Web pages change; selectors obtained from snapshots may become outdated.
- **Bot Token Specificity**: Ensure you are using the correct bot token for the intended Telegram bot.

## References

- See `references/session-2026-06-25-claude-chat-attempt.md` for a detailed transcript of a session attempting to automate a Claude chat interaction.

## Example

Not provided, as each web task is unique.