# Windsurf

**Status:** Path conflicts between community sources (`.windsurf/skills/` vs `.devin/skills/`); rules adapter from general knowledge.

## Where skills go (verify first)

Reported: `.windsurf/skills/` and `~/.codeium/windsurf/skills/`.

## Adapter

Fallback: a workspace rule in `.windsurf/rules/` that points to the skill file.

## Verify it worked

Start a new session and ask the agent which skills it can see; then run a small task (for example "use secrets-detection on this folder") on a throwaway project and check the agent cites the skill's workflow and does not run commands without your approval.

## Vendor documentation to check

Windsurf documentation at https://docs.windsurf.com (Cascade skills and rules).
