"""
================================================================================
KAPILVASTU TRANSPARENCY WATCH - ROBUST PYQGIS REPROJECTION & GEOJSON EXPORT
================================================================================
Instructions:
1. Open QGIS (v3.22, v3.28 LTR, v3.34+).
2. Press Ctrl + Alt + P (or Plugins -> Python Console).
3. Click the 'Show Editor' icon (notepad icon) in the Python console toolbar.
4. Paste this script, adjust INPUT_PATH if needed, and click the Green Run button.
================================================================================
"""

import os
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsVectorFileWriter,
    QgsMessageLog,
    Qgis
)
import processing

# -----------------------------------------------------------------------------
# 1. PATH CONFIGURATION (Windows / macOS / Linux auto-handling)
# -----------------------------------------------------------------------------
# You can set an absolute path or point to your desktop directory:
DEFAULT_DIR = os.path.expanduser("~/OneDrive/Desktop/sdrok2080/clean-repo")
if not os.path.exists(DEFAULT_DIR):
    DEFAULT_DIR = os.path.expanduser("~/Desktop")

# Replace with your actual shapefile path
INPUT_SHP = os.path.join(DEFAULT_DIR, "kapilvastu_ward_boundary.shp")

# Output GeoJSON directory & file
OUTPUT_DIR = os.path.join(DEFAULT_DIR, "exported_geojson")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_GEOJSON = os.path.join(OUTPUT_DIR, "kapilvastu_wards_wgs84.geojson")

print("=" * 65)
print(f"Target Input Shapefile : {INPUT_SHP}")
print(f"Target Output GeoJSON  : {OUTPUT_GEOJSON}")
print("=" * 65)

# -----------------------------------------------------------------------------
# 2. FILE VERIFICATION CHECK
# -----------------------------------------------------------------------------
if not os.path.exists(INPUT_SHP):
    print(f"\n[!] WARNING: File not found at '{INPUT_SHP}'.")
    print("    Please check the directory or update the 'INPUT_SHP' variable at the top.")
    print("    Ensure all companion files (.shp, .shx, .dbf, .prj) are present.\n")
else:
    # -------------------------------------------------------------------------
    # 3. LOAD VECTOR LAYER
    # -------------------------------------------------------------------------
    layer = QgsVectorLayer(INPUT_SHP, "Kapilvastu_Wards", "ogr")

    if not layer.isValid():
        print("[-] Error: Layer is invalid or cannot be read by OGR.")
        print("    Ensure the .shp file is not locked by another application and .dbf is intact.")
    else:
        # Register layer into QGIS Map Canvas
        QgsProject.instance().addMapLayer(layer)
        source_crs = layer.crs().authid() or "Unknown CRS"
        feature_count = layer.featureCount()
        geom_type = layer.geometryType()
        print(f"[✓] Successfully loaded into QGIS Canvas: {layer.name()}")
        print(f"    - Native CRS       : {source_crs}")
        print(f"    - Feature Count    : {feature_count}")

        # Check for missing .prj
        if not layer.crs().isValid():
            print("[!] Warning: Layer has no valid CRS definition (.prj missing).")
            print("    Assuming Nepal MUTM Zone 84 (EPSG:5233) or WGS 84.")

        # ---------------------------------------------------------------------
        # 4. GEOMETRY SANITIZATION (Fix slivers, unclosed rings & self-intersections)
        # ---------------------------------------------------------------------
        print("[*] Running geometry validation & auto-repair...")
        fixed_result = processing.run("native:fixgeometries", {
            'INPUT': layer,
            'OUTPUT': 'memory:'
        })
        repaired_layer = fixed_result['OUTPUT']

        # ---------------------------------------------------------------------
        # 5. REPROJECT TO WGS 84 (EPSG:4326)
        # ---------------------------------------------------------------------
        target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        print(f"[*] Reprojecting features to {target_crs.authid()} (WGS 84)...")

        reprojected_result = processing.run("native:reprojectlayer", {
            'INPUT': repaired_layer,
            'TARGET_CRS': target_crs,
            'OUTPUT': 'memory:'
        })
        reprojected_layer = reprojected_result['OUTPUT']

        # ---------------------------------------------------------------------
        # 6. EXPORT WEB-OPTIMIZED GEOJSON (5-decimal precision, bounding box)
        # ---------------------------------------------------------------------
        print(f"[*] Exporting web-optimized GeoJSON to: {OUTPUT_GEOJSON}")
        
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = "GeoJSON"
        save_options.fileEncoding = "UTF-8"
        save_options.layerOptions = [
            "COORDINATE_PRECISION=5", # ~1.1m resolution, reduces GeoJSON file size by 60%
            "WRITE_BBOX=YES",
            "RFC7946=YES"             # Modern GeoJSON standard compliance
        ]

        transform_context = QgsProject.instance().transformContext()
        err, error_msg = QgsVectorFileWriter.writeAsVectorFormatV3(
            reprojected_layer,
            OUTPUT_GEOJSON,
            transform_context,
            save_options
        )

        if err == QgsVectorFileWriter.NoError:
            file_size_kb = os.path.getsize(OUTPUT_GEOJSON) / 1024
            print("\n" + "=" * 65)
            print("✓ EXPORT SUCCESSFUL!")
            print(f"  Output Path : {OUTPUT_GEOJSON}")
            print(f"  File Size   : {file_size_kb:.2f} KB")
            print(f"  Features    : {reprojected_layer.featureCount()}")
            print("=" * 65)
            print("\nNext Step:")
            print("  Drag and drop 'kapilvastu_wards_wgs84.geojson' into the")
            print("  'Data Ingestion & QGIS' tab in KapilvastuTransparencyWatch.html!")
        else:
            print(f"[-] Export failed with error code {err}: {error_msg}")
