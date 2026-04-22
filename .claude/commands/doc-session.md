You are now in collaborative documentation mode for the DevKit documentation.

## Documentation Structure

| Manual         | Path               | Content                                              |
|----------------|--------------------|------------------------------------------------------|
| Viper Concepts | `source/concepts/` | Architecture, philosophy, patterns, domains          |
| DSM Manual     | `source/dsm/`      | Introduction, types, concepts, attachments, functions|
| Python Guide   | `source/python/`   | Tutorial, types, collections, database, blobs, API   |
| Toolchain      | `source/tools/`    | dsm_util, Kibo, templates, IDE, editors, server      |

## Workflow

1. User gives feedback (in French is fine)
2. You propose changes concisely
3. On approval ("oui", "ok", "yes"), implement immediately
4. **Always run `make html` after edits** — don't wait to be asked
5. Confirm ready for browser refresh

## Rules

- All documentation content in **English**
- Use real examples from Graph Editor / Raptor Editor when possible
- Keep it concise — cover width without noise
- Respect the "Metadata Everywhere" principle when relevant

## Git Safety

**NEVER commit without explicit user approval.**

Before ANY git state-changing operation (commit, push, merge, rebase):
1. Show `git status` and `git diff --stat`
2. Propose commit message
3. Wait for explicit user approval

## Code Examples

### Python Examples (Preferred)

- Verify against installed `dsviper` API
- Check type hints in the `.pyi` stub (`python -c "import dsviper; print(dsviper.__file__)"`)

### C++ Examples (Use Sparingly)

C++ source lives in the Viper runtime repo (private), not here. When C++ examples are
needed, base them on established patterns from existing documentation pages — do not
invent API calls.

### Authoritative Source for API

The installed `dsviper` package is the single source of truth for this repo. Use
`help(dsviper.ClassName)` or read the `.pyi` stub to verify signatures.

## Sphinx Structure Rules

**NEVER use `:caption:` to fake hierarchy.** Captions are cosmetic labels, not structure.

### Before modifying any `index.rst`:

1. Does this change require folder reorganization?
2. If hierarchical grouping is needed: propose file/folder moves FIRST
3. Inform the user of required disk operations before touching RST files

### After restructuring:

```bash
make clean && make html
```

Incremental builds cache old paths — always clean build after file moves.

---

Ready to collaborate. What would you like to improve?
