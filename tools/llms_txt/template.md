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

## Commit Engine

{{auto:source/commit/*.md}}

## Services

{{auto:source/services/*.md}}

## Commit Application Model

{{auto:source/commit-apps/*.md}}

## Tools and components

{{auto:source/dsviper-tools/*.md,source/dsviper-components/*.md}}

## For LLM agents and RAG pipelines

A concatenated Markdown corpus of the full documentation, organised as bundles tuned for LLM ingestion (NotebookLM, agents, RAG), is published with each DevKit release as `devkit-X.Y-notebooklm.zip`. Available at https://devkit.digitalsubstrate.io/downloads/.

## Optional

{{auto:source/legal/*.md}}
