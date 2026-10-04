# Using your generated SDK

Kibo turns your DSM model into code you work against every day: typed classes over the
Viper runtime, produced by the {doc}`kibo-template-viper <../kibo-template-viper/index>`
pack. This chapter is that daily surface for the code **kibo 2** and
**kibo-template-viper 2.0** generate — one page per language.

The principle is shared (the {term}`Dual Reality`: the same value seen as a typed object
and as a runtime `Value`), and so is the vocabulary — one module or namespace per DSM
namespace, structures, enumerations, keys, containers, attachments grouped by the concept
they are keyed on, function pools. The form follows each language:

- **{doc}`Python <python>`** — a package over the `dsviper` wheel. A generated object is a
  box around one Viper value, with Python's protocols: keyword constructors, `==`, `hash`,
  `<`, `enum.Enum`, `dict`- and `list`-like containers.
- **{doc}`TypeScript <node>`** — an ES module package over the `@digitalsubstrate/dsviper`
  Node binding: the same boxes, with `equals` / `hashKey` / `compare`, string-union
  enumerations and `bigint` for 64-bit integers.
- **{doc}`C++ <cpp>`** — C++17 value types (`struct`, `enum class`, STL containers) that
  cross to a `Viper::Value` through a generated codec. It is the base reference: the
  Python and TypeScript packages offer what it offers, with its restrictions.

Each page covers the same ground in the same order: what the package holds, structures and
enumerations, what is shared and what is copied, containers, keys, attachments and the
stores they read and write, the bridge to the runtime, errors, and pools.

Generating the code is {doc}`kibo-project <../kibo/kibo-project>`'s job, from a project's
`kibo.toml`; which features a project selects is described in
{doc}`../kibo-template-viper/features`, and packaging in
{doc}`../kibo-template-viper/wheels` and {doc}`../kibo-template-viper/node`.

## Coming from 1.2

The 2.0 surface replaces the 1.2 one throughout — `md.Tuto_Login` becomes `tuto.Login`,
the `<ns>_<concept>_<attachment>_set` functions become
`tuto.attachments.User.login.set`, `vpr_value` becomes `unwrap_value()` — so code written
against 1.2 output needs migrating. The *Migrating from 1.2* table of the pack's
[CHANGELOG](https://github.com/digital-substrate/kibo-template-viper/blob/main/CHANGELOG.md)
gives, name by name, what a 1.2 client writes and what it writes against 2.0, in each
language; {ref}`features-from-1-2` says where each 1.2 feature went.

```{toctree}
:maxdepth: 1

python
node
cpp
```
