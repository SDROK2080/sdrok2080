from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

def generate_chart_config(
    df: pd.DataFrame,
    chart_type: str,
    x_col: str,
    y_col: Optional[str] = None,
    group_col: Optional[str] = None,
    title: Optional[str] = None,
    max_categories: int = 25
) -> Dict[str, Any]:
    """
    Generates JSON configurations suitable for Plotly.js rendering.
    Supports: bar, horizontal_bar, line, pie, donut, histogram, scatter, box, area.
    """
    if x_col not in df.columns:
        raise ValueError(f"Column '{x_col}' does not exist in dataset.")

    chart_title = title or f"{chart_type.replace('_', ' ').title()} of {y_col or x_col}"
    data_traces = []
    layout = {
        "title": {"text": chart_title, "font": {"family": "Inter, sans-serif", "size": 18, "color": "#1e293b"}},
        "template": "plotly_white",
        "margin": {"l": 50, "r": 30, "t": 60, "b": 60},
        "hovermode": "closest",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
    }

    if chart_type in ["bar", "horizontal_bar"]:
        if y_col and y_col in df.columns:
            # Aggregate or take top categories
            sub = df[[x_col, y_col]].copy()
            sub[y_col] = pd.to_numeric(sub[y_col], errors="coerce")
            agg = sub.groupby(x_col)[y_col].sum().reset_index().sort_values(by=y_col, ascending=False).head(max_categories)
            
            if chart_type == "horizontal_bar":
                data_traces.append({
                    "type": "bar",
                    "orientation": "h",
                    "x": agg[y_col].tolist(),
                    "y": agg[x_col].astype(str).tolist(),
                    "marker": {"color": "#2563eb"}
                })
                layout["xaxis"] = {"title": y_col}
                layout["yaxis"] = {"title": x_col, "autorange": "reversed"}
            else:
                data_traces.append({
                    "type": "bar",
                    "x": agg[x_col].astype(str).tolist(),
                    "y": agg[y_col].tolist(),
                    "marker": {"color": "#2563eb"}
                })
                layout["xaxis"] = {"title": x_col}
                layout["yaxis"] = {"title": y_col}
        else:
            # Count distribution of x_col
            counts = df[x_col].value_counts().head(max_categories).reset_index()
            counts.columns = [x_col, "count"]
            data_traces.append({
                "type": "bar",
                "x": counts[x_col].astype(str).tolist(),
                "y": counts["count"].tolist(),
                "marker": {"color": "#3b82f6"}
            })
            layout["xaxis"] = {"title": x_col}
            layout["yaxis"] = {"title": "Count / Frequency"}

    elif chart_type == "line":
        if y_col and y_col in df.columns:
            sub = df[[x_col, y_col]].dropna().copy()
            sub[y_col] = pd.to_numeric(sub[y_col], errors="coerce")
            sub = sub.sort_values(by=x_col)
            
            if group_col and group_col in df.columns:
                for grp_val, grp_df in df.groupby(group_col):
                    data_traces.append({
                        "type": "scatter",
                        "mode": "lines+markers",
                        "name": str(grp_val),
                        "x": grp_df[x_col].astype(str).tolist(),
                        "y": pd.to_numeric(grp_df[y_col], errors="coerce").tolist()
                    })
            else:
                data_traces.append({
                    "type": "scatter",
                    "mode": "lines+markers",
                    "x": sub[x_col].astype(str).tolist(),
                    "y": sub[y_col].tolist(),
                    "line": {"color": "#0284c7", "width": 2.5},
                    "marker": {"size": 6}
                })
            layout["xaxis"] = {"title": x_col}
            layout["yaxis"] = {"title": y_col}

    elif chart_type in ["pie", "donut"]:
        if y_col and y_col in df.columns:
            sub = df[[x_col, y_col]].copy()
            sub[y_col] = pd.to_numeric(sub[y_col], errors="coerce")
            agg = sub.groupby(x_col)[y_col].sum().reset_index().sort_values(by=y_col, ascending=False).head(12)
            labels = agg[x_col].astype(str).tolist()
            values = agg[y_col].tolist()
        else:
            counts = df[x_col].value_counts().head(12).reset_index()
            labels = counts[x_col].astype(str).tolist()
            values = counts["count"].tolist()

        hole_size = 0.45 if chart_type == "donut" else 0.0
        data_traces.append({
            "type": "pie",
            "labels": labels,
            "values": values,
            "hole": hole_size,
            "textinfo": "label+percent"
        })

    elif chart_type == "histogram":
        s = pd.to_numeric(df[x_col], errors="coerce").dropna()
        data_traces.append({
            "type": "histogram",
            "x": s.tolist(),
            "marker": {"color": "#6366f1"}
        })
        layout["xaxis"] = {"title": x_col}
        layout["yaxis"] = {"title": "Frequency"}

    elif chart_type == "scatter":
        if y_col and y_col in df.columns:
            sub = df[[x_col, y_col]].dropna().copy()
            sub[x_col] = pd.to_numeric(sub[x_col], errors="coerce")
            sub[y_col] = pd.to_numeric(sub[y_col], errors="coerce")
            sub = sub.dropna()

            data_traces.append({
                "type": "scatter",
                "mode": "markers",
                "x": sub[x_col].tolist(),
                "y": sub[y_col].tolist(),
                "marker": {"color": "#8b5cf6", "size": 8, "opacity": 0.75}
            })
            layout["xaxis"] = {"title": x_col}
            layout["yaxis"] = {"title": y_col}

    elif chart_type == "box":
        y_target = y_col if (y_col and y_col in df.columns) else x_col
        s = pd.to_numeric(df[y_target], errors="coerce").dropna()
        
        if group_col and group_col in df.columns:
            for grp_val, grp_df in df.groupby(group_col):
                data_traces.append({
                    "type": "box",
                    "name": str(grp_val),
                    "y": pd.to_numeric(grp_df[y_target], errors="coerce").dropna().tolist()
                })
        else:
            data_traces.append({
                "type": "box",
                "y": s.tolist(),
                "name": y_target,
                "boxpoints": "outliers",
                "marker": {"color": "#10b981"}
            })
        layout["yaxis"] = {"title": y_target}

    elif chart_type == "area":
        if y_col and y_col in df.columns:
            sub = df[[x_col, y_col]].dropna().sort_values(by=x_col)
            data_traces.append({
                "type": "scatter",
                "mode": "lines",
                "fill": "tozeroy",
                "x": sub[x_col].astype(str).tolist(),
                "y": pd.to_numeric(sub[y_col], errors="coerce").tolist(),
                "line": {"color": "#059669"},
                "fillcolor": "rgba(5, 150, 105, 0.2)"
            })
            layout["xaxis"] = {"title": x_col}
            layout["yaxis"] = {"title": y_col}

    return {
        "data": data_traces,
        "layout": layout
    }
