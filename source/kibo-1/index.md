# Kibo 1

Kibo 1 — kibo 1.2.x with the kibo-template-viper 1.2.x pack, reading **Template Model 1** —
is the generator line that projects created before kibo 2 use. It generates for the same
Viper LTS-1.2 runtime as kibo 2: the DSM language, the runtime and the databases are the
same, only the generator and the code it generates differ.

**Kibo 2 is the current line**, documented in {doc}`../kibo/index`,
{doc}`../kibo-template-viper/index` and {doc}`../using-generated-sdk/index`. Moving to it:

- a template pack — {doc}`../kibo/migrating`;
- an application's code — {doc}`../using-generated-sdk/migrating`.

In the DevKit, kibo 1 sits in the `kibo-1/` folder — its jar in `kibo-1/tools/`, its pack in
`kibo-1/templates/` — and generates through `tools/dsm_util.py create_python_package` and
`create_node_package` ({doc}`../dsviper-tools/dsm_util`). Its sources are the `LTS-1.2`
branches of [kibo](https://github.com/digital-substrate/kibo/tree/LTS-1.2) and
[kibo-template-viper](https://github.com/digital-substrate/kibo-template-viper/tree/LTS-1.2).

```{toctree}
:maxdepth: 2

kibo/index
kibo-template-viper/index
using-generated-sdk/index
```
