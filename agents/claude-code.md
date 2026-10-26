# Claude Code

**Status:** Skills directory reported by community sources; not verified against vendor docs in this release.

## Where skills go (verify first)

Project: `.claude/skills/<name>/SKILL.md`. Global: `~/.claude/skills/`.

## Adapter

None needed if skills load from that path. Optional: reference `security-audit` from `CLAUDE.md` to encourage use.

## Verify it worked

Start a new session and ask the agent which skills it can see; then run a small task (for example "use secrets-detection on this folder") on a throwaway project and check the agent cites the skill's workflow and does not run commands without your approval.

## Vendor documentation to check

https://code.claude.com/docs/en/skills (listed by community sources; confirm the URL).
