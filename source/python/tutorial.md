# Tutorial

This tutorial walks through a complete example: creating a data model, setting
up a database, and performing operations with CommitDatabase.

> **Prerequisites**: This tutorial assumes you have read [DSM](dsm.md) and
> understand the basics of DSM syntax and the assemble → parse → introspect
> workflow.

## The User/Login Model

We'll create a simple model with Users who have Login credentials and Identity
information.

### Step 1: Define the Data Model

Create a file `model.dsm`:

```dsm
namespace Tuto {f529bc42-0618-4f54-a3fb-d55f95c5ad03} {

concept User;

struct Login {
    string nickname;
    string password;
};

struct Identity {
    string firstname;
    string lastname;
};

attachment<User, Login> login;
attachment<User, Identity> identity;

};
```

### Step 2: Validate the Model

Check the DSM syntax:

```bash
python3 tools/dsm_util.py check model.dsm
```

### Step 3: Create a Database

Create a Commit database that embeds the definitions:

```bash
python3 tools/dsm_util.py create_commit_database model.dsm model.cdb
```

### Step 4: Open and Explore

Open the database in Python:

```pycon
>>> from dsviper import *
>>> db = CommitDatabase.open("model.cdb")

# See the defined types
>>> db.definitions().types()
[Tuto::User, Tuto::Login, Tuto::Identity]

# See the attachments
>>> db.definitions().attachments()
[attachment<User, Login> Tuto::login,
 attachment<User, Identity> Tuto::identity]
```

### Step 5: Inject Constants

Make types accessible as constants:

```pycon
>>> db.definitions().inject()

# Now we have constants for types and attachments
>>> TUTO_A_USER_LOGIN
attachment<User, Login> Tuto::login

>>> TUTO_S_LOGIN
Tuto::Login
```

**Naming convention**: Constants follow the pattern `{NAMESPACE}_{KIND}_{NAME}`:

| Kind        | Prefix | Example                 | Description      |
|-------------|--------|-------------------------|------------------|
| Attachment  | `_A_`  | `TUTO_A_USER_LOGIN`     | Attachment type  |
| Structure   | `_S_`  | `TUTO_S_LOGIN`          | Structure type   |
| Enumeration | `_E_`  | `TUTO_E_STATUS`         | Enumeration type |
| Concept     | `_C_`  | `TUTO_C_USER`           | Concept type     |
| Path        | `_P_`  | `TUTO_P_LOGIN_NICKNAME` | Path to field    |

### Step 6: Create a Key and Document

Create a new User key:

```pycon
>>> key = TUTO_A_USER_LOGIN.create_key()
>>> key.instance_id()
'fc472756-8f9e-42aa-a06f-051d330d0108'
```

Create a Login document:

```pycon
>>> login = TUTO_A_USER_LOGIN.create_document()
>>> login
{nickname='', password=''}

>>> login.nickname = "zoop"
>>> login.password = "robust"
>>> login
{nickname='zoop', password='robust'}
```

### Step 7: Commit to Database

Create a mutable state and commit:

```pycon
# Create mutable state from initial state
>>> mutable_state = CommitMutableState(db.initial_state())

# Associate document with key
>>> mutable_state.attachment_mutating().set(TUTO_A_USER_LOGIN, key, login)

# Commit the mutations
>>> commit_id = db.commit_mutations("First Commit", mutable_state)
>>> commit_id
'87b2b1d275f0ac3b2389b18f58d7abe0214c2493'
```

```{important}
**The Dual-Layer Contract**

CommitDatabase guarantees structural integrity but NOT semantic integrity.
When concurrent streams converge, mutations on non-existent documents or unresolved paths are silently ignored.
Your application must validate business rules when consuming state.

See [The Dual-Layer Contract](../concepts/commit_contract.md).
```

### Step 8: Read from Database

Read the document back:

```pycon
>>> state = db.state(commit_id)
>>> result = state.attachment_getting().get(TUTO_A_USER_LOGIN, key)
>>> result
Optional({nickname='zoop', password='robust'})

>>> result.unwrap()
{nickname='zoop', password='robust'}
```

### Step 9: Update a Field

Update using a path-based setter:

```pycon
>>> mutable_state = CommitMutableState(db.state(db.last_commit_id()))
>>> mutable_state.attachment_mutating().update(
...     TUTO_A_USER_LOGIN, key,
...     TUTO_P_LOGIN_NICKNAME, "zoopy"
... )
>>> db.commit_mutations("Update Nickname", mutable_state)
```

### Step 10: View History

Read from different commits:

```pycon
# Latest commit
>>> state = db.state(db.last_commit_id())
>>> state.attachment_getting().get(TUTO_A_USER_LOGIN, key)
Optional({nickname='zoopy', password='robust'})

# First commit
>>> state = db.state(db.first_commit_id())
>>> state.attachment_getting().get(TUTO_A_USER_LOGIN, key)
Optional({nickname='zoop', password='robust'})

# Initial state (before any commits)
>>> state = db.initial_state()
>>> state.attachment_getting().get(TUTO_A_USER_LOGIN, key)
nil
```

### Step 11: Inspect Commit Headers

```pycon
>>> header = db.commit_header(db.last_commit_id())
>>> header.label()
'Update Nickname'
>>> header.parent_commit_id()
'87b2b1d275f0ac3b2389b18f58d7abe0214c2493'
```

## Two Approaches

Viper supports two ways to work with your data model:

### Dynamic API (Above)

Use Viper's runtime metadata directly:

- `Definitions.load()` → work with types at runtime
- Flexible, interpretive, Python-friendly
- No code generation needed

### Static API (Generated)

Generate infrastructure code from your DSM:

```bash
python3 tools/dsm_util.py create_python_package model.dsm
```

This creates a Python package with:

- Type-safe classes for concepts and structures
- Generated accessors for attachments
- IDE autocompletion support

```pycon
>>> import model.attachments as ma

# Use generated types
>>> key = ma.Tuto_UserKey.create()
>>> login = ma.Tuto_Login()
>>> login.nickname = "user"

# Use generated accessors
>>> state = CommitMutableState(db.state(db.last_commit_id()))
>>> ma.tuto_user_login_set(state.attachment_mutating(), key, login)
```

Both approaches use the same underlying Viper runtime.

## What's Next

- [Database](database.md) - Database and CommitDatabase in detail
- [Blobs](blobs.md) - Working with binary data
- [Types and Values](types_values.md) - Deep dive into the type system
