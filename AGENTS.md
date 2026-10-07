# AGENTS.md

<!-- bitpub:begin -->
## BitPub (`bitpub` CLI) — available in this project

This folder has been anchored as a BitPub project. The open-source `bitpub` CLI
(npm: `@bitpub/cli`, source: <https://github.com/bitpub/bitpub>) is installed on
this machine and gives you persistent, addressable memory across sessions. Reach
for it when you would otherwise write to `/tmp/` or a scratch buffer.

### Commands

- `bitpub list` — what's saved in this project, plus cache freshness
- `bitpub save <name> "..."` — write a slice (private + client-side-encrypted by default)
- `bitpub load <name>` — read a slice back
- `bitpub find <term>` — search by name and content (`--all` searches every private slice)
- `bitpub sync` — pull updates from the cloud (`--watch` for a live stream)
- `bitpub delete <name>` — remove (soft-delete, recoverable for 30 days with `--undo`)

### How the CLI behaves (worth knowing, not commands to you)

1. **URLs are passed through verbatim.** When a `bitpub://...` URL is given to any command, the CLI uses it as-is. Shortening one to a name before passing it in would re-resolve against the active project instead of the address the URL points at.
2. **`load` falls through on miss.** If `bitpub load <name>` misses in this project but the slice exists elsewhere in private memory, the CLI loads it and prints a stderr note like `(loaded from <full-url> — not in this project)` so you know where it actually lived.
3. **`save` is private by default.** A default-path save lands at `bitpub://private:<owner>/Projects/<this-folder>/...`, encrypted client-side. The CLI never silently writes to a group address — that requires an explicit `bitpub://group:...` URL or a `@team/...` alias.
4. **`save` suggests alternative addresses.** After a default-path save, the CLI prints other private addresses the slice could plausibly live at (`/Memory/...`, `/Inbox/...`, `/Drafts/...`, plus any defined aliases). These are suggestions — the CLI does not act on them. Leading-slash paths resolve against the private root (e.g. `bitpub save /Memory/q3-notes "..."`).

Anchors and config live in `~/.bitpub/config.json` (nothing is written inside this folder).
Full reference: `~/.claude/skills/bitpub/SKILL.md` (or `bitpub setup skill install` to (re)install).
<!-- bitpub:end -->
