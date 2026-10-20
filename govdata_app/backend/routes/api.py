import os
import json
import shutil
import pandas as pd
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from govdata_app.backend.database import get_db
from govdata_app.backend.models import Dataset, ProcessingHistory, Report, SavedAPI
from govdata_app.backend.services.scraper import scrape_web_tables
from govdata_app.backend.services.api_extractor import extract_api_data
from govdata_app.backend.services.file_processor import inspect_and_parse_file, download_file_from_url
from govdata_app.backend.services.cleaner import clean_dataset
from govdata_app.backend.services.analyzer import compute_comprehensive_statistics, perform_group_aggregation
from govdata_app.backend.services.visualizer import generate_chart_config
from govdata_app.backend.services.reporter import generate_analytical_report
from govdata_app.backend.services.source_directory import get_directory

api_router = APIRouter(prefix="/api")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
EXPORT_DIR = os.path.join(BASE_DIR, "data", "exports")
SAMPLE_DIR = os.path.join(BASE_DIR, "data", "samples")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(SAMPLE_DIR, exist_ok=True)

# Helper to read dataset dataframe
def load_dataset_dataframe(dataset: Dataset, use_cleaned_if_available: bool = True) -> pd.DataFrame:
    target_path = dataset.cleaned_file_path if (use_cleaned_if_available and dataset.cleaned_file_path and os.path.exists(dataset.cleaned_file_path)) else dataset.file_path
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Dataset physical file not found on disk.")
    
    ext = os.path.splitext(target_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(target_path)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(target_path)
    elif ext == ".json":
        return pd.read_json(target_path)
    else:
        # Fallback to general inspector
        parsed = inspect_and_parse_file(target_path)
        return parsed["dataframe"]

# --- Sources Directory ---
@api_router.get("/sources")
def list_sources():
    return {"sources": get_directory()}

# --- Scraper Endpoint ---
class ScrapeRequest(BaseModel):
    url: str
    max_tables: int = 10

@api_router.post("/scrape")
def scrape_url(req: ScrapeRequest):
    try:
        result = scrape_web_tables(req.url, max_tables=req.max_tables)
        return result
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Web extraction failed: {str(e)}")

class SaveScrapedTableRequest(BaseModel):
    url: str
    table_index: int
    dataset_name: str
    headers: List[str]
    rows: List[Dict[str, Any]]

@api_router.post("/scrape/save")
def save_scraped_table(req: SaveScrapedTableRequest, db: Session = Depends(get_db)):
    if not req.rows:
        raise HTTPException(status_code=400, detail="Cannot save empty table.")

    df = pd.DataFrame(req.rows)
    filename = f"scraped_{int(pd.Timestamp.now().timestamp())}.csv"
    dest_path = os.path.join(UPLOAD_DIR, filename)
    df.to_csv(dest_path, index=False)

    dataset = Dataset(
        name=req.dataset_name or f"Scraped Table ({req.table_index})",
        description=f"Extracted from {req.url}",
        source_type="scrape",
        source_url=req.url,
        original_filename=filename,
        file_path=dest_path,
        total_rows=len(df),
        total_columns=len(df.columns),
        columns_json=json.dumps(list(df.columns)),
        is_official_source=True
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    history = ProcessingHistory(
        dataset_id=dataset.id,
        operation="Scrape Import",
        details=f"Extracted {len(df)} rows from HTML table at {req.url}"
    )
    db.add(history)
    db.commit()

    return {"message": "Scraped table saved to workspace", "dataset_id": dataset.id}

# --- API Extractor Endpoint ---
class ApiExtractRequest(BaseModel):
    endpoint_url: str
    method: str = "GET"
    params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    auth_token: Optional[str] = None
    dataset_name: Optional[str] = None
    save_dataset: bool = False

@api_router.post("/extract/api")
def extract_api(req: ApiExtractRequest, db: Session = Depends(get_db)):
    try:
        res = extract_api_data(
            endpoint_url=req.endpoint_url,
            method=req.method,
            params=req.params,
            headers=req.headers,
            auth_token=req.auth_token
        )

        dataset_id = None
        if req.save_dataset and res.get("records"):
            df = pd.DataFrame(res["records"])
            filename = f"api_{int(pd.Timestamp.now().timestamp())}.csv"
            dest_path = os.path.join(UPLOAD_DIR, filename)
            df.to_csv(dest_path, index=False)

            dataset = Dataset(
                name=req.dataset_name or "API Ingested Dataset",
                description=f"Ingested from {req.endpoint_url}",
                source_type="api",
                source_url=req.endpoint_url,
                original_filename=filename,
                file_path=dest_path,
                total_rows=len(df),
                total_columns=len(df.columns),
                columns_json=json.dumps(list(df.columns)),
                is_official_source=True
            )
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
            dataset_id = dataset.id

            history = ProcessingHistory(
                dataset_id=dataset.id,
                operation="API Ingestion",
                details=f"Extracted {len(df)} records via {req.method} request."
            )
            db.add(history)
            db.commit()

        return {
            "status": "success",
            "total_records": res["total_records"],
            "columns": res["columns"],
            "data_types": res["data_types"],
            "preview": res["preview"],
            "dataset_id": dataset_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- File Import (Upload & URL) ---
@api_router.post("/import/upload")
async def import_upload_file(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    selected_sheet: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    safe_filename = f"{int(pd.Timestamp.now().timestamp())}_{file.filename}"
    dest_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        inspected = inspect_and_parse_file(dest_path, selected_sheet=selected_sheet)
        df = inspected["dataframe"]

        dataset = Dataset(
            name=dataset_name or file.filename,
            description="Locally imported file dataset",
            source_type="upload",
            source_url="Local Upload",
            original_filename=file.filename,
            file_path=dest_path,
            total_rows=len(df),
            total_columns=len(df.columns),
            columns_json=json.dumps(list(df.columns)),
            is_official_source=False
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        history = ProcessingHistory(
            dataset_id=dataset.id,
            operation="File Upload",
            details=f"Uploaded {file.filename} ({len(df)} rows, {len(df.columns)} cols)"
        )
        db.add(history)
        db.commit()

        return {
            "dataset_id": dataset.id,
            "metadata": inspected["metadata"]
        }
    except Exception as e:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise HTTPException(status_code=400, detail=f"File parse failed: {str(e)}")

class UrlImportRequest(BaseModel):
    file_url: str
    dataset_name: Optional[str] = None
    selected_sheet: Optional[str] = None

@api_router.post("/import/url")
def import_file_from_url(req: UrlImportRequest, db: Session = Depends(get_db)):
    try:
        saved_path = download_file_from_url(req.file_url, UPLOAD_DIR)
        inspected = inspect_and_parse_file(saved_path, selected_sheet=req.selected_sheet)
        df = inspected["dataframe"]

        dataset = Dataset(
            name=req.dataset_name or os.path.basename(saved_path),
            description=f"Imported from {req.file_url}",
            source_type="url",
            source_url=req.file_url,
            original_filename=os.path.basename(saved_path),
            file_path=saved_path,
            total_rows=len(df),
            total_columns=len(df.columns),
            columns_json=json.dumps(list(df.columns)),
            is_official_source=True
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        history = ProcessingHistory(
            dataset_id=dataset.id,
            operation="URL Download",
            details=f"Downloaded from {req.file_url} ({len(df)} rows)"
        )
        db.add(history)
        db.commit()

        return {
            "dataset_id": dataset.id,
            "metadata": inspected["metadata"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Import pre-configured official Nepal sample dataset
@api_router.post("/import/sample/{sample_name}")
def load_sample_dataset(sample_name: str, db: Session = Depends(get_db)):
    sample_file_path = os.path.join(SAMPLE_DIR, f"{sample_name}.csv")
    if not os.path.exists(sample_file_path):
        raise HTTPException(status_code=404, detail="Requested sample dataset does not exist.")

    inspected = inspect_and_parse_file(sample_file_path)
    df = inspected["dataframe"]
    
    clean_title = sample_name.replace("_", " ").title()

    dataset = Dataset(
        name=clean_title,
        description=f"Verified public reference dataset from official Nepal Government repository.",
        source_type="sample",
        source_url="Official Nepal Government Portal",
        original_filename=f"{sample_name}.csv",
        file_path=sample_file_path,
        total_rows=len(df),
        total_columns=len(df.columns),
        columns_json=json.dumps(list(df.columns)),
        is_official_source=True
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    history = ProcessingHistory(
        dataset_id=dataset.id,
        operation="Sample Dataset Loaded",
        details=f"Loaded {clean_title} ({len(df)} rows)"
    )
    db.add(history)
    db.commit()

    return {"message": "Sample loaded successfully", "dataset_id": dataset.id}

# --- Datasets Listing & Management ---
@api_router.get("/datasets")
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(Dataset).order_by(Dataset.id.desc()).all()
    results = []
    for d in datasets:
        results.append({
            "id": d.id,
            "name": d.name,
            "description": d.description,
            "source_type": d.source_type,
            "source_url": d.source_url,
            "total_rows": d.total_rows,
            "total_columns": d.total_columns,
            "columns": json.loads(d.columns_json or "[]"),
            "is_cleaned": bool(d.cleaned_file_path),
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": d.updated_at.strftime("%Y-%m-%d %H:%M")
        })
    return {"datasets": results}

@api_router.get("/datasets/{dataset_id}")
def get_dataset_detail(dataset_id: int, page: int = 1, page_size: int = 50, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_dataset_dataframe(dataset)
    total_records = len(df)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    page_rows = df.iloc[start_idx:end_idx].fillna("").to_dict(orient="records")

    # History
    history_items = [
        {"operation": h.operation, "details": h.details, "created_at": h.created_at.strftime("%Y-%m-%d %H:%M")}
        for h in dataset.history
    ]

    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
        "source_type": dataset.source_type,
        "source_url": dataset.source_url,
        "total_rows": total_records,
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {col: str(df[col].dtype) for col in df.columns},
        "is_cleaned": bool(dataset.cleaned_file_path),
        "page": page,
        "page_size": page_size,
        "total_pages": (total_records + page_size - 1) // page_size if page_size > 0 else 1,
        "rows": page_rows,
        "history": history_items
    }

@api_router.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Remove cleaned file if exists
    if dataset.cleaned_file_path and os.path.exists(dataset.cleaned_file_path):
        try:
            os.remove(dataset.cleaned_file_path)
        except Exception:
            pass

    db.delete(dataset)
    db.commit()
    return {"message": "Dataset deleted successfully"}

# --- Data Cleaning ---
class CleanDatasetRequest(BaseModel):
    operations: List[Dict[str, Any]]

@api_router.post("/datasets/{dataset_id}/clean")
def clean_dataset_endpoint(dataset_id: int, req: CleanDatasetRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Always clean starting from the raw original dataset to preserve reproducibility
    raw_df = load_dataset_dataframe(dataset, use_cleaned_if_available=False)
    
    result = clean_dataset(raw_df, req.operations)
    cleaned_df = result["cleaned_df"]

    # Save cleaned version
    cleaned_filename = f"cleaned_{dataset.id}_{int(pd.Timestamp.now().timestamp())}.csv"
    cleaned_path = os.path.join(UPLOAD_DIR, cleaned_filename)
    cleaned_df.to_csv(cleaned_path, index=False)

    dataset.cleaned_file_path = cleaned_path
    dataset.total_rows = len(cleaned_df)
    dataset.total_columns = len(cleaned_df.columns)
    dataset.columns_json = json.dumps(list(cleaned_df.columns))
    
    for log_entry in result["logs"]:
        h = ProcessingHistory(
            dataset_id=dataset.id,
            operation="Data Cleaning",
            details=log_entry
        )
        db.add(h)

    db.commit()

    return {
        "message": "Dataset cleaned successfully",
        "logs": result["logs"],
        "total_rows": len(cleaned_df),
        "total_columns": len(cleaned_df.columns),
        "columns": list(cleaned_df.columns),
        "preview": cleaned_df.head(25).fillna("").to_dict(orient="records")
    }

@api_router.post("/datasets/{dataset_id}/reset-cleaning")
def reset_cleaning_endpoint(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if dataset.cleaned_file_path and os.path.exists(dataset.cleaned_file_path):
        try:
            os.remove(dataset.cleaned_file_path)
        except Exception:
            pass
        dataset.cleaned_file_path = None

    raw_df = load_dataset_dataframe(dataset, use_cleaned_if_available=False)
    dataset.total_rows = len(raw_df)
    dataset.total_columns = len(raw_df.columns)
    dataset.columns_json = json.dumps(list(raw_df.columns))

    h = ProcessingHistory(
        dataset_id=dataset.id,
        operation="Reset Clean",
        details="Reverted dataset to raw original uncleaned version."
    )
    db.add(h)
    db.commit()

    return {"message": "Dataset reverted to original raw data"}

# --- Data Analysis ---
@api_router.get("/datasets/{dataset_id}/analyze")
def analyze_dataset_endpoint(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_dataset_dataframe(dataset)
    stats = compute_comprehensive_statistics(df)
    return stats

class AggregationRequest(BaseModel):
    group_by: str
    target_column: str
    func: str = "sum"

@api_router.post("/datasets/{dataset_id}/aggregate")
def aggregate_dataset_endpoint(dataset_id: int, req: AggregationRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_dataset_dataframe(dataset)
    try:
        aggregated_data = perform_group_aggregation(
            df=df,
            group_by_col=req.group_by,
            agg_col=req.target_column,
            agg_func=req.func
        )
        return {"result": aggregated_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Interactive Visualizations ---
class ChartConfigRequest(BaseModel):
    chart_type: str
    x_col: str
    y_col: Optional[str] = None
    group_col: Optional[str] = None
    title: Optional[str] = None

@api_router.post("/datasets/{dataset_id}/chart")
def get_chart_data(dataset_id: int, req: ChartConfigRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_dataset_dataframe(dataset)
    try:
        plotly_spec = generate_chart_config(
            df=df,
            chart_type=req.chart_type,
            x_col=req.x_col,
            y_col=req.y_col,
            group_col=req.group_col,
            title=req.title
        )
        return plotly_spec
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Reports Generation & Export ---
class ReportGenerateRequest(BaseModel):
    custom_title: Optional[str] = None
    included_sections: Optional[List[str]] = None

@api_router.post("/datasets/{dataset_id}/report")
def create_report(dataset_id: int, req: ReportGenerateRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_dataset_dataframe(dataset)
    report_dict = generate_analytical_report(
        df=df,
        dataset_name=dataset.name,
        source_url=dataset.source_url,
        source_type=dataset.source_type,
        included_sections=req.included_sections,
        custom_title=req.custom_title
    )

    db_report = Report(
        dataset_id=dataset.id,
        title=report_dict["report_title"],
        summary=report_dict["executive_summary"],
        sections_json=json.dumps(report_dict["sections"]),
        findings_json=json.dumps(report_dict["key_findings"]),
        recommendations_json=json.dumps(report_dict["recommendations"])
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    report_dict["id"] = db_report.id
    return report_dict

# Export Dataset to CSV, Excel, or JSON
@api_router.get("/datasets/{dataset_id}/export")
def export_dataset(dataset_id: int, format: str = "csv", db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_dataset_dataframe(dataset)
    format = format.lower()
    
    clean_name = "".join(c for c in dataset.name if c.isalnum() or c in (" ", "_", "-")).rstrip()
    if format == "csv":
        out_file = os.path.join(EXPORT_DIR, f"{clean_name}.csv")
        df.to_csv(out_file, index=False)
        return FileResponse(out_file, media_type="text/csv", filename=f"{clean_name}.csv")
    elif format in ["xlsx", "excel"]:
        out_file = os.path.join(EXPORT_DIR, f"{clean_name}.xlsx")
        df.to_excel(out_file, index=False)
        return FileResponse(out_file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=f"{clean_name}.xlsx")
    elif format == "json":
        out_file = os.path.join(EXPORT_DIR, f"{clean_name}.json")
        df.to_json(out_file, orient="records", indent=2)
        return FileResponse(out_file, media_type="application/json", filename=f"{clean_name}.json")
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: csv, excel, json")

# --- Dashboard Overview Stats ---
@api_router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_datasets = db.query(Dataset).count()
    all_datasets = db.query(Dataset).all()
    total_records = sum((d.total_rows or 0) for d in all_datasets)
    total_reports = db.query(Report).count()
    
    recent_imports = [
        {
            "id": d.id,
            "name": d.name,
            "source_type": d.source_type,
            "rows": d.total_rows,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for d in db.query(Dataset).order_by(Dataset.id.desc()).limit(5).all()
    ]

    recent_history = [
        {
            "operation": h.operation,
            "dataset_name": h.dataset.name if h.dataset else "Dataset",
            "details": h.details,
            "created_at": h.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for h in db.query(ProcessingHistory).order_by(ProcessingHistory.id.desc()).limit(6).all()
    ]

    return {
        "total_datasets": total_datasets,
        "total_records": total_records,
        "total_reports": total_reports,
        "recent_imports": recent_imports,
        "recent_history": recent_history
    }
