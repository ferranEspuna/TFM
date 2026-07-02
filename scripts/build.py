#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
BUILD_DIR = PROJECT_ROOT / "build"
OUT_DIR = PROJECT_ROOT / "out"
DIST_DIR = PROJECT_ROOT / "dist"
FIGURES_DIR = SRC_DIR / "figures"

FIGURE_GENERATORS = [
    PROJECT_ROOT / "scripts" / "figures" / "common_link.py",
    PROJECT_ROOT / "scripts" / "figures" / "k2_222.py",
    PROJECT_ROOT / "scripts" / "figures" / "k3_222.py",
    PROJECT_ROOT / "scripts" / "figures" / "k3_4.py",
    PROJECT_ROOT / "scripts" / "figures" / "kst_proof_sketch.py",
    PROJECT_ROOT / "scripts" / "figures" / "erdos64_dual_sketch.py",
]


@dataclass(frozen=True)
class LatexTarget:
    name: str
    tex_file: str
    output_pdf: str

    @property
    def stem(self) -> str:
        return Path(self.tex_file).stem


TARGETS = {
    "article": LatexTarget("article", "revised.tex", "article.pdf"),
    "thesis": LatexTarget("thesis", "thesis.tex", "thesis.pdf"),
    "presentation": LatexTarget(
        "presentation", "presentation.tex", "thesis-presentation.pdf"
    ),
}


def run(command: list[str], cwd: Path | None = None) -> None:
    display = " ".join(str(part) for part in command)
    print(f"+ {display}")
    subprocess.run(command, cwd=cwd, check=True)


def ensure_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(
            f"Required executable '{name}' was not found. Install a TeX distribution "
            "with latexmk and pdflatex available on PATH."
        )


def clean() -> None:
    for path in (BUILD_DIR, OUT_DIR, DIST_DIR):
        if path.exists():
            shutil.rmtree(path)

    if FIGURES_DIR.exists():
        for figure in FIGURES_DIR.glob("*.tex"):
            figure.unlink()


def generate_figures() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for script in FIGURE_GENERATORS:
        run([sys.executable, str(script)], cwd=PROJECT_ROOT)


def build_target(target: LatexTarget) -> Path:
    ensure_tool("latexmk")
    target_build_dir = BUILD_DIR / "latex" / target.name
    target_build_dir.mkdir(parents=True, exist_ok=True)
    for source_dir in (path for path in SRC_DIR.rglob("*") if path.is_dir()):
        (target_build_dir / source_dir.relative_to(SRC_DIR)).mkdir(
            parents=True, exist_ok=True
        )
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    run(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            f"-outdir={target_build_dir}",
            target.tex_file,
        ],
        cwd=SRC_DIR,
    )

    built_pdf = target_build_dir / f"{target.stem}.pdf"
    final_pdf = OUT_DIR / target.output_pdf
    shutil.copy2(built_pdf, final_pdf)
    print(f"Wrote {final_pdf.relative_to(PROJECT_ROOT)}")
    return final_pdf


def should_package(path: Path) -> bool:
    rel = path.relative_to(PROJECT_ROOT)
    excluded_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        "build",
        "dist",
        "out",
    }
    return not any(part in excluded_dirs for part in rel.parts)


def package_release(pdf_paths: list[Path]) -> Path:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DIST_DIR / "tfm-release.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for pdf_path in pdf_paths:
            archive.write(pdf_path, Path("pdfs") / pdf_path.name)

        for path in PROJECT_ROOT.rglob("*"):
            if not path.is_file() or not should_package(path):
                continue
            rel = path.relative_to(PROJECT_ROOT)
            archive.write(path, Path("source") / rel)

    print(f"Wrote {zip_path.relative_to(PROJECT_ROOT)}")
    return zip_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the article, thesis, and slides.")
    parser.add_argument(
        "--target",
        choices=sorted(TARGETS),
        action="append",
        help="Build one target. May be passed multiple times. Defaults to all targets.",
    )
    parser.add_argument(
        "--skip-figures",
        action="store_true",
        help="Do not regenerate TikZ figures before compiling LaTeX.",
    )
    parser.add_argument(
        "--figures-only",
        action="store_true",
        help="Only regenerate TikZ figures.",
    )
    parser.add_argument(
        "--package",
        action="store_true",
        help="Create dist/tfm-release.zip with PDFs and buildable source.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove generated outputs before building.",
    )
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="Remove generated outputs and exit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.clean or args.clean_only:
        clean()
    if args.clean_only:
        return

    if not args.skip_figures:
        generate_figures()
    if args.figures_only:
        return

    target_names = args.target or list(TARGETS)
    pdf_paths = [build_target(TARGETS[name]) for name in target_names]

    if args.package:
        package_release(pdf_paths)


if __name__ == "__main__":
    main()
