# Contributing to DevKit Documentation

This repository is currently maintained internally on Babel. Once it migrates to a public hosting platform, the standard fork-and-pull-request flow will be welcome.

## Reporting issues

Once published on GitHub, use GitHub Issues. Until then, contact the maintainer directly.

## Submitting changes

1. Fork the repository (when public) and create a feature branch from `main`.
2. Make your changes (see "Building locally" below).
3. Verify the build is clean: `make html` must succeed without warnings.
4. Open a pull request with a clear description of what changed and why.

## Building locally

```bash
pip install -r requirements.txt   # Sphinx, Furo theme, MyST, dsviper
make html                          # Output: build/html/index.html
```

`pyi_signatures.py` extracts type signatures from the installed `dsviper` wheel — make sure `pip install dsviper` succeeded before building.

## License

This repository uses **dual licensing** — see [LICENSE](LICENSE) for the canonical terms.

- **Prose** (`.rst`, `.md`, narrative content) is licensed under **CC-BY 4.0**.
- **Code samples**, the **Sphinx machinery** (`source/conf.py`, `source/_ext/*.py`, `tools/*.py`), and the **build glue** (`Makefile`, `make.bat`) are licensed under the **MIT License**.
- **Static assets** under `source/_static/` are CC-BY 4.0, except DS trademarks and third-party UI screenshots reproduced under the right of citation (see LICENSE Section 3).

By submitting a contribution:

- A **prose** contribution is provided under **CC-BY 4.0** (inbound = outbound on the prose track).
- A **code-or-machinery** contribution is provided under **MIT** (inbound = outbound on the code track).
- An **image / asset** contribution is provided under **CC-BY 4.0**, unless you state otherwise in the PR description and the maintainer accepts it.

No CLA is required. The track is determined by what you touch — typically a single PR is single-track, but mixed PRs are allowed and each file follows its own track.

## Translation track

Translations are first-class derivative works under CC-BY 4.0. If you initiate a translation effort, please open a tracking issue first so we can agree on the directory layout (e.g. `source/<locale>/`) and synchronisation conventions before files start landing.
