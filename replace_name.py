import os

files_to_update = [
    'RIGI_Nexus_Platform.html',
    'rigi_nexus/index.html',
    'rigi_nexus/app.js',
    'rigi_nexus/server.py',
    'rigi_nexus/README.md',
    'rigi_nexus/database.py',
    'rigi_nexus/seed_data.py'
]

for file_path in files_to_update:
    if not os.path.exists(file_path):
        continue
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace uppercase and standard forms accurately
    content = content.replace('RI-GI NEXUS', 'KMC-HSSD')
    content = content.replace('RI-GI Nexus', 'KMC-HSSD')
    content = content.replace('RI-GI', 'KMC-HSSD')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Updated {file_path}")

print("Replacement of RI-GI Nexus with KMC-HSSD completed successfully across all platform files.")
