---
name: line-webhook-watchdog
type: skill
description: "Check, diagnose, and safely recover a LINE Messaging API webhook without assuming a specific bot framework, tunnel provider, scheduler, or secret location."
version: 1.0.0
platforms: [macos]
metadata:
  tags: [LINE, Messaging-API, webhook, health-check, recovery]
---

# LINE Webhook Watchdog

Use this skill when a LINE Bot must be checked or repaired across a public webhook boundary. It is for webhook availability and acceptance gates, not for changing a bot adapter's business logic.

## Ownership boundary

AIS owns the reusable implementation and operating contract:

- Script: `${AIS_ROOT}/capabilities/scripts/line-webhook-watchdog`
- Skill: `${AIS_ROOT}/capabilities/skills/devops/line-webhook-watchdog/SKILL.md`
- Registry: `${AIS_ROOT}/capabilities/registry.yaml`

The consumer owns its secrets, service process, scheduler, and persistent state directory. Do not assume Hermes, a tunnel provider, a port, an environment-file path, or a launchd label. Supply each consumer value explicitly.

## First run

Run the offline deterministic self-test before using credentials or a public endpoint:

```bash
${AIS_ROOT}/capabilities/scripts/line-webhook-watchdog --self-test
```

The self-test creates only a temporary localhost server and temporary files. It proves the watchdog's HTTP gate, state/event persistence, bounded recovery invocation, URL validation, and LINE-test response parsing. It does not prove a particular bot can reply.

## Bounded acceptance check

Use a consumer-owned state directory. `state.json` is the current condition; `events.jsonl` is an append-only record for the next human or AI. No token is written to either file.

```bash
GUARD=${AIS_ROOT}/capabilities/scripts/line-webhook-watchdog

"$GUARD" --check \
  --health-url https://bot.example.com/health \
  --webhook-url https://bot.example.com/line/webhook \
  --state-dir /absolute/consumer/state/line-webhook
```

This only proves the public health endpoint returns HTTP 200. It is not a LINE acceptance result.

For LINE configuration and the official test webhook, the caller must load its own token into an environment variable and pass only that variable name:

```bash
"$GUARD" --check \
  --health-url https://bot.example.com/health \
  --webhook-url https://bot.example.com/line/webhook \
  --state-dir /absolute/consumer/state/line-webhook \
  --line-token-env LINE_CHANNEL_ACCESS_TOKEN \
  --line-check \
  --line-webhook-test
```

`--line-check` requires LINE to report the expected endpoint with `active=true`. `--line-webhook-test` sends one official empty-event POST and requires `success=true` with HTTP 200. It is intentionally unavailable in continuous `--watch` mode because LINE limits that test endpoint.

## Explicit endpoint repair

Changing a LINE endpoint is an external mutation. The script refuses it unless the command includes the exact confirmation string and the official post-change test. Preview first:

```bash
"$GUARD" --check \
  --health-url https://bot.example.com/health \
  --webhook-url https://bot.example.com/line/webhook \
  --state-dir /absolute/consumer/state/line-webhook \
  --set-line-endpoint --line-webhook-test --dry-run
```

Apply only after reviewing the preview:

```bash
"$GUARD" --check \
  --health-url https://bot.example.com/health \
  --webhook-url https://bot.example.com/line/webhook \
  --state-dir /absolute/consumer/state/line-webhook \
  --line-token-env LINE_CHANNEL_ACCESS_TOKEN \
  --set-line-endpoint --line-webhook-test \
  --confirm-set-line-endpoint SET_LINE_ENDPOINT
```

The tool waits up to 60 seconds after the update, then requires endpoint configuration and LINE's official test to pass. It never retries an endpoint mutation in a loop.

## Automatic service recovery

Use `--watch` only for HTTP health and an explicit consumer restart action. The restart executable must be an absolute path, runs only after consecutive failures, is rate-limited by a cooldown, receives literal arguments without a shell, and is rechecked afterwards.

```bash
"$GUARD" --watch \
  --health-url https://bot.example.com/health \
  --state-dir /absolute/consumer/state/line-webhook \
  --interval-seconds 60 \
  --repair-on-failure \
  --repair-exec /absolute/path/to/consumer-restart \
  --repair-after 2 \
  --repair-cooldown-seconds 900
```

The consumer decides how this command is scheduled. Keep that scheduler and its service-specific logs outside AIS. A separate bounded `--check --line-check --line-webhook-test` is appropriate after a recovery or as a low-frequency audit.

## Acceptance boundary

Interpret results in order:

1. Public health HTTP 200 proves that endpoint is reachable.
2. LINE endpoint information proves the configured URL and webhook enablement match.
3. LINE's official test proves LINE can deliver an empty-event POST to that URL.
4. A real user message receiving an outbound reply proves bot logic, signature verification, authorization, and reply delivery.

Do not claim a conversation works until step 4 is observed. The watchdog records steps 1–3 only.

Quick Tunnel URLs are temporary testing endpoints. Their changing hostname means automatic endpoint updates must be an explicit consumer decision; this skill does not start a tunnel or assume one is present.
