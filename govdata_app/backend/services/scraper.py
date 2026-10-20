import re
import urllib.parse
import urllib.robotparser
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
from govdata_app.backend.services.security import validate_public_url

USER_AGENT = "GovDataAnalyzer/1.0 (+https://github.com/nepalgovernment/govdata-analyzer; Public Data Research)"

def check_robots_allowed(url: str) -> bool:
    """
    Checks robots.txt for the given host to respect site policies.
    """
    try:
        parsed = urllib.parse.urlsplit(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        # If robots.txt cannot be retrieved or parsed, default to allowing with caution
        return True

def scrape_web_tables(url: str, max_tables: int = 10) -> Dict[str, Any]:
    """
    Extracts HTML tables and structured data from permitted public websites.
    """
    is_valid, err_msg = validate_public_url(url)
    if not is_valid:
        raise ValueError(f"Security Alert: {err_msg}")

    # Check robots.txt
    robots_permitted = check_robots_allowed(url)
    if not robots_permitted:
        raise PermissionError("Access restricted: Target website's robots.txt disallows automated data extraction on this path.")

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ne;q=0.8"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15, stream=True)
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to source website: {str(e)}")

    if response.status_code != 200:
        raise ConnectionError(f"HTTP error {response.status_code} received from target website.")

    # Limit response read size to 10MB to prevent memory exhaustion
    content = response.raw.read(10 * 1024 * 1024, decode_content=True)
    soup = BeautifulSoup(content, "html.parser")

    # Page metadata
    title_tag = soup.find("title")
    page_title = title_tag.get_text(strip=True) if title_tag else "Government Web Page"

    # Headings
    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"]) if h.get_text(strip=True)][:10]

    # Tables extraction
    raw_tables = soup.find_all("table")
    extracted_tables: List[Dict[str, Any]] = []

    for idx, table in enumerate(raw_tables[:max_tables]):
        table_rows = table.find_all("tr")
        if not table_rows:
            continue

        header_cols = []
        # Find headers from the first row or th elements
        first_row_ths = table.find_all("th")
        if first_row_ths:
            header_cols = [th.get_text(" ", strip=True) for th in first_row_ths]
        else:
            first_tr_tds = table_rows[0].find_all(["td", "th"])
            header_cols = [col.get_text(" ", strip=True) for col in first_tr_tds]

        # Clean header names
        cleaned_headers = []
        for i, h in enumerate(header_cols):
            clean_name = re.sub(r"\s+", " ", h).strip()
            if not clean_name:
                clean_name = f"Column_{i+1}"
            cleaned_headers.append(clean_name)

        rows_data = []
        start_row = 1 if not first_row_ths and len(table_rows) > 1 else 0
        if first_row_ths and table_rows and table_rows[0].find_all("th"):
            start_row = 1

        for row in table_rows[start_row:]:
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            row_dict = {}
            for col_idx, cell in enumerate(cells):
                col_name = cleaned_headers[col_idx] if col_idx < len(cleaned_headers) else f"Column_{col_idx+1}"
                # Append to header list if columns exceed previous headers
                if col_idx >= len(cleaned_headers):
                    cleaned_headers.append(col_name)
                row_dict[col_name] = cell.get_text(" ", strip=True)
            if row_dict and any(v for v in row_dict.values()):
                rows_data.append(row_dict)

        if rows_data:
            extracted_tables.append({
                "table_index": idx,
                "headers": cleaned_headers,
                "total_rows": len(rows_data),
                "rows_sample": rows_data[:100],  # preview
                "all_rows": rows_data
            })

    # Public download links detected
    download_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full_url = urllib.parse.urljoin(url, href)
        if any(full_url.lower().endswith(ext) for ext in [".csv", ".xlsx", ".xls", ".pdf", ".json", ".zip"]):
            download_links.append({
                "text": a.get_text(strip=True) or full_url.split("/")[-1],
                "url": full_url
            })

    return {
        "page_title": page_title,
        "url": url,
        "headings": headings,
        "tables_found": len(extracted_tables),
        "tables": extracted_tables,
        "detected_data_links": download_links[:20]
    }
