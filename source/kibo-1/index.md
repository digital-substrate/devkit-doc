# Kibo 1

Kibo 1 — kibo 1.2.x with the kibo-template-viper 1.2.x pack, reading **Template Model 1** —
generates for the Viper LTS-1.2 runtime. **It is deprecated**: it receives fixes only — no
new features — for the life of the LTS-1.2 line, and its generation says so when it runs.
Moving a project off it is {doc}`../kibo-migration/index`.

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
