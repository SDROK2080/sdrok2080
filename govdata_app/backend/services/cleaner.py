import os
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

def clean_dataset(
    df: pd.DataFrame,
    operations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Applies reversible, step-by-step cleaning operations to a dataframe without mutating raw data.
    
    Supported operations:
    - remove_duplicates: subset?: list
    - drop_na: columns?: list, how?: 'any'|'all'
    - fill_na: strategy: 'mean'|'median'|'mode'|'constant'|'ffill'|'bfill', value?: any, columns?: list
    - drop_columns: columns: list
    - rename_columns: mapping: {old: new}
    - change_dtype: column: str, target_type: 'int'|'float'|'str'|'datetime'|'bool'
    - trim_whitespace: columns?: list
    - filter_rows: column: str, condition: 'equals'|'not_equals'|'contains'|'greater_than'|'less_than', value: any
    - remove_outliers_iqr: columns: list, factor?: float
    """
    cleaned = df.copy()
    applied_logs: List[str] = []

    for op in operations:
        action = op.get("action")

        if action == "remove_duplicates":
            before = len(cleaned)
            subset = op.get("subset")
            cleaned = cleaned.drop_duplicates(subset=subset)
            applied_logs.append(f"Removed {before - len(cleaned)} duplicate rows.")

        elif action == "drop_na":
            before = len(cleaned)
            cols = op.get("columns")
            how = op.get("how", "any")
            cleaned = cleaned.dropna(subset=cols if cols else None, how=how)
            applied_logs.append(f"Dropped {before - len(cleaned)} rows with missing values.")

        elif action == "fill_na":
            strategy = op.get("strategy", "constant")
            cols = op.get("columns") or list(cleaned.columns)
            val = op.get("value")

            for col in cols:
                if col not in cleaned.columns:
                    continue
                if strategy == "constant":
                    cleaned[col] = cleaned[col].fillna(val if val is not None else "Unknown")
                elif strategy == "mean" and pd.api.types.is_numeric_dtype(cleaned[col]):
                    cleaned[col] = cleaned[col].fillna(cleaned[col].mean())
                elif strategy == "median" and pd.api.types.is_numeric_dtype(cleaned[col]):
                    cleaned[col] = cleaned[col].fillna(cleaned[col].median())
                elif strategy == "mode":
                    mode_val = cleaned[col].mode()
                    if not mode_val.empty:
                        cleaned[col] = cleaned[col].fillna(mode_val[0])
                elif strategy == "ffill":
                    cleaned[col] = cleaned[col].ffill()
                elif strategy == "bfill":
                    cleaned[col] = cleaned[col].bfill()
            applied_logs.append(f"Filled missing values using '{strategy}' strategy on columns {cols}.")

        elif action == "drop_columns":
            cols_to_drop = [c for c in op.get("columns", []) if c in cleaned.columns]
            if cols_to_drop:
                cleaned = cleaned.drop(columns=cols_to_drop)
                applied_logs.append(f"Removed columns: {', '.join(cols_to_drop)}.")

        elif action == "rename_columns":
            mapping = op.get("mapping", {})
            valid_mapping = {k: v for k, v in mapping.items() if k in cleaned.columns and str(v).strip()}
            if valid_mapping:
                cleaned = cleaned.rename(columns=valid_mapping)
                applied_logs.append(f"Renamed columns: {valid_mapping}.")

        elif action == "change_dtype":
            col = op.get("column")
            target = op.get("target_type")
            if col in cleaned.columns:
                try:
                    if target == "int":
                        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0).astype(int)
                    elif target == "float":
                        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
                    elif target == "str":
                        cleaned[col] = cleaned[col].astype(str)
                    elif target == "datetime":
                        cleaned[col] = pd.to_datetime(cleaned[col], errors="coerce")
                    elif target == "bool":
                        cleaned[col] = cleaned[col].astype(bool)
                    applied_logs.append(f"Converted column '{col}' to {target}.")
                except Exception as e:
                    applied_logs.append(f"Failed to cast '{col}' to {target}: {str(e)}")

        elif action == "trim_whitespace":
            cols = op.get("columns") or [c for c in cleaned.columns if cleaned[c].dtype == object]
            for col in cols:
                if col in cleaned.columns and cleaned[col].dtype == object:
                    cleaned[col] = cleaned[col].astype(str).str.strip()
            applied_logs.append(f"Trimmed leading/trailing whitespace on {len(cols)} text columns.")

        elif action == "filter_rows":
            col = op.get("column")
            cond = op.get("condition")
            val = op.get("value")
            if col in cleaned.columns:
                before = len(cleaned)
                if cond == "equals":
                    cleaned = cleaned[cleaned[col].astype(str) == str(val)]
                elif cond == "not_equals":
                    cleaned = cleaned[cleaned[col].astype(str) != str(val)]
                elif cond == "contains":
                    cleaned = cleaned[cleaned[col].astype(str).str.contains(str(val), case=False, na=False)]
                elif cond == "greater_than":
                    num_s = pd.to_numeric(cleaned[col], errors="coerce")
                    cleaned = cleaned[num_s > float(val)]
                elif cond == "less_than":
                    num_s = pd.to_numeric(cleaned[col], errors="coerce")
                    cleaned = cleaned[num_s < float(val)]
                applied_logs.append(f"Filtered rows on '{col}' ({cond} {val}). Rows remaining: {len(cleaned)} (removed {before - len(cleaned)}).")

        elif action == "remove_outliers_iqr":
            cols = [c for c in op.get("columns", []) if c in cleaned.columns and pd.api.types.is_numeric_dtype(cleaned[c])]
            factor = float(op.get("factor", 1.5))
            before = len(cleaned)
            for col in cols:
                q25 = cleaned[col].quantile(0.25)
                q75 = cleaned[col].quantile(0.75)
                iqr = q75 - q25
                lower_bound = q25 - factor * iqr
                upper_bound = q75 + factor * iqr
                cleaned = cleaned[(cleaned[col] >= lower_bound) & (cleaned[col] <= upper_bound)]
            applied_logs.append(f"Removed {before - len(cleaned)} outliers outside {factor}x IQR on {cols}.")

    return {
        "cleaned_df": cleaned,
        "logs": applied_logs,
        "total_rows": len(cleaned),
        "total_columns": len(cleaned.columns),
        "columns": list(cleaned.columns)
    }
