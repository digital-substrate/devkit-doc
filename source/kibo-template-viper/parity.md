# Python and TypeScript

The Python package and the TypeScript package are **one design in two idioms**. Both are thin
views over the same runtime: a generated object holds one Viper value and delegates every
operation to it, so what an operation does is the runtime's in both languages. What differs is
how each language spells it. The two surfaces stay parallel: a feature added to one is added to
the other in the same change.

Both follow the C++ surface, the pack's base reference: they offer what it offers, with its
restrictions (see {doc}`index`).

## Where the idioms differ

| Concern | Python | TypeScript |
|---|---|---|
| Viper value | `unwrap_value()` over `_value`; `S.wrap_value(value)` | `unwrapValue()`; `S.wrapValue(value)` |
| construct | `S(value \| dict \| None, **fields)` (a value is boxed), `SKey(uuid \| str)` | `new S(value \| record?)` (a value is boxed), `new SKey(uuid?)` |
| structure field | `@property` + setter | get/set accessors |
| enumeration | `enum.Enum`, `from_str`, index via `E(i)` | literal union + object: `fromStr`, `index`, `unwrapValue` |
| container | `Sequence` / `Mapping` / `Ordered`, dunder protocol | same views, `Symbol.iterator` + methods |
| absent optional | `None` | `undefined` |
| equality, hash, order, display | `==`, `hash()`, `<`, `repr()` | `equals`, `hashKey`, `compare`, `toString` / `toJSON` |
| container protocol | `len()`, `in`, `contains`, `empty`, `to_list` / `to_tuple`, `items`, `v + w`, `m[c] = column` | `size` / `length`, `has`, `toArray`, `entries`, `concat`, `setColumn` |
| a value of another type | `TypeError`, from every `wrap_value` and constructor | `TypeError`, from every `wrapValue` and constructor |
| documentation | the DSM documentation on the class, the field, the attachment | the same places; a structure's, on the class, not on its `…Init` |
| attachment | `<unit>.attachments.<Concept>.<attachment>.get(getting, key)` | `<Concept>.<attachment>.get(getting, key)` |
| attachment verbs | `keys`, `has`, `get`, `enumerate`, `diff_keys`, `set`, `delete`, `diff` (`del` is a keyword) | `keys`, `has`, `get`, `enumerate`, `diffKeys`, `set`, `del`, `diff`, as the C++ |
| field-level verbs | `set_<f>`, `union_<f>`, `subtract_<f>`, `update_<f>`, `insert_<f>`, `remove_<f>` | `set<F>`, `union<F>`, `subtract<F>`, `update<F>`, `insert<F>`, `remove<F>` |
| function pool | `Pool` (local, holding `NAME` and `UUID`) and `Remote` | `Remote`; `NAME` and `UUID` are the module's |

The argument order is the same everywhere: state first, then key, then value.

## Why the rows are idioms

Each row is the same meaning written in each language's grammar, never a different meaning.
Python spells a field in snake_case and TypeScript keeps the model's name; Python has `None`
where TypeScript has `undefined`; Python's `del` is a keyword, so an attachment deletes with
`delete` there and with `del` in TypeScript, as in C++; Python reaches a container through its
dunder protocol (`len()`, `in`, `+`), TypeScript through `Symbol.iterator` and methods; Python
hashes with `hash()`, TypeScript gives `hashKey()`, the key a native `Map` or `Set` needs.

The line between idiom and drift is the runtime. A difference that lives in the static surface
and follows the host language — an `enum.Enum` against a literal union, `del` against
`delete` — is legitimate. A difference that changes what happens at run time — another
operation, another argument order, a value that is not the runtime's — is a bug, whatever the
language. Divergences beyond the rows above are drift, not idiom.

One row records a gap rather than an idiom: a function pool. Python renders a local `Pool`
beside `Remote`; TypeScript renders the client side, `Remote`, only.

## How the parity is checked

The rows were measured, not recalled. The pack's test laboratory,
[devkit-codegen-test](https://github.com/digital-substrate/devkit-codegen-test), renders the
Python and TypeScript packages of each of its sites and lists every public member of both —
the classes and their members, an attachment's operations, the containers, the runtime the
package re-exports. It compares them by name, case and underscores aside (`diff_keys` is
`diffKeys`, `f_e` is `f_E`), together with whether each member carries documentation.

A difference is either one of the idioms above, which the laboratory holds as data with its
reason, or drift: a member one language has and the other lacks, or documents and the other
does not. Drift fails the laboratory's check (`check.py`, through `tools/parity.py`). An idiom
is added there only together with its row in the table above.
