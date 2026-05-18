# DevKit Documentation

> Digital Substrate's Python toolkit for metadata-driven data modeling. Define data structures in DSM (a purpose-built DSL), and the dsviper runtime gives you strong typing, a versioned commit DAG over your data, and seamless Python integration.

DevKit is the **distribution** that bundles **DSM** (the modeling language), **Kibo** (the code generator), **dsviper** (the Python runtime, published on PyPI), and a set of editors, components and reference apps. The names **DevKit / dsviper / Viper** are not interchangeable — see the naming page for the canonical disambiguation. This documentation is the canonical source, published at https://docs.digitalsubstrate.io/.

## Orientation

{{auto:source/ecosystem/*.md}}

## DSM — the modeling language

{{auto:source/dsm/*.md}}

## Kibo — code generation

{{auto:source/kibo/*.md}}

## kibo-template-viper — first-party template pack

{{auto:source/kibo-template-viper/*.md}}

## dsviper — Python runtime

{{auto:source/dsviper/*.md}}

## Commit

{{auto:source/commit/*.md}}

## Services

{{auto:source/services/*.md}}

## Commit Applications

{{auto:source/commit-apps/*.md}}

## Tools and components

{{auto:source/dsviper-tools/*.md,source/dsviper-components/*.md}}

## For LLM agents and RAG pipelines

- [Full documentation in one file](https://docs.digitalsubstrate.io/llms-full.txt): All pages above concatenated with `<!-- FILE: ... -->` source markers — the llms-full.txt companion to this file (see https://llmstxt.org/). Fetch this when you need to answer a question from ground truth in a single request.
- [NotebookLM-ready Markdown bundles](https://devkit.digitalsubstrate.io/downloads/): `devkit-X.Y-notebooklm.zip` — the same corpus split by subsystem for tools that ingest per-source (NotebookLM, RAG pipelines).
- [Bundle coordinates and download URLs](https://devkit.digitalsubstrate.io/version.json): Machine-readable JSON on the sister site — current LTS, build number, dsviper PyPI floor, and direct download URLs for the DevKit zip / doc archive / PDF / NotebookLM zip.

## Optional

{{auto:source/legal/*.md}}
