#!/bin/bash
# Build main.pdf. Requires a TeX distribution with pdflatex + bibtex.
# Overleaf also works: set the main document to main.tex.
set -eu
cd "$(dirname "$0")"

pdflatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex

echo
echo "errors:            $(grep -c '^!' main.log || true)"
echo "undefined cites:   $(grep -c 'Citation.*undefined' main.log || true)"
echo "undefined refs:    $(grep -c 'Reference.*undefined' main.log || true)"
echo "overfull >5pt:     $(grep -o 'Overfull \\hbox ([0-9.]*pt' main.log | awk -F'[( ]' '$4+0>5' | wc -l | tr -d ' ')"
echo "built:             $(ls -la main.pdf | awk '{print $5}') bytes"
