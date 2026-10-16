# get_drawer_css.py
import sys

with open('KMCHSSDTestProtect.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

with open('extracted_css.txt', 'w', encoding='utf-8') as out:
    for idx in range(44, 180):
        out.write(f'{idx+1}: {lines[idx]}')

print("Extracted CSS lines 45 to 180")
