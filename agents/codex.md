# OpenAI Codex

**Status:** Path conflicting between community sources; verify before use. `AGENTS.md` guidance is an adapter.

## Where skills go (verify first)

Reported: `.agents/skills/` (project) and `~/.agents/skills/`; some sources report `.codex/skills/`.

## Adapter

If skills are not discovered, add an `AGENTS.md` line such as: "For security reviews follow skills/security/security-audit/SKILL.md".

## Verify it worked

Start a new session and ask the agent which skills it can see; then run a small task (for example "use secrets-detection on this folder") on a throwaway project and check the agent cites the skill's workflow and does not run commands without your approval.

## Vendor documentation to check

OpenAI Codex documentation at https://developers.openai.com (locate the skills page).
