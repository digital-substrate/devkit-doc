# Hello dsviper

The shortest possible end-to-end use of the runtime — seven API calls
that demonstrate the full value chain.

```{doctest}
>>> key = TUTO_A_USER_LOGIN.create_key()
>>> login = TUTO_A_USER_LOGIN.create_document()
>>> login.nickname = "alice"

>>> mutable = CommitMutableState(db.initial_state())
>>> mutable.attachment_mutating().set(TUTO_A_USER_LOGIN, key, login)
>>> commit_id = db.commit_mutations("Add alice", mutable)

>>> db.state(commit_id).attachment_getting().get(TUTO_A_USER_LOGIN, key)
Optional({nickname='alice', password=''})
```

What this exercises:

- **Typed handles** — `TUTO_A_USER_LOGIN` is the runtime handle for the
  `attachment<User, Login>` declared in the Tuto fixture model.
  `create_key()` mints a typed `User` key; `create_document()` produces a
  fresh `Login` record matching the schema.
- **Transactional write** — `CommitMutableState` accumulates the staged
  mutations; `commit_mutations()` lands them as a single commit in the
  DAG and returns the new commit id (which you capture explicitly).
- **Type-safe read** — read back through the state at the new commit via
  `attachment_getting().get(...)`, which returns an `Optional`. A type
  mismatch on either side would have raised at the boundary.

This snippet runs as part of `make doctest`. The fixture (`db`,
`TUTO_A_USER_LOGIN`) is preloaded by the doctest harness; in your own
code you obtain the same handles either by importing the
[Kibo-generated package](../kibo/index.rst) (the static API) or by
[loading the DSM model at runtime](dsm.md) (the dynamic API).

For the full lifecycle — a `.cdb` on disk, browsing the mutation DAG,
querying via attachments — continue with the [Tutorial](tutorial.md).
