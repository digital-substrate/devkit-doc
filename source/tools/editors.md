# Database Editors

Viper provides two GUI applications for exploring and managing databases:

| Tool        | Purpose               | Use When                                               |
|-------------|-----------------------|--------------------------------------------------------|
| **cdbe.py** | CommitDatabase Editor | Working with versioned data (undo/redo, sync, history) |
| **dbe.py**  | Database Editor       | Simple exploration without commit history              |

Both tools are built with PySide6 and share common components from `ds_components/`.

---

## cdbe.py - CommitDatabase Editor

Full-featured GUI for exploring and managing CommitDatabases with version history.

```{figure} /_static/images/tools/cdbe.png
:alt: CommitDatabase Editor GUI showing commit history tree, attachment browser, and document inspector panels
:width: 100%

cdbe.py showing commit history, document browser, and database inspector.
```

### Launch

```bash
python3 tools/cdbe.py                      # Open file dialog
python3 tools/cdbe.py project.cdb          # Open specific database
```

### Panels

Access panels via keyboard shortcuts:

| Panel         | Shortcut | Description                               |
|---------------|----------|-------------------------------------------|
| **Commits**   | `Cmd+1`  | Browse commit history (DAG visualization) |
| **Documents** | `Cmd+2`  | Browse documents by attachment            |
| **Program**   | `Cmd+3`  | View Program in selected commit           |
| **Settings**  | `Cmd+4`  | Configure synchronization source          |
| **Undo**      | `Cmd+5`  | Undo/redo stack visualization             |
| **Sync Log**  | `Cmd+6`  | Synchronization activity log              |
| **Blobs**     | `Cmd+7`  | Browse blob storage                       |
| **Actions**   | `Cmd+8`  | Pending actions queue                     |

### Synchronization

cdbe.py supports synchronizing with a remote CommitDatabase server.

**Connection Settings:**

- TCP: `host:port` (e.g., `server.local:54321`)
- Unix socket: `/path/to/socket`

**Sync Operations:**

| Action    | Description                     |
|-----------|---------------------------------|
| **Fetch** | Pull commits from remote server |
| **Push**  | Push local commits to remote    |
| **Sync**  | Full sync (Fetch + Push)        |

**Live Mode:**

Enable automatic synchronization at configurable intervals:

- **Live Mode**: Auto-sync on timer
- **Manager Mode**: Auto-merge heads during live sync

### Inspecting Commits

1. Open the **Commits** panel (`Cmd+1`)
2. Click a commit to select it
3. Open **Commands** panel (`Cmd+3`) to see mutations
4. Double-click a document to inspect its content

### Undo/Redo

cdbe.py maintains an undo stack for local operations:

- **Undo**: `Cmd+Z`
- **Redo**: `Cmd+Shift+Z`

View the undo stack in the **Undo** panel (`Cmd+5`).

---

## dbe.py - Database Editor

Simplified GUI for exploring Database files (without commit history).

```{figure} /_static/images/tools/dbe.png
:alt: Database Editor GUI showing table list, record browser, and blob content viewer
:width: 100%

dbe.py showing document browser and database inspector.
```

### Launch

```bash
python3 tools/dbe.py                       # Open file dialog
python3 tools/dbe.py project.vpr           # Open specific database
```

### Features

| Feature                | Description                       |
|------------------------|-----------------------------------|
| **Document Browser**   | Browse documents by attachment    |
| **Blob Viewer**        | Inspect binary blob content       |
| **Database Inspector** | View UUID, codec, definitions     |
| **Network Connection** | Connect to remote Database server |

### When to Use dbe.py vs cdbe.py

| Scenario                            | Tool    |
|-------------------------------------|---------|
| Explore versioned data with history | cdbe.py |
| Simple database inspection          | dbe.py  |
| Synchronize with remote server      | cdbe.py |
| Debug blob storage                  | Either  |

---

## ds_components - Shared GUI Library

Both editors use `ds_components/`, a PySide6 widget library:

| Component                | Description                      |
|--------------------------|----------------------------------|
| `DSDocumentsCommitStore` | Document browser for CommitStore |
| `DSDocumentsDatabasing`  | Document browser for Database    |
| `DSCommitsDialog`        | Commit history panel             |
| `DSValueProgramDialog`   | Program viewer                   |
| `DSInspectDialog`        | Database inspector               |
| `DSBlobsDialog`          | Blob storage viewer              |
| `DSSettings`             | User preferences management      |

These components can be reused in custom applications built on Viper.

---

## What's Next

- [Server](server.md) - Running a CommitDatabase server
- [dsm_util](dsm_util.md) - Creating databases from DSM
