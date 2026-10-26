# Gemini CLI

**Status:** Skills path conflicts between sources; `GEMINI.md` context file and extensions are adapters.

## Where skills go (verify first)

Reported: `.gemini/skills/` and `~/.gemini/skills/`; one source reports a shared `.agents/skills/`.

## Adapter

Fallback: reference the skill path from `GEMINI.md`. Packaging as a Gemini CLI extension is possible but not done in this repository.

## Verify it worked

Start a new session and ask the agent which skills it can see; then run a small task (for example "use secrets-detection on this folder") on a throwaway project and check the agent cites the skill's workflow and does not run commands without your approval.

## Vendor documentation to check

Gemini CLI documentation at https://geminicli.com (skills, GEMINI.md, extensions).
