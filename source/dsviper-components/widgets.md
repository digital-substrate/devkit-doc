# Widgets

A catalogue of the components exposed by `dsviper-components`, grouped
by functional area. Every widget assumes the host application has
constructed a [CommitStore](../commit/commit_store.md) and a
`DSCommitStoreNotifier` as described in [Architecture](architecture.md).

```{note}
**Convention** — most widgets take the running `CommitStore` as their
first constructor argument and listen on `DSCommitStoreNotifier` to
refresh themselves. The exceptions are flagged below.
```

## Notifier

The adapter that translates runtime change notifications into Qt
Signals.

| Class                    | Purpose                                     |
|--------------------------|---------------------------------------------|
| `DSCommitStoreNotifier`  | Bridge `CommitStoreNotifying` → Qt Signals. Subclass of `QObject`; signals: `database_did_open`, `database_did_close`, `state_did_change`, `definitions_did_change`, `dispatch_error`, `database_will_reset`, `database_did_reset`, `stop_live`, `message`. |

## Database lifecycle

| Class                     | Constructor                  | Purpose                                |
|---------------------------|------------------------------|----------------------------------------|
| `DSDatabaseSelectDialog`  | `(databases: list[str])`     | File-picker for `.db` / `.cdb` files; returns the chosen path. |

## Live state inspection

| Class               | Constructor   | Purpose                                                |
|---------------------|---------------|--------------------------------------------------------|
| `DSInspectDialog`   | `()`          | Tree of every attachment / structure in the running state — refreshes on `state_did_change`. |

## The commit DAG

| Class                     | Constructor             | Purpose                                                 |
|---------------------------|-------------------------|---------------------------------------------------------|
| `DSCommitsDialog`         | `(store: CommitStore)`  | Full DAG browser — navigate commits, jump to head, compare. |
| `DSCommitsView`           | embedded                | Embeddable view used by `DSCommitsDialog`.              |
| `DSCommitActionsDialog`   | `(store: CommitStore)`  | Toggle commit visibility in batch (each toggle appends an Enable / Disable commit). |
| `DSCommitUndoDialog`      | `(store: CommitStore)`  | Undo stack as a navigable list (replay any past state). |

## Per-commit content

| Class                       | Constructor             | Purpose                                                  |
|-----------------------------|-------------------------|----------------------------------------------------------|
| `DSCommitDocumentsDialog`   | `(store: CommitStore)`  | Documents and attachments grouped by commit.             |
| `DSCommitBlobsDialog`       | `(store: CommitStore)`  | All blobs referenced anywhere in the commit history.     |
| `DSCommitSettingsDialog`    | `()`                    | Per-commit settings editor (consults the running store). |
| `DSCommitProgramDialog`     | `(store: CommitStore)`  | Python program embedded in a commit — replayable.        |

## Documents and attachments helpers

Lower-level tooling used both by the per-commit dialogs above and by
applications that want to expose a generic document tree on their own.

| Class / module                  | Purpose                                                |
|---------------------------------|--------------------------------------------------------|
| `DSDocuments`                   | Generic document tree widget, agnostic of the backend. |
| `DSDocumentsAttachmentsDialog`  | Attachment-level inspection of a document.             |
| `DSDocumentsKeysDialog`         | Key-level inspection of a document.                    |
| `DSDocumentsBuilder`            | Programmatic builder for the document tree.            |
| `DSDocumentsCommitStore`        | Backend adapter — drives `DSDocuments` from a `CommitStore`. |
| `DSDocumentsDatabasing`         | Backend adapter — drives `DSDocuments` from a `Databasing`. |
| `DSDocumentsNavigation`         | Selection / navigation helpers shared across dialogs.  |
| `DSDocumentsItem`               | Tree-item wrapper for a document.                      |
| `DSDocumentsComboBoxItem`       | Combo-box wrapper for document selection.              |

## Blobs

| Class                    | Constructor   | Purpose                                                  |
|--------------------------|---------------|----------------------------------------------------------|
| `DSBlobsDialog`          | `()`          | Standalone blob browser (independent of commit history). |
| `DSBlobsTreeViewItem`    | embedded      | Tree-view item helper used by the blob dialogs.          |

## Sync

| Class                              | Constructor   | Purpose                                                |
|------------------------------------|---------------|--------------------------------------------------------|
| `DSConnectToServerDialog`          | `()`          | Collect remote-server connection details (host, port, socket path). |
| `DSCommitSynchronizerThread`       | runtime       | Threaded worker driving fetch / push / sync off the UI thread. |
| `DSCommitSynchronizationSource`    | runtime       | Descriptor for a synchronisation source.               |
| `DSCommitSyncLogDialog`            | `()`          | Real-time sync log display.                            |

## Embedded Python scripting

| Class / module               | Purpose                                                |
|------------------------------|--------------------------------------------------------|
| `DSCodeEditorDialog`         | Script editor dialog. Constructor: `(model: PythonEditorModel)`. Carries its own Editor menu (`open_script_action`, `save_script_action`, `run_script_action`, `show_description_action`, `refresh_syntax_action`) the host application can append to its menubar. |
| `DSCodeEditor`               | Embeddable code editor (used by the dialog).           |
| `PythonEditorModel`          | Script model. Constructor: `(scripts_folder: str, namespace_vars: dict | None = None)`. Runs scripts via `exec()` in the live interpreter; `namespace_vars` are exposed as globals to user scripts. |
| `syntax_highlighter`         | Python syntax highlighter for the editor.              |

```{tip}
Pass the application's `Context` (or any object the user should be able
to script against) through `namespace_vars`. ge-py exposes
`{"ctx": Context.instance(), "store": store}` so scripts can call
`ctx.dispatch("…", λ)` exactly like the menu actions.
```

## Utilities

| Class / module                  | Purpose                                                |
|---------------------------------|--------------------------------------------------------|
| `DSDialogHelper`                | Geometry persistence and show / hide conventions for dialogs. |
| `DSItemDelegateNoEdit`          | Qt delegate that disables editing for a column.        |
| `DSItemDelegateValidate`        | Qt delegate enforcing per-cell validation.             |
| `DSLogger`                      | Runtime log compatible with `dsviper.Logging`.         |
| `DSSettings`                    | Thin wrapper over `QSettings` with default registration. |

## See also

- [Architecture](architecture.md) — the Notifier Bridge and the integration
  recipe each widget assumes.
- [ge-py walk-through](../commit-apps/ge-py.md) — a real application that
  uses most of these widgets, with the wiring code visible.
