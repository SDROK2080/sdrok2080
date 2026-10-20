import os
import json
import zipfile
import tempfile
import urllib.parse
from typing import Dict, Any, List, Optional
import pandas as pd
import requests
import pdfplumber
from pypdf import PdfReader
from govdata_app.backend.services.security import validate_public_url

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

def download_file_from_url(url: str, dest_dir: str) -> str:
    """
    Safely downloads a file from a verified public URL.
    """
    is_valid, err_msg = validate_public_url(url)
    if not is_valid:
        raise ValueError(f"Security Alert: {err_msg}")

    headers = {"User-Agent": "GovDataAnalyzer/1.0 (+https://github.com/nepalgovernment/govdata-analyzer)"}
    
    with requests.get(url, headers=headers, stream=True, timeout=30) as r:
        if r.status_code != 200:
            raise ConnectionError(f"HTTP {r.status_code} when attempting to download file from URL.")
        
        # Determine filename
        filename = "downloaded_data"
        content_disp = r.headers.get("Content-Disposition", "")
        if "filename=" in content_disp:
            parts = content_disp.split("filename=")
            filename = parts[1].strip('"\' ')
        else:
            path_part = urllib.parse.urlsplit(url).path
            base_name = os.path.basename(path_part)
            if base_name:
                filename = base_name

        dest_path = os.path.join(dest_dir, filename)
        
        # Enforce size limit
        bytes_read = 0
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    bytes_read += len(chunk)
                    if bytes_read > MAX_FILE_SIZE_BYTES:
                        raise ValueError(f"Downloaded file exceeds maximum permitted size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB.")
                    f.write(chunk)

    return dest_path

def inspect_and_parse_file(
    file_path: str,
    selected_sheet: Optional[str] = None,
    pdf_page_range: Optional[str] = None
) -> Dict[str, Any]:
    """
    Parses CSV, Excel, PDF, JSON, and ZIP data into structured DataFrame representations.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError("File exceeds maximum permissible size limit.")

    ext = os.path.splitext(file_path)[1].lower()
    meta: Dict[str, Any] = {
        "file_name": os.path.basename(file_path),
        "file_size": file_size,
        "format": ext.replace(".", "").upper(),
        "available_sheets": [],
        "selected_sheet": selected_sheet,
        "pdf_pages": 0,
        "extracted_tables_count": 0
    }

    df: Optional[pd.DataFrame] = None

    if ext == ".csv":
        # Auto detect encoding and delimiter
        encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]
        delimiters = [",", "\t", ";", "|"]
        
        for enc in encodings:
            for sep in delimiters:
                try:
                    df_candidate = pd.read_csv(file_path, encoding=enc, sep=sep, nrows=50)
                    if len(df_candidate.columns) > 1:
                        df = pd.read_csv(file_path, encoding=enc, sep=sep)
                        meta["detected_encoding"] = enc
                        meta["detected_delimiter"] = sep
                        break
                except Exception:
                    continue
            if df is not None:
                break

        if df is None:
            # Fallback
            df = pd.read_csv(file_path, encoding="utf-8", on_bad_lines="skip")

    elif ext in [".xlsx", ".xls"]:
        xl = pd.ExcelFile(file_path)
        meta["available_sheets"] = xl.sheet_names
        sheet_to_use = selected_sheet if (selected_sheet and selected_sheet in xl.sheet_names) else xl.sheet_names[0]
        meta["selected_sheet"] = sheet_to_use
        df = pd.read_excel(file_path, sheet_name=sheet_to_use)

    elif ext == ".json":
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
        if isinstance(data, list):
            df = pd.json_normalize(data)
        elif isinstance(data, dict):
            # Check nested keys
            for key in ["data", "records", "results", "items"]:
                if key in data and isinstance(data[key], list):
                    df = pd.json_normalize(data[key])
                    break
            if df is None:
                df = pd.json_normalize([data])

    elif ext == ".pdf":
        all_tables = []
        full_text = []
        with pdfplumber.open(file_path) as pdf:
            meta["pdf_pages"] = len(pdf.pages)
            for page_idx, page in enumerate(pdf.pages):
                txt = page.extract_text()
                if txt:
                    full_text.append(f"--- Page {page_idx+1} ---\n{txt}")
                extracted = page.extract_tables()
                if extracted:
                    for t in extracted:
                        if len(t) > 1:
                            all_tables.append(t)

        meta["extracted_tables_count"] = len(all_tables)
        meta["extracted_text_snippet"] = ("\n".join(full_text))[:1500] if full_text else "No text extracted."

        if all_tables:
            # Convert first substantial table to DataFrame
            first_table = all_tables[0]
            header = [str(c or f"Col_{i+1}").strip() for i, c in enumerate(first_table[0])]
            rows = first_table[1:]
            df = pd.DataFrame(rows, columns=header)
        else:
            # If no tables found, construct tabular lines from text
            lines = [l.strip() for l in ("\n".join(full_text)).split("\n") if l.strip()]
            df = pd.DataFrame({"Text_Content": lines[:500]})

    elif ext == ".zip":
        with zipfile.ZipFile(file_path, "r") as z:
            names = [n for n in z.namelist() if not n.startswith("__MACOSX") and os.path.splitext(n)[1].lower() in [".csv", ".xlsx", ".json"]]
            if not names:
                raise ValueError("Zip archive contains no supported data files (.csv, .xlsx, .json).")
            # Extract first data file to temp directory
            extracted_path = z.extract(names[0], path=os.path.dirname(file_path))
            return inspect_and_parse_file(extracted_path)

    else:
        raise ValueError(f"Unsupported file format: {ext}")

    if df is None or df.empty:
        df = pd.DataFrame({"Notice": ["Empty dataset or unable to extract tabular records."]})

    # Clean column headers
    df.columns = [str(c).strip() if str(c).strip() else f"Column_{i+1}" for i, c in enumerate(df.columns)]
    
    meta["total_rows"] = len(df)
    meta["total_columns"] = len(df.columns)
    meta["columns"] = list(df.columns)
    meta["dtypes"] = {col: str(df[col].dtype) for col in df.columns}
    meta["preview"] = df.head(50).fillna("").to_dict(orient="records")

    return {
        "metadata": meta,
        "dataframe": df
    }
