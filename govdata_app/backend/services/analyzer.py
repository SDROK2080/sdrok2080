import math
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

def compute_comprehensive_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes rigorous descriptive and diagnostic statistics on a given DataFrame.
    """
    total_records = len(df)
    total_columns = len(df.columns)

    numeric_cols = []
    categorical_cols = []
    datetime_cols = []

    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            numeric_cols.append(c)
        elif pd.api.types.is_datetime64_any_dtype(df[c]):
            datetime_cols.append(c)
        else:
            # Check if strings are parseable as numeric
            sample_clean = pd.to_numeric(df[c].dropna().head(50), errors="coerce")
            if sample_clean.notna().sum() > 40:
                numeric_cols.append(c)
            else:
                categorical_cols.append(c)

    # Column level statistics
    col_stats: Dict[str, Any] = {}
    
    for c in df.columns:
        s = df[c]
        missing_count = int(s.isna().sum())
        missing_pct = round((missing_count / total_records * 100) if total_records > 0 else 0, 2)
        unique_count = int(s.nunique(dropna=True))
        
        stat_item = {
            "name": c,
            "type": "numeric" if c in numeric_cols else "categorical",
            "missing_count": missing_count,
            "missing_pct": missing_pct,
            "unique_count": unique_count,
        }

        if c in numeric_cols:
            num_s = pd.to_numeric(s, errors="coerce").dropna()
            if not num_s.empty:
                mean_val = float(num_s.mean())
                std_val = float(num_s.std()) if len(num_s) > 1 else 0.0
                min_val = float(num_s.min())
                max_val = float(num_s.max())
                median_val = float(num_s.median())
                q25 = float(num_s.quantile(0.25))
                q75 = float(num_s.quantile(0.75))
                iqr = q75 - q25
                
                # Outlier detection (1.5 IQR rule)
                outliers_count = int(((num_s < (q25 - 1.5 * iqr)) | (num_s > (q75 + 1.5 * iqr))).sum())

                stat_item.update({
                    "sum": round(float(num_s.sum()), 2),
                    "mean": round(mean_val, 2),
                    "std": round(std_val, 2),
                    "variance": round(float(num_s.var()) if len(num_s) > 1 else 0.0, 2),
                    "min": round(min_val, 2),
                    "max": round(max_val, 2),
                    "range": round(max_val - min_val, 2),
                    "median": round(median_val, 2),
                    "q25": round(q25, 2),
                    "q75": round(q75, 2),
                    "outliers_count": outliers_count
                })
        else:
            # Categorical frequency distribution
            top_vals = s.value_counts(dropna=True).head(5).to_dict()
            stat_item["top_frequencies"] = {str(k): int(v) for k, v in top_vals.items()}

        col_stats[c] = stat_item

    # Correlation matrix for numerical fields
    correlations = {}
    if len(numeric_cols) >= 2:
        try:
            num_df = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
            corr_df = num_df.corr().round(3)
            # Convert NaN to None
            correlations = corr_df.replace({np.nan: None}).to_dict()
        except Exception:
            correlations = {}

    # Detect geospatial / administrative hierarchies typical for Nepal datasets
    geo_columns = [c for c in df.columns if any(k in c.lower() for k in ["district", "province", "municipality", "pradesh", "jilla", "palika", "region", "country"])]
    time_columns = [c for c in df.columns if any(k in c.lower() for k in ["year", "date", "month", "fiscal", "bs_year"])]
    gender_columns = [c for c in df.columns if any(k in c.lower() for k in ["sex", "gender", "male", "female"])]

    return {
        "summary": {
            "total_records": total_records,
            "total_columns": total_columns,
            "numeric_columns_count": len(numeric_cols),
            "categorical_columns_count": len(categorical_cols),
            "columns": list(df.columns),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "detected_geo_columns": geo_columns,
            "detected_time_columns": time_columns,
            "detected_gender_columns": gender_columns
        },
        "column_statistics": col_stats,
        "correlations": correlations
    }

def perform_group_aggregation(
    df: pd.DataFrame,
    group_by_col: str,
    agg_col: str,
    agg_func: str = "sum"
) -> List[Dict[str, Any]]:
    """
    Performs grouping and aggregation (e.g. by District, Province, Municipality, Year).
    """
    if group_by_col not in df.columns or agg_col not in df.columns:
        raise ValueError("Selected columns do not exist in the dataset.")

    work_df = df[[group_by_col, agg_col]].copy()
    work_df[agg_col] = pd.to_numeric(work_df[agg_col], errors="coerce")
    
    grouped = work_df.groupby(group_by_col)[agg_col]
    if agg_func == "sum":
        res = grouped.sum()
    elif agg_func == "mean":
        res = grouped.mean()
    elif agg_func == "count":
        res = grouped.count()
    elif agg_func == "min":
        res = grouped.min()
    elif agg_func == "max":
        res = grouped.max()
    else:
        res = grouped.sum()

    res = res.reset_index().sort_values(by=agg_col, ascending=False)
    # Return as list of dicts
    return [{str(group_by_col): row[group_by_col], str(agg_col): (round(float(row[agg_col]), 2) if pd.notna(row[agg_col]) else 0)} for _, row in res.iterrows()]
