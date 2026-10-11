import fitz

import os
pdf_path = 'main.pdf' if os.path.exists('main.pdf') else 'naacl/main.pdf'
doc = fitz.open(pdf_path)
print("Total pages:", len(doc))
import sys
sys.stdout.reconfigure(encoding='utf-8')
for i in range(len(doc)):
    text = doc[i].get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    first_two = lines[:2] if len(lines) >= 2 else lines
    last_two = lines[-2:] if len(lines) >= 2 else lines
    print(f"Page {i+1} ({len(lines)} lines): first={first_two}, last={last_two}")
