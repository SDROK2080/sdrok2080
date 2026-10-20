import json
import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

def generate_analytical_report(
    df: pd.DataFrame,
    dataset_name: str,
    source_url: Optional[str] = None,
    source_type: str = "Government Data Portal",
    included_sections: Optional[List[str]] = None,
    custom_title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Constructs an evidence-based, professional analytical report.
    Adheres strictly to factual findings, avoiding unsubstantiated causality claims.
    """
    total_records = len(df)
    total_columns = len(df.columns)
    
    # Calculate factual summary
    missing_total = int(df.isna().sum().sum())
    dup_count = int(df.duplicated().sum())

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = [c for c in df.columns if c not in numeric_cols]

    # Generate key findings
    key_findings = []
    key_findings.append(f"The dataset comprises {total_records:,} observed records across {total_columns} attributes.")
    
    if dup_count > 0:
        key_findings.append(f"Identified {dup_count} duplicate row(s) requiring deduplication.")
    else:
        key_findings.append("No identical duplicate rows detected across recorded dimensions.")

    if missing_total > 0:
        missing_pct = round((missing_total / (total_records * total_columns if total_records * total_columns > 0 else 1)) * 100, 2)
        key_findings.append(f"Encountered {missing_total:,} missing/empty values ({missing_pct}% of total data matrix).")
    else:
        key_findings.append("Data matrix is fully populated with zero missing cells.")

    # Numerical statistics findings
    sample_stats = []
    for c in numeric_cols[:4]:
        num_s = pd.to_numeric(df[c], errors="coerce").dropna()
        if not num_s.empty:
            mean_v = round(float(num_s.mean()), 2)
            med_v = round(float(num_s.median()), 2)
            min_v = round(float(num_s.min()), 2)
            max_v = round(float(num_s.max()), 2)
            key_findings.append(f"For '{c}': Mean value is {mean_v:,.2f}, Median is {med_v:,.2f}, ranging from {min_v:,.2f} to {max_v:,.2f}.")
            sample_stats.append({
                "metric": c,
                "mean": mean_v,
                "median": med_v,
                "min": min_v,
                "max": max_v,
                "std": round(float(num_s.std()), 2) if len(num_s) > 1 else 0
            })

    # Geographical/Administrative insights if present
    geo_cols = [c for c in df.columns if any(k in c.lower() for k in ["district", "province", "municipality", "pradesh"])]
    if geo_cols and numeric_cols:
        target_geo = geo_cols[0]
        target_num = numeric_cols[0]
        try:
            geo_agg = df.groupby(target_geo)[target_num].sum().sort_values(ascending=False)
            top_entity = geo_agg.index[0]
            top_val = geo_agg.iloc[0]
            key_findings.append(f"Highest recorded aggregate for '{target_num}' by '{target_geo}' is held by {top_entity} ({top_val:,.2f}).")
        except Exception:
            pass

    # Methodological limitations & scientific precautions
    limitations = [
        "Analysis reflects solely the publicly extracted snapshot at the collection timestamp.",
        "Correlations observed between indicators denote statistical association and must not be interpreted as causal relationships without experimental control.",
        "Discrepancies in administrative naming conventions (e.g. Romanized vs Devanagari transliteration) can affect regional aggregation accuracy."
    ]

    # Concrete, data-supported recommendations
    recommendations = [
        "Maintain standardized reporting schemas across municipal and provincial reporting entities.",
        "Implement continuous data hygiene protocols to replace arbitrary missing values with standardized null representations.",
        "Cross-reference key figures against official Gazette notifications or audited National Statistics Office publications."
    ]

    report_title = custom_title or f"Analytical Data Report: {dataset_name}"

    sections = [
        {"id": "exec_summary", "title": "1. Executive Summary", "enabled": True},
        {"id": "provenance", "title": "2. Data Source & Collection Provenance", "enabled": True},
        {"id": "quality", "title": "3. Data Quality & Cleaning Audit", "enabled": True},
        {"id": "findings", "title": "4. Statistical Findings & Aggregations", "enabled": True},
        {"id": "limitations", "title": "5. Limitations & Analytic Assumptions", "enabled": True},
        {"id": "recommendations", "title": "6. Empirical Recommendations", "enabled": True}
    ]

    return {
        "report_title": report_title,
        "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "dataset_name": dataset_name,
        "source_url": source_url or "Direct upload / Official Open Portal",
        "source_type": source_type,
        "total_records": total_records,
        "total_columns": total_columns,
        "executive_summary": (
            f"This analytical assessment provides empirical evaluation of '{dataset_name}'. "
            f"A total of {total_records:,} records spanning {total_columns} attributes were ingested. "
            f"Descriptive parameters were derived using rigorous Python numerical processing, "
            f"summarizing central tendencies, distributions, and structural characteristics."
        ),
        "data_quality": {
            "duplicate_records": dup_count,
            "missing_cells": missing_total,
            "integrity_score": f"{max(0, 100 - round((missing_total / (total_records * total_columns if total_records * total_columns > 0 else 1)) * 100, 1))}%"
        },
        "key_findings": key_findings,
        "numeric_summary_table": sample_stats,
        "limitations": limitations,
        "recommendations": recommendations,
        "sections": sections
    }
