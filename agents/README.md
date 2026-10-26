# Agent Integration

Skills follow the Agent Skills specification: a folder containing `SKILL.md` with `name` and `description` frontmatter.

## What is confirmed and what is not

| Claim | Status |
| --- | --- |
| `SKILL.md` frontmatter rules (name, description, optional fields), directory layout, progressive disclosure | **Confirmed** against https://agentskills.io/specification (read 2026-10-26 via search result excerpts; the validator encodes these rules) |
| Project and global skills directories per agent (table below) | **Unverified against vendor documentation.** Taken from third-party community repositories that disagree in places (for example Codex `.agents/skills/` vs `.codex/skills/`; Windsurf `.windsurf/skills/` vs `.devin/skills/`). Check the vendor docs linked in each agent file before relying on a path. |
| Rule-file adapters (Cursor rules, Copilot instructions, Windsurf rules, `GEMINI.md`, `AGENTS.md`) | **Adapter guidance from general knowledge, not tested in this repository.** |

No claim of "native compatibility" is made for any agent in this repository.

## Paths reported by community sources

| Agent | Project path | Global path | Note |
| --- | --- | --- | --- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | see `claude-code.md` |
| OpenAI Codex | `.agents/skills/` (some sources: `.codex/skills/`) | `~/.agents/skills/` | see `codex.md` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` | see `cursor.md` |
| GitHub Copilot | `.github/skills/` | `~/.copilot/skills/` | see `copilot.md` |
| Gemini CLI | `.gemini/skills/` (some sources: `.agents/skills/`) | `~/.gemini/skills/` | see `gemini-cli.md` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` | see `windsurf.md` |

## Generic procedure

1. Pick only the skills you need (start with `security-audit`).
2. Copy the skill **folder** into the agent's skills directory: `cp -r skills/security/security-audit <target>/`.
3. Run `python scripts/validate_skills.py` in this repository first.
4. Start a new session; ask the agent to list available skills, to confirm it loaded them.
5. Test on a throwaway project before using on real code. Keep agent permissions minimal and approvals on.

Repository paths mentioned in skills (such as `scripts/scan_project.py`) exist only in this repository. If you copy skills elsewhere, either copy those scripts too or have the agent use the project's own tools.
