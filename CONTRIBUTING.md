# Contributing

This repository is a **generated export**. Files here are produced by
`release-prepare` in the upstream (private) AIS project, so a pull request that
edits `skills/` or `knowledge/` content will be overwritten by the next export.

## What is useful

- **Issues** — corrections, counter-evidence, or "this failed differently on my
  platform" reports. Each knowledge record is a claim about observed behaviour;
  evidence that a claim no longer holds is the most valuable thing you can send.
- **New knowledge records** — open an issue with the record in the frontmatter
  format below. Records are validated against
  `schema/knowledge-record.schema.json`.

## What happens to contributions

Incoming claims are not merged as prose. They are re-derived upstream into a
check that can fail (a guard, a test, or a control), and only the resulting
record is exported here. A claim nobody can re-run is a claim nobody can trust —
including ours.

## Record format

Every record is Markdown with YAML frontmatter:

```yaml
---
id: kebab-case-id            # must equal the filename stem
type: reference | explanation | policy | decision
title: one line
description: one line, used as the retrieval key
tags: [list, of, lowercase, tags]
status: stable | draft
shareable: true              # only `true` records are exported
reviewed_at: YYYY-MM-DD      # when a human last reviewed it for publication
timestamp: 'YYYY-MM-DDTHH:MM:SS+08:00'
---
```

`source:` entries that read `private-source` point at files on the original
machine (the private engine, or another private repo). The `digest` is over the
excerpted source content, not the path, so whoever holds the source can still
verify it; you cannot, and that is deliberate.

## Language

Most records are written in Traditional Chinese, because they were written for
the environment that produced them and translating them would put a second,
drifting copy of each claim in circulation. Titles and descriptions carry enough
for machine retrieval; open an issue if a specific record is worth translating.
