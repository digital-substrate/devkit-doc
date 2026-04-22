---
name: write-documentation
description: Ensures all Sphinx documentation is written in English with consistent formatting. Use when creating or editing any .md or .rst file in source/.
allowed-tools: Read, Write, Edit, Bash
---

# Documentation Writing Skill

## Language Requirement

**CRITICAL: All documentation content MUST be written in English.**

This applies to file content, code comments, diagram labels, and examples.
The conversation with the user may be in French, but written files are always in English.

## File Conventions

- Use MyST Markdown (`.md`) for content pages
- Use reStructuredText (`.rst`) for toctree index files
- Always specify language in code blocks: ` ```python `, ` ```cpp `, ` ```dsm `

## Writing Style

### DO:

- Use active voice
- Be concise and factual
- Use technical terms consistently
- Include tables for structured information
- Verify code examples against the installed `dsviper` API

### DON'T:

- Use emphatic language ("amazing", "powerful")
- Add marketing speak
- Use emojis unless explicitly requested
- Invent code examples without verifying they work

## Post-Modification Workflow

After editing documentation:

1. **Always run `make html`** — check for warnings
2. If files were moved or renamed: `make clean && make html`
3. Verify cross-references (Sphinx reports broken links as warnings)

## Sphinx Directives

Use MyST syntax for callouts:

````markdown
```{note}
Important information.
```

```{tip}
Helpful suggestion.
```

```{warning}
Caution about potential issues.
```
````

## Code Examples

### Python (Preferred)

Verify against installed `dsviper`:
```bash
python -c "import dsviper; help(dsviper.ClassName)"
```

### C++ (Use Sparingly)

C++ source lives in the Viper runtime repo (private). Base C++ examples on established
patterns from existing documentation — do not invent API calls.

### DSM

Use ` ```dsm ` for DSM code blocks (custom lexer provides syntax highlighting).
