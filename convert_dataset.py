"""
Dataset Converter
==================
Converts a raw downloaded CSV (e.g. from Kaggle) into the schema the agent
expects: columns [date, description, amount, type] where type is exactly
"debit" or "credit".

Run once, locally, after downloading your dataset:

    python convert_dataset.py path/to/kaggle_file.csv data/sample_transactions.csv

No other project files need to change — this just produces a clean CSV that
drops straight into the existing pipeline (load_and_categorize_statement).

Handles common column-naming variants automatically:
  date        <- Date, transaction_date, Transaction Date, txn_date
  description <- Transaction Description, description, merchant, notes, Notes
  amount      <- Amount, amount, value, Amount (USD), amount_usd
  type        <- Type, transaction_type, Category Type (Income/Expense -> credit/debit)
"""
import sys
import pandas as pd

COLUMN_ALIASES = {
    "date": ["date", "transaction_date", "transaction date", "txn_date", "record_date"],
    "description": ["description", "transaction description", "merchant", "notes", "narration"],
    "amount": ["amount", "amount_usd", "amount (usd)", "value", "amt"],
    "type": ["type", "transaction_type", "transaction type", "flag"],
    "category": ["category", "category name", "expense category"],
}

TYPE_VALUE_MAP = {
    "income": "credit", "credit": "credit", "deposit": "credit", "in": "credit",
    "expense": "debit", "debit": "debit", "withdrawal": "debit", "out": "debit",
}


def find_column(df_columns_lower, aliases):
    for alias in aliases:
        if alias in df_columns_lower:
            return df_columns_lower[alias]
    return None


def convert(input_path: str, output_path: str):
    df = pd.read_csv(input_path)
    original_columns = list(df.columns)
    lower_map = {c.strip().lower(): c for c in df.columns}

    resolved = {}
    for target, aliases in COLUMN_ALIASES.items():
        found = find_column(lower_map, aliases)
        if found is None:
            if target == "category":
                continue  # optional — fall back to keyword categorization if absent
            raise ValueError(
                f"Could not find a column for '{target}' in {original_columns}. "
                f"Rename the relevant column to one of {aliases} and retry."
            )
        resolved[target] = found

    print("Column mapping detected:")
    for target, source in resolved.items():
        print(f"  {source!r}  ->  {target}")

    out = pd.DataFrame()
    out["date"] = pd.to_datetime(df[resolved["date"]], errors="coerce").dt.date
    out["description"] = df[resolved["description"]].astype(str).str.strip()

    # Normalize amount: strip currency symbols/commas, coerce to float
    amount_raw = df[resolved["amount"]].astype(str).str.replace(r"[^\d.\-]", "", regex=True)
    out["amount"] = pd.to_numeric(amount_raw, errors="coerce")

    # Normalize type values (Income/Expense -> credit/debit), case-insensitive
    type_raw = df[resolved["type"]].astype(str).str.strip().str.lower()
    out["type"] = type_raw.map(TYPE_VALUE_MAP)
    unmapped = out["type"].isna()
    if unmapped.any():
        unique_unmapped = type_raw[unmapped].unique()
        print(f"Warning: {unmapped.sum()} rows had unrecognized type values {list(unique_unmapped)} — dropping them. "
              f"Add them to TYPE_VALUE_MAP if they should map to credit/debit.")
        out = out[~unmapped]

    # Pass through an existing category column if the source file has one —
    # this matters when descriptions are anonymized/synthetic and can't be
    # keyword-matched (e.g. "Score each." tells you nothing about spend type)
    if "category" in resolved:
        out["category"] = df.loc[out.index, resolved["category"]].astype(str).str.strip()
        print(f"\nNote: Source file has its own Category column — using it directly "
              f"instead of re-deriving categories from (possibly anonymized) descriptions.")

    # Data quality check: flag categories that are inconsistently typed
    # (e.g. a category that's sometimes Income and sometimes Expense, or a
    # category with a name suggesting income but typed as debit)
    if "category" in out.columns:
        cat_type_counts = out.groupby("category")["type"].nunique()
        mixed = cat_type_counts[cat_type_counts > 1]
        if not mixed.empty:
            print(f"Warning: Data quality note: category/type mix looks inconsistent for: {list(mixed.index)}")
        income_like_names = [c for c in out["category"].unique() if any(k in c.lower() for k in ["salary", "income", "wage"])]
        for c in income_like_names:
            types_seen = out.loc[out["category"] == c, "type"].unique()
            if "credit" not in types_seen:
                print(f"Warning: Data quality note: category '{c}' looks income-related by name but every "
                      f"row is typed as 'debit' in the source file. Preserved as-is (not silently fixed) — "
                      f"flag this to your mentor as a data quality finding.")

    # Ensure debit amounts are negative and credit amounts are positive,
    # since that's the convention the agent's tools assume
    out.loc[out["type"] == "debit", "amount"] = -out.loc[out["type"] == "debit", "amount"].abs()
    out.loc[out["type"] == "credit", "amount"] = out.loc[out["type"] == "credit", "amount"].abs()

    before = len(out)
    required_cols = ["date", "description", "amount", "type"]
    out = out.dropna(subset=required_cols)
    after = len(out)
    if before != after:
        print(f"Warning: Dropped {before - after} rows with missing/unparseable values.")

    out = out.sort_values("date")
    out.to_csv(output_path, index=False)
    print(f"\nDone: Wrote {len(out)} clean transactions to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_dataset.py <input_csv> <output_csv>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
