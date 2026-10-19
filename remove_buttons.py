import os
import re

files_to_modify = ['RIGI_Nexus_Platform.html', 'rigi_nexus/index.html']

for file_path in files_to_modify:
    if not os.path.exists(file_path):
        continue

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove the header "Project Guide & Help" button
    header_button_pattern = r'<!-- Step-by-Step Project Guide Help Button -->\s*<button onclick="openHelpGuideModal\(\)".*?<\/button>'
    content = re.sub(header_button_pattern, '', content, flags=re.DOTALL)

    # 2. Remove the bottom right floating "STEP-BY-STEP GUIDE" button
    floating_fab_pattern = r'<!-- Floating Help & Guide Action Button \(FAB\) -->\s*<div class="fixed bottom-6 right-6 z-40">.*?<\/div>'
    content = re.sub(floating_fab_pattern, '', content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Removed buttons from {file_path}")

print("Both buttons successfully removed.")
