# PDF Parser (Docling)

An isolated PDF-to-Markdown and evidence-candidate extractor for official Italian conservatory and audition notices.

## Safety boundary

- Input is a local PDF file. Download official documents separately and check the source URL.
- Maximum input size: 25 MB; maximum converted pages: 20.
- Output is a local JSON review file. It is not written into \`data/\`, GitHub Pages, or the production workflow.
- Extracted values are explicitly marked \`pending_manual_review\`; never treat them as verified deadlines or requirements without checking the original PDF.
- Do not commit private PDFs, generated review files, or applicant data.

## Install

Use a dedicated Python environment. The main project requirements and daily GitHub Actions workflow are deliberately unchanged.

\`\`\`bash
python3 -m venv .venv-docling
source .venv-docling/bin/activate
python -m pip install --upgrade pip
python -m pip install -r tools/pdf_parser/requirements.txt
\`\`\`

## Run

\`\`\`bash
python tools/pdf_parser/parse_pdf.py /path/to/official-bando.pdf
\`\`\`

By default, the output is saved beside the PDF as \`official-bando.candidates.json\`. Choose another path with \`--output\`. Add \`--include-markdown\` to include the converted Markdown text in the JSON file.

## Test candidate extraction without installing Docling

\`\`\`bash
cd tools/pdf_parser
python -m unittest -v
\`\`\`

## What it extracts

The first version collects evidence snippets for:

- application deadlines (when a deadline phrase and date/time occur together)
- age-limit wording
- voice types
- repertoire, exam, and document requirements
- date-like text

This is intentionally evidence-first. It does not yet normalize dates, infer eligibility, or update the website database.
