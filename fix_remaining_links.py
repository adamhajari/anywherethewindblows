#!/usr/bin/env python3
import os
import re
from pathlib import Path

def fix_file(filepath):
    """Fix broken links in an HTML file"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    original_content = content

    # 1. Fix /2012/... and ../../../2012/... patterns to use /anywherethewindblows/2012/...
    # Match both absolute and relative paths to 2012 posts

    # Pattern 1: Fix relative paths like ../../../2012/MM/DD/post/
    # Replace with /anywherethewindblows/2012/MM/DD/post/
    content = re.sub(
        r'href=(["\'])\.\./\.\./\.\./2012/(\d{2}/\d{2}/[^"\']*)\1',
        r'href=\1/anywherethewindblows/2012/\2\1',
        content
    )

    # Pattern 2: Fix malformed relative paths like ../../06/03/... to absolute paths
    # These came from misinterpreted relative paths
    content = re.sub(
        r'href=(["\'])\.\./\.\./(\d{2}/\d{2}/[^"\']*)\1',
        r'href=\1/anywherethewindblows/2012/\2\1',
        content
    )

    # Pattern 3: Fix root-level /2012/... paths to /anywherethewindblows/2012/...
    content = re.sub(
        r'href=(["\'])/2012/(\d{2}/\d{2}/[^"\']*)\1',
        r'href=\1/anywherethewindblows/2012/\2\1',
        content
    )

    # Pattern 4: Fix root-level /about-us/ to /anywherethewindblows/about-us/
    content = re.sub(
        r'href=(["\'])/about-us/',
        r'href=\1/anywherethewindblows/about-us/',
        content
    )

    # Write back if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Process all HTML files
fixed_count = 0
for root, dirs, files in os.walk('/Users/adam/dev/web/hostgator3/'):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            if fix_file(filepath):
                print(f"✓ Fixed: {filepath}")
                fixed_count += 1

print(f"\nDone! Fixed {fixed_count} files.")
