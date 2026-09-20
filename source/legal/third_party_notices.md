# Third-Party Notices

The Viper runtime statically links five third-party components, and both
binding packages carry it: the wheel ships their copyright notices and full
license texts at `dsviper-<version>.dist-info/licenses/THIRD-PARTY-NOTICES.txt`,
the npm package at `package/THIRD-PARTY-NOTICES.txt`. The file below is that
same file, and the two are checked against each other at build time.

Components used only by the command-line tools or the C++ test harness are not
listed here, because they are not in the runtime and ship in neither package.

| Component | Version | License |
|---|---|---|
| [ANTLR 4 C++ runtime](https://www.antlr.org/) | 4.12.0 | BSD-3-Clause |
| [Stephan Brumme's hash-library](https://create.stephan-brumme.com/hash-library/) | — | zlib-style |
| [nlohmann/json](https://github.com/nlohmann/json) | 3.11.2 | MIT |
| [SQLite](https://www.sqlite.org/) | 3.47.2 | Public Domain |
| [pugixml](https://pugixml.org/) | 1.14 | MIT |

Each component retains its own copyright. Inclusion in dsviper does not
re-license these components — the Digital Substrate Commercial License
applies to dsviper itself, not to the embedded third-party code.

Full texts below.

```{literalinclude} THIRD-PARTY-NOTICES.txt
:language: text
```
