import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from govdata_app.backend.database import init_db
from govdata_app.backend.routes.api import api_router
from govdata_app.backend.services.source_directory import generate_sample_datasets

app = FastAPI(
    title="GovData Analyzer - Government Data Extraction & Analysis Platform",
    description="Full-stack enterprise platform for public government web scraping, API extraction, data cleaning, statistical analysis, interactive charts, and reporting.",
    version="1.0.0"
)

# Enable CORS for flexible integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main API routes
app.include_router(api_router)

# Frontend directories
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")
SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "samples")

# Mount static assets
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
def on_startup():
    init_db()
    generate_sample_datasets(SAMPLE_DIR)

@app.get("/")
def serve_index():
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "GovData Analyzer API is live. OpenAPI docs available at /docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("govdata_app.backend.main:app", host="127.0.0.1", port=8000, reload=True)
