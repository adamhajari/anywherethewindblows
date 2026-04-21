#!/usr/bin/env python3
import os
import re

def remove_query_links(content):
    """Remove WordPress query parameter links and clean up empty sections"""

    # Remove all query parameter links regardless of attribute order
    # Matches: <a ...href="/?tag=..." ...>text</a>, <a href="/?cat=..." ...>text</a>, etc.
    content = re.sub(r'<a[^>]*href="(?:/anywherethewindblows)?/\?(?:tag|cat|author)=[^"]*"[^>]*>[^<]*</a>', '', content)

    # Clean up leftover commas and spaces from removed links
    content = re.sub(r'and tagged \s*by', 'by', content)  # "and tagged by" -> "by" (if no tags)
    content = re.sub(r' in \s+ and tagged', ' and tagged', content)  # "in   and tagged" -> "and tagged"
    content = re.sub(r' in  by', ' by', content)  # "in  by" -> "by" (if no categories)
    content = re.sub(r'posted in \s+ and', 'posted', content)  # "posted in   and" -> "posted"
    content = re.sub(r'posted in  by', 'posted by', content)  # "posted in  by" -> "posted by"
    content = re.sub(r'by \s*\.', '.', content)  # "by ." -> "." (if no author)
    content = re.sub(r',\s*,', ',', content)  # Double commas
    content = re.sub(r' , ', ' ', content)  # Spaces around commas
    content = re.sub(r'\s+,', ',', content)  # Space before comma
    content = re.sub(r',\s*by', ' by', content)  # Comma before by
    content = re.sub(r'\s+and\s+$', ' ', content)  # Trailing "and"
    content = re.sub(r'  +', ' ', content)  # Multiple spaces to single space
    content = re.sub(r',\s+\n', '\n', content)  # Trailing comma before newline

    return content

# Process all HTML files
fixed_count = 0
total_removed = 0

for root, dirs, files in os.walk('/Users/adam/dev/web/hostgator3'):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content

            # Count query links before removal
            query_tags = len(re.findall(r'href="(?:/anywherethewindblows)?/\?(?:tag|cat|author)=[^"]*"', content))

            content = remove_query_links(content)

            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                total_removed += query_tags
                if query_tags > 0:
                    print(f"✓ Cleaned: {filepath} (removed {query_tags} links)")

print(f"\nDone! Cleaned {fixed_count} files and removed {total_removed} query parameter links.")
