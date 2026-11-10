# PDF Parser

Reserved for an isolated PDF parsing module.

## Planned use

Parse publicly accessible competition and conservatory documents and extract candidate fields such as:

- application deadline
- age limits
- voice types
- repertoire requirements
- application fee
- official source URL

## Initial implementation plan

1. Select a small set of representative public PDFs.
2. Test Docling locally in an isolated Python environment.
3. Compare extracted text and tables against the original documents.
4. Save structured output as a review candidate, not as automatically verified public data.
5. Add a separate scheduled workflow only after runtime, memory use, and output quality are understood.

No Docling dependency or production workflow change is introduced by this placeholder.
