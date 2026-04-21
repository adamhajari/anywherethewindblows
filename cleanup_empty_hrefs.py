#!/usr/bin/env python3
import os
import re

def clean_empty_hrefs(content):
    """Remove empty href attributes and problematic link elements"""

    # Remove canonical and shortlink meta elements with empty href
    content = re.sub(r'<link href=""" rel="(?:canonical|shortlink)"[^>]*/?>', '', content)

    # Remove oEmbed links with empty href
    content = re.sub(r'<link rel="alternate"[^>]*href=""" />', '', content)

    # Fix all remaining href=""" patterns (with extra quote) to href="#"
    # This handles all the comment-related links, timestamps, etc.
    content = content.replace('href="""', 'href="#"')

    return content

# Process all HTML files
fixed_count = 0
for root, dirs, files in os.walk('/Users/adam/dev/web/hostgator3'):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content
            content = clean_empty_hrefs(content)

            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                print(f"✓ Cleaned: {filepath}")

print(f"\nDone! Cleaned {fixed_count} files.")
