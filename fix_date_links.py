#!/usr/bin/env python3
import os
import re

def get_relative_path(from_file, to_path):
    """Convert /2012/MM/DD/post to ../../../2012/MM/DD/post"""
    to_path_clean = to_path.lstrip('/')
    if not to_path_clean.startswith('2012/'):
        return to_path
    to_path_clean = to_path_clean.rstrip('/')
    if to_path_clean.endswith('/index.html'):
        to_path_clean = to_path_clean[:-len('/index.html')]
    if to_path.endswith('/') or to_path.endswith('/index.html'):
        to_path_clean += '/'
    return '../../../' + to_path_clean

# Find all HTML files under 2012 directory
fixed_count = 0
for root, dirs, files in os.walk('/Users/adam/dev/web/hostgator3/2012'):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content

            # Fix both /2012/... and 2012/... patterns
            # Use a simple approach: find all href="..." with 2012 path
            def replace_func(match):
                quote = match.group(1)
                href = match.group(2)
                # Normalize to start with /
                if not href.startswith('/'):
                    href = '/' + href
                return f'href={quote}{get_relative_path(filepath, href)}{quote}'

            # Match any href that contains /2012/ or 2012/ with dates
            content = re.sub(r'href=(["\'])(/?2012/\d{2}/\d{2}/[^"\']*)\1', replace_func, content)

            # Write back if changed
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Fixed: {filepath}")
                fixed_count += 1

print(f"\nDone! Fixed {fixed_count} files.")
