# GitHub Copilot

**Status:** Skills path reported by community sources; instruction-file adapter from general knowledge.

## Where skills go (verify first)

Reported: `.github/skills/` (project), `~/.copilot/skills/` (global); `.claude/skills/` also mentioned as legacy by one source.

## Adapter

Fallback: `.github/copilot-instructions.md` or `.github/instructions/*.instructions.md` with a pointer to the skill file; keep it short.

## Verify it worked

Start a new session and ask the agent which skills it can see; then run a small task (for example "use secrets-detection on this folder") on a throwaway project and check the agent cites the skill's workflow and does not run commands without your approval.

## Vendor documentation to check

GitHub Docs: https://docs.github.com (Copilot, agent skills and custom instructions pages).
