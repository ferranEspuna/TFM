# TFM

Automated build for the article, thesis, and thesis presentation.

## Project layout

- `src/`: LaTeX sources, bibliography files, class/style files, and the university-provided thesis cover PDF.
- `scripts/build.py`: cross-platform build entry point.
- `scripts/figures/`: Python generators for the TikZ figures used by the thesis and slides.
- `experiments/algorithm/`: exploratory code for algorithm experiments, kept separate from the PDF build.
- `out/`: generated final PDFs.
- `build/`: LaTeX intermediates.
- `dist/`: release zip.

Generated files are intentionally ignored by git: `out/`, `build/`, `dist/`,
and `src/figures/*.tex`. `src/portada.pdf` is a source asset and stays in git.

## Requirements

Install a TeX distribution with `latexmk`, `pdflatex`, and BibTeX available on
`PATH`:

- Linux: TeX Live packages such as `latexmk`, `cm-super`, `texlive-latex-extra`,
  `texlive-science`, and `texlive-pictures`.
- Windows: MiKTeX or TeX Live, with `latexmk` enabled.

Install Python dependencies in a virtual environment.

Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Build

Build all PDFs:

```bash
python scripts/build.py
```

Outputs:

- `out/article.pdf`
- `out/thesis.pdf`
- `out/thesis-presentation.pdf`

Clean and build the release package:

```bash
python scripts/build.py --clean --package
```

This creates `dist/tfm-release.zip` containing the PDFs and a buildable source
tree with the generated figures included.

Useful variants:

```bash
python scripts/build.py --target thesis
python scripts/build.py --target article --target presentation
python scripts/build.py --figures-only
python scripts/build.py --clean-only
```

## GitHub releases

`.github/workflows/build.yml` runs on every push. It installs Python and TeX
dependencies, runs:

```bash
python scripts/build.py --clean --package
```

and publishes or updates a release named `pdf-build-<branch>` with the three
PDFs plus `dist/tfm-release.zip`.

## Experiments

The algorithm experiments are optional and do not affect the document build.
See `experiments/algorithm/README.md` for their extra dependencies and entry
point.
