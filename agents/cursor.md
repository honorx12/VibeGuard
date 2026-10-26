# Cursor

**Status:** Skills path reported by community sources; Cursor rules are the documented-in-practice alternative; neither tested here.

## Where skills go (verify first)

Reported: `.cursor/skills/` and `~/.cursor/skills/`.

## Adapter

Fallback: create `.cursor/rules/security-audit.mdc` containing a short description (frontmatter `description`, `alwaysApply: false`) and a pointer to the copied SKILL.md path. Do not paste untrusted content into rules.

## Verify it worked

Start a new session and ask the agent which skills it can see; then run a small task (for example "use secrets-detection on this folder") on a throwaway project and check the agent cites the skill's workflow and does not run commands without your approval.

## Vendor documentation to check

Cursor documentation at https://docs.cursor.com (rules and skills pages).
