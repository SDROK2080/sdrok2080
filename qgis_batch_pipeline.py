from qgis.core import (
    QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem,
    QgsVectorFileWriter, QgsFeatureRequest
)
import processing, os

# Configure workspace export folder (handles Windows OneDrive and standard Desktop paths)
primary_dir = os.path.expanduser("~/OneDrive/Desktop/sdrok2080/clean-repo")
fallback_dir = os.path.expanduser("~/Desktop/sdrok2080/clean-repo")
BASE_DIR = primary_dir if os.path.exists(primary_dir) else fallback_dir

OUTPUT_DIR = os.path.join(BASE_DIR, "exported_geojson")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Layers to batch process and export
layers_to_export = [
    {"layer_name": "Kapilvastu_Ward_Boundaries", "out_name": "kapilvastu_wards.geojson"},
    {"layer_name": "Kapilvastu_Infrastructure_Contracts", "out_name": "kapilvastu_contracts.geojson"}
]

print("=== Starting QGIS Pipeline for Kapilvastu Transparency Watch ===")
print(f"Destination Directory: {OUTPUT_DIR}\n")

for item in layers_to_export:
    lyr_match = QgsProject.instance().mapLayersByName(item["layer_name"])
    if not lyr_match:
        print(f"[-] Layer '{item['layer_name']}' not found in QGIS Canvas. Skipping.")
        print(f"    Tip: In QGIS, rename the target layer in your Layers panel to '{item['layer_name']}'.")
        continue
    
    layer = lyr_match[0]
    out_path = os.path.join(OUTPUT_DIR, item["out_name"])
    print(f"[*] Processing: {item['layer_name']} ({layer.featureCount()} features, Source CRS: {layer.crs().authid()})")
    
    # Step 1: Geometry Repair (Resolves topological self-intersections and slivers)
    fixed = processing.run("native:fixgeometries", {'INPUT': layer, 'OUTPUT': 'memory:'})['OUTPUT']
    
    # Step 2: Reproject to WGS 84 (EPSG:4326)
    reprojected = processing.run("native:reprojectlayer", {
        'INPUT': fixed,
        'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
        'OUTPUT': 'memory:'
    })['OUTPUT']
    
    # Step 3: Write GeoJSON with 5-decimal precision (~1.1 meter accuracy, reduces file size by ~60%)
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "GeoJSON"
    save_options.fileEncoding = "UTF-8"
    save_options.layerOptions = [
        "COORDINATE_PRECISION=5",
        "WRITE_BBOX=YES",
        "RFC7946=YES"
    ]
    
    err, msg = QgsVectorFileWriter.writeAsVectorFormatV3(
        reprojected, out_path, QgsProject.instance().transformContext(), save_options
    )
    
    if err == QgsVectorFileWriter.NoError:
        size_kb = os.path.getsize(out_path) / 1024
        print(f"[✓] Exported: {item['out_name']} | Size: {size_kb:.2f} KB | Features: {reprojected.featureCount()}\n")
    else:
        print(f"[✗] Export failed for {item['out_name']}: {msg}\n")

print("=== Pipeline Complete! Ingest exported GeoJSON into KapilvastuTransparencyWatch.html ===")
