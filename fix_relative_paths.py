#!/usr/bin/env python3
import os
import re

def fix_relative_paths(content, filepath):
    """Fix relative paths in post files that resolve incorrectly"""

    # Pattern: ../../../2012/MM/DD/... should be ../../MM/DD/...
    # This applies to links within the 2012 directory

    # Fix blog post links: ../../../2012/MM/DD/post-name/ -> ../../MM/DD/post-name/
    content = re.sub(
        r'href="\.\./\.\./\.\./2012/(\d{2}/\d{2}/[^"]*)"',
        r'href="../../\1"',
        content
    )

    return content

# Process all HTML files in the 2012 directory
fixed_count = 0
total_fixed = 0

for root, dirs, files in os.walk('/Users/adam/dev/web/hostgator3/2012'):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content

            # Count instances before fixing
            instances = len(re.findall(r'href="\.\./\.\./\.\./2012/\d{2}/\d{2}/', content))

            content = fix_relative_paths(content, filepath)

            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                total_fixed += instances
                if instances > 0:
                    print(f"✓ Fixed: {filepath} (corrected {instances} paths)")

print(f"\nDone! Fixed {fixed_count} files and corrected {total_fixed} relative paths.")
