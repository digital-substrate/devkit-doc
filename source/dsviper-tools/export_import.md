# Export & Import

`database_export.py` and `database_import.py` move a database's contents
through an **open, human-readable JSON bundle**. Together they give you a
backup-and-restore path, a diff-and-inspect surface, and — above all — the
guarantee that your data is never trapped in an opaque binary file: it
round-trips through a format you can read, store, and rebuild from without
a proprietary reader.

| Tool                   | Direction       | Produces / consumes                   |
|------------------------|-----------------|---------------------------------------|
| **database_export.py** | database → JSON | an export *bundle* (a directory)      |
| **database_import.py** | JSON → database | a fresh `Database` / `CommitDatabase` |

```{note}
The round-trip is **state-level**, not history-level. Exporting a
`CommitDatabase` captures its materialised state *at one commit* — not the
commit DAG. Re-importing builds a brand-new database whose history starts
at a single `import` commit. Use export/import for portability and backup
of a *state*, not to preserve or transfer commit history (for that,
synchronise against a [commit server](server.md)).
```

## database_export.py

Serialise a `Database` or `CommitDatabase` to a JSON bundle — embedded
definitions, one document file per attachment, and blobs with their
layouts.

```bash
# Plain Database — exports the current state
python3 tools/database_export.py project.vpr

# CommitDatabase — --commit-id is required (last / first / <id>)
python3 tools/database_export.py project.cdb --commit-id last

# Custom output directory
python3 tools/database_export.py project.cdb --commit-id last --output backup/
```

### Options

| Option        | Description                                                                                                      | Default         |
|---------------|----------------------------------------------------------------------------------------------------------------|-----------------|
| `--commit-id` | Commit to export (`last`, `first`, or an id) — **required for a `CommitDatabase`**, ignored for a plain `Database` | -               |
| `--output`    | Output directory                                                                                               | `<name>.export` |
| `--indent`    | JSON indentation                                                                                              | `2`             |
| `-v`          | Report what was written                                                                                        | quiet           |

### Bundle layout

The export directory is self-describing:

```
<name>.export/
├── manifest.json      # kind, commit id, definitions digest, counts
├── definitions.json   # the DSM definitions, as dsm-json
├── documents/         # one JSON file per attachment
│   └── <attachment>.json
└── blobs/             # binary blobs, keyed by id
```

## database_import.py

Rebuild a database from an export bundle, **preserving blob ids**. The
target type defaults to whatever the bundle recorded; override it with
`--as`.

```bash
# Rebuild, matching the source type recorded in the bundle
python3 tools/database_import.py project.export rebuilt.cdb

# Force a target type
python3 tools/database_import.py project.export rebuilt.vpr --as database
python3 tools/database_import.py project.export rebuilt.cdb --as commit-database
```

### Options

| Option            | Description                                           | Default          |
|-------------------|-------------------------------------------------------|------------------|
| `--as`            | Target type: `database` or `commit-database`          | match the bundle |
| `--label`         | Commit label when creating a `CommitDatabase`         | `import`         |
| `--documentation` | Override the documentation stored in the new artefact | from the bundle  |
| `--force`         | Overwrite the output file if it exists                | off              |
| `-v`              | Report what was imported                              | quiet            |

```{warning}
Importing into a `CommitDatabase` creates it with a **single commit**
(labelled `import` by default). The original commit history is not
reconstructed — only the exported state is.
```
