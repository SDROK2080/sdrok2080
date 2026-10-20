import json
from typing import Dict, Any, List, Optional
import requests
import pandas as pd
from govdata_app.backend.services.security import validate_public_url

def extract_api_data(
    endpoint_url: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    auth_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extracts structured data from official government and open-data APIs.
    """
    is_valid, err_msg = validate_public_url(endpoint_url)
    if not is_valid:
        raise ValueError(f"Security Alert: {err_msg}")

    request_headers = {
        "User-Agent": "GovDataAnalyzer/1.0 (+https://github.com/nepalgovernment/govdata-analyzer)",
        "Accept": "application/json, text/csv, application/vnd.api+json, text/plain;q=0.9"
    }

    if headers:
        for k, v in headers.items():
            # Disallow forbidden host headers
            if k.lower() not in {"host", "connection", "transfer-encoding"}:
                request_headers[k] = v

    if auth_token:
        request_headers["Authorization"] = f"Bearer {auth_token}"

    try:
        if method.upper() == "GET":
            response = requests.get(endpoint_url, params=params, headers=request_headers, timeout=20, stream=True)
        else:
            response = requests.request(method.upper(), endpoint_url, params=params, headers=request_headers, timeout=20, stream=True)
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"API request failed: {str(e)}")

    if response.status_code >= 400:
        raise ConnectionError(f"API returned error status code: {response.status_code} ({response.reason})")

    content_type = response.headers.get("Content-Type", "").lower()
    
    # Read up to 15MB
    raw_body = response.raw.read(15 * 1024 * 1024, decode_content=True)

    records: List[Dict[str, Any]] = []

    if "json" in content_type or raw_body.strip().startswith((b"{", b"[")):
        try:
            data = json.loads(raw_body.decode("utf-8", errors="replace"))
        except Exception as e:
            raise ValueError(f"Could not parse response as JSON: {str(e)}")

        # Unpack nested structures commonly found in Gov APIs (e.g., CKAN {success: true, result: {records: [...]}})
        if isinstance(data, list):
            records = [r for r in data if isinstance(r, dict)]
        elif isinstance(data, dict):
            # Check CKAN / Socrata / common formats
            if "result" in data and isinstance(data["result"], dict) and "records" in data["result"]:
                records = data["result"]["records"]
            elif "data" in data and isinstance(data["data"], list):
                records = [r for r in data["data"] if isinstance(r, dict)]
            elif "records" in data and isinstance(data["records"], list):
                records = [r for r in data["records"] if isinstance(r, dict)]
            elif "items" in data and isinstance(data["items"], list):
                records = [r for r in data["items"] if isinstance(r, dict)]
            elif "results" in data and isinstance(data["results"], list):
                records = [r for r in data["results"] if isinstance(r, dict)]
            else:
                # If dict of key-value pairs or single record
                records = [data]
    else:
        # Check if CSV
        import io
        try:
            df = pd.read_csv(io.BytesIO(raw_body))
            records = df.to_dict(orient="records")
        except Exception:
            raise ValueError("Unsupported or non-tabular API response format.")

    if not records:
        return {
            "status": "success",
            "total_records": 0,
            "columns": [],
            "preview": [],
            "records": []
        }

    df = pd.json_normalize(records)
    columns = list(df.columns)
    
    # Detect types
    dtypes = {col: str(df[col].dtype) for col in columns}

    return {
        "status": "success",
        "total_records": len(df),
        "columns": columns,
        "data_types": dtypes,
        "preview": df.head(100).fillna("").to_dict(orient="records"),
        "records": df.fillna("").to_dict(orient="records")
    }
