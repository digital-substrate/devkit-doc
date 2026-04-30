# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile notebooklm distzip pdf

# Documentation version (from conf.py `release` — keep in sync).
DOC_VERSION ?= 1.2

# Build text bundles for NotebookLM (one .txt per top-level section).
notebooklm:
	@SOURCE_DIR="$(SOURCEDIR)" BUILD_DIR="$(BUILDDIR)" python tools/build_notebooklm.py

# Build a release-ready offline doc archive (multi-page HTML).
# Uses multi-page HTML rather than singlehtml because autosummary's
# generated API stubs are not concatenated by the singlehtml builder
# (links into the API reference would be dead).
distzip: html
	@mkdir -p "$(BUILDDIR)/dist"
	@rm -f "$(BUILDDIR)/dist/devkit-$(DOC_VERSION)-doc.zip"
	@cd "$(BUILDDIR)" && zip -qr "dist/devkit-$(DOC_VERSION)-doc.zip" html -x "html/.buildinfo"
	@echo "wrote $(BUILDDIR)/dist/devkit-$(DOC_VERSION)-doc.zip"
	@du -sh "$(BUILDDIR)/dist/devkit-$(DOC_VERSION)-doc.zip"

# Build a release-ready PDF via xelatex (requires BasicTeX or full TeX Live).
# The default `latexpdf` target writes to build/latex/devkit.pdf — we copy it
# to build/dist/ alongside the zip for symmetric distribution artifacts.
pdf: latexpdf
	@mkdir -p "$(BUILDDIR)/dist"
	@cp "$(BUILDDIR)/latex/devkit.pdf" "$(BUILDDIR)/dist/devkit-$(DOC_VERSION)-doc.pdf"
	@echo "wrote $(BUILDDIR)/dist/devkit-$(DOC_VERSION)-doc.pdf"
	@du -sh "$(BUILDDIR)/dist/devkit-$(DOC_VERSION)-doc.pdf"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
