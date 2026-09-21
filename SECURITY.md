# Security

## Authentication

Passwords are stored with bcrypt hashes. Authentication failures return generic messages.

## User isolation

Transactions, budgets, import records, documents, conversation memory, and document-RAG collections are scoped by authenticated user ID.

## Upload security

- Supported extensions are restricted.
- Filenames are normalized with `basename`.
- Path traversal markers are rejected.
- Upload size limits are enforced.
- CSV imports are parsed before commit.
- Duplicate rows and duplicate files are reported.
- Existing datasets are not replaced unless the user explicitly selects replacement.
- Private documents are not written to public/static directories.

## Prompt injection

Memory and retrieved document text are treated as untrusted data. Stored text is sanitized before prompt injection, retrieval is user-scoped, and document instructions do not override system/security instructions.

## Secrets

API keys are read from environment variables. Logs redact common secret fields. `.env` is excluded by `.gitignore` and is not included in the release ZIP.

## Financial safety

The product provides informational analysis. It does not claim guaranteed investment returns or licensed advisory status. External market facts are separated from model interpretation.

## Export safety

CSV export is generated from application data. Future spreadsheet-style exports should prefix formula-leading cells before writing them to CSV.
