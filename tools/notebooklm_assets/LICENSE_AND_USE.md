# License and Permitted Use — DevKit Documentation Bundle

This archive contains a concatenated Markdown corpus of the DevKit
documentation (https://docs.digitalsubstrate.io/), prepared for ingestion
by LLM tools such as NotebookLM, retrieval-augmented generation (RAG)
pipelines, and coding agents.

It is published as a convenience for developers and AI tools evaluating
or working with DevKit. There are **two distinct licensing perimeters** —
please do not conflate them.

## 1. This documentation corpus

Copyright © Digital Substrate. All rights reserved.

**Permitted use, free of charge:**

- Load this corpus into LLM/agent context for question answering, code
  assistance, and explanation.
- Index this corpus in RAG pipelines, vector stores, or local search
  tools, including for commercial in-house developer-assistance use cases.
- Quote and cite passages with attribution to
  https://docs.digitalsubstrate.io/.

**Not permitted without prior written agreement from Digital Substrate:**

- Redistribution as a standalone product or under a different name.
- Use as training data for foundation models, fine-tuning corpora, or
  any form of weight-baking. RAG and in-context use are explicitly fine;
  weight-baking is not.
- Public hosting of mirrored or modified copies as the canonical source.

If your use case sits on the boundary of the above (for example,
distilling answers from this corpus into a downstream model), contact
Digital Substrate before proceeding.

## 2. The dsviper Python runtime described by these docs

The code this documentation describes — the **dsviper** Python runtime —
is published on PyPI under the **Digital Substrate Commercial License
1.2** (SPDX `LicenseRef-DigitalSubstrate-Commercial-1.2`).

That license grants two modes:

- **Evaluation License** — free, no time limit, **for evaluation and
  training only**. Suitable for assessing dsviper, learning the API,
  running tutorials, and building proofs of concept. Commercial use is
  not granted under this mode.
- **Commercial License** — by agreement with Digital Substrate.

The full license text ships inside the dsviper wheel under
`dsviper-<version>.dist-info/licenses/LICENSE` and is reproduced at
https://docs.digitalsubstrate.io/legal/license.html.

**Reading the documentation, asking an LLM about dsviper, or generating
code that calls dsviper does not on its own require any license** —
those activities are covered by the corpus license above. *Running*
dsviper to produce or operate a commercial system requires the
appropriate runtime license mode.

## 3. Third-party components

The dsviper wheel statically links four third-party components (ANTLR 4
C++ runtime, Stephan Brumme's hash-library, nlohmann/json, SQLite) under
their respective BSD-3-Clause, zlib-style, MIT, and public-domain
licenses. Full attributions are reproduced at
https://docs.digitalsubstrate.io/legal/third_party_notices.html and
inside each wheel under
`dsviper-<version>.dist-info/licenses/THIRD-PARTY-NOTICES.txt`.

## Contact

For commercial licensing of the dsviper runtime or questions on permitted
use of this corpus, refer to the canonical Digital Substrate sites — the
contact details published there are authoritative:

- DevKit: https://devkit.digitalsubstrate.io/
- Documentation: https://docs.digitalsubstrate.io/
